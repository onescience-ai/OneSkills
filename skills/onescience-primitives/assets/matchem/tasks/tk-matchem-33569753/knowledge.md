# 骨架任务：活性选择性稳定性联评

- domain: matchem
- 复用场景数: 19
- 实例任务数: 19

## 步骤描述（跨场景聚合去重）
- 比较目标产物、竞争反应和结构稳定性。

## 执行 prompt（跨场景聚合去重）
- 在 {REACTION_CONDITION} 下联评活性、选择性、稳定性和副反应，输出限制步骤或证据缺口。

## 输入槽（var/hint/default）
- {REACTION_CONDITION} | required=True | type=object | var_name=反应条件 | hint=目标产物、温度、压力、电位/pH、反应物 | default={'target_product': 'specified product', 'temperature_K': 298}

## 产出
- 综合性能表
- 限制步骤分析

## 质量门禁 quality_gate
- 不以单一描述符替代完整选择性分析
- 长期稳定性不由短时数据替代

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1e89fbc6
- it-265e5a3e
- it-30ab0fff
- it-421ab556
- it-437bf678
- it-52613432
- it-543c22fe
- it-632a66bc
- it-85a13285
- it-8f4c4104
- it-af465628
- it-b0105d7b
- it-c4257d98
- it-c60ed8c2
- it-c7d1cc76
- it-d054254a
- it-d53d493c
- it-d82a3818
- it-ef184312

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
