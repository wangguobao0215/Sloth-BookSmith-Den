# Changelog

All notable changes to Sloth-BookSmith-Den will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-09

### Added
- 多格式输出架构：单一代码库支持 PDF、HTML、ePub、MOBI、AZW3 五种格式
- HTML 独立导出（含 @media print 分页与 @media screen 响应式样式）
- ePub 2.0 手动 ZIP 构建，含图片资源自动打包与路径重写
- MOBI / AZW3 格式（通过 Calibre ebook-convert 转换）
- 代码语法高亮（Pygments + codehilite）与配套 CSS
- 交叉引用自动链接（参见/参阅/参考/见）
- 子章节独立锚点链接（H2 ID 注入 + 目录 href）
- PDF 子章节书签（H2 级别 PDF outline）
- PDF XMP 元数据与文档信息字典双向注入
- ePub 封面元数据标记（dc:description 等）
- 水印支持（--watermark 参数 + CSS position: fixed）
- 深色电子书主题预设（dark-ebook）
- 现代 CJK 字体回退链（PingFang SC、Hiragino Sans GB）

### Changed
- 品牌命名统一为 Sloth-BookSmith-Den（树懒家族 Den 系列）
- CLI 参数体系重构，支持 --format 指定输出格式
- 字体检测逻辑改为与预设合并而非覆盖

### Fixed
- 字体预设被 detect_fonts() 完全覆盖的问题
- 交叉引用正则将"参见"拆分为"见"+"参"的问题
- 目录页码不连续（counter-reset 位置错误）
- 首字下沉跨页溢出
- 冗余的 .pagedjs_page .page-header 覆盖样式
- 章节扉页显示 running header 的问题

## [1.0.0] - 2026-05-08

### Added
- Initial release of Sloth-BookSmith-Den (formerly Sloth-Booksmith-Eido)
- Markdown to publication-quality PDF conversion engine
- 5 theme presets: publishing-classic, academic-serif, tech-modern, consulting-navy, literary-minimal
- 5 cover styles: solid, gradient, image, texture, academic
- Automatic front matter generation (cover, copyright, TOC)
- Chapter opener pages with large typography
- Professional body typography (2em indent, 1.75 line-height)
- Running headers with alternating book title / chapter name
- Proper CJK font support for Windows/macOS/Linux
- Image handling with captions
- Table and code block styling
- WeasyPrint-based HTML/CSS → PDF pipeline
- CLI interface with theme and cover customization
- Output quality validation checklist
