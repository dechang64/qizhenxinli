"""SQLite 数据库层 — 匿名社交、情绪统计、树洞记录

设计原则：
- 所有用户数据匿名，不存储任何个人标识
- 树洞内容不持久化（释放即消失），仅统计聚合数据
- 社交帖子匿名存储，仅保留内容+情绪标签+时间戳
- 情绪统计用于联邦学习聚合

track-3 升级（共鸣社交）：
- posts 表新增 source / session_id 列（来源：manual / treehole）
- 新增 post_comments / post_warm_words / post_reports 三张社交表
- 树洞 track-2 会调用 create_post(content, emotion, scene, source="treehole", session_id=...)
- 树洞 track-2 会通过 session_state 给本会话设 session_id
"""

import sqlite3
import json
import time
import threading
import html
from contextlib import contextmanager
from core.config import DB_PATH, EMOTIONS

_lock = threading.Lock()
_conn = None  # 单例连接（内存数据库必须共享同一个连接）

def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        if DB_PATH != ":memory:":
            _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn

@contextmanager
def get_db():
    conn = _get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    # 内存数据库不关闭连接，保持单例

def init_db():
    """建表（幂等）"""
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                emotion TEXT NOT NULL,
                scene TEXT DEFAULT '',
                resonates INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_posts_emotion ON posts(emotion);
            CREATE INDEX IF NOT EXISTS idx_posts_scene ON posts(scene);
            CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);

            CREATE TABLE IF NOT EXISTS treehole_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT NOT NULL,
                emotion TEXT NOT NULL,
                word_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_th_stats_created ON treehole_stats(created_at);

            CREATE TABLE IF NOT EXISTS emotion_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_emotions TEXT NOT NULL,
                scene TEXT DEFAULT '',
                message_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_emotion_snap_created ON emotion_snapshots(created_at);

            CREATE TABLE IF NOT EXISTS fl_rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                round_num INTEGER NOT NULL,
                aggregated_emotions TEXT NOT NULL,
                client_count INTEGER DEFAULT 0,
                entropy_weights TEXT DEFAULT '{}',
                created_at REAL NOT NULL
            );
        """)

        # ── track-3 升级：posts 表新增 source / session_id 列（幂等） ──
        # 老数据库（已部署在 Streamlit Cloud 上）需要 ALTER TABLE 兼容
        for alter_sql in [
            "ALTER TABLE posts ADD COLUMN source TEXT DEFAULT 'manual'",
            "ALTER TABLE posts ADD COLUMN session_id TEXT DEFAULT ''",
        ]:
            try:
                db.execute(alter_sql)
            except Exception:
                # 列已存在，SQLite 会抛 "duplicate column name"，吞掉
                pass

        # ── track-3 升级：社交三张表 ──
        db.executescript("""
            CREATE TABLE IF NOT EXISTS post_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                session_id TEXT DEFAULT '',
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_post_comments_post ON post_comments(post_id);
            CREATE INDEX IF NOT EXISTS idx_post_comments_created ON post_comments(created_at);

            CREATE TABLE IF NOT EXISTS post_warm_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                session_id TEXT DEFAULT '',
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_post_warm_post ON post_warm_words(post_id);
            CREATE INDEX IF NOT EXISTS idx_post_warm_created ON post_warm_words(created_at);

            CREATE TABLE IF NOT EXISTS post_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                session_id TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_post_reports_post ON post_reports(post_id);

            CREATE INDEX IF NOT EXISTS idx_posts_session ON posts(session_id);
            CREATE INDEX IF NOT EXISTS idx_warm_session ON post_warm_words(session_id);

            -- TRACK-1-HEALING-CORE: 树洞疗愈反馈（1-5 星评分，闭环）
            -- 字段：id, session_id, emotion, score, method, created_at
            CREATE TABLE IF NOT EXISTS treehole_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                emotion TEXT DEFAULT '',
                score INTEGER NOT NULL,
                method TEXT DEFAULT '',
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_th_fb_session ON treehole_feedback(session_id);
            CREATE INDEX IF NOT EXISTS idx_th_fb_created ON treehole_feedback(created_at);
        """)


# 模块加载时自动建表（内存数据库必须在使用前初始化）
init_db()


# ═══════════════════════════════════════════════════════════
#  匿名社交
# ═══════════════════════════════════════════════════════════

def create_post(content: str, emotion: str, scene: str = "",
                source: str = "manual", session_id: str = "") -> int:
    """创建匿名帖子。

    老调用 create_post(content, emotion, scene) 仍然兼容（source/session_id 默认值）。
    track-2 树洞会调用 create_post(content, emotion, scene, source="treehole", session_id=session_id)。
    """
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO posts (content, emotion, scene, source, session_id, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (html.escape(content[:500]), emotion, scene, source, session_id, time.time())
            )
            return cur.lastrowid

def get_posts(limit: int = 50, emotion: str = "", scene: str = "") -> list[dict]:
    with get_db() as db:
        q = "SELECT * FROM posts"
        params = []
        conditions = []
        if emotion:
            conditions.append("emotion = ?")
            params.append(emotion)
        if scene:
            conditions.append("scene = ?")
            params.append(scene)
        if conditions:
            q += " WHERE " + " AND ".join(conditions)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = db.execute(q, params).fetchall()
        return [dict(r) for r in rows]

def resonate_post(post_id: int) -> bool:
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "UPDATE posts SET resonates = resonates + 1 WHERE id = ?", (post_id,)
            )
            return cur.rowcount > 0

def get_emotion_distribution(days: int = 7) -> dict[str, int]:
    """获取最近N天的情绪分布"""
    with get_db() as db:
        cutoff = time.time() - days * 86400
        rows = db.execute(
            "SELECT emotion, COUNT(*) as cnt FROM posts WHERE created_at > ? GROUP BY emotion",
            (cutoff,)
        ).fetchall()
        return {r["emotion"]: r["cnt"] for r in rows}


# ═══════════════════════════════════════════════════════════
#  track-3：共鸣社交 — 评论 / 温暖留言 / 举报 / 我的 / 一签
# ═══════════════════════════════════════════════════════════

def get_post_by_id(post_id: int) -> dict | None:
    """按 ID 查单个帖子（None 表示不存在）"""
    with get_db() as db:
        row = db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
        return dict(row) if row else None


def add_comment(post_id: int, content: str, session_id: str = "") -> int:
    """添加评论，返回评论 ID"""
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO post_comments (post_id, content, session_id, created_at) "
                "VALUES (?, ?, ?, ?)",
                (post_id, html.escape(content[:300]), session_id, time.time())
            )
            return cur.lastrowid


def get_comments(post_id: int, limit: int = 5) -> list[dict]:
    """获取帖子的评论（按时间倒序）"""
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM post_comments WHERE post_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (post_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def add_warm_word(post_id: int, content: str, session_id: str = "") -> int:
    """添加温暖留言，同时自动 +1 共鸣数（原子操作：两步在同一连接上执行）"""
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO post_warm_words (post_id, content, session_id, created_at) "
                "VALUES (?, ?, ?, ?)",
                (post_id, html.escape(content[:200]), session_id, time.time())
            )
            wid = cur.lastrowid
            # 自动给帖子 +1 共鸣（"共鸣+留言"是升级版共鸣）
            db.execute(
                "UPDATE posts SET resonates = resonates + 1 WHERE id = ?", (post_id,)
            )
            return wid


def get_warm_words(post_id: int, limit: int = 5) -> list[dict]:
    """获取帖子的温暖留言（按时间倒序）"""
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM post_warm_words WHERE post_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (post_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def add_report(post_id: int, session_id: str = "", reason: str = "") -> int:
    """添加举报记录，返回举报 ID"""
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO post_reports (post_id, session_id, reason, created_at) "
                "VALUES (?, ?, ?, ?)",
                (post_id, session_id, reason, time.time())
            )
            return cur.lastrowid


def get_my_posts(session_id: str, limit: int = 20) -> list[dict]:
    """获取指定 session_id 发布的所有帖子（"我发布的"）"""
    if not session_id:
        return []
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM posts WHERE session_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_warm_words_for_user(session_id: str, limit: int = 10) -> list[dict]:
    """获取我收到的温暖留言（我发布的帖子收到的温暖留言）"""
    if not session_id:
        return []
    with get_db() as db:
        rows = db.execute(
            "SELECT w.*, p.content AS post_content, p.emotion AS post_emotion "
            "FROM post_warm_words w "
            "JOIN posts p ON p.id = w.post_id "
            "WHERE p.session_id = ? AND w.session_id != ? "
            "ORDER BY w.created_at DESC LIMIT ?",
            (session_id, session_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_top_posts_by_resonates(limit: int = 5, days: int = 7) -> list[dict]:
    """获取近 N 天共鸣数最高的帖子（"今日一签"用）"""
    with get_db() as db:
        cutoff = time.time() - days * 86400
        rows = db.execute(
            "SELECT * FROM posts WHERE created_at > ? AND resonates > 0 "
            "ORDER BY resonates DESC, created_at DESC LIMIT ?",
            (cutoff, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_post_count_by_emotion(days: int = 7) -> dict[str, int]:
    """近 N 天每个情绪的帖子数（情绪分布图用，复用 get_emotion_distribution 的同款逻辑）"""
    return get_emotion_distribution(days=days)


def get_post_count(session_id: str) -> int:
    """我发布的帖子数（用于匿名等级计算）"""
    if not session_id:
        return 0
    with get_db() as db:
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM posts WHERE session_id = ?", (session_id,)
        ).fetchone()
        return row["cnt"] or 0 if row else 0


# ═══════════════════════════════════════════════════════════
#  树洞统计（不存储内容，仅统计）
# ═══════════════════════════════════════════════════════════

def record_treehole(method: str, emotion: str, word_count: int = 0):
    with _lock:
        with get_db() as db:
            db.execute(
                "INSERT INTO treehole_stats (method, emotion, word_count, created_at) VALUES (?, ?, ?, ?)",
                (method, emotion, word_count, time.time())
            )

def get_treehole_stats(days: int = 7) -> dict:
    with get_db() as db:
        cutoff = time.time() - days * 86400
        rows = db.execute(
            "SELECT method, COUNT(*) as cnt, SUM(word_count) as total_words "
            "FROM treehole_stats WHERE created_at > ? GROUP BY method",
            (cutoff,)
        ).fetchall()
        return {r["method"]: {"count": r["cnt"], "total_words": r["total_words"] or 0} for r in rows}


# ═══════════════════════════════════════════════════════════
#  情绪快照（用于联邦学习）
# ═══════════════════════════════════════════════════════════

def save_emotion_snapshot(emotions: dict, scene: str = "", message_count: int = 0):
    """保存一次会话的情绪统计快照（不存储原始消息）"""
    with _lock:
        with get_db() as db:
            db.execute(
                "INSERT INTO emotion_snapshots (session_emotions, scene, message_count, created_at) VALUES (?, ?, ?, ?)",
                (json.dumps(emotions, ensure_ascii=False), scene, message_count, time.time())
            )

def get_recent_snapshots(limit: int = 100) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM emotion_snapshots ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["session_emotions"] = json.loads(d["session_emotions"])
            result.append(d)
        return result


# ═══════════════════════════════════════════════════════════
#  联邦学习轮次记录
# ═══════════════════════════════════════════════════════════

def save_fl_round(round_num: int, aggregated: dict, client_count: int, entropy_weights: dict):
    with _lock:
        with get_db() as db:
            db.execute(
                "INSERT INTO fl_rounds (round_num, aggregated_emotions, client_count, entropy_weights, created_at) VALUES (?, ?, ?, ?, ?)",
                (round_num, json.dumps(aggregated, ensure_ascii=False), client_count,
                 json.dumps(entropy_weights, ensure_ascii=False), time.time())
            )

def get_fl_rounds(limit: int = 20) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM fl_rounds ORDER BY round_num DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["aggregated_emotions"] = json.loads(d["aggregated_emotions"])
            d["entropy_weights"] = json.loads(d["entropy_weights"])
            result.append(d)
        return result


# ═══════════════════════════════════════════════════════════
#  TRACK-1-HEALING-CORE: 树洞疗愈反馈（1-5 星评分，闭环）
# ═══════════════════════════════════════════════════════════

def record_treehole_feedback(session_id: str, score: int, emotion: str = "",
                             method: str = "") -> int:
    """记录一次树洞疗愈回复的反馈评分。

    TRACK-1-HEALING-CORE: 1-5 星反馈入口，5 个评分 button 都调这个。

    Args:
        session_id: 会话 ID（来自 st.session_state.session_id）
        score: 1-5 星
        emotion: 当时检测到的情绪标签
        method: 释放方式（wind/lake/petal/smoke/silent）

    Returns:
        新插入行的 id
    """
    with _lock:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO treehole_feedback (session_id, emotion, score, method, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, emotion, int(score), method, time.time())
            )
            return cur.lastrowid


def get_feedback_stats(days: int = 7) -> dict:
    """汇总近 N 天的反馈：平均分 + 各分数计数。TRACK-1-HEALING-CORE 配套。"""
    with get_db() as db:
        cutoff = time.time() - days * 86400
        rows = db.execute(
            "SELECT score, COUNT(*) as cnt, AVG(score) as avg_score "
            "FROM treehole_feedback WHERE created_at > ? GROUP BY score",
            (cutoff,),
        ).fetchall()
        total = sum(r["cnt"] for r in rows)
        avg = 0.0
        if total > 0:
            avg = sum(r["score"] * r["cnt"] for r in rows) / total
        by_score = {r["score"]: r["cnt"] for r in rows}
        return {"total": total, "avg_score": round(avg, 2), "by_score": by_score}
