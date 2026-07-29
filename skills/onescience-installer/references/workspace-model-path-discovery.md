# 工作流 - Workspace 模型路径自动发现

当 installer 完成 conda 环境检测或安装后，自动探测 workspace 中是否存在模型权重目录与数据集目录，并写入 `onescience.json`。

## 目的

许多已有 workspace（如 `/public/home/onesci/bioscience/`）在 `<workspace>/onescience/env.sh` 或 `<workspace>/onemodel/` 中已经预置了模型权重路径，但 `onescience.json` 的默认配置可能指向不同路径。本工作流在 installer 检测到已有环境后，自动探测并写入正确的模型与数据集路径，**避免下游技能在模型加载阶段反复搜索模型路径**。

## 触发时机

- `detect-existing-onescience.md` 检测到情况 A（当前环境有 onescience）或情况 B（conda 环境有 onescience）之后
- `install-onescience-conda.md` 或 `install-onescience-current.md` 安装验证成功之后
- 用户明确指定了 `bioscience-xxx` 或类似 workspace 相关环境名时

## 步骤

### 1. 探测 workspace 根路径

从上下文推断 workspace 根路径，优先级：

1. `onescience.json.runtime.ssh.remote_work_dir`（远程 workspace）
2. `onescience.json.runtime.script.work_dir` 及当前项目路径向上搜索
3. 用户提到的已知路径（如 `/public/home/onesci/bioscience/`）
4. 根据 conda 环境名前缀推断（如 `bioscience-evo2` → 检查 `/public/home/onesci/bioscience/`）

### 2. 探测 `env.sh` 中的环境变量

在推测的 workspace 根路径下，按以下顺序搜索 `env.sh`：

```bash
# 远程
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'bash -lc "for dir in {workspace_root} {workspace_root}/onescience /public/home/onesci/bioscience /public/home/onesci/bioscience/onescience; do if [ -f \$dir/env.sh ]; then echo ENV_SH_FOUND=\$dir/env.sh && source \$dir/env.sh 2>/dev/null && echo ONESCIENCE_MODELS_DIR=\${ONESCIENCE_MODELS_DIR:-NOT_SET} && echo ONESCIENCE_DATASETS_DIR=\${ONESCIENCE_DATASETS_DIR:-NOT_SET}; break; fi; done"'

# 本地
bash -lc "for dir in {workspace_root} {workspace_root}/onescience /public/home/onesci/bioscience /public/home/onesci/bioscience/onescience; do if [ -f \$dir/env.sh ]; then echo ENV_SH_FOUND=\$dir/env.sh && source \$dir/env.sh 2>/dev/null && echo ONESCIENCE_MODELS_DIR=\${ONESCIENCE_MODELS_DIR:-NOT_SET} && echo ONESCIENCE_DATASETS_DIR=\${ONESCIENCE_DATASETS_DIR:-NOT_SET}; break; fi; done"
```

### 3. 探测 `onemodel` 目录直接存在性

如果 `env.sh` 未找到或未设置 `ONESCIENCE_MODELS_DIR`，直接探测常见路径下是否存在 `onemodel` 目录：

```bash
# 远程
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'for dir in {workspace_root}/onemodel /public/home/onesci/bioscience/onemodel /public/share/sugonhpcapp01/onestore/onemodels; do if [ -d "$dir" ]; then echo ONEMODEL_DIR=$dir && ls "$dir/" 2>/dev/null | head -10; break; fi; done'

# 本地
for dir in {workspace_root}/onemodel /public/home/onesci/bioscience/onemodel /public/share/sugonhpcapp01/onestore/onemodels; do if [ -d "$dir" ]; then echo ONEMODEL_DIR=$dir && ls "$dir/" 2>/dev/null | head -10; break; fi; done
```

### 4. 探测 `onedata` 目录

```bash
# 远程
ssh {ssh_options} -p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server} 'for dir in {workspace_root}/onedata /public/home/onesci/bioscience/onedata /public/share/sugonhpcapp01/onestore/onedatasets; do if [ -d "$dir" ]; then echo ONEDATA_DIR=$dir && ls "$dir/" 2>/dev/null | head -10; break; fi; done'
```

### 5. 写回 `onescience.json`

若探测到路径，且与现有配置不同（或现有配置为默认值），写入：

```json
{
  "runtime": {
    "script": {
      "env_vars": {
        "ONESCIENCE_MODELS_DIR": "<探测到的模型路径>",
        "ONESCIENCE_DATASETS_DIR": "<探测到的数据集路径>"
      }
    }
  }
}
```

**写回规则**：
- 如果 `onescience.json.runtime.script.env_vars` 中已有用户显式设置的值（非默认值），保留用户值，不覆盖。
- 默认值判定：`ONESCIENCE_MODELS_DIR` 为 `/public/share/sugonhpcapp01/onestore/onemodels/` 时视为默认值，可覆盖；否则为用户显式设置，保留。
- 只写入实际探测到的路径；未探测到的字段不写入。

### 6. 输出报告

```
【模型路径自动发现报告】
- env.sh 位置: <路径 或 未找到>
- ONESCIENCE_MODELS_DIR: <路径>
  - 探测方式: <env.sh 解析 / 目录直接探测 / onemodel 目录发现>
  - 目录内容预览: <列出前 5-10 个子目录/文件>
- ONESCIENCE_DATASETS_DIR: <路径 或 未找到>
- 写入 onescience.json: <是/否（原因）>
```

## 参考案例

从历史会话中总结的典型 workspace 布局：

| workspace 根路径 | env.sh 路径 | onemodel 路径 | 环境名前缀 |
|---|---|---|---|
| `/public/home/onesci/bioscience/` | `.../onescience/env.sh` | `.../onemodel/evo2/`, `.../onemodel/AlphaFold3/`, `.../onemodel/esm_models/` | `bioscience-` |
| `/public/share/sugonhpcapp01/onestore/` | 无 | `.../onemodels/` | — |

`env.sh` 典型内容：
```bash
export ONESCIENCE_DATASETS_DIR="/public/home/onesci/bioscience/onedata"
export ONESCIENCE_MODELS_DIR="/public/home/onesci/bioscience/onemodel"
```

## 禁止行为

- 不要因为未找到模型路径而阻断安装或检测流程；路径发现是增强功能，失败时仅报告，不阻塞。
- 不要覆盖用户已在 `onescience.json` 中显式设置的非默认路径。
- 不要在本地 Windows 环境中探测 `/public/home/onesci/` 等远程 Linux 路径（除非是远程 SSH 执行）。
