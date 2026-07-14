#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Toobey本草食蔬 - 批量下载全部蔬菜图片（后台运行）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import download_images as di
import json, time, re

JSON_PATH = di.JSON_PATH
IMG_DIR = di.IMG_DIR

# 加载蔬菜列表
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    veggies = json.load(f)

print(f'开始下载 {len(veggies)} 种蔬菜图片...')
print(f'保存到: {IMG_DIR}')
print()

success = 0
failed = []
batch_size = 30

for i, veg in enumerate(veggies):
    name = veg['name']
    result = di.download_veggie_image(name)
    
    if result:
        success += 1
    else:
        failed.append(name)
    
    if (i + 1) % 5 == 0 or result == False or i == len(veggies) - 1:
        pct = (i + 1) / len(veggies) * 100
        print(f'  [{i+1}/{len(veggies)}] {pct:.0f}% 成功={success} 失败={len(failed)}')
    
    if (i + 1) % batch_size == 0 and i + 1 < len(veggies):
        print(f'  --- 暂停 2 秒 ---')
        time.sleep(2)

print(f'\n{"="*60}')
print(f'下载完成！成功: {success}/{len(veggies)}, 失败: {len(failed)}')
if failed:
    print(f'失败列表: {failed}')
    with open(os.path.join(os.path.dirname(JSON_PATH), 'dl_failed.txt'), 'w') as f:
        f.write('\n'.join(failed))

# 更新JSON添加图片字段
updated = 0
for veg in veggies:
    name = veg['name']
    img_name = di.safe_filename(name) + '.jpg'
    img_path = os.path.join(IMG_DIR, img_name)
    veg['image'] = img_name if os.path.isfile(img_path) else ''
    if veg['image']:
        updated += 1

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(veggies, f, ensure_ascii=False, indent=2)
print(f'JSON已更新：{updated} 种有图片')
