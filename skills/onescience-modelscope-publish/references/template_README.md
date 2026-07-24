---
license: Apache License 2.0 
tasks:
  - test # 说明自己的任务 
frameworks:
  - pytorch # 说明自己的框架
language:
  - en
  - zh
tags:
  - OneScience # 输入自己对应的标签，可以自己设置多个
datasets:
 - OneScience/ERA5 # 如果魔搭有对应的数据集可以指定
---
<p align="center">
  <strong>
    <span style="font-size: 30px;">Model Name</span>
  </strong>
</p>

# 模型介绍

简单介绍一下模型，如场景等，参考如下：

Pangu-Weather 是华为云提出的全球中期天气预报模型，可对地表变量和多气压层高空变量进行快速预测。
论文：Accurate medium-range global weather forecasting with 3D neural networks  
https://www.nature.com/articles/s41586-023-06185-3

# 模型描述

描述一下模型结构，参考如下：
Pangu-weather基于 3D Earth-Specific Transformer 架构，使用ERA5数据进行训练，面向短中期开展天气预报

# 适用场景

描述模型使用的场景，参考如下：

| 场景 | 说明 |
| :---: | :--- |
| 天气预报训练 | 使用 ERA5 HDF5 数据训练 Pangu-Weather |
| 本地快速验证 | 使用虚拟数据检查数据读取、模型训练与推理、推理结果可视化。 |
| ModelScope/OneCode 运行 | 作为独立模型包下载后直接安装依赖并运行脚本。 |
| 多卡训练 | 通过 `torchrun` 启动多进程训练。 |


# 使用说明

## 1. OneCode 使用

可通过 OneCode 在线环境体验智能化一键式 AI4S 编程：

[点击体验智能化一键式 AI4S 编程](https://web-2069360198568017922-iaaj.ksai.scnet.cn:58043/home)

## 2. 手动安装使用

**硬件要求**

- 推荐使用 GPU 或 DCU 运行。
- CPU 可以用于导入和小配置连通性验证，完整训练和推理速度较慢。
- DCU 用户需要预先安装 DTK，建议使用 DTK 25.04.2 以上版本或与当前集群匹配的 OneScience 推荐版本。

### 下载模型包

# 根据当前仓库自行设置
```bash
modelscope download --model OneScience/Template --local_dir ./model
cd model
```

### 安装运行环境


**DCU环境**

```bash
# 请首先激活DTK及CONDA
conda create -n onescience311 python=3.11 -y
conda activate onescience311
# 支持uv安装，安装的时候注意自己对应的领域，目前支持earth、cfd、matchem、bio、all（全领域）
pip install onescience[earth-dcu] -i http://mirrors.onescience.ai:3141/pypi/simple/  --trusted-host mirrors.onescience.ai 
```

**GPU环境**
```bash
# 请首先激活CONDA
conda create -n onescience311 python=3.11 -y libstdcxx-ng=12 libgcc-ng=12 gcc_linux-64=12 gxx_linux-64=12
conda activate onescience311
# 支持uv安装，安装的时候注意自己对应的领域，目前支持earth、cfd、matchem（全领域）
pip install onescience[earth-gpu] -i http://mirrors.onescience.ai:3141/pypi/simple/  --trusted-host mirrors.onescience.ai
```

### 训练数据介绍

如果魔搭有对应的数据集，在这里介绍下数据集仓库名字等

```bash
modelscope download --dataset OneScience/ERA5 --local_dir ./data
```

### 训练

在此处提供运行脚本，下方为参考案例

单卡：

```bash
python scripts/train.py
```

多卡：

```bash
torchrun --nproc_per_node=8 --nnodes=1 --rdzv_id=1000 --rdzv_backend=c10d --max_restarts=0 --master_addr="localhost" --master_port=29500 scripts/train.py
```

训练会在 `data/checkpoints/` 下保存 `model_bak.pth`。

### 训练权重

已经有权重的上传，没有的可以写上即将上传

### 推理

```bash
python scripts/inference.py
```

推理果会保存至 `result/output/`。

### 评估和可视化

```bash
python scripts/result.py
```

# OneScience 官方信息

| 平台 | OneScience 主仓库 | Skills 仓库 |
| --- | --- | --- |
| Gitee | https://gitee.com/onescience-ai/onescience | https://gitee.com/onescience-ai/oneskills |
| GitHub | https://github.com/onescience-ai/OneScience | https://github.com/onescience-ai/oneskills |

# 引用与许可证

开源仓库复用上游内容，复现的论文可参考下面描述

- 本仓库为Pangu-Weather原始论文的复现版本。



