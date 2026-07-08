# architecture_overview

该应用卡提供实验室仪器文件到 ASM JSON/CSV 的可执行工具入口。任务必须先区分 raw measurement、metadata、instrument settings 和 calculated values，再把本卡脚本入口写入 handoff；应用卡只提供转换、校验和展平入口，不直接代表已完成生产级 LIMS 集成。

# parameter_scale

非模型原语。规模由仪器文件数量、样本数、孔位数、测量通道、时间点和字段映射复杂度决定。

# architecture_structure

- `convert_to_asm.py`：把仪器文件转换为结构化 ASM JSON 的主入口。
- `validate_asm.py`：校验 ASM JSON 字段、单位、技术类型和计算数据溯源。
- `flatten_asm.py`：把 ASM JSON 展平为二维 CSV。
- `export_parser.py`：导出可交给数据工程的解析器代码。

# input_schema

输入包括 instrument_type、input_files、raw_measurements、calculated_fields、metadata_fields、target_schema、validation_rules 和 deliverable。字段分类必须明确原始测量、计算值、元数据和仪器设置。

# output_schema

输出包括 ASM JSON、flattened CSV、validation report、parser code 或 parser handoff。若单位不明或计算字段来源不清，只能输出待确认项和部分转换结果。

# shape_transformations

instrument file
  -> parsed records
  -> ASM JSON hierarchy
  -> validation report
  -> flattened CSV rows

# key_dependencies

- 仪器类型和文件格式。
- 字段分类规则。
- ASM schema 结构。
- 单位、样本、孔位、批次和仪器设置。

# common_modification_points

- 新增仪器 parser。
- 字段映射和单位规则。
- 计算字段溯源。
- ASM flattening 列命名策略。

# implementation_risks

- 不可把计算值伪装成原始测量。
- 不可在单位不明时自动换算。
- 不可丢失样本、孔位、批次和仪器设置。
- 不可把轻量转换脚本当成已通过生产 LIMS 验证的 parser。

# code_references

- primitive 脚本目录：`assets/bio_lab_quality_asm_app/script/bio_lab_quality_tools/`
- 语义来源标签：`clinical-lab-quality`
- 语义来源标签：`lab-instrument-standardization`
