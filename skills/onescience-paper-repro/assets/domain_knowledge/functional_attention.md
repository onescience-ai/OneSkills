# Functional / Operator Attention 复现知识卡

本卡适用于 neural operator attention、functional attention、slice/token aggregation、dual-form
attention 和不规则网格注意力论文。它只提供专业取证与核验问题，不给当前论文填入固定维度或
默认公式。

## 变量与输入语义

提取并区分：

- 坐标/位置 `x`、函数值或场 `f(x)`、条件/变换 `T`、监督 target 和输出场；
- structured grid、mesh、point/node 和 batch/channel/head/group 轴；
- 可选函数输入为 `None` 时的合法语义，是零函数、仅位置模式还是另一模型变体；
- unified/reference grid 是替换原位置、拼接到输入，还是只用于距离/基函数构造。

## 模型结构和参数关系

重点查明：

- position、function/value、slice/group、query/key/value 投影位于主模型还是 block 内；
- 投影输出在 block 间共享，还是每个 block 重新计算；
- blocks 是独立参数实例、共享权重还是循环调用同一 block；
- 普通 block 与最后 block 的输出投影、MLP 或 residual 差异；
- slice/group 数、head 数和 head dimension 的关系；
- 不规则节点如何聚合到 latent token，再如何逆投影回物理点。

## Dual-form 和数值求解

若论文使用 dual form、kernel solve 或 regularized inverse，必须提取：

- 正规方程或等价公式；
- solve/inverse 发生在 node、group、basis 还是 head-dimension 空间；
- 矩阵乘法和 einsum 每个指标的轴语义；
- 正则项、identity 大小、normalization 和数值稳定方法；
- 聚合权重沿哪个轴 softmax，token 与物理空间的正/逆映射；
- 求解结果如何进入 residual、attention output 或最终预测。

不能把数学上相似的 primal attention、standard self-attention 或伪逆实现替代 dual-form 定义。

## 数据、loss 和评测

- 几何/坐标输入与监督场的样本轴必须对齐；
- target 是位移、应力、标量响应还是其它物理量；
- relative L2、MSE 等的计算对象、reduction 和归一化空间；
- 训练和评测是否使用相同节点、随机采样节点或跨网格泛化；
- checkpoint、结果和可视化输出映射到正确实验变体。

## 可验证行为不变量

- slice/group 权重沿来源确认的轴归一化；
- 共享投影只定义/计算一次并供所有 block 使用；
- 独立 block 参数对象不同，且每个 block 实际影响输出；
- dual solve 的 identity 和矩阵维度对应正确求解空间；
- einsum 输入输出 shape 与轴语义闭合；
- 改变位置、函数值或条件会按规格影响输出；可选输入为 `None` 时走合法分支；
- 最后 block 的专用 projection/MLP 确实被调用；
- 输出恢复到原节点顺序和目标 shape，且结果有限。

