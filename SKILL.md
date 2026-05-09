---
name: sloth-booksmith-den
version: 2.0.0
description: >-
  Professional book typesetting engine. Converts Markdown and Word (.docx) manuscripts
  to publication-quality ebooks in PDF, HTML, ePub, MOBI, and AZW3 formats.
  Use when user asks to typeset a book, format a manuscript, create a publishable PDF/ebook,
  convert markdown to a professionally typeset book, or generate multi-format ebooks.
description_zh: >-
  匠书 · 出版排版引擎。将 Markdown 与 Word 书稿转换为出版级电子书，
  支持 PDF、HTML、ePub、MOBI、AZW3 五种格式输出。
  当用户要求排版书籍、格式化书稿、制作可出版电子书、或将 Markdown 转为专业排版书籍时调用。
license: MIT
compatibility: >
  Requires Python 3.8+, markdown, pygments, pymupdf, playwright, pyyaml, python-docx.
  Windows: SimSun + Consolas. macOS: Songti SC + Menlo. Linux: Noto CJK.
  MOBI/AZW3 output requires Calibre (ebook-convert).
metadata:
  author: lovstudio (Sloth-Eido family)
  tags: book typesetting pdf epub mobi azw3 html markdown publishing typography cjk
  internal: true
---

# Sloth-BookSmith-Den — 匠书 · 出版排版引擎 v2.0

> <p align="center"><img src="https://raw.githubusercontent.com/wangguobao0215/Sloth-BookSmith-Den/master/assets/qrcode.jpg" width="80" /><br/><sub>扫码关注 <b>树懒老K</b> · 获取更多 AI 技能</sub><br/><i>慢一点，深一度</i></p>
>
> 将 Markdown 与 Word 书稿转换为出版级电子书。专业排版 = 字体 × 间距 × 版式 × 封面。

---

## 欢迎页面

> <p align="center"><img src="https://raw.githubusercontent.com/wangguobao0215/Sloth-BookSmith-Den/master/assets/qrcode.jpg" width="80" /><br/><sub>扫码关注 <b>树懒老K</b> · 获取更多 AI 技能</sub><br/><i>慢一点，深一度</i></p>

欢迎使用 **匠书 · 出版排版引擎**。本技能将 Markdown 或 Word 书稿一键转换为出版级电子书，支持 PDF、HTML、ePub、MOBI、AZW3 五种输出格式。

---

## 核心能力

```
Markdown/Word → [解析] → [主题应用] → [HTML/CSS构建] → [渲染] → PDF/HTML/ePub/MOBI/AZW3
```

| 能力 | 说明 |
|------|------|
| **多格式输出** | 单一代码库生成 PDF、HTML、ePub、MOBI、AZW3 五种电子书格式 |
| **双格式输入** | 原生 Markdown + 自动检测并转换 Word (.docx) 文档 |
| **专业封面** | 5 种版式（纯色/渐变/图片/纹理/学术），自动配色 |
| **版权页** | 自动生成标准版权页（ISBN、版本、版权声明） |
| **目录页** | 自动生成可点击目录，PDF 带动态页码，ePub 含 NCX 导航 |
| **章节扉页** | 每章独立扉页，大字号标题 + 装饰线 |
| **正文排版** | 首行缩进 2em、行距 1.75、段间距 0.5em |
| **页眉页脚** | 左页书名 + 右页章名，页码居中 |
| **避头尾** | 自动处理中英文混排断行 |
| **首字下沉** | 首章首段支持 drop cap（可选） |
| **代码高亮** | Pygments 语法高亮，支持 fenced code 代码块 |
| **交叉引用** | 自动识别「参见/参阅/参考/见」并生成可点击链接 |
| **子章节导航** | H2 锚点注入，目录直达子章节，PDF 含 H2 级别书签 |
| **水印支持** | CLI 参数注入全页水印 |
| **图片处理** | 自动居中 + 图注，ePub 自动打包本地图片资源 |
| **元数据注入** | PDF XMP + info dict，ePub dc:description |

---

## 六大主题预设

| 预设 | 风格 | 适合 | 主色调 |
|------|------|------|--------|
| `publishing-classic` | 经典出版 | 文学、小说、社科 | 暖纸 + 墨黑 + 深红点缀 |
| `academic-serif` | 学术期刊 | 论文、专著、教材 | 象牙白 + 藏蓝 |
| `tech-modern` | 科技现代 | 技术书籍、手册 | 纯白 + 品牌蓝 |
| `consulting-navy` | 咨询深蓝 | 商业报告、白皮书 | 纯白 + 海军蓝 |
| `literary-minimal` | 文学极简 | 散文、随笔、回忆录 | 米白 + 炭灰 |
| `dark-ebook` | 深色电子书 | 夜间阅读、电子墨水 | 深灰 + 琥珀强调 |

---

## 使用方式

### 快速开始

```bash
python scripts/booksmith.py --input manuscript.md --format pdf
```

### 指定主题与格式

```bash
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format pdf
python scripts/booksmith.py --input manuscript.md --theme tech-modern --format html
python scripts/booksmith.py --input manuscript.md --theme publishing-classic --format epub
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format mobi
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format azw3
```

### Word 输入（自动检测）

```bash
python scripts/booksmith.py --input manuscript.docx --theme academic-serif --format pdf
```

### 带水印

```bash
python scripts/booksmith.py --input manuscript.md --format pdf --watermark "内部资料"
```

### 完整自定义

```bash
python scripts/booksmith.py \
  --input manuscript.md \
  --format pdf \
  --theme publishing-classic \
  --cover-style gradient \
  --cover-image /path/to/image.jpg \
  --author "作者名" \
  --publisher "出版社" \
  --isbn "978-7-xxx-xxxxx-x" \
  --watermark "样章"
```

---

## 前置确认（Mandatory）

在生成电子书前，**必须**用 `AskUserQuestion` 确认以下参数：

| 参数 | 选项 | 默认 |
|------|------|------|
| 输出格式 | pdf / html / epub / mobi / azw3 | pdf |
| 主题 | publishing-classic / academic-serif / tech-modern / consulting-navy / literary-minimal / dark-ebook | publishing-classic |
| 封面版式 | solid / gradient / image / texture / academic | gradient |
| 是否首字下沉 | 是 / 否 | 否（仅文学类推荐） |
| 纸张 | A4 / B5 / 6×9英寸 | A4 |
| 水印 | 无 / 自定义文字 | 无 |

---

## 排版规范

### 字体回退链

| 平台 | 正文（衬线） | 标题（无衬线） | 代码 |
|------|------------|--------------|------|
| Windows | SimSun (宋体) / PingFang SC | Microsoft YaHei (微软雅黑) | Consolas |
| macOS | Songti SC (宋体-简) / Hiragino Sans GB | PingFang SC (苹方) | Menlo |
| Linux | Noto Serif CJK SC | Noto Sans CJK SC | DejaVu Sans Mono |

### 字号体系

| 元素 | 字号 | 行距 |
|------|------|------|
| 封面标题 | 36-48pt | 1.2 |
| 章标题（扉页） | 28pt | 1.3 |
| H1（正文内） | 18pt bold | 1.4 |
| H2 | 15pt bold | 1.4 |
| H3 | 13pt bold | 1.4 |
| 正文 | 11pt | 1.75 |
| 代码块 | 9pt | 1.4 |
| 页眉/页脚 | 9pt | 1.3 |
| 图注 | 9pt italic | 1.4 |

### 页面边距

| 边距 | A4 | B5 | 6×9英寸 |
|------|-----|-----|--------|
| 上 | 25mm | 22mm | 0.875in |
| 下 | 25mm | 22mm | 0.875in |
| 内侧（装订） | 22mm | 20mm | 0.75in |
| 外侧 | 18mm | 16mm | 0.625in |

---

## 依赖

```bash
# Core
pip install markdown pygments pymupdf playwright pyyaml python-docx

# Browser engine for PDF rendering
playwright install chromium

# MOBI/AZW3 conversion (requires Calibre installed)
# Download: https://calibre-ebook.com/download
```

---

## 输出质量检查清单

生成后自动验证：

- [ ] 封面页存在且无空白
- [ ] 版权页包含 ISBN（如提供）
- [ ] 目录页可点击跳转，PDF 目录页码正确
- [ ] 每章有独立扉页
- [ ] 正文首行缩进 2em
- [ ] 页眉左右交替（书名/章名）
- [ ] 页码连续，章节扉页无页眉
- [ ] 图片不跨页断裂
- [ ] 表格不跨页断裂
- [ ] 代码块语法高亮正常
- [ ] 交叉引用链接可点击
- [ ] 子章节锚点可跳转
- [ ] 无 widows/orphans（段落首/尾行单独成页）

---

## 扩展

自定义主题参见 `references/theme-gallery.md`。

封面模板参见 `assets/templates/covers/`。
