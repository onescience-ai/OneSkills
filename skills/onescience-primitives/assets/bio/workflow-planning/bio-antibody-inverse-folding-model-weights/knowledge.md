# 抗体反向折叠模型权重获取与验证

## 适用范围
适用于需要获取抗体反向折叠模型权重文件的场景，包括但不限于：亲和力优化的结构感知抗体反向折叠、抗体CDR序列设计、抗体-抗原结合亲和力预测等任务。适用于使用AntiFold、ESM-IF、ProteinMPNN、LM-Design、IgBert、IgT5等模型的场景。

## 输入
- 抗体结构文件：PDB格式的抗体可变域结构（如antibody_complex.pdb）。
- 模型名称：指定要使用的反向折叠模型（如AntiFold、ESM-IF等）。

## 输出
- 模型权重文件：.ckpt、.pt、.bin等格式的检查点文件。
- 权重来源信息：下载URL、仓库地址、许可证信息。
- 验证结果：文件完整性校验（如SHA256）、加载测试结果。

## 流程节点
1. **模型选择**：根据任务需求选择合适的反向折叠模型。
2. **权重检索**：从公开来源检索模型权重文件。
3. **下载权重**：使用wget、curl或git克隆下载权重文件。
4. **完整性验证**：检查文件大小、SHA256校验和、加载测试。
5. **兼容性检查**：验证权重文件与PDB输入文件的版本对应关系。
6. **备选方案**：若无公开权重，评估替代模型或触发用户确认流程。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AntiFold权重 | GitHub仓库 | [1] | https://github.com/oxpig/AntiFold，BSD 3-Clause许可证 |
| ESM-IF权重 | HuggingFace | [2] | https://github.com/facebookresearch/esm，MIT许可证 |
| ProteinMPNN权重 | GitHub仓库 | [2] | https://github.com/dauparas/ProteinMPNN，MIT许可证 |
| LM-Design权重 | GitHub仓库 | [2] | https://github.com/lucahorta/LM-Design，MIT许可证 |
| IgBert/IgT5权重 | Zenodo | [3] | https://doi.org/10.5281/zenodo.10876909，CC-BY-4.0许可证 |
| 权重文件大小 | 100MB-1GB | [1,2,3] | 取决于模型架构和训练数据 |
| 输入PDB格式 | PDB 2.x/3.x | [1,2] | 抗体可变域结构，需包含重链和轻链 |

## 边界与分流
- **无公开权重**：若模型权重未公开发布，应在task_state.json的risks中记录“需要用户提供权重”并触发用户确认流程。
- **许可证限制**：某些权重可能受许可证限制（如仅限学术使用），需在任务规划阶段明确。
- **版本不匹配**：权重文件版本与PDB输入文件不兼容时，需降级或升级权重版本。
- **下载失败**：网络问题导致下载失败时，可尝试镜像源或代理。

## 质量检查
- **文件完整性**：下载后检查文件大小是否与预期相符（如AntiFold权重约500MB）。
- **SHA256校验**：使用sha256sum命令验证文件哈希值。
- **加载测试**：使用Python加载权重文件，确认无报错。
- **兼容性测试**：使用权重文件对测试PDB进行推理，确认输出合理。

## 回退策略
- **替代模型**：若目标模型权重不可用，可使用功能相似的替代模型（如用AntiFold替代ab_if.ckpt）。
- **本地训练**：若有训练数据和计算资源，可从头训练模型。
- **用户提供的权重**：若无公开权重，提示用户提供权重文件路径。

## 资源召回建议
- 当任务涉及抗体反向折叠、CDR设计、亲和力优化时，应召回本卡片。
- 配套资源：bio-antibody-inverse-folding-anarci（ANARCI编号工具）、bio-antibody-inverse-folding-workflow-dependencies（工作流依赖管理）。

## 证据来源
[1] AntiFold: improved structure-based antibody design using inverse folding, Magnus Haraldson Høie et al., Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae202
[2] Benchmarking inverse folding models for antibody CDR sequence design, Yifan Li et al., PLoS ONE, 2025, DOI: 10.1371/journal.pone.0324566
[3] Large scale paired antibody language models, Henry Kenlay et al., PLoS Computational Biology, 2024, DOI: 10.1371/journal.pcbi.1012646