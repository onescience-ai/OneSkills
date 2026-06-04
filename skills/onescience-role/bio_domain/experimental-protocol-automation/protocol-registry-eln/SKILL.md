---
name: bio-protocol-registry-eln
description: 生物实验协议、注册和 ELN 交接 skill。用于实验协议检索整理、步骤结构化、样本/构件/库存登记字段、ELN 条目、材料试剂、版本控制和实验可追溯性。
---

# 实验协议、注册与 ELN 交接

## 使用边界

用于把实验方案、公开协议、内部步骤或样本构件信息整理为可追溯记录。若需要真正访问远程系统，必须由执行层处理凭据和 API。

## 可复用资源

- `onescience-coder/assets/bio_protocol_templates/protocol_record.yaml`：实验目的、材料、步骤、样本、构件、版本和输出模板。
- `references/protocol_registry_fields.md`：ELN、样本、构件、库存和协议字段建议。

## 推荐流程

1. 明确目标：协议检索、步骤结构化、ELN 记录、样本注册、构件注册或库存交接。
2. 抽取字段：材料、试剂、设备、样本、构件、浓度、批号、时间、温度、安全事项。
3. 版本化：protocol version、deviation、operator、date、linked data、expected outputs。
4. 与下游连接：如果需要液体处理，交给 `../liquid-handling-protocols/SKILL.md`；如果需要报告，交给 `../../clinical-lab-quality/qc-reporting-reproducibility/SKILL.md`。

## 交接物

```yaml
bio_task_family: experimental-protocol-automation
experiment_task: protocol-registry-eln
protocol_source:
materials_and_reagents:
sample_or_construct_records:
steps:
versioning:
data_outputs:
access_or_credential_boundary:
execution_entry:
```

## 禁止事项

- 不要把 API key、token 或私有 ELN 链接写进 skill 或模板。
- 不要省略 protocol version 和 deviation。
- 不要把未经验证的公开协议改写成内部批准 SOP。
