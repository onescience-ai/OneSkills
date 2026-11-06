## description
为本地 MPtrj 多格式过滤数据选择读取、能量口径、分组划分和材料势模型接入方案。

## when_to_use
任务明确使用此 MPtrj 本地包，或需要多元素材料能量/力/应力监督时召回；不能据此假设已具备独立测试集。

## inputs
数据根目录或 `MPTRJ_DATASET_DIR`、目标模型字段契约、拟用能量口径、可用内存和 split 需求。来源默认 `/work2/share/sugonhpcapp01/OneData/wangrui10/matchem/datasets/mptrj/`。

## outputs
单一主视图绑定、分片/分组清单、标签及 mask 映射、单位与能量口径记录、训练统计和可追踪的验证协议。

## procedure
1. 选定 extxyz、HDF5 或 ASELMDB 主视图，登记来源版本和过滤状态。
2. 抽样解析结构与标签，按 `None` 和 property_weights 屏蔽无效属性。
3. 确定总能/校正能/每原子能的唯一监督口径，核对单位和 stress 约定。
4. 保留 train/val，按材料与轨迹 ID 检查泄漏；需要 test 时另建分组清单。
5. 用 974 帧 smoke 验证 reader、邻居图和有效标签，再按 shard 扩展。
6. 从训练数据生成统计；按相同标签定义分层报告能量、力、应力误差。

## constraints
不按行号跨格式配对，不以 HDF5 子键存在断言标签有效，不把空 test 目录当测试集；统计量不得使用验证/测试样本重新拟合。

## next_phase_recommendation
将本卡的字段映射、标签 mask、能量/单位协议和 split 清单交给数据标准化或编码技能；完成消费接口验证后再由用户任务决定是否训练。

## fallback
HDF5 或 ASELMDB reader 不兼容时先用 extxyz smoke；缺少应力协议时先保留能量/力任务，无法确认能量单位时只交付结构接入和待核实项，不生成伪标签。
