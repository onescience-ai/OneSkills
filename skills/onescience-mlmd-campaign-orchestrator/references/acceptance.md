# 验收门限

## 主门限：验证集力 RMSE
- 指标 `RMSE_F = sqrt(mean(|F_pred - F_ref|^2))`，单位 **meV/Å**。
- 门限 `train.acceptance.forces_rmse_meV_per_A`，默认 **10.0 meV/Å**。
- 同时报告 `RMSE_E_per_atom`（meV/atom）。

### PASS / FAIL
- `RMSE_F ≤ 门限` → PASS，进入 S5（导出 LAMMPS）。
- `RMSE_F > 门限` → **FAIL，停下报告**：当前值、门限、差距，以及**可选建议**
  （更多/更长的 AIMD 帧、`r_max`、模型容量、`forces_weight`、epoch 数、切分是否合理）。
  **不允许**擅自加数据、改超参或“挑一个好看的 checkpoint”。

## 数据侧（S3）
- 键为真值（非 `None`）、`REF_forces` 形状 `(N,3)`、有限值、量级合理。
- 冻结原子：若 mask，报被 mask 的原子数与元素。
- 切分：time-block、`shuffle=false`、三集合帧区间无重叠。

## 力场侧（S5）
- `*-lammps.pt` 可 `torch.jit.load`；元素顺序 == `export.elements`；
- **导出代码版本 == 训练代码版本**。

## 长时 MD（S6）
- 短程 NVE 能量漂移量级合理；无原子飞散/穿层；温度可控。
- Caveat：势函数适用域受训练数据覆盖限制。

## 报告模板
```
阶段 <Sx> 验收
RMSE_F = <x> meV/Å（门限 ≤ <y>）；RMSE_E/atom = <z> meV
切分：time-block(block=100, shuffle=false)；train/valid/test 帧区间 = ...
证据：sha256(<artifact>) = <hash>；命令 = <cmd>
结论：PASS / FAIL（FAIL：差距=…；建议=…，等待用户确认）
```
