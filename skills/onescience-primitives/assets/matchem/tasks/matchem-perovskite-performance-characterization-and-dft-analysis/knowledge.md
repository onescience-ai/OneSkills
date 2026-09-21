# 钙钛矿太阳能电池性能表征与DFT分析

## 适用范围
本卡片适用于钙钛矿太阳能电池的性能测试和DFT计算分析，包括J-V曲线测试、稳定性测试、迟滞分析以及DFT计算工具调用和结果解释。适用于实验表征和计算模拟。

## 输入
- 器件J-V曲线数据
- 稳定性测试数据（如光照、热老化）
- DFT计算输出文件（如VASP的OUTCAR、CONTCAR）
- 吸附能、态密度等计算结果

## 输出
- 性能参数（PCE、Voc、FF、Jsc）
- 稳定性曲线（效率保持率随时间变化）
- 迟滞指数
- DFT计算结果解释（吸附能物理意义、钝化效率关联）

## 流程节点
1. 测试J-V曲线（AM1.5G, 100 mW/cm²）
2. 计算性能参数（PCE = Voc × Jsc × FF / Pin）
3. 进行稳定性测试（ISOS标准）
4. 分析迟滞现象（正向和反向扫描）
5. 调用DFT计算工具（如VASP、Gaussian）
6. 分析吸附能和电子结构
7. 解释结果与性能关联

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 测试条件 | AM1.5G, 100 mW/cm² | [论文1] | 标准测试条件 |
| 扫描速率 | 50-200 mV/s | [论文1] | 避免瞬态效应 |
| 迟滞指数 | <0.1 | [论文1] | 低迟滞判据 |
| 吸附能 | 负值（稳定吸附） | [论文2] | 物理意义 |
| DFT工具 | VASP/Gaussian | [论文2] | 常用计算软件 |

## 边界与分流
- 若J-V曲线测试条件不标准，需校准
- 若稳定性测试数据不足，可采用加速老化模型
- 若DFT计算资源不足，可使用简化模型

## 质量检查
- 性能参数是否合理（PCE > 20%为高效器件）
- 稳定性曲线是否平滑
- DFT结果是否收敛

## 回退策略
- 参考已发表性能数据
- 使用经验公式估算性能
- 咨询测试专家

## 资源召回建议
- 当分析J-V曲线时召回本卡片
- 当解释DFT计算结果时召回本卡片
- 配套资源：性能测试设备、DFT计算工具

## 证据来源
[1] Khenkin, M. et al. Consensus statement for stability assessment and reporting for perovskite photovoltaics based on ISOS procedures. Nature Energy 5, 35–49 (2020). DOI: 10.1038/s41560-019-0529-5
[2] Tao, Q. et al. Machine learning for perovskite materials design and discovery. npj Comput Mater 7, 2 (2021). DOI: 10.1038/s41524-021-00495-8