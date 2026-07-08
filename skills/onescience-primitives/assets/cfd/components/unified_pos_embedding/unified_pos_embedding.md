# Contract: UnifiedPosEmbedding

## 基本信息

- 组件名：`UnifiedPosEmbedding`
- 所属模块族：`embedding`
- 统一入口：`not_applicable`
- 注册名：`style="UnifiedPosEmbedding"`

## 组件说明
unified_pos_embedding 位于 embedding 模块，是无状态函数原语，面向规则 1D/2D/3D 网格生成到参考网格的距离型位置编码。

## 用途
- 做什么：生成输入网格点到参考网格点的距离矩阵。
- 解决问题：将不同分辨率网格映射到固定参考锚点距离空间。
- 适用场景：PDE/CFD 网格相对位置特征、注意力 bias、跨分辨率条件编码。
- 不适用场景：非结构点云、经纬球面距离、可学习绝对位置表。

## 输入规格
- `shapelist`: 长度为 1、2 或 3 的整数列表，如 `[L]`、`[H, W]`、`[D, H, W]`。
- `ref`: 每个维度参考网格分辨率。
- `batchsize=1`: 输出 batch 数。
- `device='cuda'`: 目标设备；传 `None` 时按 CUDA 可用性选择。

## 输出规格
`pos`: `(Batch, N_input, N_ref)`，其中 `N_input=prod(shapelist)`，`N_ref=ref ** len(shapelist)`；元素是归一化坐标空间中的欧氏距离。

## 参数
- `shapelist`：输入规则网格尺寸。
- `ref`：参考锚点分辨率。
- `batchsize`：复制到 batch 维。
- `device`：输出设备。

## 关键依赖
- torch
- numpy

## 使用注意与风险
- 输出矩阵规模为 `batchsize * prod(shapelist) * ref^dim`，高分辨率 3D 会快速占用大量显存。
- 只支持规则网格，不支持任意坐标输入。
- 默认 device 为 `cuda`，无 GPU 环境需显式传 `device='cpu'` 或 `None`。
- 源码对非法 shapelist 长度没有显式报错，可能返回未定义变量。

## 启动方式
Python API 启动示例：

``` sh
python -c "from onescience.modules.embedding.unified_pos_embedding import unified_pos_embedding; print(unified_pos_embedding([32,32], ref=4, batchsize=2, device='cpu').shape)"
```

## 输入规格
从配置或数据张量分辨率生成 `shapelist`；根据显存预算选择 `ref`；无 GPU 或调试时显式使用 CPU。

## 运行接口
- `unified_pos_embedding(shapelist, ref, batchsize=1, device='cuda')`：返回距离型统一位置编码。

## 主要函数
- `unified_pos_embedding`

## 执行资源
CPU/GPU 均可；2D/3D 高分辨率和较大 ref 会产生大矩阵，建议提前估算内存。

## 操作限制
仅支持 1D/2D/3D 规则归一化笛卡尔网格；不处理非结构坐标、周期边界或球面测地距离。

## 规划决策

### 描述
将 unified_pos_embedding 规划为规则网格的位置/距离特征生成阶段，用于跨分辨率参考锚点表达。

### 使用时机
当模型需要固定参考网格的相对距离特征，而输入是规则 1D/2D/3D 网格时使用。

### 输入
- 输入网格尺寸。
- 参考分辨率 ref。
- batchsize 和设备。
- 下游是否接受距离矩阵形状 `(B,N,M)`。

### 输出
- 距离位置编码张量。
- 内存估算。
- 下游字段名和拼接/加性 bias 策略。

### 执行步骤
1. 从输入张量确定 shapelist。
2. 根据预算选择 ref。
3. 估算输出矩阵大小。
4. 调用函数生成 pos。
5. 接入 attention bias 或特征拼接分支。

### 约束
shapelist 长度必须为 1、2 或 3；ref 不宜过大；非结构网格应改用坐标编码或图位置特征。

### 下一阶段建议
若用于大规模 3D，下一阶段应实现缓存、低秩近似或按块生成，避免重复构造大距离矩阵。

### 回退策略
显存不足时降低 ref、减小 batch、转 CPU 预计算或改用局部/可学习位置编码。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/embedding/unified_pos_embedding.py`
