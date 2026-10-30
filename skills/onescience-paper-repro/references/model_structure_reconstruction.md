# 模型结构重建与实现级表达

## 目标

本参考用于把论文和版本匹配的官方实现证据重建为 coder 可直接消费的模型结构。输出仍写入唯一
`reproduction_spec.md`；不生成独立模型契约、JSON IR 或 coder 视图。

模型结构不能只用架构概述、模块名单或单张 Tensor Program 表表达。完整规格按适用性包含六个
互相校验的视图：总体职责、模块树、Tensor 数据流、数学算子、shape/变量语义、参数关系与行为
不变量。

## 1. 需求驱动的结构取证

先从用户要求确定必须重建的模型变体、公开接口、输入/输出和结构限制，再围绕缺口阅读：

1. 找到模型总体定义、目标任务和端到端输入输出。
2. 从正文、公式、算法、图注和附录提取一级模块、分支、重复、残差和循环。
3. 为每个模块找到输入、输出、运算、shape、参数和调用顺序。
4. 论文未写明但实现必需时，定点检查匹配版本官方仓库的配置、类和目标符号。
5. 对照用户要求裁决变体，避免把其它实验、消融或较新仓库结构混入目标模型。
6. 为每个关键结构事实附短 `source_id`；详细论文或仓库定位只写在集中来源索引。

不要按论文段落顺序抄写。要围绕“输入如何经过哪些可学习或固定运算变成输出”重建可闭合结构。

## 2. 视图一：总体职责与边界

先用简洁文字说明：

- 模型解决的子任务和不负责的任务；
- 输入、输出和条件信息的科学语义；
- 主干、条件分支、辅助网络、预测头及它们的连接；
- 单步、多步、自回归、扩散、反演或算子学习形式；
- 目标模型变体与其它变体的差异。

不能用“encoder-backbone-decoder”之类泛称替代实际职责。总体说明中每个一级模块必须能在后续
模块树或 Tensor 数据流中找到。

## 3. 视图二：模块树

模块树表达结构层级，不表达完整计算。按来源可确认的粒度记录：

```text
module_id
name_or_role
parent_id
module_type_or_mathematical_role
count_or_repeat_rule
ordered_children
ordinary_vs_terminal_difference
public_name_if_constrained
source_ids
status
```

特别核对：

- 重复 block 是同一个实例重复调用，还是多个独立实例；
- 投影、embedding、normalization 或 head 位于主模型还是 block 内；
- 普通 block 与首/末 block 是否不同；
- 条件分支在什么层级注入；
- ModuleList/Sequential/普通列表等代码容器是否真的被用户或来源约束；
- 辅助模块是否参与 forward、只用于训练，还是只用于预处理。

来源只给概念关系时使用角色名，不猜测 Python 类名、属性名或容器。

## 4. 视图三：Tensor 数据流

以稳定 tensor ID 按实际执行顺序展开 forward、训练专用分支和推理专用分支：

```text
step_id
input_tensor_ids
operation_or_module_id
output_tensor_ids
branch_condition
merge_or_residual_rule
repeat_or_loop_rule
state_update
source_ids
status
```

必须显式表达：

- 多输入如何投影、拼接、相加、调制或交叉注意；
- 主干、skip、residual、条件和 mask 的来源与合并位置；
- reshape、flatten、permute、分头、聚合、插值和逆变换；
- 循环状态、rollout state、扩散 timestep 和随机噪声如何更新；
- 可选输入为 `None` 时走哪条路径；
- 训练和推理调用链的差异。

不能只写输入和最终输出，中间改变语义、轴或分辨率的步骤必须出现。

## 5. 视图四：数学算子

对影响科学语义的运算写明：

- 公式及所有符号定义；
- 输入/输出 tensor ID；
- 求和、积分、变换或归一化的轴；
- einsum/matmul 的指标含义，不只写字符串；
- inverse、solve、FFT、Radon、kernel/operator 等运算发生的空间；
- residual、normalization、activation、dropout、gating 的先后顺序；
- epsilon、正则项、clamp、mask、边界强制和数值稳定处理；
- 是否 detach、stop-gradient、create_graph 或共享中间结果。

若论文只给方法名称或引用其它论文，不等于完整给出算子。先检查引用或官方实现；仍缺失时按
`UNRESOLVED` 或 `PROPOSED_CHOICE` 处理，不能从方法名补写一套常见公式。

## 6. 视图五：Shape 与变量语义

每个关键 tensor 记录：

```text
tensor_id
scientific_role
producer_and_consumers
shape_with_named_axes
dtype
unit_or_normalized_space
optional_or_required
valid_range_or_mask
variant_conditions
source_ids
status
```

轴必须命名，例如 `[batch, head, node, group]`，不能只写 `[B,H,N,G]` 而不解释。区分：

- 原始变量、模型输入、条件输入和静态特征；
- 模型输出、训练 target、噪声 target、residual/delta 和评估 target；
- node、cell、point、grid、token、head、channel、mode、time 和 ensemble 轴；
- 原始单位、归一化空间和反归一化后的评测空间。

对每一步做 shape 算术。分支合并、einsum、矩阵求解和输出恢复无法闭合时，回查来源，不用广播
或 reshape 猜测掩盖矛盾。

## 7. 视图六：参数关系与行为不变量

### 参数关系

记录模块或参数之间的：

- 共享、独立、复制初始化或 weight tying；
- 重复调用同一实例与创建多个实例的区别；
- 冻结、解冻、预训练加载和训练阶段更新对象；
- 初始化、参数化约束和可学习/固定状态；
- checkpoint 中的命名或包装要求，仅在来源明确时约束。

### 行为不变量

把结构事实转换成 coder 可以验证的行为，而不是只要求属性存在。按适用性包括：

- 输入敏感性：改变应被使用的输入会改变输出；无关输入不应泄漏；
- 条件敏感性：条件、timestep、mask 或边界确实影响对应分支；
- 归一化：权重沿正确轴求和为 1，统计量只来自规定 split；
- 共享/独立：共享模块只计算或存储一次，独立 block 参数对象不同；
- 组件使用：hook 或干预关键模块会传播到最终输出；
- 形状和有限性：合法输入输出 shape/dtype 正确且有限，非法输入按规格失败；
- 随机性：固定 generator/seed 的可重复范围与随机采样范围符合协议；
- 梯度：应更新的参数有有限梯度，冻结或 detach 的路径不更新；
- 训练语义：loss 的 prediction 和 target 与规格一致，不用另一个可运行目标替代；
- 推理语义：sample/rollout 实际重复调用规定的去噪器或状态更新，不返回与条件无关的占位值。

行为不变量必须来自已确认结构或用户要求。知识卡只能提醒检查项，不能让当前论文凭空获得某个
不变量。

## 8. 变体、缺口与候选实现

- 多个论文变体分别记录差异，不合并层数、通道或分支。
- 用户指定变体优先实现，论文基线仍保留在冲突表。
- 官方仓库只补与目标版本和实验匹配的缺口。
- 未知但局部可隔离的结构用配置、策略接口或多变体表示，继续交付。
- 采用候选时记录 `PROPOSED_CHOICE`、默认候选、替换边界和 `paper_fidelity` 影响。
- 未知组件不能用空模块、恒等映射或未参与 forward 的属性伪装实现完成。

## 9. 六视图一致性检查

交付规格前逐项检查：

1. 总体说明中的一级模块都出现在模块树。
2. 模块树中的关键 forward 模块都出现在 Tensor 数据流。
3. 每条 Tensor 数据流边都有 shape 和变量语义。
4. 数学算子的轴、维度和数据流顺序一致。
5. 所有分支、残差、循环和可选路径都有输入、输出和合并规则。
6. prediction、训练 target、loss target 和评估 target 没有混用。
7. 参数共享、独立、冻结和更新对象没有互相冲突。
8. 普通/首/末 block、正式/消融变体没有串用。
9. 每个关键结构至少有一个行为不变量或明确说明无法验证的原因。
10. 每个确定事实都有 source ID；每个未知项都有分类、影响和继续方式。

固定模块数、表格行数或章节齐全不能证明模型结构正确。正确性来自来源适用、六视图互相闭合和
行为不变量能够验证结构语义。
