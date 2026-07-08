# description

把实验室仪器输出标准化为 ASM JSON/CSV，并形成 LIMS/ELN 或数据工程 handoff。

# when_to_use

用于 plate reader、qPCR、cell counter、spectrophotometer、chromatography、electrophoresis 等仪器文件标准化。

# inputs

- instrument_type 和 input_files。
- raw_measurements、calculated_fields、metadata_fields。
- target_schema、validation_rules 和 deliverable。

# outputs

- ASM JSON。
- flattened CSV。
- validation report。
- parser handoff。

# procedure

1. 根据任务标签判断任务属于仪器数据标准化。
2. 读取字段分类和支持仪器边界。
3. 选择本 application 脚本。
4. coder 生成参数化命令或 parser 扩展任务。
5. runtime 执行转换、校验和展平。

# constraints

- 不得混淆原始测量和计算值。
- 不得自动换算不明单位。
- 不得丢失样本、孔位、批次和仪器设置。

# next_phase_recommendation

转换后可交给 QC report app 生成报告，或交给数据工程扩展生产 parser。

# fallback

若仪器类型不支持，输出字段分类表和 parser 开发 handoff；若单位/字段不明，只执行结构检查并列出待确认项。
