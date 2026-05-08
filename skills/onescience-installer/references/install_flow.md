# Install Flow

本文件用于提供 `onescience-installer` 的详细安装流程、命令模板与常见问题。

## 用户输入要求

用户在使用本技能时，必须确认以下信息：

1. **安装领域**（必须确认）：用户未指定时，智能体必须主动询问用户选择。领域对应关系如下：
   - 地球科学 -> `earth`
   - 流体仿真/结构力学 -> `cfd`
   - 生物信息 -> `bio`
   - 材料化学 -> `matchem`
   - 全部安装 -> `all`

## 安装流程概览

**重要：所有安装操作必须在远程 DCU 平台执行，不得在本地执行。**

**关键要求：**

- 阶段 1（加载环境、获取代码并安装）使用一个远程命令执行
- 阶段 2（安装验证）使用独立的远程命令执行

### 前置准备阶段

1. 读取完整硬件画像
2. 确认安装领域
3. 准备远程安装与验证命令

### 远程安装阶段

4. 远程执行安装
5. 远程执行验证

## 阶段 1：安装命令

若用户未指定领域，必须先询问用户选择：

- earth（地球科学）
- cfd（流体仿真/结构力学）
- bio（生物信息）
- matchem（材料化学）
- all（全部安装）

如果 `conda create` 失败，再重试一次，并在 `module load sghpc-mpi-gcc/26.3` 之后、`conda create` 之前插入：

```bash
source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate
```

标准安装命令：

```bash
# 加载 DAS 模块
module load sghpcdas/25.6
source ~/.bashrc
# 加载 DTK 模块
module load sghpc-mpi-gcc/26.3
# 如果 conda 命令不可用，执行以下激活命令
# source /work2/share/sghpc_sdk/Linux_x86_64/25.6/das/conda/bin/activate
# 创建 Python 3.11 环境
conda create -n onescience311 python=3.11 -y
# 激活 conda 环境
conda activate onescience311
# 获取 OneScience 代码
if [ ! -d onescience ]; then
  git clone https://gitee.com/onescience-ai/onescience.git
fi
cd onescience
git fetch --all
git checkout main
git pull --ff-only

# 根据用户选择执行对应安装命令
# 安装全部领域（用户选择 all 时执行）
bash install.sh

# 安装指定领域
bash install.sh earth
bash install.sh cfd
bash install.sh bio
bash install.sh matchem
```

## 阶段 2：验证命令

安装完成后，执行以下完整命令验证安装是否成功：

```bash
module load sghpcdas/25.6 && source ~/.bashrc && module load sghpc-mpi-gcc/26.3 && conda activate onescience311 && python -c 'import torch; print(torch.__version__)' && python -c 'import onescience; print(onescience.__version__)'
```

约束：

- 禁止创建验证脚本
- 必须直接执行上述验证命令
- 不要向命令中添加额外内容

## 领域说明

| 领域 | 领域名 | 说明 |
|------|--------|------|
| 地球科学 | earth | 气象、海洋等地球科学相关模型 |
| 流体仿真/结构力学 | cfd | 计算流体力学、结构力学相关模型 |
| 生物信息 | bio | 蛋白质结构预测、基因分析等生物信息模型 |
| 材料化学 | matchem | 材料科学、化学模拟相关模型 |

## 安装注意事项

- 平台为国产 DCU 远程服务器
- 默认用户已完成 SSH 免密登录配置
- 命令顺序要固定，避免 `conda` 与 `module` 环境不一致
- Python 版本固定为 3.11（`onescience311`）
- 用户未指定领域时，必须先确认领域

## 常见问题

1. **`conda` 命令不可用**：确认已执行 `module load sghpcdas/25.6`
2. **`conda init bash` 后未生效**：执行 `source ~/.bashrc` 后再继续
3. **分支不存在或切换失败**：先执行 `git fetch --all`，再重试 `git checkout <branch>`
4. **`install.sh` 执行报错**：确认当前目录为仓库根目录 `onescience/`
5. **领域未确认**：先询问用户选择 `earth/cfd/bio/matchem/all`
