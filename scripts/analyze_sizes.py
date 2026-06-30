import requests
r = requests.get('https://api.github.com/repos/dechang64/dgy-treehole/releases/tags/v1.0-music', timeout=30)
assets = r.json().get('assets', [])
print('v1 release 短 mp3 (< 1.7 MB, < 90s):')
for a in sorted(assets, key=lambda x: x['size']):
    if a['size'] < 1_700_000 and a['name'].endswith('.mp3'):
        print(f'  {a["name"]:40s} {a["size"]/1024/1024:6.2f} MB')
print()
print('v1 release 边界 1.7-2.5 MB (90-130s):')
for a in sorted(assets, key=lambda x: x['size']):
    if 1_700_000 <= a['size'] < 2_500_000 and a['name'].endswith('.mp3'):
        print(f'  {a["name"]:40s} {a["size"]/1024/1024:6.2f} MB')
print()
print('v1 release 正常 (>= 2.5 MB, >= 130s):')
normal_count = 0
for a in assets:
    if a['size'] >= 2_500_000 and a['name'].endswith('.mp3'):
        normal_count += 1
print(f'  共 {normal_count} 段')
