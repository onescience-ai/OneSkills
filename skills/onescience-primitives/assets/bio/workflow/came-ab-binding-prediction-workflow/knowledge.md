# CAME-AB Binding Prediction Workflow

## 适用范围
Standard 4-step workflow for antibody-antigen binding site prediction using CAME-AB or similar multimodal deep learning models. Use this workflow when performing binding site prediction on antigen surfaces given antibody sequences/structures. Defines clear input-output contracts for each step to ensure reproducibility and proper data flow.

## 输入
- **Antibody sequences**: Heavy and light chain amino acid sequences in FASTA format
- **Antigen sequences/structures**: Antigen amino acid sequences or PDB structures
- **Model weights**: Pretrained CAME-AB or equivalent model parameters
- **Configuration**: Numbering scheme, prediction threshold, output format preferences

## 输出
- **Binding site predictions**: Per-residue binding probability scores on antigen
- **Filtered results**: High-confidence binding sites above threshold
- **Report**: Performance metrics, visualizations, quality assessment

## 流程节点

### Step 1: Input Validation (s01)
- **Operation**: Validate input files, check format compatibility, verify data completeness
- **Parameters**: File format checks, sequence length limits, missing value detection
- **Tools**: Custom validators, BioPython sequence parsers
- **Quality gate**: All inputs must pass format validation before proceeding
- **Output**: Validated sequences, structures, and configuration

### Step 2: Feature Preparation (s02)
- **Operation**: Extract and compute all modality features for model input
- **Parameters**: Amino acid encodings, BLOSUM profiles, LM embeddings, structure features, GCN graphs
- **Tools**: ANARCI for CDR numbering, PDB parsers for structure, embedding models for LM features
- **Quality gate**: All five modalities must be present and properly formatted
- **Output**: Feature tensors ready for model inference

### Step 3: Inference Execution (s03)
- **Operation**: Run model prediction on prepared features
- **Parameters**: Batch size, device selection, confidence thresholds
- **Tools**: CAME-AB model, GPU/CPU inference engine
- **Quality gate**: Predictions must complete without errors, confidence scores available
- **Output**: Raw prediction scores, attention weights, feature representations

### Step 4: Evaluation and Filtering (s04)
- **Operation**: Filter predictions, compute metrics, generate report
- **Parameters**: Binding threshold (default 0.5), minimum cluster size, evaluation metrics
- **Tools**: Metrics computation (AUPRC, F1, MCC), visualization libraries
- **Quality gate**: Results must pass quality checks, metrics within expected ranges
- **Output**: Filtered binding sites, performance report, visualizations

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Modality count | 5 | [1] | Amino acid, BLOSUM, LM, structure, GCN |
| Interface distance | 5 Å | [2] | Binding site definition threshold |
| Default threshold | 0.5 | [1] | Classification threshold for binding prediction |
| Test set split | Independent | [1] | No sequence/structure overlap with training |
| Evaluation metrics | AUPRC, F1, MCC | [1] | Primary performance indicators |

## 边界与分流
- **Missing modalities**: If structure unavailable, use sequence-only features with reduced accuracy
- **Large antigens**: May require chunking or subsampling for memory efficiency
- **Multi-chain antigens**: Process each chain separately, then combine predictions
- **Low-confidence predictions**: Flag for manual review or experimental validation

## 质量检查
- Validate all steps complete successfully with no errors
- Check prediction confidence distribution for anomalies
- Verify binding site clusters are biologically plausible (size, location, composition)
- Confirm metrics meet minimum performance thresholds

## 回退策略
- If model inference fails, check input format and model compatibility
- If features missing, compute fallback features or use alternative models
- If evaluation shows poor performance, retrain or fine-tune model
- For production use, implement automated quality monitoring

## 资源召回建议
- When performing systematic antibody-antigen binding site prediction
- When integrating binding prediction into antibody design pipelines
- When benchmarking multiple prediction methods on same dataset
- Pair with ANARCI for CDR annotation, SAbDab for data, PDB for structures

## 证据来源
[1] Li H, Ma J, Shi Z, et al. CAME-AB: Cross-Modality Attention with Mixture-of-Experts for Antibody Binding Site Prediction. arXiv:2509.06465. 2025.
[2] Jeon W, Kim D. AbFlex: designing antibody complementarity determining regions with flexible CDR definition. Bioinformatics. 2024;40(3):btae122. doi:10.1093/bioinformatics/btae122