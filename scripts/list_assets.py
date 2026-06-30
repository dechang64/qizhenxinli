import requests
r = requests.get('https://api.github.com/repos/dechang64/dgy-treehole/releases/tags/v1.0-music', timeout=30)
data = r.json()
assets = data.get('assets', [])
print(f'total: {len(assets)}')
ascii_assets = [a for a in assets if all(ord(c) < 128 for c in a['name'])]
print(f'ASCII 资产: {len(ascii_assets)}')
for a in sorted(ascii_assets, key=lambda x: x['name']):
    print(f"  {a['name']:40s} {a['size']/1024/1024:6.2f} MB")
print('---')
# 找 ouxiangxie / ouxxiangxie
for a in assets:
    if 'iangxie' in a['name']:
        print(f"  found: {a['name']} {a['size']/1024/1024:.2f} MB")
