# 人工提交知识贡献 Issue 操作说明（Gitee 网页端）

> 适用背景：gitee.com 的建 Issue API 只服务**付费企业版空间**，对个人仓库（如 `wangqi00001/...`）和组织 group 仓库（如 `onescience-ai/...`）都会返回 `404 project or enterprise`，无法用脚本自动提交。因此知识贡献默认走本文件描述的**人工网页提交**流程。领域同事不需要懂命令行，按下面的步骤点鼠标即可。

## 谁来做

- **贡献作者**（做完一次任务、想沉淀经验的人）：触发 `onescience-knowledge-capture` 技能，技能会一次性生成本地贡献、`issue_payload.json` 与 `submission_card.md`（提交卡片由技能自动渲染，**无需再手动敲命令**）。
- **提交人**（可就是作者本人，也可由领域同事代提）：打开 Gitee 网页，把 `submission_card.md` 里的标题 / 标签 / 正文复制进去，创建 Issue。
- **审核人**：在 Issue 下评审，通过后由维护者把贡献迁移进 `onescience-primitives` 或对应技能（这一步不属于本 SOP）。

## 提交卡片从哪来（技能已自动渲染）

正常情况下**你不需要执行任何命令**：`onescience-knowledge-capture` 技能在生成 `issue_payload.json` 后，会自动调用渲染脚本在同一贡献目录产出 `submission_card.md`，把**标题、标签清单、正文**分好三块，直接对着复制即可。

只有当卡片缺失、或你手工改过 `issue_payload.json` 需要重生成时，才在 `oneskills-dev` 仓库根目录手动跑一次（只读本地文件，不联网、不碰任何 token）：

```bash
python skills/onescience-knowledge-capture/scripts/render_issue_payload.py \
  --payload skills/onescience-knowledge-capture/contributions/<domain>/<contribution_id>/issue_payload.json \
  --repo onescience-ai/oneskills-dev \
  --stdout
```

- `<domain>`：`bio` / `cfd` / `climate` / `matchem` / `general` 之一。
- `<contribution_id>`：技能生成的目录名，例如 `2026-09-16_xxx`。

> 若终端中文显示为乱码，只是 PowerShell 控制台编码问题，`submission_card.md` 文件本身是 UTF-8，用编辑器打开显示正常。

## 提交步骤（Gitee 网页端）

1. **打开目标仓库**：浏览器访问 `https://gitee.com/onescience-ai/oneskills-dev`（或你和团队约定的其它仓库），登录有权限的账号。
2. **进入 Issues**：点仓库顶部导航栏的 **「Issues」** 标签。
   - 如果提示未开启 Issues，先到仓库 **「管理」→「仓库设置」→ 功能开关** 勾选启用 Issues（需要仓库管理员权限）。
3. **新建 Issue**：点右上角 **「新建 Issue」** 按钮。
4. **填标题**：把 `submission_card.md` 中 **「① 标题」** 代码块里的整行文字复制粘贴到标题框。
   - 标题格式约定为 `[Knowledge Contribution][<domain>] <短标题>`，不要改前缀，方便后续按标签/前缀筛选。
5. **填正文**：把 **「③ 正文」** 中 `---` 分隔线之间的全部内容，复制粘贴到正文编辑框（保持 Markdown 原样，不要带最外层的 `---`）。
6. **加标签**：在右侧 **「标签 / Labels」** 处，按 **「② 标签」** 列出的名称逐个添加：
   - 必带 `knowledge-contribution`；
   - 再带上 `domain:<domain>`、`kind:<knowledge|integration|both>` 等。
   - **标签若不存在**：点标签下拉里的「新建标签」手动创建同名标签（颜色随意），创建一次后全仓库可复用。图省事也可以先只加 `knowledge-contribution`，标题里的 `[<domain>]` 前缀已足够分类。
7. **（可选）关联**：如果这个贡献是为了修某个已知问题，可在右侧关联对应的里程碑或指派给审核人；没有就留空。
8. **提交**：点 **「创建 Issue」**。
9. **登记编号**：创建成功后，把页面地址栏里的 Issue 编号（URL 末尾的 `Ixxxxx`）记下来，回到贡献目录在 `contribution.json` 的 `submission` 字段手动补上：

   ```json
   "submission": {
     "mode": "payload_only",
     "status": "submitted",
     "repository": "onescience-ai/oneskills-dev",
     "issue_number": "Ixxxxx",
     "issue_url": "https://gitee.com/onescience-ai/oneskills-dev/issues/Ixxxxx"
   }
   ```
   - 这一步保证本地贡献文档和线上 Issue 能对上，避免重复提交。

## 提交前后自检清单

- [ ] 已跑过 `validate_contribution.py`，输出 `VALID`。
- [ ] `submission_card.md` 的正文里**没有**密钥、token、内网地址、个人隐私、本机绝对路径。
- [ ] Issue 标题前缀、正文与本仓库贡献目录内容一致。
- [ ] 已把 Issue 编号回填进 `contribution.json.submission`。

## 常见问题

- **不想复制两次？** `submission_card.md` 就是为了一次看清标题+标签+正文；也可以直接打开同目录的 `issue_payload.json`，但那是 JSON、不利于粘贴。
- **能不能不建 Issue？** 如果只是想留档、暂不进入审核队列，作者可只保留本地 `contributions/` 目录，跳过网页提交；贡献状态维持 `proposed`。
- **以后能全自动吗？** 如果团队购买了 **Gitee 企业版**，把仓库迁到企业空间下，即可改脚本走 `/enterprises/{企业}/issues` 自动提交（当前个人/组织空间不支持，故先走人工）。
