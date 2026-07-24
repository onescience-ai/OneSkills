---
name: onescience-modelscope-publish
description: OneScience ModelScope 模型发布技能。将论文复现模型产物重组为 ModelScope 标准目录结构，检查核心目录内容完整性，生成平台必需的配置模板和审计工具，并输出 modelscope upload 命令引导用户推送到魔搭平台。作为 onescience-orchestrator 的执行技能使用。
type: executor
---

# OneScience ModelScope 模型发布

## 职责边界

本技能负责将论文复现后的模型产物按 ModelScope（魔搭）仓库规范重组为标准目录结构，引导用户推送模型。**不执行 `modelscope upload` 命令本身**。

- 作为执行技能：由 `onescience-orchestrator` 调用，接收标准化输入，返回标准化输出。
- 核心职责：产物扫描归类、目标目录创建、文件复制组织、空目录检查、平台模板生成、上传命令输出。
- 不负责：模型训练、推理验证、ModelScope 账号认证、token 管理、手动分类纠错后的重新打包。

## 输入输出接口

### 输入（从 onescience-orchestrator 接收）

```yaml
pack_handoff:
  source_dir: <论文复现产物根目录（绝对路径）>
  model_name: <ModelScope 上的模型名称，如 "MARIO">
  target_dir: <目标输出目录，可选，默认为当前工作目录>
  modelscope_org: <ModelScope 组织名，可选，默认为 "OneScience">
```

### 输出（返回给 onescience-orchestrator）

```yaml
execution_result:
  skill: onescience-modelscope-publish
  status: <success | partial | failed>
  artifacts:
    target_dir: <目标目录绝对路径>
    directories_created: [model, weight, scripts, conf]
    files_copied_count: <归类复制的文件总数>
    files_excluded_count: <排除的文件总数>
    files_by_category:
      model: <归入 model/ 的文件列表>
      weight: <归入 weight/ 的文件列表>
      scripts: <归入 scripts/ 的文件列表>
      conf: <归入 conf/ 的文件列表>
      excluded: <排除（未复制）的文件列表>
    templates_generated: [configurations.json, README.md]
  observation:
    empty_directories: [<内容为空的子目录名称列表>]
    warnings: [<告警信息列表>]
    script_availability:
      train: <found | missing>
      inference: <found | missing>
      evaluation: <found | missing>
    upload_command: "modelscope upload {org}/{model_name} {model_name} --token ***"
  notes: <补充说明>
```

## 核心流程

### 阶段一：输入校验

1. 校验 `source_dir` 是否存在且为有效目录路径。
   - 若不存在，返回 `status=failed`，提示用户确认产物目录路径。
2. 校验 `source_dir` 是否有可访问的文件。
   - 若目录为空，返回 `status=failed`，提示用户确认产物目录是否包含文件。
3. 若 `model_name` 为空，尝试从 `source_dir` 的父目录名推断，若仍无法推断，询问用户指定。

### 阶段二：产物扫描与分类

1. 递归遍历 `source_dir` 下的所有文件（排除隐藏文件和 `.ipynb_checkpoints/`）。
2. 对每个文件，按以下**文件分类规则**确定目标子目录：

| 扩展名 | 目标子目录 | 匹配条件 |
|--------|-----------|---------|
| `.py` | `model/` | 文件名含：`model`、`net`、`module`、`nn`、`backbone`、`unet`、`encoder`、`decoder`、`layer`、`block`、`attention`、`transformer`、`resnet`、`vgg`、`densenet`、`lstm`、`gru`、`gan`、`diffusion`、`embedding`、`activation`、`normalization`、`conv`、`pooling`、`head`、`neck` |
| `.py` | `scripts/` | 文件名含：`train`、`infer`、`eval`、`test`、`preprocess`、`run`、`main`、`demo`、`predict`、`deploy`、`serve`、`download`、`setup`、`install`、`convert`、`export`、`benchmark`、`profile` |
| `.py` | `model/` | 其他 `.py` 文件默认归入 model/ |
| `.pth`, `.pt`, `.ckpt`, `.safetensors`, `.bin`, `.h5`, `.keras`, `.onnx`, `.pb`, `.pkl`, `.joblib`, `.weights` | `weight/` | 模型权重文件 |
| `.yaml`, `.yml`, `.json`, `.toml`, `.ini`, `.cfg`, `.conf`, `.config` | `conf/` | 配置文件（排除根目录的 `configurations.json`） |
| `.sh`, `.bash`, `.bat`, `.ps1` | `scripts/` | Shell 脚本 |
| `.ipynb` | `scripts/` | Jupyter Notebook |
| `.log`, `.csv`, `.tsv`, `.npy`, `.npz`, `.png`, `.jpg`, `.jpeg`, `.pdf`, `.tar`, `.gz`, `.zip`, `.pickle`, `.data`, `.db`, `.sqlite`, `.txt`, `.md`, `.pkl`（非权重类）、`.gitattributes`、`.gitignore` | **排除** | 与模型配置/权重/训练测试脚本无关的文件，不放入目标目录 |

### 阶段三：目标目录创建与文件复制

1. 确定目标根目录：`{target_dir}/{model_name}/`。
   - 若 `target_dir` 未指定，使用当前工作目录。
2. 创建子目录：`model/`、`weight/`、`scripts/`、`conf/`。
3. 按分类结果将文件**复制**（非移动）到对应子目录。
   - 源目录中的文件不做任何修改。
   - 若目标文件已存在，覆盖写入（幂等操作）。
4. 输出分类统计信息（每个子目录的文件数量和文件名）。

### 阶段四：空目录检查

1. 检查以下四个核心目录是否包含文件：
   - `target_dir/model/`
   - `target_dir/weight/`
   - `target_dir/scripts/`
   - `target_dir/conf/`
2. 若某个目录为空（无任何文件），输出以下格式的告警信息：

   ```text
   ⚠️ 警告：{子目录名称} 文件夹下内容为空。
   原因：源产物目录中未找到可归类到 {子目录名称}/ 的文件。
   建议：请确认是否需要补充 {对应的文件类型} 后再推送。
   ```

3. 空目录告警不阻断流程，仅记录在 `observation.warnings` 和 `observation.empty_directories` 中。
4. 若所有核心目录均为空，设置 `status=partial`；否则为 `success`。

### 阶段五：模板文件生成

在目标根目录（`{target_dir}/{model_name}/`）生成以下文件：

#### 5.1 `configurations.json`（魔搭模型身份证骨架）

```json
{
  "framework": "请根据模型填写，如 PyTorch / TensorFlow / PaddlePaddle",
  "task": "请根据模型填写任务类型",
  "allow_remote": true,
  "model": {
    "type": "请填写魔搭平台识别的模型类型",
    "repo_id": "OneScience/{model_name}"
  },
  "pipeline": {
    "type": "请填写魔搭 pipeline 类型"
  },
  "preprocessor": {},
  "train": {}
}
```

#### 5.2 `README.md`（模型卡片页）

README.md 基于 `references/template_README.md` 的结构生成，并根据 `source_dir` 扫描结果填充实际内容。生成策略如下：

**第一步：扫描 source_dir 收集填充素材**

在阶段二文件分类完成后，汇总以下信息：
- 分类到 `model/` 的文件名列表（推断模型架构类型）
- 分类到 `scripts/` 的文件名列表（识别训练/推理/评估入口脚本）
- 分类到 `weight/` 的文件名列表及文件大小
- 分类到 `conf/` 的配置文件名列表
- 检测框架类型：若权重文件含 `.pth`/`.pt`/`.safetensors`，框架为 PyTorch；若含 `.h5`/`.keras`，框架为 TensorFlow/Keras；默认 PyTorch
- 检测 `source_dir` 中是否存在论文引用文件（`.pdf` 文件名、`README.md` 中的论文标题/链接等）

**第二步半：命令可用性检查（在生成 README 命令前执行，静态文件存在性检查）**

对于 README 中即将生成的 `python scripts/{script_name}` 类运行命令，必须先验证目标脚本是否**实际存在于** `target_dir/scripts/` 目录中，确保生成的命令可执行。

1. 列出 `target_dir/scripts/` 目录下所有实际存在的文件名（不含路径前缀），记为 `available_scripts`。
2. 对以下三类命令，分别检查对应的脚本文件：
   - **训练命令**：检查 `available_scripts` 中是否存在文件名匹配 `train` 或 `run` 关键字的 `.py` 或 `.sh` 文件
   - **推理命令**：检查 `available_scripts` 中是否存在文件名匹配 `infer` 或 `predict` 关键字的 `.py` 或 `.sh` 文件
   - **评估命令**：检查 `available_scripts` 中是否存在文件名匹配 `eval` 或 `test` 关键字的 `.py` 或 `.sh` 文件
3. **检查规则**：
   - 若脚本文件**存在** → 正常生成实际命令，如 `python scripts/train.py`
   - 若脚本文件**不存在** → **不生成该命令**，改用 HTML 注释标注缺失原因，如 `<!-- 训练脚本未在 scripts/ 目录中找到，请补充 -->`
   - 此规则同样适用于**训练节**、**推理节**、**评估和可视化节**三个章节
4. 此检查**仅验证文件是否存在于目标目录**，不验证语法正确性、依赖完整性和运行时行为（这些属于用户职责）。
5. 检查结果写入 `observation.script_availability`：

   ```yaml
   observation:
     script_availability:
       train: <found | missing>
       inference: <found | missing>
       evaluation: <found | missing>
   ```

**第三步：按章节构造 README.md**

直接输出 Markdown 格式内容，不使用模板变量（除 `{model_name}`、`{modelscope_org}` 外）。各章节填充规则：

| 章节 | 填充策略 |
|------|---------|
| **Frontmatter** | 使用 `license: Apache License 2.0`；`tasks` 字段根据 `scripts/` 中检测到的脚本类型填入（如 `[train, inference, evaluation]`），无法确定时使用 `- 请根据模型填写任务类型`；`frameworks` 根据检测到的框架类型填入；`language` 固定 `[en, zh]`；`tags` 固定含 `OneScience`，并进行关键词补充；`datasets` 若 source_dir 中有明确数据集引用则填入，否则使用 `- 请填写训练数据集` |
| **模型名称居中标题** | `<p align="center"><strong><span style="font-size: 30px;">{model_name}</span></strong></p>` |
| **# 模型介绍** | 若 source_dir 中存在 README.md 且含论文描述，提取并改写为模型介绍简介；否则填写 `（请在此处描述模型的背景、论文来源和应用场景）` |
| **# 模型描述** | 列出 model/ 中的主要模型文件（如 `model.py`、`net.py` 等），根据文件名关键词推测架构类型（如含 `transformer` → "Transformer 架构"），以列表形式呈现；若 model/ 为空则填写通用占位 |
| **# 适用场景** | 根据 scripts/ 中检测到的脚本生成场景表格，格式：`| 场景 | 说明 |`，每行一个场景（如 "模型训练 | 使用 xxx 数据训练"、"模型推理 | 加载权重进行预测"等）。若某类命令因脚本缺失未生成，对应场景仍保留说明行 |
| **# 使用说明 → OneCode 使用** | 保留模板中的固定内容 |
| **# 使用说明 → 手动安装使用 → 硬件要求** | 保留模板中的 GPU/DCU/CPU 说明 |
| **# 使用说明 → 手动安装使用 → 下载模型包** | 将模板中的 `modelscope download --model OneScience/Template` 替换为 `modelscope download --model {modelscope_org}/{model_name}` |
| **# 使用说明 → 手动安装使用 → 安装运行环境** | 保留 DCU/GPU 的 conda + pip 安装命令 |
| **# 使用说明 → 手动安装使用 → 训练数据介绍** | 若 source_dir 中有数据集相关信息（文件名、路径引用等），生成具体的下载说明；否则保留占位 `（请在此处说明训练数据来源和获取方式）` |
| **# 使用说明 → 手动安装使用 → 训练** | 基于**第二步半的检查结果**：若 `script_availability.train == found`，生成实际命令（如 `python scripts/train.py`）；若为 `missing`，用 HTML 注释标注 `<!-- 训练脚本未在 scripts/ 目录中找到，请补充 -->`，不生成不可执行的命令 |
| **# 使用说明 → 手动安装使用 → 训练权重** | 若 weight/ 非空，列出权重文件清单；否则填写"即将上传" |
| **# 使用说明 → 手动安装使用 → 推理** | 基于**第二步半的检查结果**：若 `script_availability.inference == found`，生成实际命令；若为 `missing`，用 HTML 注释标注 `<!-- 推理脚本未在 scripts/ 目录中找到，请补充 -->` |
| **# 使用说明 → 手动安装使用 → 评估和可视化** | 基于**第二步半的检查结果**：若 `script_availability.evaluation == found`，生成实际命令；若为 `missing`，用 HTML 注释标注 `<!-- 评估脚本未在 scripts/ 目录中找到，请补充 -->` |
| **# OneScience 官方信息** | 保留模板中的 Gitee/GitHub 链接表格 |
| **# 引用与许可证** | 若 source_dir 中有明确论文引用（标题、链接），提取并填写；否则填写 `（请在此处填写论文引用信息）` |

**第四步：关键原则**

- 能从 source_dir 推断的信息，**必须自动填充**（如脚本路径、权重文件列表、框架类型），不得留空位
- 无法推断的信息，使用中文占位提示如 `（请填写...）`，确保用户知道需要补充
- 模板中的固定内容（OneCode 链接、OneScience 官方信息、安装命令、硬件要求）直接原样保留
- 输出格式为完整可用的 Markdown 文件，不包含任何"此处应填写模板"等元说明
- **命令可用性优先**：不生成引用不存在脚本的命令；缺失命令以注释标注，不输出不可执行的代码块

### 阶段六：输出上传引导命令

1. 在所有检查完成后，输出以下信息：

   ```text
   模型产物已重组完成，目标目录：{target_dir_absolute}

   目录结构概览：
   model/     - {file_count} 个文件
   weight/    - {file_count} 个文件
   scripts/   - {file_count} 个文件
   conf/      - {file_count} 个文件
   (已排除)    - {file_count} 个文件（日志/数据/临时文件等，未复制到目标目录）

   {如果有空目录告警，在此显示}

   模板文件已生成：
   - configurations.json（魔搭模型身份证骨架，需手动补充模型信息）
   - README.md（模型卡片页）

   使用以下命令将模型推送到 ModelScope：
   modelscope upload {org}/{model_name} {model_name} --token ***
   ```

2. `modelscope upload` 命令格式：
   - `{org}`：由 `modelscope_org` 参数指定，默认 `OneScience`
   - `{model_name}`：由 `model_name` 参数指定
   - `--token ***`：token 占位符，提示用户替换为自己的 ModelScope access token

## 文件分类规则（完整映射表）

`.py` 文件根据文件名关键词进行二次分类：

**归类到 `model/` 的关键词**（模型结构/网络定义类）：
`model`、`net`、`module`、`nn`、`backbone`、`unet`、`encoder`、`decoder`、`layer`、`block`、`attention`、`transformer`、`resnet`、`vgg`、`densenet`、`lstm`、`gru`、`gan`、`diffusion`、`embedding`、`activation`、`normalization`、`conv`、`pooling`、`head`、`neck`

**归类到 `scripts/` 的关键词**（脚本/入口类）：
`train`、`infer`、`eval`、`test`、`preprocess`、`run`、`main`、`demo`、`predict`、`deploy`、`serve`、`download`、`setup`、`install`、`convert`、`export`、`benchmark`、`profile`

**默认规则**：未匹配以上关键词的 `.py` 文件默认归入 `model/`。

## 文件排除规则

以下类型文件与模型配置、权重、训练/测试脚本无关，**直接排除，不放入目标目录**：

| 排除项 | 说明 |
|--------|------|
| `.log` | 训练/运行日志文件 |
| `.csv`, `.tsv` | 数据表格文件（如训练日志导出的 loss/accuracy 记录） |
| `.npy`, `.npz` | NumPy 数据文件（训练/测试用的中间数据） |
| `.png`, `.jpg`, `.jpeg`, `.pdf` | 图片/文档文件（如可视化图表、论文 PDF） |
| `.tar`, `.gz`, `.zip` | 压缩归档文件 |
| `.pickle`, `.data`, `.db`, `.sqlite` | 序列化数据/数据库文件 |
| `.pkl`（非权重类） | 非模型权重的 pickle 文件（需结合文件名判断） |
| `.txt` | 文本文件（如日志、notes、requirements 等） |
| `.md` | Markdown 文档文件 |
| `gitattributes`（无前置点） | 无前置点的 `gitattributes` 不被 git 识别为配置文件，属误生成文件，应删除。仅 `.gitattributes`（带点）有效。 |

> **例外**：`.pkl` 若为模型权重文件（文件名含 `weight`/`model` 等关键词）仍归入 `weight/`。

## 空目录检查规则

- 核心检查目录：`model/`、`weight/`、`scripts/`、`conf/`
- 检查时机：文件复制完成后、模板文件生成前
- 判定标准：目录下不含任何文件（空目录递归扫描，忽略子目录）
- 告警格式：

  ```text
  ⚠️ 警告：{dir_name}/ 文件夹下内容为空。 原因：源产物目录中未找到可归类到 {dir_name}/ 的文件。 建议：请确认是否需要补充{对应文件类型}后再推送。
  ```

  - `model/` 空 → 提示"模型结构代码文件"
  - `weight/` 空 → 提示"模型权重文件（.pth/.ckpt/.safetensors 等）"
  - `scripts/` 空 → 提示"训练/推理脚本文件"
  - `conf/` 空 → 提示"配置文件（.yaml/.json 等）"

## 输出契约

执行完成后必须返回标准化的 `execution_result`（符合"输入输出接口"章节定义），包含：

- `status`：`success`（所有核心目录非空）、`partial`（存在空核心目录）、`failed`（source_dir 不可用或无文件）
- `artifacts`：包含目标目录路径、创建的子目录列表、文件分类统计和生成的模板文件列表
- `observation`：包含空目录列表、告警信息和上传命令字符串
- `notes`：补充说明（如分类过程中的特殊情况）
