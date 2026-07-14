#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Toobey本草食蔬 手机版HTML"""
import json, os, base64, re

JSON_PATH = r'C:\Users\Administrator\Desktop\本草时蔬\build_ebook\veggies_data.json'
IMG_DIR = r'C:\Users\Administrator\Desktop\本草时蔬\build_ebook\images'
OUTPUT = r'C:\Users\Administrator\Desktop\本草时蔬\Toobey本草食蔬.html'

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    veggies = json.load(f)

# 将图片转为 base64 嵌入（仅限小于 200KB 的图片）
def img_to_b64(img_name):
    path = os.path.join(IMG_DIR, img_name)
    if not os.path.isfile(path):
        return ''
    size = os.path.getsize(path)
    if size > 200 * 1024:  # 超过200KB不嵌入
        return ''
    with open(path, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(img_name)[1].lower()
    mime = 'image/jpeg' if ext in ('.jpg', '.jpeg') else 'image/png'
    return f'data:{mime};base64,{base64.b64encode(data).decode()}'

# 为每条蔬菜生成内联图片数据
for v in veggies:
    img_name = v.get('image', '')
    b64 = img_to_b64(img_name) if img_name else ''
    v['_img'] = b64

# 构建安全的JS数据字符串
def js_str(s):
    return json.dumps(s, ensure_ascii=False)

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>Toobey本草食蔬</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --cold:#3b82f6;--cool:#60a5fa;--neutral:#22c55e;
  --warm:#f59e0b;--hot:#ef4444;
  --bg:#f5f0eb;--card:#ffffff;--text:#1e293b;--muted:#64748b;
  --radius:12px;--shadow:0 2px 8px rgba(0,0,0,.08);
}
body{font-family:-apple-system,BlinkMacSystemFont,"Microsoft YaHei","PingFang SC",sans-serif;background:var(--bg);color:var(--text);-webkit-tap-highlight-color:transparent}
/* ── Header ── */
.header{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:16px 16px 12px;position:sticky;top:0;z-index:100}
.header h1{font-size:18px;font-weight:700;letter-spacing:1px}
.header p{font-size:11px;color:#94a3b8;margin-top:2px}
/* ── Search ── */
.search-bar{display:flex;gap:8px;margin-top:10px}
.search-bar input{flex:1;padding:8px 12px;border:0;border-radius:8px;font-size:14px;outline:0;background:#475569;color:#fff}
.search-bar input::placeholder{color:#94a3b8}
.search-bar input:focus{background:#334155}
.search-bar button{padding:8px 16px;border:0;border-radius:8px;background:#10b981;color:#fff;font-size:14px;font-weight:600;white-space:nowrap}
/* ── Category tabs ── */
.tabs{display:flex;gap:6px;padding:10px 12px;overflow-x:auto;scrollbar-width:none;background:var(--bg);position:sticky;top:60px;z-index:99}
.tabs::-webkit-scrollbar{display:none}
.tab{padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap;border:1.5px solid #cbd5e1;background:#fff;color:var(--text);cursor:pointer;transition:all .2s}
.tab.active{color:#fff;border-color:transparent}
.tab.cold.active{background:var(--cold)}
.tab.cool.active{background:var(--cool)}
.tab.neutral.active{background:var(--neutral)}
.tab.warm.active{background:var(--warm)}
.tab.hot.active{background:var(--hot)}
.tab .count{font-size:10px;opacity:.7;margin-left:3px}
/* ── Veggie grid ── */
.list{padding:6px 12px 80px;display:grid;grid-template-columns:1fr 1fr;gap:8px}
.card{background:var(--card);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);cursor:pointer;transition:transform .15s}
.card:active{transform:scale(.96)}
.card-img{width:100%;height:120px;object-fit:cover;display:block;background:#e2e8f0}
.card-body{padding:8px 10px 10px}
.card-name{font-size:14px;font-weight:700}
.card-tags{display:flex;gap:4px;margin-top:4px}
.tag{font-size:10px;padding:2px 6px;border-radius:4px;color:#fff;font-weight:600}
.tag.cold{background:var(--cold)}.tag.cool{background:var(--cool)}
.tag.neutral{background:var(--neutral)}.tag.warm{background:var(--warm)}
.tag.hot{background:var(--hot)}
.card-effect{font-size:11px;color:var(--muted);margin-top:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
/* ── Detail panel ── */
.detail-overlay{display:none;position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.5)}
.detail-panel{position:fixed;bottom:0;left:0;right:0;max-height:85vh;overflow-y:auto;background:var(--card);border-radius:16px 16px 0 0;z-index:210;padding:0;transform:translateY(100%);transition:transform .35s ease;box-shadow:0 -4px 24px rgba(0,0,0,.2)}
.detail-panel.open{transform:translateY(0)}
.detail-handle{width:40px;height:4px;background:#cbd5e1;border-radius:2px;margin:10px auto}
.detail-img{width:100%;height:200px;object-fit:cover;background:#e2e8f0}
.detail-content{padding:12px 16px 24px}
.detail-header{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.detail-name{font-size:20px;font-weight:700}
.detail-nature{padding:4px 12px;border-radius:6px;font-size:13px;font-weight:700;color:#fff}
.detail-taste{font-size:14px;color:var(--muted)}
.detail-section{margin-top:10px}
.detail-section h3{font-size:13px;font-weight:700;color:var(--text);margin-bottom:4px;padding-bottom:4px;border-bottom:2px solid #e2e8f0}
.detail-section p,.detail-section div.info-row{font-size:13px;color:#334155;line-height:1.7}
.info-row{display:flex;padding:3px 0}
.info-row .label{flex:0 0 60px;font-weight:600;color:var(--text)}
.info-row .value{flex:1}
/* ── Empty ── */
.empty{grid-column:1/-1;text-align:center;padding:40px 20px;color:var(--muted);font-size:14px}
/* ── No image placeholder ── */
.no-img{width:100%;height:120px;display:flex;align-items:center;justify-content:center;background:#e2e8f0;color:#94a3b8;font-size:32px}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <h1>🥬 Toobey 本草食蔬</h1>
  <p>收录 ''' + str(len(veggies)) + r''' 种蔬菜 · 性味归经 · 药用价值</p>
  <div class="search-bar">
    <input id="searchInput" placeholder="搜索蔬菜名称、功效、主治..." oninput="doSearch(this.value)">
    <button onclick="doSearch(document.getElementById('searchInput').value)">搜索</button>
  </div>
</div>

<!-- Category Tabs -->
<div class="tabs" id="tabBar"></div>

<!-- Veggie List -->
<div class="list" id="veggieList"></div>

<!-- Detail Overlay -->
<div class="detail-overlay" id="detailOverlay" onclick="closeDetail()"></div>
<div class="detail-panel" id="detailPanel">
  <div class="detail-handle"></div>
  <img class="detail-img" id="detailImg" src="" alt="">
  <div class="detail-content" id="detailContent"></div>
</div>

<script>
// ── DATA ──
var DATA = ''' + json.dumps(veggies, ensure_ascii=False) + r''';

// ── Helpers ──
var NATURE_EMOJI = {寒:'❄️',凉:'🌊',平:'🌿',温:'🔥',热:'⚡'};
var NATURE_CLS   = {寒:'cold',凉:'cool',平:'neutral',温:'warm',热:'hot'};
var NATURE_COLOR = {寒:'#3b82f6',凉:'#60a5fa',平:'#22c55e',温:'#f59e0b',热:'#ef4444'};

function esc(t){var d=document.createElement('div');d.appendChild(document.createTextNode(t));return d.innerHTML}

// ── Render ──
var currentCategory = '全部';
var currentQuery = '';

function render(){
  var items = currentQuery
    ? DATA.filter(function(v){ return v.name.indexOf(currentQuery)>=0 || v.effect.indexOf(currentQuery)>=0 || v.indications.indexOf(currentQuery)>=0 })
    : (currentCategory==='全部' ? DATA : DATA.filter(function(v){ return v.nature===currentCategory }));
  
  var html = '';
  if(items.length===0){
    html = '<div class="empty">未找到匹配的蔬菜</div>';
  } else {
    for(var i=0;i<items.length;i++){
      var v=items[i], c=NATURE_CLS[v.nature], e=NATURE_EMOJI[v.nature];
      var img = v._img ? '<img class="card-img" src="'+v._img+'" alt="'+esc(v.name)+'" onerror="this.style.display=\'none\'">' : '<div class="no-img">🥬</div>';
      html += '<div class="card" onclick="showDetail('+DATA.indexOf(v)+')">'
        + img
        + '<div class="card-body">'
        + '<div class="card-name">'+e+' '+esc(v.name)+'</div>'
        + '<div class="card-tags"><span class="tag '+c+'">'+v.nature+'性</span><span class="tag '+c+'" style="opacity:.8">味'+v.taste+'</span></div>'
        + '<div class="card-effect">'+esc(v.effect)+'</div>'
        + '</div></div>';
    }
  }
  document.getElementById('veggieList').innerHTML = html;
  updateTabs();
}

function updateTabs(){
  var names = ['全部','寒性','凉性','平性','温性','热性'];
  var counts = {};
  counts['全部'] = DATA.length;
  for(var i=0;i<DATA.length;i++){ var n=DATA[i].nature+'性'; counts[n]=(counts[n]||0)+1; }
  var clsMap = {'全部':'','寒性':'cold','凉性':'cool','平性':'neutral','温性':'warm','热性':'hot'};
  var emojiMap = {'全部':'📋','寒性':'❄️','凉性':'🌊','平性':'🌿','温性':'🔥','热性':'⚡'};
  var html = '';
  for(var i=0;i<names.length;i++){
    var n=names[i], cls=clsMap[n], active=(n===currentCategory&&!currentQuery)?'active':'', cnt=counts[n]||0;
    html += '<div class="tab '+cls+' '+active+'" onclick="switchCategory(\''+n+'\')">'+emojiMap[n]+n+' <span class="count">'+cnt+'</span></div>';
  }
  document.getElementById('tabBar').innerHTML = html;
}

// ── Actions ──
function switchCategory(cat){
  currentCategory = cat;
  currentQuery = '';
  document.getElementById('searchInput').value = '';
  render();
}

function doSearch(q){
  q = q.trim();
  currentQuery = q;
  if(!q){ currentCategory='全部'; render(); return; }
  render();
}

function showDetail(idx){
  var v = DATA[idx];
  var c = NATURE_CLS[v.nature];
  var nc = NATURE_COLOR[v.nature];
  
  // Image
  var imgEl = document.getElementById('detailImg');
  if(v._img){
    imgEl.src = v._img;
    imgEl.style.display = 'block';
  } else {
    imgEl.style.display = 'none';
  }
  
  // Content
  var html = '<div class="detail-header">'
    + '<div class="detail-name">'+v.name+'</div>'
    + '<div class="detail-nature" style="background:'+nc+'">'+v.nature+'性</div>'
    + '<div class="detail-taste">味'+v.taste+'</div></div>';
  
  var fields = [
    ['归经',v.meridian],
    ['功效',v.effect],
    ['主治',v.indications],
    ['禁忌',v.contra],
    ['建议食法',v.usage],
  ];
  html += '<div class="detail-section"><h3>📋 基本信息</h3>';
  for(var i=0;i<fields.length;i++){
    html += '<div class="info-row"><span class="label">'+fields[i][0]+'</span><span class="value">'+esc(fields[i][1])+'</span></div>';
  }
  html += '</div>';
  
  html += '<div class="detail-section" style="margin-top:12px">'
    + '<h3>📊 营养成分</h3><p>'+esc(v.nutrition)+'</p></div>';
  
  html += '<div class="detail-section" style="margin-top:12px">'
    + '<h3>📖 详细介绍</h3><p>'+esc(v.desc)+'</p></div>';
  
  document.getElementById('detailContent').innerHTML = html;
  
  // Show panel with animation
  document.getElementById('detailOverlay').style.display = 'block';
  var panel = document.getElementById('detailPanel');
  panel.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeDetail(){
  var panel = document.getElementById('detailPanel');
  panel.classList.remove('open');
  document.getElementById('detailOverlay').style.display = 'none';
  document.body.style.overflow = '';
}

// ── Init ──
render();
</script>
</body>
</html>'''

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(OUTPUT)
print(f'✅ 生成完毕！')
print(f'📄 {OUTPUT}')
print(f'📏 {size/1024:.0f} KB')
print(f'🥬 {len(veggies)} 种蔬菜')
