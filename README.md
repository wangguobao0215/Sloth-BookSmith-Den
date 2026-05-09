# Sloth-BookSmith-Den

> 专业书籍排版引擎 — 将 Markdown 转换为出版级 PDF
>
> 慢一点，深一度

---

## 简介

Booksmith 是一个专业的 Markdown → PDF 排版引擎，旨在生成具有出版级质量的电子书。

与普通的 Markdown 转 PDF 工具不同，Booksmith 关注**排版细节**：

- **专业封面**：5 种版式（纯色/渐变/图片/纹理/学术），自动配色
- **版权页**：自动生成标准版权页（ISBN、版本、版权声明）
- **目录页**：自动生成可点击目录，三级层级
- **章节扉页**：每章独立扉页，大字号标题 + 装饰线
- **正文排版**：首行缩进 2em、行距 1.75、段间距 0.5em
- **页眉页脚**：左页书名 + 右页章名，页码居中
- **避头尾**：自动处理中英文混排断行
- **首字下沉**：首章首段支持 drop cap（可选）

---

## 快速开始

### 安装依赖

```bash
pip install weasyprint pyyaml markdown
```

Windows 用户可能需要额外安装 GTK：
```bash
# 下载并安装 GTK3 for Windows
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
```

### 基本用法

```bash
python scripts/booksmith.py --input manuscript.md --output book.pdf
```

### 指定主题

```bash
python scripts/booksmith.py \
  --input manuscript.md \
  --output book.pdf \
  --theme publishing-classic
```

### 完整选项

```bash
python scripts/booksmith.py \
  --input manuscript.md \
  --output book.pdf \
  --theme publishing-classic \
  --title "脱耦：AI重铸中国制造" \
  --author "GUOBAO WANG" \
  --subtitle "智造重构引擎理论与实践" \
  --date "2026-01-04" \
  --isbn "978-7-xxx-xxxxx-x" \
  --publisher "机械工业出版社" \
  --cover-style gradient \
  --drop-cap
```

---

## 五大主题预设

| 预设 | 风格 | 适合 |
|------|------|------|
| `publishing-classic` | 经典出版 | 文学、小说、社科 |
| `academic-serif` | 学术期刊 | 论文、专著、教材 |
| `tech-modern` | 科技现代 | 技术书籍、手册 |
| `consulting-navy` | 咨询深蓝 | 商业报告、白皮书 |
| `literary-minimal` | 文学极简 | 散文、随笔、回忆录 |

---

## Markdown 格式要求

Booksmith 期望 Markdown 文件遵循以下结构：

```markdown
---
title: 书名
author: 作者名
date: 2026-01-01
---

# 第一章 章标题

正文段落。首行会自动缩进 2em。

## 节标题

更多内容...

### 小节标题

- 列表项 1
- 列表项 2

> 引用内容

```python
# 代码块
print("Hello")
```

| 列1 | 列2 |
|-----|-----|
| 数据 | 数据 |

![图片说明](images/fig01.png)
*图 1：图片说明*

---

# 第二章 另一章

...
```

### 关键规则

1. **`# H1` 作为章分隔符** — 每个 `# ` 标题会生成一个独立的章节扉页
2. **`## H2` 作为节标题** — 正文内的二级标题
3. **`### H3` 作为小节标题** — 正文内的三级标题
4. **图片自动居中** — Markdown 图片会自动居中并添加图注
5. **YAML frontmatter** — 可选，用于设置书名、作者等元数据

---

## 封面版式

| 版式 | 说明 | 适合 |
|------|------|------|
| `gradient` | 渐变色背景 | 默认，适合大多数场景 |
| `solid` | 纯色背景 | 简洁正式 |
| `image` | 全幅图片背景 | 需配合 `--cover-image` |
| `texture` | 纹理背景 | 复古/文艺风格 |
| `academic` | 学术极简 | 论文、专著 |

---

## 排版规范

### 字体选择

| 平台 | 正文 | 标题 | 代码 |
|------|------|------|------|
| Windows | SimSun | SimSun | Consolas |
| macOS | Songti SC | Songti SC | Menlo |
| Linux | Noto Serif CJK | Noto Serif CJK | DejaVu Sans Mono |

### 页面尺寸

| 尺寸 | 适用场景 |
|------|---------|
| A4 | 默认，适合大多数 |
| B5 | 日本文艺书籍 |
| 6×9英寸 | 欧美平装书 |

---

## 许可证

MIT License. See [LICENSE](LICENSE).

---

## 归属

Sloth-Eido 技能家族成员。

> 慢一点，深一度
