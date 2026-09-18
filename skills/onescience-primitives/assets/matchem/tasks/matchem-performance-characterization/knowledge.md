# 性能表征任务

## 适用范围
适用于钙钛矿太阳能电池性能表征，包括J-V曲线测试、稳定性测试、迟滞分析。

## 输入
- 器件样品（钝化前后）
- 测试设备（太阳模拟器、电化学工作站）
- 测试标准（ISOS、ASTM）

## 输出
- 性能数据（PCE、Voc、FF、Jsc）
- 稳定性曲线（效率随时间变化）
- 迟滞指数（正向和反向扫描差异）
- 机制分析（载流子复合机制、缺陷态密度分析）

## 操作步骤
1. 进行J-V曲线测试（正向和反向扫描）
2. 计算光电转换效率（PCE）
3. 进行稳定性测试（持续光照或暗态存储）
4. 分析迟滞效应（计算迟滞指数）
5. 进行电化学阻抗谱（EIS）分析
6. 分析载流子复合机制

## 输出产物
- `performance_data.csv`：性能数据
- `stability_curve.png`：稳定性曲线
- `hysteresis_analysis.md`：迟滞分析
- `mechanism_report.md`：机制分析报告

## 质量门禁
- 验证测试条件符合标准（如AM1.5G，100 mW/cm²）
- 检查数据重复性（至少3个器件）
- 确认迟滞指数<0.1（低迟滞）

## 回退策略
- 若测试设备故障，使用参考电池进行校准
- 若数据异常，重新测试或使用参考数据
- 若机制分析不明确，进行补充测试（如PL、TRPL）

## 资源召回建议
- 当需要J-V曲线测试方法时召回本任务
- 当需要稳定性测试标准时召回本任务
- 当需要迟滞分析方法时召回本任务

## 证据来源
[1] Synergistic Defect Passivation by Metformin Halides for Improving Perovskite Solar Cell Performance, The Journal of Physical Chemistry C, 2023, DOI: 10.1021/acs.jpcc.3c02121.s001