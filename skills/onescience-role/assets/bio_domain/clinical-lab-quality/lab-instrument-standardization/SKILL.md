---
name: bio-lab-instrument-standardization
description: 实验室仪器数据标准化 skill。用于 plate reader、qPCR、cell counter、spectrophotometer、chromatography、electrophoresis、CSV/Excel/PDF/TXT 输出到结构化 JSON/CSV、LIMS/ELN 上传和字段映射。
---

# 实验室仪器数据标准化

## 可复用资源

- `onescience-coder/assets/bio_lab_quality_tools/convert_to_asm.py`：把仪器文件转换为结构化 ASM JSON 的主入口。
- `onescience-coder/assets/bio_lab_quality_tools/flatten_asm.py`：把 ASM JSON 展平为二维 CSV。
- `onescience-coder/assets/bio_lab_quality_tools/validate_asm.py`：校验 ASM JSON 字段、单位、技术类型和计算数据溯源。
- `onescience-coder/assets/bio_lab_quality_tools/export_parser.py`：导出可交给数据工程的解析器代码。
- `references/field_classification_guide.md`：区分 raw measurement、calculated value、metadata、settings。
- `references/asm_schema_overview.md`：ASM schema 结构概览。
- `references/flattening_guide.md`：展平规则。
- `references/supported_instruments.md`：支持仪器类型。

需要生成可运行转换时，先读取 field classification，再把 coder 资产路径写入 `handoff_artifacts`；role 层不直接运行脚本。

## 推荐流程

1. 明确仪器类型、文件格式、原始测量和计算字段。
2. 分离 raw measurement、metadata、instrument settings、calculated values。
3. 建立字段映射：sample、well、time、unit、method、operator、batch。
4. 输出结构化 JSON/CSV 和解析说明。
5. 需要生产化时，交给 data-engineer 生成可维护 parser 和验证规则。

## 交接物

```yaml
task_context: lab-instrument-standardization
instrument_type:
input_files:
raw_measurements:
calculated_fields:
metadata_fields:
target_schema:
validation_rules:
deliverable:
execution_entry:
```

## 禁止事项

- 不要把计算值伪装成原始测量。
- 不要在单位不明时自动换算。
- 不要丢失样本、孔位、批次和仪器设置。
