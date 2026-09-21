# 公开合金数据库查询B2金属间化合物数据

## 适用范围
当需要获取B2金属间化合物（空间群Pm-3m, #221）的真实实验或高通量DFT计算数据时，使用本流程从Materials Project、OQMD、AFLOW、ICSD等公开数据库查询。适用于合金相稳定性筛选、形成能数据采集、训练数据集构建等任务。

## 输入
- 目标合金体系的元素组成（如CoTi、NiAl、FeCo等）
- 结构类型约束（B2, space group 221）
- 所需属性字段（formation_energy_per_atom、energy_above_hull、band_gap等）

## 输出
- 结构化合金数据（JSON/CSV），包含composition、space_group、formation_energy、stability等字段
- 数据审计报告，标注数据来源和质量等级

## 流程节点

### 1. Materials Project API (mp-api) 查询
```
from mp_api.client import MPRester
with MPRester("YOUR_API_KEY") as mpr:
    docs = mpr.materials.summary.search(
        chem_system=element_pair,  # 如 "Co-Ti"
        space_group_symbols="Pm-3m",
        fields=["material_id", "composition", "formation_energy_per_atom",
                "energy_above_hull", "structure", "density"]
    )
```
- **关键参数**：`space_group_symbols="Pm-3m"` 过滤B2结构；`energy_above_hull` < 25 meV/atom 判定热力学稳定 [1]
- **API密钥**：需在 materialsproject.org 注册获取
- **限制**：免费层有速率限制；部分合金体系数据不完整

### 2. OQMD 批量下载
- 网址：http://oqmd.org/
- 下载方式：Analysis → Download → 选择元素对 → CSV格式
- 关键字段：`formation_energy`、`spacegroup`、`natoms`
- 数据许可：CC BY 4.0 [2]
- 注意：OQMD包含约100万条DFT计算数据，B2相需通过spacegroup=221过滤

### 3. AFLOW REST API 查询
```
GET https://aflowlib.duke.edu/search/API/?ael_bulk_modulus_vegt&species=Co,Ti&spacegroup=Pm-3m
```
- AFLOW使用aflowlib REST接口，支持元素、空间群等多维过滤
- 关键字段：`ael_bulk_modulus_vegt`（弹性模量）、`formation_energy_atom`
- 参考：AFLOW Library of Crystallographic Prototypes [3]

### 4. ICSD 检索（需机构订阅）
- 检索关键词：`elements=Co+Ti AND spacegroup=Pm-3m AND structure_type=B2`
- 导出格式：CIF或结构数据
- 注意：ICSD为商业数据库，需通过机构访问

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| B2空间群 | Pm-3m (#221) | [1] | 所有B2结构的统一空间群标识 |
| 稳定性阈值 | energy_above_hull < 25 meV/atom | [1] | Materials Project热力学稳定性判据 |
| OQMD数据许可 | CC BY 4.0 | [2] | 可自由使用需注明来源 |
| 形成能公式 | E_form = E_compound - Σxi·E_element | [1] | 标准DFT形成能计算定义 |

## 边界与分流
- Materials Project API不可用 → 降级到OQMD CSV批量下载
- OQMD无目标体系数据 → 降级到AFLOW REST查询
- 所有数据库均无数据 → 使用合成数据作为fallback，但必须在报告中标注数据来源为synthetic
- ICSD无机构订阅 → 跳过ICSD，使用前三者

## 质量检查
- 数据来源字段必须为public_database（非synthetic）
- formation_energy_per_atom数值范围应在合理区间（金属间化合物通常 -2~0 eV/atom）
- space_group验证：通过pymatgen验证结构是否确实为B2

## 回退策略
- 当所有API不可用时，可使用pymatgen的Structure批量生成B2结构，再通过简化物理模型估算形成能
- 必须在数据审计报告中明确标注回退策略及不确定性

## 资源召回建议
- 当任务涉及合金数据采集、相稳定性筛选时召回本卡
- 配套资源：pymatgen（结构操作）、matminer（特征工程）

## 证据来源
[1] Materials Project documentation, https://next-gen.materialsproject.org/
[2] OQMD, http://oqmd.org/, Open Quantum Materials Database
[3] AFLOW Library of Crystallographic Prototypes, Computational Materials Science, 2019, DOI: 10.1016/j.commatsci.2019.04.012
