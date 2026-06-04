---
name: bio-restriction-cloning-mapping
description: 限制性酶切、克隆和质粒消化图谱 skill。用于查找酶切位点、选择酶、单酶切和双酶切片段、兼容粘性末端、插入片段方向验证、模拟凝胶和克隆方案交接。
---

# 限制性酶切与克隆图谱

## 使用边界

用于限制性酶切位点查询、酶选择、消化片段预测、克隆方案验证和质粒构建 QC。若用户需要完整质粒 feature 注释，读取 `../plasmid-annotation-verification/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_molecular_templates/restriction_map_request.yaml`：记录序列、拓扑、酶集合、插入片段和约束。
- `references/cloning_decision_rules.md`：单/双酶切、兼容末端、methylation sensitivity、方向性和诊断酶切规则。
- `onescience-coder/assets/bio_molecular_tools/restriction_digest_report.py`：内置常见酶识别序列的简易线性/环状消化片段报告。

## 推荐流程

1. 明确输入：FASTA/GenBank/raw DNA，linear 或 circular，坐标是否 1-based。
2. 明确目标：找 cut site、选择 unique cutter、诊断酶切、double digest、插入片段方向验证。
3. 过滤酶：避开 insert 内部切位、考虑 buffer/温度/star activity/methylation sensitivity。
4. 生成图谱：cut position、fragment size、overhang/blunt、expected gel bands。
5. 对 cloning 输出：vector/insert 末端、ligation 方向、screening digest、Sanger primer。

## 交接物

```yaml
bio_task_family: molecular-biology-design
molecular_task: restriction-cloning-mapping
sequence_input:
topology:
enzyme_set:
cloning_goal:
excluded_sites:
expected_fragments:
validation_digest:
execution_entry:
```

## 禁止事项

- 环状质粒片段计算必须闭合首尾，不要按线性序列直接解释。
- 不要只列酶名；必须说明 cut position、片段大小和是否 unique cutter。
- 不要忽略 methylation sensitivity 和插入片段内部切位。
