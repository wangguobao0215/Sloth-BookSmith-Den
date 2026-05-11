<p align="center">
  <img src="assets/sloth-avatar-round.png" width="120" />
</p>

<h1 align="center">匠书 · 出版排版引擎</h1>

<p align="center">
  <strong>将 Markdown 与 Word 书稿一键转换为出版级电子书</strong><br/>
  支持 PDF / HTML / ePub / MOBI / AZW3 五种格式输出
</p>

<p align="center">
  <img src="assets/qrcode.jpg" width="140" /><br/>
  <sub>扫码关注 <strong>树懒老K</strong> · 获取更多 AI 技能</sub><br/>
  <em>慢一点，深一度</em>
</p>

---

## 品名释义

**「匠」** — 取自工匠精神，寓意对排版细节的极致追求。BookSmith（书籍工匠）的核心正是以匠人态度对待每一页的字距、行距与版式。

**「书」** — 双关：既指书籍本身，也含「书写」「成书」之意，点明技能将零散文稿转化为完整成书的核心能力。

**「匠书」** — 整体品名传递「以工匠之心，铸书籍之美」的定位：不追求快速生成，而是深耕排版精度，让每一份书稿都具备出版级品质。

---

## 功能概览

- **多格式输出**：单一代码库生成 PDF、HTML、ePub、MOBI、AZW3 五种电子书格式
- **双格式输入**：原生支持 Markdown，自动检测并转换 Word (.docx) 文档
- **专业排版引擎**：首行缩进、比例边距、页眉页脚、章节扉页、首字下沉、避头尾控制
- **智能目录**：自动生成三级目录，PDF 目录带动态页码，ePub 含 NCX 导航
- **代码高亮**：集成 Pygments，支持 fenced code 与代码块语法高亮
- **交叉引用**：自动识别「参见/参阅/参考/见」并生成可点击链接
- **子章节导航**：H2 锚点注入，支持目录直达子章节，PDF 含 H2 级别书签
- **封面系统**：5 种版式（纯色/渐变/图片/纹理/学术）+ 深色电子书主题
- **字体回退**：现代 CJK 字体链（PingFang SC、Hiragino Sans GB、Microsoft YaHei）
- **元数据注入**：PDF XMP + 文档信息字典，ePub dc:description 完整元数据
- **水印支持**：命令行参数注入水印，全页覆盖
- **图片处理**：自动识别图片段落并转 figure，ePub 自动打包本地图片资源

---

## 支持格式

| 格式 | 特性 | 适用场景 |
|------|------|----------|
| PDF | 分页排版、书签、页眉页脚、水印 | 印刷出版、存档 |
| HTML | 响应式、@media print 分页、代码高亮 | 网页阅读、在线预览 |
| ePub | 标准 2.0、NCX 目录、封面元数据 | 通用电子书阅读器 |
| MOBI | Kindle 旧格式 | 旧款 Kindle 设备 |
| AZW3 | Kindle 现代格式，排版更优 | 现代 Kindle 设备 |

---

## 主题预设

| 主题 | 风格 | 适用场景 |
|------|------|----------|
| publishing-classic | 经典出版，宋体/明朝体 | 文学、学术作品 |
| academic-serif | 学术专用，宽边距脚注 | 论文、研究报告 |
| tech-modern | 科技现代，无衬线代码高亮 | 技术文档、开发者手册 |
| consulting-navy | 咨询报告，藏蓝数据表格 | 商业提案、战略报告 |
| literary-minimal | 文学极简，大量留白 | 散文、诗集 |
| dark-ebook | 深色护眼，琥珀色强调 | 夜间阅读、电子墨水 |

---

## 快速开始

### 安装依赖

```bash
pip install markdown pygments pymupdf playwright pyyaml python-docx
playwright install chromium
```

> MOBI / AZW3 输出需要安装 [Calibre](https://calibre-ebook.com/download)。

### 基础用法

```bash
# PDF 输出
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format pdf

# HTML 输出
python scripts/booksmith.py --input manuscript.md --theme tech-modern --format html

# ePub 输出
python scripts/booksmith.py --input manuscript.md --theme publishing-classic --format epub

# MOBI / AZW3（需 Calibre）
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format mobi
python scripts/booksmith.py --input manuscript.md --theme dark-ebook --format azw3

# Word 输入（自动检测）
python scripts/booksmith.py --input manuscript.docx --theme academic-serif --format pdf

# 带水印
python scripts/booksmith.py --input manuscript.md --watermark "内部资料" --format pdf
```

### Markdown 书稿结构

```markdown
# 书名

作者：XXX
日期：2026-05-09

## 第一章 标题

正文内容……

## 第二章 标题

正文内容……
```

---

## 版本

当前版本：**2.0.0**

详见 [CHANGELOG.md](CHANGELOG.md)。

---

## 许可证

MIT License © 2026 lovstudio (Sloth-Eido family)
