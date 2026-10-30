# Neural Operator / PDE 复现知识卡

本卡适用于 FNO、RNO、DeepONet、图神经算子及其它 PDE operator learning 论文。它只提供取证问题、
语义区分和核验不变量；当前任务的具体值必须来自用户、目标论文或版本匹配的官方实现。

## 数据与任务语义

重点提取：

- PDE、系数场、源项、边界/初始条件、解场及它们的单位和坐标域；
- 模型输入、输出、训练 target、residual/delta 和评估 target；
- 原始文件、字段别名、样本维、空间维、通道维和复数表示；
- 原始分辨率、目标分辨率、stride/crop/interpolation、端点和周期边界处理；
- train/validation/test 数量及按 case、参数、时间或轨迹的隔离方式；
- 归一化对象、公式、统计轴、统计量拟合 split、反归一化和防泄漏；
- structured grid、unstructured mesh、point cloud 或 spectral coefficient 的 layout。

常见错误：把 `[N,X,Y]` 直接当 BCHW；丢失通道维；对子采样端点处理不一致；使用全数据统计量；
把系数场和解场互换；把论文结果分辨率当成原始数据分辨率。

## 模型结构

按六视图检查：

- lifting/input projection 的输入通道是否包含坐标、系数或边界特征；
- operator block 的数量、残差、局部支路和全局/变换域支路；
- spectral/Radon/kernel/integral 变换的方向、离散化、mode/angle/basis 和逆变换；
- block 参数共享还是独立，变换基或角度权重是否可学习；
- fusion、projection 和普通/末 block 的差异；
- 不同分辨率下 shape 是否闭合，坐标网格是否按实际输入构造。

RNO 类方法还需查明：Radon/逆 Radon 的离散定义、角度集合、插值、padding/crop、变换域 operator、
角度/频率权重和局部空间支路如何融合。不能从“使用 Radon transform”推断具体库或离散参数。

## 损失、训练和评测

- relative L2、MSE、H1、PDE residual 等必须分别提取 prediction、target、reduction 和 epsilon；
- 指标是在归一化空间还是物理空间计算，先逐样本还是全局聚合；
- optimizer、scheduler、epoch、batch、seed 和 checkpoint 绑定具体实验；
- best/last checkpoint 选择依据和评测 split；
- 多分辨率、超分辨率或 rollout 评测不能与单步同分辨率结果混用。

## 可验证行为不变量

- 输出 shape 与目标场一致，并支持来源明确的合法分辨率；
- 修改输入系数场、坐标或边界条件会影响输出；
- operator/Radon/频域支路的干预会传播到输出，不是未使用属性；
- 独立 block 参数对象不同，共享基或投影只存储一次；
- 归一化仅使用训练统计量，评测可正确反归一化；
- relative error 的分子、分母和 reduction 与规格一致；
- 数据字段缺失、非有限值和不合法 shape 被明确拒绝。

