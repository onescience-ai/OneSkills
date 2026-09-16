# 实例任务：闭环策略部署与滚动仿真 @ CFD_S082

- domain: cfd
- 骨架: cfd-closed-loop-strategy-deployment-rolling-simulation-task
- 场景: cfd-differentiable-and-generative-pde-optimal-control-scenario (CFD_S082)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S082
- 关联论文: NeuralFluid_ Nueral Fluidic System Design and Control with Differentiable Simulation | doi:; From Uncertain to Safe_ Conformal Adaptation of Diffusion Models for Safe PDE Control | doi:; DiffPhyCon_ A Generative Approach to Control Complex Physical Systems | doi:

## 本实例步骤描述
在独立流动工况中部署策略，滚动记录观测、动作、载荷和安全约束。

## 本实例执行 prompt
加载{CHECKPOINT}作为控制策略，在独立初值和工况上执行闭环滚动。每个控制周期记录观测、动作、阻力或载荷、控制能耗及约束违例，并与无控制和基线控制器对比；不得在测试轨迹继续训练。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- closed_loop_trajectories/
- control_actions.csv
- baseline_comparison.json

## 本实例质量门禁
- 动作满足幅值频率安全约束
- 闭环过程稳定无数值发散
- 收益扣除控制能耗后仍成立

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
