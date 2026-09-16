# 骨架任务：候选筛选与验证设计

- domain: matchem
- 复用场景数: 19
- 实例任务数: 19

## 步骤描述（跨场景聚合去重）
- 给出优先候选及验证实验或高保真计算。

## 执行 prompt（跨场景聚合去重）
- 输出优先候选、关键参数和验证方案；把模型适用域外结论标为待验证。

## 输入槽（var/hint/default）
- （源场景未提供）

## 产出
- PASS/REJECT/BLOCKED 结论
- 候选排序
- 验证方案

## 质量门禁 quality_gate
- 每项推荐有原始数据支撑
- 预测与实验结果分列

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-candidate-screening-validation-copper-nanocrystal-co2-to-inst
- matchem-candidate-screening-validation-cusn-atomic-interface-co2-inst
- matchem-candidate-screening-validation-fe-single-atom-nitrate-inst
- matchem-candidate-screening-validation-fe-single-atom-orr-fuel-inst
- matchem-candidate-screening-validation-fenx-site-durability-pem-inst
- matchem-candidate-screening-validation-high-entropy-alloy-lattice-inst
- matchem-candidate-screening-validation-lamn-doped-cobalt-spinel-inst
- matchem-candidate-screening-validation-metal-nitrogen-doped-carbon-inst
- matchem-candidate-screening-validation-mof-electrocatalytic-co2-inst
- matchem-candidate-screening-validation-molecular-metal-interface-inst
- matchem-candidate-screening-validation-mos2-case2-heterostructure-inst
- matchem-candidate-screening-validation-ni-single-atom-mo2c-water-inst
- matchem-candidate-screening-validation-nickel-catalyst-co2-activati-inst
- matchem-candidate-screening-validation-oxidation-derived-copper-inst
- matchem-candidate-screening-validation-pdceo2-single-atom-catalyst-inst
- matchem-candidate-screening-validation-pt-single-atom-heterostructu-inst
- matchem-candidate-screening-validation-ru-single-atom-nife-ldh-inst
- matchem-candidate-screening-validation-snbi-alloy-co2-formate-inst
- matchem-candidate-screening-validation-ultra-thin-mof-array-electro-inst

## 复用场景
- CuSn原子界面CO2到CO选择性优化
- FeNx位点耐久性质子交换膜燃料电池分析
- Fe单原子催化硝酸盐还原制氨
- Fe单原子氧还原燃料电池催化剂设计
- LaMn掺杂钴尖晶石酸性析氧催化设计
- MOF电催化CO2还原活性位设计
- MoS2CoSe2异质结构析氢催化设计
- Ni单原子Mo2C水分解微环境优化
- PdCeO2单原子催化剂CO氧化动态分析
- Pt单原子异质结构碱性析氢优化
- Ru单原子NiFe层状双氢氧化物水分解优化
- SnBi合金CO2到甲酸盐稳定电催化设计
- 分子金属界面CO2到乙醇催化设计
- 氧化衍生铜CO2电还原活性位分析
- 超薄MOF阵列电催化水分解设计
- 金属氮掺杂碳CO2电还原选择性设计
- 铜纳米晶CO2到C2产物选择性设计
- 镍催化剂CO2活化与碳碳偶联分析
- 高熵合金晶格氧活化析氧催化设计
