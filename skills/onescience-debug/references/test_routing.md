# Test Routing

本文件用于给 `onescience-debug` 提供任务识别与测试路径映射规则。

如需查看仓库内的标准 debug 输入示例，可参考：

- `../assets/examples/dcu_e2e_remote_debug_distributed_blocked.json`
- `../assets/examples/dcu_e2e_remote_debug_from_ssh_slurm.json`
- `../assets/examples/dcu_e2e_remote_debug_request.json`
- `../assets/examples/gpu_model_remote_debug_from_scnet_mcp.json`
- `../assets/examples/gpu_model_remote_debug_request.json`
- `../assets/examples/gpu_model_remote_debug_torch_blocked.json`
- `../assets/examples/cpu_datapipe_remote_debug_request.json`

## Backend 状态与预检状态

远程 debug 请求至少要区分两层语义：

- `expected_resolution.status`
  这表示 debug 链路对该 backend 的支持状态，例如 `supported` 或 `planned_backend`
- `expected_resolution.precheck.outcome`
  这表示当前 host 上是否已经 `ready_to_debug`

因此：

- `status=supported` 不等于一定可以立刻开始远程调试
- 只要 `precheck.outcome=blocked`，就必须先解决当前 host 的 runtime readiness 问题

## 可测试任务与测试路径

| 可测试任务类型 | 识别重点 | 测试路径 |
| --- | --- | --- |
| 完整训练或推理流程端到端测试 | 任务覆盖 `datapipe` 或 `dataset`、`model`、`train` 或 `inference`、`config` 或 `runner` 等多个部分，并形成可运行闭环 | `./e2e_pipeline_test.md` |
| 模型测试 | 任务聚焦模型结构、实例化、前向传播、梯度或设备兼容性 | `./model_test.md` |
| Earth DataPipe 测试 | 任务聚焦 Earth 或气象数据的 DataPipe、Dataset、时间窗口、区域裁剪、读取链路 | `./earth_datapipe_test.md` |

## 任务识别层级

按下面顺序识别任务范围，再选择测试路径：

1. 先判断任务是否要求交付或测试完整训练 / 推理流程，而不是只测局部模块
2. 如果不是完整流程任务，再判断是否明显属于 Earth 或气象场景下的 DataPipe 测试
3. 如果也不是 Earth DataPipe 任务，再判断是否收敛为独立模型测试
4. 如果一个任务同时带有多个信号，优先选择覆盖范围更大的测试路径
5. 如果证据不足以支持完整流程测试，就不要放大范围，改为选择证据最充分的那条

核心原则不是简单罗列优先级，而是先看任务边界，再看领域特征，最后看局部组件。

## 各类测试说明

### 完整训练或推理流程测试

这类任务关注整条链路是否打通，而不是某一个文件是否单独可用。通常会同时涉及多个组成部分，例如：

- `datapipe.py` 或 `dataset.py`
- `model.py`
- `train.py`
- `inference.py`
- `config.*`
- `runner` 或启动脚本

当任务目标是验证“数据加载 -> 模型构建 -> 训练或推理启动 -> 运行若干步”时，应视为这类测试。即使任务里也包含模型修改或 DataPipe 适配，只要这些改动共同服务于完整链路，就应归到这里。

常见触发表述包括：

- “整套适配”
- “完整流程”
- “沿用某个 example 的架构及训练流程”
- “补齐 datapipe、model、train、config”
- “在 case 目录内完成整套实现并测试”

### 模型测试

这类任务只关注模型自身是否满足最基本的可执行要求，通常不要求补齐完整训练或推理流程。常见范围包括：

- 模型类是否能实例化
- `forward` 是否可执行
- loss 或 backward 是否可运行
- CPU / GPU 设备兼容性是否正常

如果模型测试只是完整项目中的一个组成部分，而任务整体仍然要求完整链路验证，则不要映射到这里。

### Earth DataPipe 测试

这类任务只关注 Earth 或气象数据的读取与组织是否正确，通常不要求交付完整训练项目。常见范围包括：

- DataPipe 或 Dataset 格式是否适配
- 时间窗口、变量顺序、区域切片是否正确
- batch 组织与读取链路是否正常

如果 Earth DataPipe 只是完整训练或推理流程中的一部分，而任务整体目标仍然是验证完整链路，则不要单独映射到这里。

## 映射方法

按下面的方法进行判断：

1. 提取任务中的交付范围  
   看任务是否要求同时生成、修改或测试 `datapipe/dataset`、`model`、`train/inference`、`config/runner` 中的多个部分
2. 提取任务中的测试目标  
   看用户要验证的是单点能力，还是“能否形成完整训练或推理闭环”
3. 提取任务中的领域线索  
   如果任务明确是 Earth 或气象数据读取问题，且目标集中在 DataPipe 或 Dataset，本轮判断优先考虑 Earth DataPipe 测试
4. 比较任务边界与测试路径的覆盖范围  
   如果多个测试路径都能部分覆盖，选择覆盖任务目标更完整的那一条，而不是选择最局部的那一条
5. 用反证法回看  
   如果把当前任务映射到更小范围的测试路径，会遗漏 `train`、`inference`、`config`、`runner` 或整条启动链路验证，就应回到完整流程测试

## 典型信号

### 直接映射到完整训练或推理流程测试

- 同时出现 `datapipe` 或 `dataset`、`model`、`train`、`config` 等多个关键词
- 明确要求“沿用现有架构和训练流程”
- 明确要求“所有生成文件写入某个 `case` 目录”
- 明确要求“训练入口和推理入口都能启动”

### 直接映射到模型测试

- 只提模型类、`forward`、`loss`、`backward`、设备兼容
- 没有要求训练入口、推理入口、配置文件或完整目录闭环

### 直接映射到 Earth DataPipe 测试

- 明确是 Earth 或气象场景
- 重点是 DataPipe、Dataset、时间窗口、区域裁剪、变量顺序、batch 读取
- 没有要求完整训练或推理启动
