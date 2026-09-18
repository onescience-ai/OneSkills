# 抗体反向折叠工作流依赖与预检

## 适用范围
适用于抗体反向折叠任务的工作流规划与执行，确保各阶段依赖关系正确、前置检查完整。涵盖从输入验证到模型推理的全流程依赖管理。

## 输入
- 任务规划文档：planner_proposal.json、global_plan.md。
- 输入文件：antibody_complex.pdb（抗体-抗原复合物结构）。
- 模型权重：ab_if.ckpt或其他反向折叠模型权重。

## 输出
- 工作流执行轨迹：execution-manifest.json，包含s01-s04子阶段状态。
- 前置检查结果：各阶段输入验证报告。
- 风险记录：task_state.json中的risks字段。

## 流程节点
1. **s01阶段：输入验证**
   - 检查antibody_complex.pdb文件完整性和格式。
   - 验证PDB文件包含抗体重链和轻链。
   - 记录输入文件状态（available/missing/corrupted）。

2. **s02阶段：模型权重预检与加载**
   - 检查ab_if.ckpt文件存在性和可读性。
   - 验证权重文件与PDB输入的兼容性。
   - 执行ANARCI编号（若需要）。
   - 加载模型权重并构建条件特征。

3. **s03阶段：反向折叠推理**
   - 使用模型权重对CDR区域进行序列设计。
   - 生成候选抗体序列。
   - 计算序列属性（如结合亲和力预测）。

4. **s04阶段：结果验证与输出**
   - 验证生成序列的结构合理性。
   - 评估序列与原始结构的相似性。
   - 生成最终报告和可视化结果。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| s01输入验证 | PDB解析 | [1] | 使用BioPython或OpenBabel解析PDB文件 |
| s02权重预检 | 文件检查 | [1,2] | 检查文件大小、加载测试、SHA256校验 |
| s02 ANARCI调用 | 编号方案 | [1] | 使用Chothia方案定义CDR区域 |
| s03推理温度 | 0.2 | [1] | 采样温度，控制序列多样性 |
| s04 RMSD阈值 | <2.0 Å | [2] | 生成序列与原始结构的RMSD阈值 |
| 依赖关系 | s01→s02→s03→s04 | [1] | 严格顺序执行，不可跳过 |

## 边界与分流
- **权重缺失**：若s02阶段发现权重文件缺失，应阻断任务并记录风险，而非跳过。
- **ANARCI失败**：若ANARCI编号失败，应尝试替代工具或手动定义CDR区域。
- **PDB格式错误**：若PDB文件格式错误，应使用工具修复或提示用户提供正确文件。
- **计算资源不足**：若模型推理需要GPU但无可用资源，应降级到CPU模式或使用轻量级模型。

## 质量检查
- **前置条件检查**：每个阶段开始前验证所有前置条件是否满足。
- **状态一致性**：确保execution-manifest.json与global_plan.md的步骤描述一致。
- **阻断条件**：明确各阶段的阻断条件（如权重缺失、PDB损坏）。
- **恢复路径**：定义失败时的恢复路径（如重新下载权重、修复PDB文件）。

## 回退策略
- **阶段回退**：若某阶段失败，可回退到前一阶段重新执行。
- **任务终止**：若关键依赖无法满足，应终止任务并记录原因。
- **用户干预**：对于无法自动解决的问题（如权重缺失），应触发用户确认流程。

## 资源召回建议
- 当任务涉及抗体反向折叠工作流规划、执行、调试时，应召回本卡片。
- 配套资源：bio-antibody-inverse-folding-model-weights（模型权重获取）、bio-antibody-inverse-folding-anarci（ANARCI编号工具）。

## 证据来源
[1] Benchmarking inverse folding models for antibody CDR sequence design, Yifan Li et al., PLoS ONE, 2025, DOI: 10.1371/journal.pone.0324566
[2] AntiFold: improved structure-based antibody design using inverse folding, Magnus Haraldson Høie et al., Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae202