# SAbDab抗体结构数据库

## 适用范围
适用于需要获取实验解析抗体结构数据的任务，包括抗体建模训练数据获取、结构验证参考、CDR构象分析、抗体-抗原复合物研究等场景。不适用于序列-only分析或非抗体蛋白质研究。

## 输入
- 查询条件（PDB ID、抗原类型、物种、实验方法等）
- 可选：序列相似度阈值
- 可选：分辨率和R-factor过滤条件

## 输出
- 抗体结构数据（PDB/mmCIF格式）
- CDR区域标注（Chothia/IMGT编号）
- 序列信息（重链/轻链）
- 元数据（抗原、物种、实验方法、分辨率等）

## 流程节点
1. **数据库访问** → 通过Web界面或API查询SAbDab
2. **条件筛选** → 按需求过滤结构（分辨率、抗原类型等）
3. **数据下载** → 获取结构文件和注释信息
4. **格式转换** → 转换为分析工具所需格式
5. **数据验证** → 检查数据完整性和质量

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据库URL | opig.stats.ox.ac.uk/webapps/newsabdab/ | [1] | 官方访问地址 |
| 结构数量 | >5400条目（2021年） | [2] | 持续更新中 |
| 编号方案 | Chothia（默认）/IMGT | [1][2] | 支持多种编号 |
| 数据格式 | PDB/mmCIF | [1] | 标准结构格式 |
| 更新频率 | 每周更新 | [2] | 保持数据时效性 |
| 许可证 | CC-BY 4.0 | [2] | 学术和商业使用 |

## 边界与分流
- 结构缺失：某些治疗性抗体可能没有实验结构，需使用同源建模
- 分辨率限制：低分辨率结构（>3.0 Å）可能不适合精细分析
- 序列覆盖度：某些CDR区域可能在晶体结构中无序或缺失
- 数据许可：商业使用需额外许可（SAbBox虚拟机）

## 质量检查
- 结构分辨率验证（推荐<3.0 Å）
- CDR区域完整性检查
- 序列与结构一致性验证
- 元数据准确性确认

## 回退策略
- SAbDab不可用：使用PDB直接查询抗体结构
- 无匹配结构：使用ABodyBuilder进行同源建模
- 数据格式不兼容：使用BioPython/PyMOL进行格式转换

## 资源召回建议
当任务涉及以下场景时应召回本卡片：
- 抗体建模训练数据获取
- 生成抗体结构验证参考
- CDR构象数据库查询
- 抗体-抗原复合物分析

配套资源：
- abode-model-deployment：可使用SAbDab数据进行微调
- anarci-antibody-numbering：SAbDab使用ANARCI进行编号
- cdr-rmsd-calculation：提供验证参考结构

## 证据来源
[1] Raybould MIJ, Marks C, Lewis AP, et al. Thera-SAbDab: the Therapeutic Structural Antibody Database. Nucleic Acids Research, 2019. DOI: 10.1093/nar/gkz827
[2] Schneider C, Raybould MIJ, Deane CM. SAbDab in the age of biotherapeutics: updates including SAbDab-nano, the nanobody structure tracker. Nucleic Acids Research, 2021. DOI: 10.1093/nar/gkab1050
