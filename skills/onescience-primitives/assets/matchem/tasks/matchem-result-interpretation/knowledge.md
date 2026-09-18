# 结果解释任务

## 适用范围
适用于DFT计算结果的解释，包括吸附能物理意义、钝化效率与器件性能关联，敏感性分析方法。

## 输入
- DFT计算输出文件（OUTCAR、DOSCAR）
- 性能数据（PCE、Voc、FF、Jsc）
- 文献参考数据

## 输出
- 结果解释报告（物理解释、误差分析）
- 敏感性分析图表（参数变化对结果的影响）
- 机制分析（载流子复合机制、缺陷态密度分析）

## 操作步骤
1. 分析吸附能数据（负值表示稳定吸附）
2. 计算钝化效率（缺陷态密度减少百分比）
3. 关联DFT结果与器件性能
4. 进行敏感性分析（计算参数、分子构象变化）
5. 生成物理解释和误差分析
6. 撰写结果解释报告

## 输出产物
- `result_interpretation.md`：结果解释报告
- `sensitivity_analysis.png`：敏感性分析图表
- `mechanism_analysis.md`：机制分析报告

## 质量门禁
- 验证吸附能物理意义（负值表示稳定吸附）
- 检查钝化效率计算合理性
- 确认敏感性分析覆盖关键参数

## 回退策略
- 若结果解释不明确，查阅文献或进行补充计算
- 若敏感性分析异常，调整参数范围
- 若机制分析困难，采用简化模型或参考文献

## 资源召回建议
- 当需要吸附能解释方法时召回本任务
- 当需要敏感性分析方法时召回本任务
- 当需要机制分析方法时召回本任务

## 证据来源
[1] Synergistic Defect Passivation by Metformin Halides for Improving Perovskite Solar Cell Performance, The Journal of Physical Chemistry C, 2023, DOI: 10.1021/acs.jpcc.3c02121.s001