#!/usr/bin/env python3
"""Render index.html from data.json (single self-contained file)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub 今日热榜 · __DATE__</title>
<style>
:root{--bg:#f6f8fa;--card:#fff;--fg:#1f2328;--muted:#656d76;--border:#d0d7de;--accent:#0969da;--chip:#ddf4ff;--chipfg:#0550ae;--hot:#cf222e;--shadow:0 1px 3px rgba(31,35,40,.08),0 8px 24px rgba(31,35,40,.04)}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d1117;--card:#161b22;--fg:#e6edf3;--muted:#8d96a0;--border:#30363d;--accent:#4493f8;--chip:#122d4f;--chipfg:#79c0ff;--hot:#ff7b72;--shadow:none}}
:root[data-theme=dark]{--bg:#0d1117;--card:#161b22;--fg:#e6edf3;--muted:#8d96a0;--border:#30363d;--accent:#4493f8;--chip:#122d4f;--chipfg:#79c0ff;--hot:#ff7b72;--shadow:none}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC","Noto Sans SC",sans-serif;line-height:1.6}
.wrap{max-width:980px;margin:0 auto;padding:32px 20px 60px}
header{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:20px}
h1{margin:0;font-size:30px;letter-spacing:.5px}
h1 span{background:linear-gradient(90deg,#f78166,#d2a8ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.meta{color:var(--muted);font-size:14px}
.meta a{color:var(--accent);text-decoration:none}
.toolbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:10px;padding:12px 0;background:var(--bg);margin-bottom:8px}
.toolbar input,.toolbar select,.toolbar button{font:inherit;font-size:14px;color:var(--fg);background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 12px}
.toolbar input{flex:1 1 240px}
.toolbar button{cursor:pointer}
.toolbar input:focus,.toolbar select:focus{outline:2px solid var(--accent);outline-offset:-1px}
.count{color:var(--muted);font-size:13px;margin:4px 0 12px}
.card{display:grid;grid-template-columns:48px 1fr;gap:4px 16px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:14px;box-shadow:var(--shadow);transition:transform .15s,border-color .15s}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.rank{grid-row:span 6;font-size:26px;font-weight:700;color:var(--muted);text-align:center;font-variant-numeric:tabular-nums}
.rank.top{color:var(--hot)}
.name{font-size:19px;font-weight:600;word-break:break-word}
.name a{color:var(--accent);text-decoration:none}
.name a:hover{text-decoration:underline}
.name .owner{font-weight:400}
.tagline{font-size:16px;font-weight:600;margin-top:2px}
.summary{margin:6px 0 4px;font-size:15px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.tag{background:var(--chip);color:var(--chipfg);font-size:12px;padding:2px 10px;border-radius:999px}
.orig{color:var(--muted);font-size:13px;font-style:italic;margin:2px 0 6px}
.stats{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--muted);align-items:center}
.stats b{color:var(--fg);font-weight:600;font-variant-numeric:tabular-nums}
.stats .today b{color:var(--hot)}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:5px;vertical-align:-1px;border:1px solid rgba(127,127,127,.3)}
.empty{text-align:center;color:var(--muted);padding:40px}
footer{color:var(--muted);font-size:12px;text-align:center;margin-top:30px}
@media (max-width:600px){h1{font-size:24px}.card{grid-template-columns:1fr;padding:16px}.rank{grid-row:auto;text-align:left;font-size:18px}.rank::before{content:"#"}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <h1>🔥 <span>GitHub 今日热榜</span></h1>
    <div class="meta">数据抓取时间：__DATE__（北京时间） · 来源：<a href="https://github.com/trending" target="_blank" rel="noopener">github.com/trending</a>（每日 · 全部语言）</div>
  </div>
  <button id="theme" title="切换明暗模式" style="font:inherit;font-size:14px;cursor:pointer;color:var(--fg);background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 12px">🌓 主题</button>
</header>
<div class="toolbar">
  <input id="q" type="search" placeholder="搜索项目名、描述、中文简介或标签…" aria-label="搜索">
  <select id="lang" aria-label="语言筛选"><option value="">全部语言</option></select>
  <select id="sort" aria-label="排序">
    <option value="rank">按热榜排名</option>
    <option value="stars_today">按今日新增星标</option>
    <option value="stars">按总星标</option>
    <option value="forks">按 Fork 数</option>
  </select>
</div>
<div class="count" id="count"></div>
<main id="list"></main>
<footer>中文简介依据各项目的官方描述与 README 撰写 · 页面为静态单文件，可离线打开</footer>
</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);const R=D.repos;
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n.toLocaleString('zh-CN');
const langs=[...new Set(R.map(r=>r.language).filter(Boolean))].sort();
for(const l of langs){const c=R.filter(r=>r.language===l).length;$('#lang').insertAdjacentHTML('beforeend',`<option value="${esc(l)}">${esc(l)} (${c})</option>`)}
if(R.some(r=>!r.language))$('#lang').insertAdjacentHTML('beforeend','<option value="__none">未标注语言</option>');
function card(r){
  const lang=r.language?`<span><span class="dot" style="background:${esc(r.language_color||'#8b949e')}"></span>${esc(r.language)}</span>`:'<span>未标注语言</span>';
  return `<article class="card">
  <div class="rank ${r.rank<=3?'top':''}">${r.rank}</div>
  <div class="name"><a href="${esc(r.url)}" target="_blank" rel="noopener"><span class="owner">${esc(r.owner)} / </span>${esc(r.name)}</a></div>
  ${r.zh_tagline?`<div class="tagline">${esc(r.zh_tagline)}</div>`:''}
  ${r.zh_summary?`<p class="summary">${esc(r.zh_summary)}</p>`:''}
  ${r.zh_tags&&r.zh_tags.length?`<div class="tags">${r.zh_tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>`:''}
  ${r.description?`<div class="orig">${esc(r.description)}</div>`:''}
  <div class="stats">${lang}<span>⭐ 星标 <b>${fmt(r.stars)}</b></span><span>🍴 Fork <b>${fmt(r.forks)}</b></span><span class="today">📈 今日新增 <b>+${fmt(r.stars_today)}</b></span></div>
</article>`}
function render(){
  const q=$('#q').value.trim().toLowerCase(),l=$('#lang').value,s=$('#sort').value;
  let list=R.filter(r=>{
    if(l==='__none'?r.language:(l&&r.language!==l))return false;
    if(!q)return true;
    return [r.full_name,r.description,r.zh_tagline,r.zh_summary,(r.zh_tags||[]).join(' '),r.language].join(' ').toLowerCase().includes(q)});
  list.sort((a,b)=>s==='rank'?a.rank-b.rank:b[s]-a[s]);
  $('#list').innerHTML=list.length?list.map(card).join(''):'<div class="empty">没有匹配的项目</div>';
  $('#count').textContent=`共 ${R.length} 个项目，当前显示 ${list.length} 个`;
}
['q','lang','sort'].forEach(id=>$('#'+id).addEventListener('input',render));
const root=document.documentElement,saved=localStorage.getItem('gt-theme');if(saved)root.dataset.theme=saved;
$('#theme').onclick=()=>{const dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;root.dataset.theme=dark?'light':'dark';localStorage.setItem('gt-theme',root.dataset.theme)};
render();
</script>
</body>
</html>
"""

def main():
    d = json.load(open(os.path.join(HERE, "data.json")))
    payload = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.replace("__DATE__", d["fetched_at_display"]).replace("__DATA__", payload)
    out = os.path.join(HERE, "index.html")
    open(out, "w").write(html)
    print("rendered", out, f"({len(d['repos'])} repos)")

if __name__ == "__main__":
    main()
