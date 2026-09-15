# 骨架任务：方程求解与物理残差恢复

- domain: cfd
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 在查询配点或网格上恢复解场、导数、边界值与方程残差。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差。保存解场与残差场；禁止只依据训练损失判定方程已求解。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- boundary_residuals.csv
- pde_residuals/
- solution_fields/

## 质量门禁 quality_gate
- 独立数值解或解析解可对照
- 解场导数与残差均为有限值
- 边初值逐项满足门限

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0007d40a
- it-21d28858
- it-525c9c04
- it-a2f5d01d
- it-b109b296
- it-bcd3602b
- it-bfe6f1b9
- it-d212ca36
- it-d45a4668
- it-d7860553
- it-e86372c3
- it-fa69beed

## 复用场景
- CFD_S036
- CFD_S037
- CFD_S038
- CFD_S039
- CFD_S040
- CFD_S041
- CFD_S042
- CFD_S043
- CFD_S044
- CFD_S045
- CFD_S046
- CFD_S047
