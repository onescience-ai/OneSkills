# New Dataset Workflow

本文件用于补充 `onescience-coder` 在处理“仓库中尚未登记的新数据集”时的最小设计流程。

## 适用场景

- 用户提供新的数据集 README
- 用户提供样例文件或目录结构
- 用户要求把一个未登记数据集接入现有 OneScience 训练流程

## 最小执行步骤

1. 先判断任务是 `datapipe-only`、`full-adaptation` 还是 `full-adaptation + benchmark-comparison`
2. 明确最接近的参考 datapipe 与参考 example
3. 明确新数据集的：
   - 目录结构
   - 样本切分方式
   - 输入输出字段
   - 时间 / 空间 / 变量组织方式
4. 明确是否需要桥接现有训练脚本的 batch 协议
5. 优先保持模型主体和训练主循环不变
6. 先在 datapipe、配置或调用层做最小改动

## 第一轮规格必须输出

- 参考 datapipe
- 参考 example
- 新 datapipe 文件名
- 新 datapipe 类名
- 输入输出结构
- batch 协议
- 最小桥接方案
- 是否需要修改 config / loss / metrics / inference

## 多模型训练对比补充规则

当用户提供新数据集，并要求“在不同 PDE / CFD / operator 模型上训练并对比效果”时，将任务视为 `full-adaptation + benchmark-comparison`。

第一轮必须先完成以下判断：

- 数据形态
  - 规则网格
  - 非结构点云
  - PyG 图
  - DGL 图
  - VTK / mesh surface
  - HDF5 / PDEBench 风格
- 字段可信度
  - README 是否明确写出输入字段、目标字段、shape、split
  - 若 README 不完整，先生成只读探测脚本或探测方案，不要直接假设字段名和通道数
- 默认候选模型
  - 用户未指定模型时，默认先考虑 `Transolver`、`FNO`、`U_Net (CFD_Benchmark)`、`LSM`
  - 最终是否生成训练代码由数据协议兼容性决定，不要强行让所有模型接入

多模型对比时，优先生成一个 canonical datapipe，再为不同模型生成 adapter / view：

- 点云或非结构翼型视图
  - 面向 `Transolver`
  - 典型协议：`pos / x / y` 或 PyG `Data`
- operator 视图
  - 面向 `FNO`、`LSM`
  - 典型协议：`x -> (Batch, NumPoints, space_dim)`，`fx -> (Batch, NumPoints, fun_dim)`，`y -> (Batch, NumPoints, out_dim)`
- 规则网格视图
  - 面向 `U_Net (CFD_Benchmark)`
  - 典型协议：规则网格张量或可 reshape 的 `(x, fx, y)`
  - 若原始数据是非结构网格，必须明确插值、采样或跳过该模型
- 图视图
  - 面向 `MeshGraphNet / GraphSAGE / Graph_UNet`
  - 只有当数据具备边、邻接关系或可可靠构图时再加入

第一轮规格中必须输出模型兼容性表：

- `direct`
  - 数据协议已匹配，可直接生成训练配置
- `adapter-required`
  - 需要 adapter / collate / reshape / interpolation
- `not-recommended`
  - 当前 README 或样本信息不足，或数据形态明显不匹配

第二轮代码生成默认包括：

- 新 datapipe 文件
- 模型 adapter / view 文件
- 每个候选模型的 config
- 单模型训练入口或统一训练入口
- 推理 / 评估入口
- 结果汇总说明或汇总脚本

约束：

- 不要把多模型差异硬塞进 datapipe 的 `__getitem__`
- 不要让某个模型的 batch 协议污染其它模型
- 不要为了让默认模型都能跑而隐式丢弃目标变量、坐标或边界条件
- 如果某个默认模型不适配，第一轮明确说明并保留跳过逻辑

## 默认命名建议

- 文件名：`<DatasetName>.py`
- 数据集类：`<DatasetName>Dataset`
- 数据管道类：`<DatasetName>Datapipe`

## 约束

- 若用户没有明确要求改主库，优先输出到目标 `case` 目录
- 不要默认直接修改 `onescience/src/`
- 不要在未核对 batch 协议时假设可直接复用已有训练流程
