# 骨架任务：活性位与反应网络定义

- domain: matchem
- 复用场景数: 19
- 实例任务数: 19

## 步骤描述（跨场景聚合去重）
- 建立催化剂活性位、目标产物和竞争反应网络。

## 执行 prompt（跨场景聚合去重）
- 读取 {CATALYST_STRUCTURE} 与 {REACTION_CONDITION}，定义活性位、反应中间体和竞争路径；缺少电位或对照条件时标记 BLOCKED。

## 输入槽（var/hint/default）
- {CATALYST_STRUCTURE} | required=True | type=doc | var_name=催化剂结构或制备信息 | hint=活性位、晶面、组成、缺陷或制备方法。 | default=CIF/POSCAR/制备配方
- {REACTION_CONDITION} | required=True | type=object | var_name=反应条件 | hint=目标产物、温度、压力、电位/pH、反应物 | default={'target_product': 'specified product', 'temperature_K': 298}

## 产出
- 反应网络
- 活性位模型

## 质量门禁 quality_gate
- 活性位和目标产物明确
- 竞争反应未被忽略

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-02f91a5f
- it-1ae2b35f
- it-22b2310a
- it-291fbc9b
- it-3e5a3d76
- it-5413b689
- it-6514929b
- it-72fbc5cc
- it-79c53701
- it-7c1b215a
- it-90a90af1
- it-90e29901
- it-988afef0
- it-a0a422fb
- it-be65f867
- it-cf6a7bda
- it-d9503dc3
- it-f8a00477
- it-fce267d6

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
