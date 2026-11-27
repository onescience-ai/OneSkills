# 实例任务：结构质控与汇总 @ B02

- domain: bio
- 骨架: bio-structure-quality-control-and-summary-task
- 场景: bio-openfold-component-ablation-structural-generalization-scenario (B02)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
先用几何完整性筛选并锁定候选，再用独立参考评分和汇总。

## 本实例执行 prompt
先按事前几何规则锁定候选，再用独立参考计算 TM-score。{QUALITY_THRESHOLD}只用于评分后的低质量标记，不改变主分析候选或配对范围；按{OUTPUT_FORMAT}导出结构。

- **候选锁定**：按事前规则在同一靶标、同一组的合格候选中确定主分析候选，预先规定并列处理，不用 pTM、pLDDT 或终评分回选。
- **单链 TM-score**：按明确的原链、残基编号和插入码建立 Cα 对应关系，以参考靶标全长归一化，不以已匹配片段的长度替代。复合物、界面或状态评估使用与对象相符的映射和指标，不静默拆链套用单链得分。
- **配对效应**：在两组共同可评分的靶标上计算 `ΔTM = 消融组 − 基线组`。用独立靶标或预先定义的同源簇估计不确定度，不把候选或残基当作独立样本；没有合格配对时不估计效应。

## 本实例输入槽
- {QUALITY_THRESHOLD} | required=False | type=float | var_name=质量阈值 | hint=仅用于评分后标记低质量候选 | default=0.7
- {OUTPUT_FORMAT} | required=False | type=enum | var_name=结构格式 | hint=选择结构输出格式 | default=mmCIF

## 本实例产出
- 排序结构
- TM-score汇总表
- 结构质控报告

## 本实例质量门禁
- 结构文件可解析
- 候选锁定早于独立参考访问，低质量标记不回写主分析。
- 结果可追溯到参数

## 可调资源（edge:resource，仅真实存在）
- datasets/tm-score-evaluation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
