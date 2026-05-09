---
name: sloth-booksmith-den
version: 2.0.0
description: >-
  Professional book typesetting engine. Converts Markdown to publication-quality PDF
  with typographic precision: first-line indents, proportional margins, running headers,
  chapter openers, drop caps, proper widow/orphan control, and 5 curated theme presets.
  Use when user asks to typeset a book, format a manuscript, create a publishable PDF,
  or convert markdown to a professionally typeset book.
description_zh: >-
  专业级书籍排版引擎。将 Markdown 转换为出版级 PDF，具备专业排版精度：
  首行缩进、比例边距、页眉页脚、章节扉页、首字下沉、避头尾规则、5 种专业配色主题。
  当用户要求排版书籍、格式化书稿、制作可出版 PDF、或将 Markdown 转为专业排版书籍时调用。
license: MIT
compatibility: >
  Requires Python 3.8+, weasyprint (`pip install weasyprint`), and appropriate CJK fonts.
  Windows: SimSun (宋体) + Consolas/Courier New. macOS: Songti SC + Menlo. Linux: Noto CJK.
metadata:
  author: lovstudio (Sloth-Eido family)
  tags: book typesetting pdf markdown publishing typography cjk
  internal: true
---

# Sloth-BookSmith-Den — 专业书籍排版引擎 v2.0

> <p align="center"><img src="https://raw.githubusercontent.com/wangguobao0215/Sloth-BookSmith-Den/main/assets/qrcode.jpg" width="80" /><br/><sub>扫码关注 <b>树懒老K</b> · 获取更多 AI 技能</sub><br/><i>慢一点，深一度</i></p>
>
> 将 Markdown 书稿转换为出版级 PDF。专业排版 = 字体 × 间距 × 版式 × 封面。

---

## 核心能力

```
Markdown → [解析] → [主题应用] → [HTML/CSS构建] → [WeasyPrint] → 出版级PDF
```

| 能力 | 说明 |
|------|------|
| **专业封面** | 5 种版式（纯色/渐变/图片/纹理/学术），自动配色 |
| **版权页** | 自动生成标准版权页（ISBN、版本、版权声明） |
| **目录页** | 自动生成可点击目录，三级层级 |
| **章节扉页** | 每章独立扉页，大字号标题 + 装饰线 |
| **正文排版** | 首行缩进 2em、行距 1.75、段间距 0.5em |
| **页眉页脚** | 左页书名 + 右页章名，页码居中 |
| **避头尾** | 自动处理中英文混排断行 |
| **首字下沉** | 首章首段支持 drop cap（可选） |
| **表格/代码** | 专业样式表格、代码块语法高亮底色 |
| **图片** | 自动居中 + 图注（figure + figcaption） |

---

## 五大主题预设

| 预设 | 风格 | 适合 | 主色调 |
|------|------|------|--------|
| `publishing-classic` | 经典出版 | 文学、小说、社科 | 暖纸 + 墨黑 + 深红点缀 |
| `academic-serif` | 学术期刊 | 论文、专著、教材 | 象牙白 + 藏蓝 |
| `tech-modern` | 科技现代 | 技术书籍、手册 | 纯白 + 品牌蓝 |
| `consulting-navy` | 咨询深蓝 | 商业报告、白皮书 | 纯白 + 海军蓝 |
| `literary-minimal` | 文学极简 | 散文、随笔、回忆录 | 米白 + 炭灰 |

---

## 使用方式

### 快速开始

```bash
python scripts/booksmith.py --input manuscript.md --output book.pdf
```

### 指定主题

```bash
python scripts/booksmith.py --input manuscript.md --output book.pdf --theme publishing-classic
```

### 自定义封面

```bash
python scripts/booksmith.py \
  --input manuscript.md \
  --output book.pdf \
  --theme publishing-classic \
  --cover-style gradient \
  --cover-image /path/to/image.jpg \
  --author "作者名" \
  --publisher "出版社" \
  --isbn "978-7-xxx-xxxxx-x"
```

---

## 前置确认（Mandatory）

在生成 PDF 前，**必须**用 `AskUserQuestion` 确认以下参数：

| 参数 | 选项 | 默认 |
|------|------|------|
| 主题 | publishing-classic / academic-serif / tech-modern / consulting-navy / literary-minimal | publishing-classic |
| 封面版式 | solid / gradient / image / texture / academic | gradient |
| 是否首字下沉 | 是 / 否 | 否（仅文学类推荐） |
| 纸张 | A4 / B5 / 6×9英寸 | A4 |
| 水印 | 无 / 自定义文字 | 无 |

---

## 排版规范

### 字体选择

| 平台 | 正文（衬线） | 标题（无衬线） | 代码 |
|------|------------|--------------|------|
| Windows | SimSun (宋体) | Microsoft YaHei (微软雅黑) | Consolas |
| macOS | Songti SC (宋体-简) | PingFang SC (苹方) | Menlo |
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
# Core engine
pip install weasyprint markdown

# Windows 额外依赖（WeasyPrint 需要 GTK）
# 推荐用 pip install weasyprint[fonts]
```

---

## 输出质量检查清单

生成后自动验证：

- [ ] 封面页存在且无空白
- [ ] 版权页包含 ISBN（如提供）
- [ ] 目录页可点击跳转
- [ ] 每章有独立扉页
- [ ] 正文首行缩进 2em
- [ ] 页眉左右交替（书名/章名）
- [ ] 页码连续
- [ ] 图片不跨页断裂
- [ ] 表格不跨页断裂
- [ ] 无 widows/orphans（段落首/尾行单独成页）

---

## 扩展

自定义主题参见 `references/theme-gallery.md`。

封面模板参见 `assets/templates/covers/`。
