# GitHub 今日热榜 · 中文总结

每日抓取 [GitHub Trending](https://github.com/trending)（每日 · 全部语言），为每个项目附上中文一句话简介、2–3 句总结和标签。

🔗 在线访问：**https://wlxweb.github.io/github-trending-zh/**

## 文件说明

- `index.html`：单文件静态页面（支持搜索、语言筛选、排序、明暗模式）
- `data.json`：热榜数据与中文总结
- `build.py`：抓取热榜与 README，合并已有中文总结，生成 `data.json` 并渲染页面
- `render.py`：仅根据 `data.json` 重新渲染 `index.html`
- `publish.sh`：提交并推送更新

## 更新流程

```bash
python3 build.py      # 抓取最新热榜
# 在 data.json 中补写缺失的 zh_tagline / zh_summary / zh_tags
python3 render.py     # 重新渲染
./publish.sh          # 提交并推送，GitHub Pages 自动更新
```
