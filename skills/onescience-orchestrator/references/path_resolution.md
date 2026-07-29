# Path Resolution Strategy

本文档定义 orchestrator 在执行 `orchestrator_step` 中文件搜索操作时的渐进式路径解析策略。当用户提供的路径信息较模糊、或前次搜索失败时，必须按本文档执行，不得随机尝试不同路径。

## 1. 路径解析原则

- **优先使用用户明确指定的路径**：若用户已提供完整路径，直接使用；不要额外搜索。
- **优先使用 `onescience.json` 中已记录的环境变量**：`ONESCIENCE_MODELS_DIR` 和 `ONESCIENCE_DATASETS_DIR` 如果在 `onescience.json.runtime.script.env_vars` 中已有有效值，优先使用。
- **逐步放宽搜索范围**：每次失败后必须分析原因（工具不可用、路径层级错误、模式失配），再调整策略；不得直接换一种模式无差别重试。
- **最多 3 轮渐进式重试**：每轮都需要明确的策略调整依据；达到 3 轮上限后不再继续搜索，改为向用户报告候选目录。
- **每次搜索前评估工具可用性**：在执行搜索命令前，先确认目标环境是否具备所需的搜索工具（如 `find`、`ls`、`grep`、`rg`、`locate`）。对于远程主机，优先通过 SSH 执行搜索命令。

## 2. 渐进式路径搜索策略

### 第 1 轮：精确匹配

**目标**：用最精确的模式定位文件。

1. 从用户描述中提取关键路径片段（目录名、文件名）
2. 构造候选路径：`已知的工作目录 + 用户提到的路径片段`
3. 日志输出中包括：当前轮次、候选基础路径、匹配模式
4. 使用 Glob 精确搜索，如 `**/<keyword>` 或 `**/<keyword>/**`

**示例**：
- 用户说 "onescience仓库中的evo2"，已知工作目录 `/public/home/onesci/bioscience/`
- 构造候选路径：`/public/home/onesci/bioscience/onescience/`
- 搜索模式：`**/*evo2*`（注意：使用 `*keyword*` 包含匹配而非仅前缀匹配）

### 第 2 轮：前缀/包含匹配

**目标**：放宽匹配条件，扩大搜索范围。

若第 1 轮失败，分析失败原因后执行：

1. **模式放宽**：将 `**/keyword` 改为 `**/*keyword*`（前缀匹配 → 包含匹配）
   - 案例：`**/*evo*` → `**/*evo*` 未能匹配 `evo2_s288c_chrV_completion` 时，先检查是否是 Glob 工具对 `_` 的特殊处理导致；若是，改为在目标目录下列出全部内容再手动过滤
2. **层级放宽**：将 `**/path_a/path_b` 尝试去掉中间层级
   - 案例：`/public/home/onesci/onescience` 不存在 → 改为列出 `/public/home/onesci/` 顶层目录，发现实际存在 `bioscience/` 子目录，然后构造 `/public/home/onesci/bioscience/onescience/`
3. **大小写不敏感变体**：若适用，尝试大小写变体

**关键**：在第 2 轮放宽之前，必须先分析第 1 轮失败的具体原因（路径不存在、模式不匹配、工具报错），然后有针对性地调整，不是无差别放宽。

### 第 3 轮：语义关联搜索

**目标**：基于目录结构推断候选路径。

若前两轮均失败：

1. 先列出现有工作目录的顶层结构（使用 `ls` 或 `Glob` 列出子目录，不使用通配符全局搜索）
2. 从顶层目录名称中找出与用户关键字语义相关的候选目录
3. 在筛选出的候选目录内进行精确搜索
4. 若必须搜索较大范围目录，限制在已知项目目录内（如 `/public/home/onesci/`），避免在 `/` 或 `/home/` 级别搜索触发用户拒绝

**第 3 轮结束后的处理**：
- 若仍未找到：不继续搜索，改为向用户报告搜索结果
- 报告内容：已尝试的路径列表、每次失败的原因、当前可见的相关目录结构、建议用户选择或提供更精确的路径

## 5. 模型权重路径快速定位

当用户提及"onemodel"、"模型权重"、"权重文件"或具体模型名（如 evo2、AlphaFold3、ESM）时，在启动渐进式搜索前，先执行以下快速路径：

### 5.1 从 onescience.json 获取

1. 检查 `onescience.json.runtime.script.env_vars.ONESCIENCE_MODELS_DIR`：
   - 若值非空且非默认值（`/public/share/sugonhpcapp01/onestore/onemodels/`），直接使用该路径作为模型根目录。
   - 若为默认值，说明 installer 未探测到 workspace 特有路径，继续下一步。

### 5.2 检查环境变量

2. 在目标执行环境中 echo `$ONESCIENCE_MODELS_DIR`：
   - 远程：`ssh {ssh_user}@{ssh_server} 'echo $ONESCIENCE_MODELS_DIR'`
   - 若返回非空且路径存在（`test -d`），直接使用。

### 5.3 探测常见 workspace 路径

3. 按以下优先级探测常见路径（按 workspace 类型）：
   - `/public/home/onesci/bioscience/onemodel/` — 生信 workspace
   - `/public/home/onesci/onemodel/` — 通用 workspace
   - `/public/share/sugonhpcapp01/onestore/onemodels/` — 共享存储
   
   若上述路径存在且包含目标模型子目录，使用该路径。

### 5.4 定位特定模型

4. 在模型根目录下定位具体模型：
   - 若用户提到"onemodel 中查找"但未指定具体模型名，列出模型根目录的子目录供选择。
   - 若用户提到具体模型名（如 evo2），在模型根目录下搜索对应子目录：
     ```bash
     find <MODELS_DIR> -maxdepth 2 -type d -iname "*<model_keyword>*" 2>/dev/null
     ```

### 5.5 成功后写回

5. 若通过上述步骤定位到有效路径，且 `onescience.json` 中尚未记录，建议通过 `onescience-installer` 写回，或在当前会话中记录为 `resource_bindings.model_root`。

### 参考案例

| 用户提示 | 模型根目录定位 | 具体模型路径 |
|---|---|---|
| "所需模型权重可在 onemodel 中查找"（bioscience workspace） | `/public/home/onesci/bioscience/onemodel/`（通过探测发现） | `evo2/evo2_7b_262k/`, `AlphaFold3/`, `esm_models/` |
| 没有 workspace 上下文 | `/public/share/sugonhpcapp01/onestore/onemodels/`（默认值） | 按需搜索 |

## 6. 远程 vs 本地路径处理

### 6.1 工具可用性检查

在执行搜索命令前，先确认目标环境可用的搜索工具：

| 环境 | 优先工具 | 回退工具 |
|------|----------|----------|
| 本地 Windows | Glob（IDE 工具） | — |
| 本地 Linux | Glob / find | ls + grep |
| SSH 远程 Linux | `find` + `grep`（通过 SSH 执行） | `ls` + 手动遍历 |

**注意**：
- 不要假设远程主机安装了 `rg`（ripgrep）。若 `rg` 不可用，立即回退到 `find` 或 `ls`
- 案例：`rg` 在远程主机上未安装 → 应回退到 `find <remote_path> -name "<pattern>" -type d`

### 6.2 SSH 远程搜索

若涉及 SSH 远程主机，搜索命令通过 SSH 执行：

```bash
ssh <host> 'find <remote_path> -name "<pattern>" -type d 2>/dev/null'
```

远程搜索失败时，先检查 SSH 连接是否正常、路径前缀是否存在，再调整搜索策略。

## 7. 失败诊断与用户反馈

搜索失败时，按以下标准流程处理：

### 7.1 分析失败原因

每次 Glob/Grep/Bash 搜索失败后，必须分析：

1. **工具不可用**：工具是否安装？→ 回退到更基础的工具
2. **路径不存在**：目录是否实际存在？→ 列出父目录确认实际结构
3. **模式失配**：匹配模式是否过于严格？→ 放宽模式
4. **权限拒绝**：是否有权限访问？→ 缩小搜索范围

### 7.2 用户反馈格式

当 3 轮搜索均失败后，向用户输出：

```
【路径搜索报告】
- 搜索目标：<用户描述的关键文件/目录>
- 已尝试的搜索：
  - 第 1 轮：<路径> + <模式> → <失败原因>
  - 第 2 轮：<路径> + <模式> → <失败原因>
  - 第 3 轮：<路径> + <模式> → <失败原因>
- 当前可见的相关目录：
  - <目录 A>（<简要描述>）
  - <目录 B>（<简要描述>）
- 建议：请确认目标文件位于以上哪个目录，或提供更精确的路径信息。
```

### 7.3 参考案例

失败路径与正确路径对照：

| 搜索的路径 | 失败原因 | 正确的路径 |
|-----------|----------|-----------|
| `/public/home/onesci/onescience/` | 缺少中间目录 `bioscience/` | `/public/home/onesci/bioscience/onescience/` |
| `rg` 命令搜索 | 远程主机未安装 `rg` | 回退到 `find` |
| `**/*evo*` | Glob 未匹配含下划线的目录名 | 先 `ls` 列出目录再手动匹配 |

从以上案例中总结的标准应对：
- 路径层级错误 → 列出父目录确认实际结构，再构造正确路径
- 远程工具缺失 → 确认可用工具，回退到基础命令
- Glob 模式失配 → 改为先列出目录内容，再按目录名手动筛选
