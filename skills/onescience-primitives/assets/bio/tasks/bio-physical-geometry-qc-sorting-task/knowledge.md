# 骨架任务：物理几何质控与排序

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 按DCC通过率、碰撞和内部几何筛选对接结果。
- 按PoseBusters通过率、碰撞和内部几何筛选对接结果。
- 按RMSD通过率、碰撞和内部几何筛选对接结果。
- 按Top1成功率、碰撞和内部几何筛选对接结果。
- 按Top5成功率、碰撞和内部几何筛选对接结果。
- 按富集因子、碰撞和内部几何筛选对接结果。

## 执行 prompt（跨场景聚合去重）
- 检查碰撞与键几何，计算DCC通过率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- 检查碰撞与键几何，计算PoseBusters通过率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- 检查碰撞与键几何，计算RMSD通过率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- 检查碰撞与键几何，计算Top1成功率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- 检查碰撞与键几何，计算Top5成功率并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。
- 检查碰撞与键几何，计算富集因子并按{MAX_RMSD}标记成功构象，每个配体保留前{TOP_K}个。

## 输入槽（var/hint/default）
- {MAX_RMSD} | required=False | type=float | var_name=RMSD阈值 | hint=设置成功构象阈值 | default=2
- {TOP_K} | required=False | type=int | var_name=保留姿态数 | hint=设置每配体保留数量 | default=5

## 产出
- DCC通过率汇总表
- PoseBusters通过率汇总表
- RMSD通过率汇总表
- Top1成功率汇总表
- Top5成功率汇总表
- 几何质控报告
- 富集因子汇总表
- 排序姿态

## 质量门禁 quality_gate
- 入选姿态无严重碰撞
- 失败配体原因已记录
- 排序分数定义明确

## 可调资源（edge:resource，仅真实存在）
- models/diffdock

## 实例任务（本骨架在各场景的实例化）
- bio-physical-geometry-qc-sorting-docking-guided-large-scale-inst
- bio-physical-geometry-qc-sorting-geodesic-path-guided-flexibl-inst
- bio-physical-geometry-qc-sorting-global-blind-docking-conform-inst
- bio-physical-geometry-qc-sorting-high-precision-protein-inst
- bio-physical-geometry-qc-sorting-lightweight-interpretable-inst
- bio-physical-geometry-qc-sorting-multi-pocket-conditioned-inst
- bio-physical-geometry-qc-sorting-physical-rule-constrained-inst
- bio-physical-geometry-qc-sorting-pocket-prediction-enhanced-inst
- bio-physical-geometry-qc-sorting-protein-ligand-joint-generat-inst
- bio-physical-geometry-qc-sorting-unknown-binding-site-protein-inst

## 复用场景
- B41
- B45
- B50
- B47
- B46
- B49
- B42
- B43
- B48
- B44
