## description
规划 MatterGen MP20 缓存的分数坐标读取、条件属性掩码和晶体生成数据交接。

## when_to_use
需要 MP20 小晶胞晶体生成、条件化、缓存到材料对象转换或生成评估时使用。

## inputs
数据缓存根目录、目标模型的坐标/晶胞/条件字段协议、所需属性、单位来源和 train/val/test 使用范围。

## outputs
按 split/structure_id 的结构索引、扁平原子 offset、分数/笛卡尔坐标映射、属性 value/mask 和来源、仅从 train 拟合的统计及评测配置。

## procedure
1. 读取每个 split 的数组形状，核对结构数、原子总数和 ID 一致性。
2. 按 num_atoms 累积 offset 切片，保留 frac 与对应 cell/atomic_numbers。
3. 解析属性 JSON，保留 provenance，以有限值构建每属性 mask。
4. 按消费模型核对坐标和单位；只用 train 估计条件缩放。
5. 小批回验周期结构和 batch，保留既有 split，检查 ID/等价结构泄漏。
6. 按生成或属性预测任务交接；评测时逐条件报告有效样本分母。

## constraints
不能把 pos 当笛卡尔坐标、属性缺失当零标签、形成能当总能；跨原始 CIF 与缓存不能仅按原子行号配对。

## next_phase_recommendation
由数据标准化/编码技能实现缓存 adapter，与 MatterGen 模型实际配置核对后再交接推理或训练；生成后物理验证应独立规划。

## fallback
条件属性不完整时采用有效样本子集或模型支持的无条件/masked 路径并记录筛选规则；坐标协议冲突时用同 ID raw CIF 交叉验证，不凭范围猜测或裁剪。
