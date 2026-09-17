# 闭合项预测与后验CFD耦合

## 适用范围

适用于将训练好的闭合模型嵌入CFD求解器执行先验与后验评估。当需要验证闭合项预测的物理一致性与求解器稳定性时，执行本步骤。

## 输入

- CHECKPOINT：通过训练门限的模型权重
- DEVICE：计算设备（CPU或CUDA）
- BATCH_SIZE：推理批大小

## 输出

- apriori_closure/：先验闭合项预测结果（应力、通量或源项）
- aposteriori_fields/：后验流场结果
- solver_stability.csv：求解器稳定性记录

## 流程节点

1. 加载CHECKPOINT权重 → 验证模型结构兼容性
2. 在独立快照上预测闭合项 → 计算先验误差
3. 可实现性检查 → 验证闭合张量满足物理约束（正定性、对称性等）
4. 嵌入RANS或LES求解器 → 配置求解器参数
5. 执行后验推进 → 保存残差、能谱、统计剖面
6. 稳定性监控 → 记录发散或非物理行为

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| DEVICE | cuda | 场景需求书 | 默认GPU推理 |
| BATCH_SIZE | 8 | 场景需求书 | 按显存调整 |
| 闭合项类型 | 应力/通量/源项 | 场景需求书 | 取决于模型输出 |

## 方法细节

### 先验评估
- 在独立快照上预测闭合项
- 计算预测误差（RMSE、相对误差）
- 验证闭合张量满足约束：
  - 对称性（应力张量）
  - 正定性（扩散系数）
  - 能量守恒（非局部闭合）[3]

### 后验耦合
- 嵌入RANS：预测湍流粘性或应力项，求解雷诺平均方程
- 嵌入LES：预测子网格应力，求解滤波Navier-Stokes方程
- 稳定性判据：CFL条件、残差收敛、能量谱合理性

## 边界与分流

- 闭合张量不满足约束 → 调整模型或添加投影层
- 后验求解发散 → 降级为纯先验评估
- 非物理结果 → 检查闭合项可实现性

## 质量检查

- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

## 回退策略

- 后验失败 → 仅报告先验误差
- 求解器不稳定 → 调整时间步长或闭合项裁剪
- 能谱异常 → 检查小尺度闭合项

## 资源召回建议

- 需要了解先验/后验评估方法时召回本卡
- 需要了解CFD耦合策略时召回本卡

## 证据来源

[1] Ilersich, A.F., Nair, P.B. (2025). Learning Stochastic Multiscale Models. arXiv:2506.22655.
[2] Heyder, F., Schumacher, J. (2021). Echo State Network for turbulent moist Rayleigh-Bénard convection. Physical Review E, 103, 053107.
[3] Charalampopoulos, A.-T.G., Sapsis, T.P. (2022). Machine-learning energy-preserving nonlocal closures. Physical Review Fluids, 7, 024305.
