# launch

转换仪器文件为 ASM JSON：

```sh
python script/bio_lab_quality_tools/convert_to_asm.py --instrument BECKMAN_VI_CELL_BLU --input data.csv --output output.asm.json
```

校验 ASM JSON：

```sh
python script/bio_lab_quality_tools/validate_asm.py output.asm.json --reference known_good.json
```

展平 ASM JSON：

```sh
python script/bio_lab_quality_tools/flatten_asm.py --input output.asm.json --output flattened.csv
```

# input_schema

必须显式传入仪器类型、输入文件、输出路径、目标 schema 或参考 JSON。字段分类应区分 raw_measurements、calculated_fields、metadata_fields、instrument settings 和 validation_rules。

# runtime_interfaces

- CLI 工具：`convert_to_asm.py`、`validate_asm.py`、`flatten_asm.py`、`export_parser.py`
- 适用任务标签：`lab-instrument-standardization`
- execution_kind：executable

# main_functions

- convert instrument file to ASM
- validate ASM
- flatten ASM
- export parser

# execution_resources

CPU 表格/JSON 任务。大批量仪器文件需要批处理目录规划和日志输出。

# operation_limits

该卡不保证所有供应商格式可解析；遇到新仪器或复杂 PDF 需要先做字段分类和 parser 扩展。
