# 论文来源获取与复用

## 目标

确认唯一论文身份，优先取得机器可读、保留公式与表格结构的完整官方文本；只有官方文本不可用
或不完整时才回退到 PDF。来源应足以覆盖正文、附录和补充材料。本阶段不提取复现结论，不生成
独立交付文件。

## 1. 识别论文与本地缓存

从按主技能“输入与启动”接收的当前任务要求中提取标题、作者、venue、年份、DOI、arXiv ID、
PDF/出版页 URL 和项目名；已有明确论文线索即可开始核验，不以逐字 prompt 是否保留为条件。
先检查：

1. 用户提供的本地路径。
2. `.onescience` 中与当前任务有关的论文映射。
3. `.paper2code_work/<id>/paper_fulltext.html`、`paper_source/`、`paper_text_full.md`、`paper.pdf`
   或等价缓存。

`.onescience` 可能只保存当前任务或过期状态，不能把单条 `task_state.json` 当作完整论文索引。
每个候选都要用标题、作者和版本交叉确认；目录名相似或任务名相同不等于论文身份一致。

先检查已有结构化全文是否来自官方来源、身份和版本一致、没有截断，并保留正文、公式、表格、
脚注、附录及其引用关系。验证通过后直接复用，不得再次下载或覆盖。只有结构化全文不存在或未
通过检查时才检查已有 `paper.pdf` 的文件头、页数可读性、标题、作者、版本和内容覆盖；已有 PDF
不改变“先尝试官方文本、再解析 PDF”的顺序。

## 2. 工作目录

材料保存在 `.paper2code_work/<id>/`：

- arXiv 论文使用去掉版本号的 arXiv ID。
- 无 arXiv ID 时使用 DOI slug。
- 只有标题时，必须先消歧确认，再使用稳定 title slug。

允许保留的来源缓存只有实际需要的文件，例如：

```text
.paper2code_work/<id>/
  paper_fulltext.html
  paper_source/
  paper.pdf
  paper_text_full.md
  reproduction_spec.md
```

只保留实际取得和使用的缓存，不要求四类来源同时存在。`paper_fulltext.html` 保存未删改的官方
HTML；`paper_source/` 保存从官方源码包中安全解包且与正文有关的 TeX/Bib/样式文件；
`paper_text_full.md` 是可选的结构保真规范化副本，不是进入提取阶段的前置条件。图片二进制可不
保存，但图注和正文中的引用应保留。不得用规范化文本覆盖原始 HTML 或源码。

不要为阶段状态额外生成 summary、intent profile、figures/tables、audit、contract 或 handoff 文件。
解析异常可在当前执行记录中报告，不必持久化一组流程文件。

## 3. 缺少本地全文时

本地不存在有效全文时，在用户允许的获取范围内使用官方来源。公开论文的读取属于论文复现任务
本身；用户已有授权持续有效，不为每次下载重复确认。无论用户给出的是 arXiv 摘要页、PDF URL、
DOI 还是标题，确认身份和精确版本后都按以下顺序获取内容：

1. 官方结构化全文：arXiv HTML，或出版社/OpenReview/PMC 等提供的官方全文 HTML/XML。
2. 官方论文源码：arXiv e-print 源码包；用于 HTML 不可用、转换不完整或复杂公式/表格需要补全
   的情况。
3. 官方 PDF：只有前两种文本来源不可用或仍存在任务相关缺口时才下载并解析。

arXiv export API、`/abs/` 摘要页只提供元数据或摘要，不是全文。搜索片段、聚合站、第三方镜像、
博客和模型记忆也不能替代全文或支撑 `PAPER_FACT`。补充材料含复现细节时一并取得；若其只有
PDF，则只对该缺口使用 PDF 回退，不必放弃已经取得的正文结构化文本。

### 3.1 获取官方结构化全文

arXiv 论文优先使用已核验版本的 `https://arxiv.org/html/<versioned-arxiv-id>`，例如输入明确为
某一版本时保留 `vN`，不得静默切换到最新版。将完整响应流式保存为
`paper_fulltext.html.part`，校验通过后再改名为 `paper_fulltext.html`。不要依赖工具把整篇 HTML
一次性展示在上下文中，也不要把截断的 markdown 转换结果保存成“全文”。

有效的 arXiv HTML 必须满足：

- 最终响应是论文正文而非摘要、登录、限流、错误或“HTML conversion unavailable”页面。
- 标题、作者和 arXiv 版本与目标一致。
- 存在正文容器，并覆盖摘要、方法、实验/结果、参考文献和适用的附录。
- 公式保留 MathML 或 LaTeX annotation，表格保留行列、表头、合并单元格和标题结构。
- 转换告警没有导致任务相关公式、表格或附录缺失。

其它来源也优先使用官方全文 HTML/XML，并执行同等的身份、版本、范围和结构检查。只有完整响应
已保存时，`webfetch`/浏览器读取才可作为获取通道；若响应会被截断，应改为流式下载到本地后
分段读取。

### 3.2 获取 arXiv 官方源码

官方 HTML 不存在或转换质量不足时，下载
`https://arxiv.org/e-print/<versioned-arxiv-id>`。源码响应通常是压缩包，但也可能是单个 TeX、
其它压缩格式或 PDF-only 投稿；先识别实际格式，再安全解包到临时目录，禁止按文件名假定格式。
校验身份和版本后才保存为 `paper_source/`，且不得覆盖已有有效缓存。PDF-only 投稿不算文本源码，
直接进入 3.3。

从源码构造规范化全文时：

- 以包含 `\\documentclass` 和 `\\begin{document}` 的主入口为起点，递归解析实际启用的
  `\\input`/`\\include`，不能只读取字符数最大的 `.tex` 文件。
- 保留自定义宏及其定义；展开宏会改变含义或工具不可靠时，保留原始 LaTeX 表达并记录宏定义。
- 公式保留 LaTeX 环境、编号、label 和上下标；表格保留 `tabular`/`array`、多级表头、跨行跨列、
  caption、单位和脚注，不能压平成空格分隔文本。
- 读取附录和相关补充 TeX。图片可以忽略，但保留图注、label 及正文引用；参考文献可从 `.bib`
  或生成的 bibliography 中恢复。
- 发现缺失的私有样式、生成文件、条件分支或未随包提交的输入时，标记具体缺口，不能声称源码
  已完整解析。

源码包是正文证据，不等于官方实现仓库；不得从论文 TeX 中没有出现的内容推测工程实现。源码包
也不要求本地 LaTeX 编译器，文本组装和结构核验即可。

### 3.3 PDF 回退

仅当结构化全文和源码均不可用或不完整时，确定官方 PDF 地址：

- arXiv：`https://arxiv.org/pdf/<versioned-arxiv-id>`。
- OpenReview、出版社、DOI 或作者项目页：从官方落地页解析 PDF 直链，不得把 HTML 落地页、
  登录页或错误页保存为 `paper.pdf`。
- 用户提供的 URL：确认域名、标题、作者和版本后再跟随重定向。

同一来源不要无限重试。记录失败 URL、通道、退出码和错误摘要后尝试下一个已确认的官方来源。
**区分下载与工具展示限制**：`webfetch` 的 `Response too large`、二进制不支持或 markdown 转换
失败，不是官方文件下载失败。PDF 必须下载到本地，只输出路径、大小、SHA-256 和校验摘要，随后
本地提取并分段读取；不要把 PDF/base64 或全文一次性返回到工具输出。

可使用本技能的 [../scripts/fetch_paper_pdf.py](../scripts/fetch_paper_pdf.py) 流式落盘工具
（仅依赖 Python 标准库；路径从本次实际加载的技能目录解析，不能硬编码某宿主的安装路径）：

```bash
python <paper-repro技能目录>/scripts/fetch_paper_pdf.py \
  --url '<已核验的官方PDF直链>' \
  --output '.paper2code_work/<id>/paper.pdf'
```

工具检查 HTTP、完整传输、PDF 文件头/结束标记并计算散列，复用已有文件且不覆盖目标。
它不核验标题、作者、版本、页数或正文完整性；这些仍须由以下本地解析与身份核验完成。
若工具因网络或站点兼容性失败，按下述 curl/wget 流程回退；不要反复重跑同一失败通道。

通过 shell 中的 `curl` 获取 PDF，失败时以 `wget` 回退。先写入临时文件，只有校验通过后才
改名，避免中断下载或 HTML 错误页污染已有缓存。执行前再次确认目标 `paper.pdf` 不存在或已被
判定无效；不得覆盖已经验证有效的文件。

```bash
mkdir -p ".paper2code_work/<id>"
partial_pdf=".paper2code_work/<id>/paper.pdf.part"

if ! curl -L --fail --retry 2 --connect-timeout 20 --max-time 120 \
  -A "Mozilla/5.0" \
  -o "$partial_pdf" \
  "<official_pdf_url>"; then
  rm -f "$partial_pdf"
  wget --tries=2 --timeout=30 \
    --user-agent="Mozilla/5.0" \
    -O "$partial_pdf" \
    "<official_pdf_url>"
fi

test -s "$partial_pdf"
file "$partial_pdf"
```

`file` 必须将临时文件识别为 PDF；还要检查文件头、页数、标题、作者和版本。验证成功后执行
`mv "$partial_pdf" ".paper2code_work/<id>/paper.pdf"`。若文件为空、不是 PDF、无法打开，或
实际内容是 HTML、登录页、限流页或错误页，则删除临时文件并按上述受控回退规则处理，不能进入
文本提取阶段。补充材料使用相同流程，并保存为含义清楚且不会覆盖正文的文件名。

如果 HTML、源码或 PDF 获取失败，不能反向降低来源标准去使用摘要。若没有保存完整响应或解析
二进制的能力，明确报告宿主能力限制；不能将工具限制解释为“prompt 足够，论文无需读取”。只有
论文标题且无法唯一识别时，也不能根据任务描述反推一篇论文。目标身份已确认但正文或附录不可得
时，记录实际来源边界，并按第 6 节分别判断来源完整度和实现就绪度。

## 4. 规范化文本与完整性

已验证的 `paper_fulltext.html` 和 TeX 文件本身就是可直接分段读取的全文。缺少 HTML/LaTeX 转换
工具时直接读取原文件及其结构，不因此回退到 PDF，也不阻止提取。只有现有工具能够保持结构时
才生成可选的 `paper_text_full.md`；不能用正则删除标签或把 LaTeX 环境简单拼接为纯文本：

- 公式优先保留官方 HTML 中的 LaTeX annotation；没有 annotation 时保留完整 MathML。源码通道
  保留原始 LaTeX。不得把公式降为缺少上下标、分式、矩阵边界的字符序列。
- 简单表格可转 Markdown；含跨行、跨列、多级表头、公式或脚注的表格保留 HTML/LaTeX 片段。
  每个单元格与表头关系、单位、caption 和注释必须可恢复。
- 保留标题层级、列表、算法、脚注、引用、label/编号关系和附录边界。图片可省略，但图注与
  正文引用不可因删图而丢失。
- 每一段规范化内容都应能映射回原始 HTML 元素、TeX label/环境或 PDF 页，详细定位随后统一写入
  `reproduction_spec.md` 的来源索引，而不是写进科学描述。

若进入 PDF 回退，从有效 PDF 提取带页码边界的全文文本，保留公式、表格、图注、算法框和附录
的可定位信息。优先使用已有的 `pdftotext -layout paper.pdf paper_text_full.md`，也可用已有
`pymupdf`/`pypdf` 按页提取并加入页码。先确认 PDF 可打开和总页数，再分段读取全文。工具输出
被截断时缩小窗口继续，不把截断文本视为已读全文。本地解析器缺失、PDF 无文本层与网络下载失败
分别诊断；不为提取失败重复下载有效 PDF，而应回查 HTML/源码通道。

无论使用哪种通道，覆盖范围都不能只包含摘要和主文：

- 标题、作者、摘要和版本信息。
- 方法/模型/算法与相关公式。
- 数据、实验设置、训练、推理和评估。
- 结果表、消融、限制、附录和补充材料。

结构化文本与 PDF 有冲突时先核对版本。HTML 转换无法表达某个公式或表格时优先回看同版本 TeX
源码，再回看 PDF；不要用破碎 OCR、被拉平的表格或错误宏展开猜测数值列、上下标、箭头方向或
公式符号。最终只有正文、适用附录/补充材料以及任务相关公式和表格都已覆盖，才可将全文标为完整。

## 5. 官方仓库补证

论文信息缺失、含糊或因宿主限制无法完整取得时，主动读取对应官方 GitHub 等官方仓库补证；
用户禁止仓库来源时跳过并保留来源限制。仓库证据始终标为 `OFFICIAL_REPO_DETAIL`，不能因论文
不可得而升级为 `PAPER_FACT`。已有许可不重复询问：

1. 从论文或作者/项目官网确认官方仓库；无法确认时不用。
2. 定点只读相关文件或符号，不 clone、不下载快照、不复制源码。
3. 优先匹配论文版本、发布 tag 和目标实验配置，沿配置引用定位相关符号。记录论文/作者官网的
   官方身份链接、仓库 URL、固定 commit SHA（branch 还须解析到 SHA）、文件/符号/行段、
   目标实验、训练阶段、更新对象、证据摘录及所补字段。
4. 仓库与用户要求或论文不同时，按
   [source_conflict_resolution.md](source_conflict_resolution.md) 分别保留来源、适用版本、最终采用值
   和忠实度影响，不把仓库细节写成论文事实。
5. 较晚版本、其它实验或其它训练阶段的参数不能自动移用；无法确认适用范围或仍无证据时保持
   `UNRESOLVED`。官方 GitHub 补证不能代替论文全文，也不授权执行仓库代码。

## 6. 来源状态与实现就绪度

来源检查后分别记录，不能把“全文不完整”等同于“无法继续实现”：

- `source_status=verified_fulltext`：身份、版本、正文、适用的附录/补充材料以及任务相关公式和表格
  结构均已核验；完整官方 HTML/源码可以独立达到该状态，不要求同时取得 PDF。
- `source_status=partial_official_sources`：身份可确认，但只取得部分官方正文、补充材料或版本匹配的
  官方实现；明确列出未覆盖内容。
- `source_status=identity_only`：只能确认论文身份，不能把摘要或模型记忆写成论文事实。

再独立判断：

- `implementation_readiness=ready`：用户要求与来源足以闭合 data -> model -> loss -> train ->
  checkpoint -> inference -> metric 所需信息。
- `implementation_readiness=ready_with_configurable_choices`：存在明确候选或工程自由度，可通过配置、
  可替换策略或多变体实现继续交付。
- `implementation_readiness=insufficient`：目标本身无法唯一确定，或缺失的信息使任何候选都会误导
  用户且没有可隔离的实现边界。

只有 `insufficient` 才阻止 coder 交接。无论状态如何，都要记录实际读取的来源范围、缓存复用和
用户许可；不要用固定字符数、标题数量或文件存在性代替语义完整性判断。
