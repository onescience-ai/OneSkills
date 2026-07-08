# launch
Python API 示例：

``` python
from onescience.modules.loss.uma_loss import DDPMTLoss, MAELoss

loss_fn = DDPMTLoss(
    loss_fn=MAELoss(),
    reduction="mean",
    coefficient=1.0,
)
loss = loss_fn(
    input=pred,
    target=target,
    mult_mask=mask,
    natoms=natoms,
)
```

Hydra/训练命令示例：

``` sh
python examples/matchem/uma/train.py --config-name=uma_finetune --tasks.energy.property=energy --tasks.energy.loss_fn=mae --tasks.energy.reduction=mean --tasks.energy.coefficient=1.0 --tasks.forces.property=forces --tasks.forces.loss_fn=l2norm --tasks.forces.reduction=mean --tasks.forces.coefficient=50.0 --trainer.max_epochs=10 --optim.batch_size=2
```

# input_schema
损失输入组织：

预测与标签
  input / pred
    energy: (NumGraphs,) 或 (NumGraphs, 1)
    forces: (NumAtoms, 3)
    stress: (NumGraphs, 9) 或任务约定形态
  target
    shape 与 input 对齐

归约辅助
  natoms: (NumGraphs,)
    per_atom / per_structure 需要
  mult_mask
    按任务屏蔽无效样本或原子

训练上下文
  coefficient
    子任务权重
  DDP world
    修正全局平均

# runtime_interfaces
- `DDPMTLoss.forward(input, target, mult_mask, natoms)`：支持 mask、coefficient、mean/sum/per_structure 和 DDP 修正。
- `DDPLoss.forward(input, target, natoms)`：基础 DDP loss 包装。
- `MAELoss.forward(pred, target, natoms)`：逐元素 L1 loss。
- `MSELoss.forward(pred, target, natoms)`：逐元素 MSE loss。
- `PerAtomMAELoss.forward(pred, target, natoms)`：标量 per-atom MAE。
- `L2NormLoss.forward(pred, target, natoms)`：向量 L2 范数误差。

# main_functions
- `forward`
- `mean`
- `sum`
- `per_structure`

# execution_resources
- loss 本身计算成本低，主要资源消耗来自 head/backbone forward。
- DDP all-reduce 会引入少量通信开销。
- `per_structure` reduction 需要根据 `natoms` 构建结构索引。
- 模型并行场景中 `gp_utils.scale_backward_grad` 会影响反向梯度尺度。

# operation_limits
- `input.shape`、`target.shape` 和 `mult_mask` 首维必须对齐。
- `PerAtomMAELoss` 当前适合标量任务，不适合向量或高阶张量。
- `L2NormLoss` 要求 target 为二维向量张量且第二维不是 1。
- DDP/global sample 修正依赖分布式环境正确初始化。
- NaN 处理不是数据清洗替代，频繁出现时应回查标签或模型输出。
