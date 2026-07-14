#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toobey本草食蔬 - 蔬菜图片下载器
为每种蔬菜从网络搜索并下载对应的实物照片
"""
import json, os, time, re
import requests
from urllib.parse import quote

IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'veggies_data.json')
FAIL_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_failed.txt')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

os.makedirs(IMG_DIR, exist_ok=True)

# 加载蔬菜列表
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    veggies = json.load(f)

print(f'共 {len(veggies)} 种蔬菜，开始下载图片...\n')

def safe_filename(name):
    """安全文件名"""
    s = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    return re.sub(r'[<>"|?*]', '', s)

def download_image(veggie_name, search_keyword=None, retries=2):
    """从Baidu图片搜索下载蔬菜图片"""
    keyword = search_keyword or veggie_name + ' 蔬菜 实物'
    fname = safe_filename(veggie_name) + '.jpg'
    fpath = os.path.join(IMG_DIR, fname)
    
    if os.path.isfile(fpath) and os.path.getsize(fpath) > 2000:
        return True  # 已存在
    
    url = f'https://image.baidu.com/search/flip?tn=baiduimage&word={quote(keyword)}&pn=0&rn=1'
    
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            
            # 从页面提取图片URL (百度图片的缩略图URL)
            import re as regex
            # 正则匹配objURL或thumbURL
            patterns = [
                r'"thumbURL":"([^"]+)"',
                r'"objURL":"([^"]+)"',
                r'"middleURL":"([^"]+)"',
                r'"hoverURL":"([^"]+)"',
            ]
            
            img_url = None
            for pat in patterns:
                matches = regex.findall(pat, r.text)
                if matches:
                    img_url = matches[0]
                    break
            
            if not img_url:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return False
            
            # 下载图片
            img_r = requests.get(img_url, headers=HEADERS, timeout=15)
            img_r.raise_for_status()
            
            with open(fpath, 'wb') as f:
                f.write(img_r.content)
            
            size = os.path.getsize(fpath)
            if size > 2000:
                return True
            else:
                os.remove(fpath)
                return False
                
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return False
    
    return False

# ── 分批下载 ──
success = 0
failed = []
batch_size = 20

for i, veg in enumerate(veggies):
    name = veg['name']
    # 使用蔬菜名 + '蔬菜' 或 '食材' 作为搜索词
    keyword = f"{name} 蔬菜 高清"
    
    # 对较常见蔬菜使用更精准的搜索词
    if name in ['白菜', '菠菜', '黄瓜', '番茄', '土豆', '辣椒']:
        keyword = f"{name} 蔬菜 高清 图片"
    
    result = download_image(name, keyword)
    
    if result:
        success += 1
        status = '✅'
    else:
        failed.append(name)
        status = '❌'
    
    if (i + 1) % 5 == 0 or i == len(veggies) - 1 or result == False:
        print(f'  [{i+1}/{len(veggies)}] {status} {name}')
    
    # 每批之间暂停避免被屏蔽
    if (i + 1) % batch_size == 0:
        print(f'  --- 已下载 {success} 张，暂停 3 秒 ---\n')
        time.sleep(3)

# ── 结果汇总 ──
print(f'\n{"="*50}')
print(f'下载完成！成功: {success}, 失败: {len(failed)}')
if failed:
    with open(FAIL_LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(failed))
    print(f'失败列表已保存: {FAIL_LOG}')

# ── 更新JSON添加图片路径 ──
for veg in veggies:
    name = veg['name']
    img_name = safe_filename(name) + '.jpg'
    img_path = os.path.join(IMG_DIR, img_name)
    if os.path.isfile(img_path):
        veg['image'] = img_name
    else:
        veg['image'] = ''

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(veggies, f, ensure_ascii=False, indent=2)
print(f'JSON已更新，添加了图片文件名字段')
