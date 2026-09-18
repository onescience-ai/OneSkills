# 器件设计表制定任务

## 适用范围
适用于钙钛矿太阳能电池器件设计表的制定，包括层序、材料、厚度、面积、制备方法等参数定义。

## 输入
- 钙钛矿太阳能电池类型（平面、介孔）
- 已知材料（钙钛矿层、传输层、电极层）
- 制备工艺（旋蒸、蒸镀、刮涂）

## 输出
- 器件设计表（表格形式，包含层序、材料、厚度、面积、制备方法）
- 失效判据文档（效率衰减阈值、稳定性测试条件）

## 操作步骤
1. 收集器件结构信息（Glass/ITO/ETL/Perovskite/HTL/Au）
2. 定义各层材料组成（如CH3NH3PbI3、TiO2、Spiro-OMeTAD）
3. 确定各层厚度（钙钛矿层~500 nm，传输层~50 nm）
4. 记录制备方法（旋涂、蒸镀等）
5. 制定失效判据（如PCE保持率>80% after 1000 h）

## 输出产物
- `device_design_table.csv`：器件设计表
- `failure_criteria.md`：失效判据文档

## 质量门禁
- 验证器件设计表包含所有必要字段
- 检查失效判据是否符合国际标准（如ISOS）
- 确认材料和工艺参数合理性

## 回退策略
- 若材料信息不全，查阅文献或使用标准材料
- 若工艺参数缺失，使用典型值或进行实验确定
- 若失效判据不明确，参考国际标准（如ISOS）

## 资源召回建议
- 当需要钙钛矿器件设计规范时召回本任务
- 当需要失效判据标准时召回本任务

## 证据来源
[1] Construction of 1D perovskite nanowires by Urotropin passivation towards efficient and stable perovskite solar cell, Zardari et al., Solar Energy Materials and Solar Cells, 2021, DOI: 10.1016/j.solmat.2021.111119