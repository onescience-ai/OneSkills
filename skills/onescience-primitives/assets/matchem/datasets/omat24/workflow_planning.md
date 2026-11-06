## description
规划 OMat24 本地多视图的选择、MessagePack LMDB 读取、物理字段映射及大规模训练数据交接。

## when_to_use
需要此 OMat24 全量/下采样材料数据进行接入、预训练准备或构型泛化验证，且需清楚区分其与 1m 衍生视图时使用。

## inputs
`OMAT24_DATASET_DIR` 或默认本地根目录、目标视图、转换器类型表与单位协议、目标模型契约、资源额度及评测划分要求。

## outputs
确定的 LMDB/split 路径、nframes/索引策略、类型映射和物理单位契约、去重/泄漏审计方案、分片采样和指标配置。

## procedure
1. 选择 full、subsampled 或已核实合并来源的 combined，记录视图和来源。
2. 从小批 LMDB key 解析 MessagePack，核对 dtype/shape 与元数据计数。
3. 取得并回验 atype 元素表、PBC、单位和 virial 定义。
4. 保留该视图 train/val，用来源 ID/指纹检查与其它视图、1m 数据的重叠。
5. 仅从 train 估计统计，规划惰性索引、worker 和原子数 batch 上限。
6. 先验收小批模型输入，再交接资源配置和分层评测协议。

## constraints
不混加转换副本计数、不虚构 test、不让未核实的类型映射或 virial 转换进入训练；本卡提供资源知识，不执行作业。

## next_phase_recommendation
先由数据标准化/编码技能落实 LMDB adapter 及物理字段契约；资源与数据验证通过后，按具体用户授权交给训练技能。

## fallback
full 元数据/内存开销过大时只取头部字段和少量 key，或切换明确的 subsampled 视图；映射缺失时保留原始类型/virial 字段并登记待补协议，不盲目转换。
