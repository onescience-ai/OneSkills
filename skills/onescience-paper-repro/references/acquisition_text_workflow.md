# 下载与文本提取工作流

## 目标

获取论文正文、附录和补充材料的可读文本，并验证内容是否足够支撑后续结构化提取。本阶段只处理来源、下载、解析和完整性校验，不抽取复现结论。

## 输入来源

优先级：

1. 用户提供的本地 PDF。
2. 用户提供的 PDF/arXiv/DOI/出版页 URL。
3. 用户提供的论文标题。
4. 用户粘贴的正文片段。

优先使用论文、附录、补充材料、用户提供材料、数据集官方页面和必要的文献元数据页面。只有当这些来源对某个实现必需细节仍缺失或说明不足时，才允许补充获取官方开源仓库只读参考：先从论文材料中解析官方仓库 URL 或名称；若论文未给出，再在 GitHub 上搜索官方开源仓库。只允许在线读取与该缺失细节直接相关的模型、数据处理、特征/变量选择、训练、推理、评估实现内容，禁止下载、clone、复制仓库到本地，禁止使用第三方复现仓库，也不得把官方仓库当成默认首轮信息源。

## 工作目录

所有下载、复制和解析得到的论文材料必须保存到 `.paper2code_work/<id>/`。`<id>` 的确定规则：

1. 优先使用不带版本号的 arXiv ID，例如 `2406.01465v2` 的目录仍为 `.paper2code_work/2406.01465/`。
2. 无 arXiv ID 但有 DOI 时，使用 DOI slug。
3. 只有标题时，使用标题 slug；后续识别到 arXiv ID 后迁移到 `.paper2code_work/<arxiv_id>/`。
4. 不得把论文 PDF、补充材料或解析文本保存到用户指定 `output_dir`；`output_dir` 只用于最终代码生成。

推荐布局：

```text
.paper2code_work/<id>/
  paper.pdf
  paper_text_full.md
  paper_text.md
  paper_sections/
  figures_tables.md
  extraction_notes.md
  paper_content_summary.md
  variable_channel_ledger.json
  reproduction_spec.md
  coder_task_description.md
  download_errors.md
```

用户指定的 `output_dir` 只表示最终代码生成位置，不改变论文工作目录。

## PDF 优先策略

禁止把 arXiv HTML、ar5iv 或其它 HTML 镜像作为主要来源；长论文可能被截断。优先下载 PDF：

- arXiv：`https://arxiv.org/pdf/<arxiv_id>`
- 其它来源：优先 PDF 直链或出版页 PDF
- 保存为 `.paper2code_work/<id>/paper.pdf`

PDF 下载必须通过 `bash` 工具执行 `curl` 或 `wget`，不要使用浏览器、HTML 镜像或非命令行下载方式。下载前先创建论文工作目录，下载后检查目标文件非空且文件头是 PDF；如果 `curl` 失败，再用 `wget` 兜底。

推荐命令：

```bash
mkdir -p ".paper2code_work/<id>"
curl -L --fail --retry 3 --connect-timeout 20 \
  -A "Mozilla/5.0" \
  -o ".paper2code_work/<id>/paper.pdf" \
  "<pdf_url>" \
|| wget --tries=3 --timeout=30 --user-agent="Mozilla/5.0" \
  -O ".paper2code_work/<id>/paper.pdf" \
  "<pdf_url>"

test -s ".paper2code_work/<id>/paper.pdf"
file ".paper2code_work/<id>/paper.pdf"
```

如果 `file` 输出不是 PDF、文件为空、返回的是 HTML/登录页/错误页，删除无效 `paper.pdf`，把 URL、命令、退出码和错误摘要写入 `download_errors.md`，再尝试其它官方 PDF 来源或请求用户提供完整 PDF。补充材料如果是 PDF，也按同样方式下载到论文工作目录中的清晰文件名，例如 `supplement.pdf`。

## 文本提取

优先使用 `pymupdf` 提取全文：

```python
import pymupdf

doc = pymupdf.open("<paper_workdir>/paper.pdf")
with open("<paper_workdir>/paper_text_full.md", "w", encoding="utf-8") as f:
    for i, page in enumerate(doc):
        f.write(f"## Page {i + 1}\n\n")
        f.write(page.get_text())
        f.write("\n\n")
```

备选：`pdfminer`。如果用户粘贴正文，直接写入 `paper_text.md`，并在后续 `reproduction_spec.md` 标注来源。

## 内容完整性校验

提取后必须检查：

- 标题、作者、摘要是否存在。
- 方法/模型/实验/结果/附录等核心章节是否存在或可定位。
- 表格、图注、算法框、公式是否有可读文本或可截图定位。
- 是否存在明显截断、乱码、重复页、页码跳跃或关键章节缺失。
- 用户任务所需的关键信息是否可定位，例如任务定义、数据、模型、训练、推理、评估。

完整性校验是领域无关的；不要在这里写某个领域的变量表或指标结论。

## 输出文件

- `paper_text_full.md`：PDF 原始全量提取文本。
- `paper_text.md`：按章节整理后的可读文本。
- `paper_sections/`：按章节拆分，按需创建。
- `figures_tables.md`：图注、表格、算法框、公式位置和内容摘要。
- `download_errors.md`：下载失败、补充材料不可访问或解析失败时创建。

不要生成 `paper_source.json` 或 `evidence_index.md`；来源元数据和证据位置后续写入 `reproduction_spec.md`。

## 失败处理

如果论文无法获取或文本不足：

- 输出已获得的来源、URL、错误和缺失项。
- 请求用户提供完整 PDF、补充材料或正文。
- 只有摘要时，只能生成“摘要级复现草案”，并标记不可直接编码。
