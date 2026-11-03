# modelscope-resource-provisioning — 使用说明

## 何时用
任务里出现「下载模型 / 数据集」「缺少数据集 / 权重」「准备训练数据」「接入数据」，
或只给出一个训练 / 微调 / 评测 / 复现类 AI4S 任务却没点任何资源名时。

## 两个子命令
- `provision`：缺即下、物化到本地并注册（默认不回问用户）。
- `search`：只读检索，关键词 → 打分候选，供任务级规划挑选。

## 最小示例
只给裸名（无需组织名 / repo_id）：

    python scripts/fetch_resource.py provision --name pets_small

只给任务（自动反推资源需求 + 检索 + 择优）：

    python scripts/fetch_resource.py provision --name catdog_clf \
        --search-query "猫狗 图像分类" \
        --task-hint "训练一个猫狗图像分类器" \
        --max-repo-bytes 5000000

## 常用参数
- `--kind dataset|model`：仓库类型（默认 dataset）。
- `--search-query`（可多次）：追加检索词；整句 0 命中时脚本自动拆词重试。
- `--task-hint`（可多次）：任务语义提示，参与打分。
- `--max-repo-bytes` / 环境变量 `ONESCIENCE_RESOURCE_MAX_REPO_BYTES`：
  自动择优体积上限（默认 8 GiB）。
- `--candidate-attempts`：逐候选降级重试次数（默认 3）。
- `--strict-name`：多同名不猜，报 `repo_ambiguous`。
- `--allow-gated`：允许需登录的受控仓库。

## 输出解读
`selection` 字段透明给出 chosen / score / reasons / alternatives / excluded / searched，
可据此判断为何选中该仓库；`fetch.method` 表明实际走了 SDK / CLI / Git LFS 哪条路。
