# 骨架任务：闭环策略部署与滚动仿真

- domain: cfd
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 在独立流动工况中部署策略，滚动记录观测、动作、载荷和安全约束。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}作为控制策略，在独立初值和工况上执行闭环滚动。每个控制周期记录观测、动作、阻力或载荷、控制能耗及约束违例，并与无控制和基线控制器对比；不得在测试轨迹继续训练。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- baseline_comparison.json
- closed_loop_trajectories/
- control_actions.csv

## 质量门禁 quality_gate
- 动作满足幅值频率安全约束
- 收益扣除控制能耗后仍成立
- 闭环过程稳定无数值发散

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-463aa52e
- it-5021404f
- it-587d7a45
- it-695b302f
- it-abf6a06e

## 复用场景
- CFD_S081
- CFD_S082
- CFD_S083
- CFD_S084
- CFD_S085
