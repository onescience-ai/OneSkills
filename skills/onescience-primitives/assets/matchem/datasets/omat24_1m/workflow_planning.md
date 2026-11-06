## description
规划 OMat24-1m 本地 LMDB 的独立资源绑定、物理字段确认、来源去重和可复现划分。

## when_to_use
指定此 `omat24-1m/omat24_full.lmdb`，需要百万级数据准备或与全量 OMat24 比较时使用。

## inputs
LMDB 目录或 `OMAT24_1M_LMDB`、目标模型契约、类型/单位说明、来源关联信息与评测需求。

## outputs
1,009,850 帧资源声明、float64 reader 配置、类型/单位协议、已保存的 split 索引及与其它视图的重叠审计状态。

## procedure
1. 核对路径为现有目录，读取 nframes 和少量 12 位 key。
2. 验证各字段的 dtype/shape，保留原始 atype/virial。
3. 绑定来源元素表、PBC、单位和 virial 转换，回验结构。
4. 获取来源 ID 或结构指纹，排查与 OMat24 其它视图重叠。
5. 建立分组 split 并保存索引，仅从 train 生成统计。
6. 小批验收模型输入后交接训练/评测配置，并注明独立性边界。

## constraints
没有已确认官方 split，不假设 1m 与 full 相互独立，不用全量 float32 编码假设覆盖本视图 float64 数据。

## next_phase_recommendation
先完成类型表和去重/划分来源调查，再交由数据标准化/编码技能实现；训练仅在输入契约与用户具体任务满足后推进。

## fallback
来源/类型映射不可取得时仅保留原字段读取与待核实清单；若需要已带 split 的入口，可使用 `omat24` 的 full/subsampled train/val，但须明确切换了数据视图。
