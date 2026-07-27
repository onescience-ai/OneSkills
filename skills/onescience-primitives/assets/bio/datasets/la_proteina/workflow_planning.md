
## description
为 La-Proteina 数据与权重集合 选择接入、解析、分流和评测路线的规划知识。

## when_to_use
当任务与该数据源直接相关，且需要先判断它是训练样本、推理输入、benchmark 分割还是数据库依赖时使用。

## inputs
数据根目录：/public/share/sugonhpcapp01/onestore/onedatasets/la-proteina/dataset。任务输入通常是序列、结构、图、图像、问答对、标签、数据库包或预处理缓存。

## outputs
输出结构应与任务定义一致：训练时输出样本、标签和 split；推理时输出模型可消费的 batch、索引或检索结果；数据库集合则输出挂载与索引状态。

## procedure
1. 先校验目录是否可读，并确认顶层文件与子目录类型。
2. 再确认它属于样本集、benchmark、数据库包还是权重/缓存集合。
3. 读取 spec.md，明确 schema、存储格式、样本单位和 split 约束。
4. 读取 usage.md，确定任务类型、消费接口和前置处理。
5. 先做样本级探测或顶层文件抽查，确认字段、后缀和目录粒度。
6. 再决定是进入 datapipe、模型 adapter、数据库挂载或仅做只读索引。
7. 若用于训练/评测，补齐 split、缓存和验证口径。

## constraints
先检查 pdb_train 的训练划分和 AFDB 结构是否一致，再核对权重版本。

## next_phase_recommendation
若目录已经明确是训练样本，则进入 dataset-specific datapipe；若是数据库包或权重集合，则先做挂载/索引；若任务需要更细的字段字典，再做样本级补全。

## fallback
若文件权限、格式解析或依赖失败，先记录失败路径和错误信息，降级为只读索引模式；不要把未解析的目录直接写成训练集。
