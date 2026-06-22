---
name: bio-crispr-guide-editing
description: CRISPR guide 与编辑实验设计 skill。用于 sgRNA、Cas9/Cas12a、CRISPRa/i、base editing、prime editing、HDR donor、off-target 过滤、编辑窗口和验证引物交接。
---

# CRISPR Guide 与编辑实验设计

## 使用边界

用于设计或评估 CRISPR guide、编辑窗口、donor template 和验证计划。若用户只是需要 PCR 验证引物，读取 `../primer-probe-design/SKILL.md`；若需要质粒构建核对，读取 `../plasmid-annotation-verification/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_molecular_templates/crispr_design_request.yaml`：记录 nuclease、PAM、目标区域、编辑类型、参考版本、排除区域和验证方案。
- `references/crispr_design_rules.md`：knockout、CRISPRa/i、base editor、prime editor、HDR 和 off-target 的选择规则。
- `onescience-coder/assets/bio_molecular_tools/pam_scan.py`：无第三方依赖的 Cas9/Cas12a PAM 扫描和候选 guide 初筛脚本。

## 推荐流程

1. 明确编辑目标：knockout、activation、interference、base edit、prime edit、knock-in、tagging 或 variant correction。
2. 明确 nuclease/editor：SpCas9 NGG、SaCas9 NNGRRT、Cas12a TTTV、ABE/CBE、prime editor。
3. 定义靶区：coding exon、TSS window、enhancer、具体 variant、剪接位点或插入位点。
4. 生成 guide：扫描 PAM、记录 strand/cut site/editing window、过滤 poly-T、极端 GC、重复区、常见 SNP。
5. 评估风险：on-target、off-target、isoform 覆盖、旁观者编辑、PAM-disrupting mutation、可交付验证。
6. 输出候选表和实验验证：top guide、donor/pegRNA 元件、PCR/amplicon-seq 引物、阴性和阳性对照。

## 交接物

```yaml
bio_task_family: molecular-biology-design
molecular_task: crispr-guide-editing
editing_goal:
nuclease_or_editor:
organism_reference:
target_locus_or_sequence:
candidate_guides:
off_target_strategy:
donor_or_pegRNA:
validation_assay:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在没有参考基因组版本时声称 off-target 已经合格。
- Base editing 和 prime editing 必须写明编辑窗口、旁观者碱基和期望 edit。
- 不要把 guide activity score 当成实验效率保证。
