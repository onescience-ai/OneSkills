# 蛋白功能预测模型权重文件管理

## 适用范围
蛋白功能预测任务中，模型权重文件的获取、验证与加载流程；适用于使用预训练蛋白质语言模型（如ESM-2、ProstT5）作为特征提取器或backbone的场景。

## 输入
- 模型架构配置文件（含backbone类型、层数、隐藏维度等）
- 目标权重文件路径或HuggingFace模型ID
- 参考数据集（如UniProtKB）用于验证权重版本兼容性

## 输出
- 验证通过的权重文件路径
- 权重参数维度与配置一致性的验证结果
- 备选权重文件列表（如main checkpoint不存在时的fallback）

## 流程节点
1. 权重文件存在性检查 → 验证指定路径下权重文件是否存在
2. 权重版本确认 → 对比权重文件名与模型架构版本
3. 参数维度验证 → 加载权重后验证与模型配置维度匹配
4. 备选方案检索 → 若主权重不存在，检索同系列备选文件

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 权重文件命名模式 | model_best.ckpt, model_final.ckpt, best_model.pth | [1] | 常见checkpoint命名变体 |
| ESM-2模型ID | facebook/esm2_t33_650M_UR50D | [1] | HuggingFace标准路径 |
| 权重文件大小 | 约2.5GB（ESM-2 650M参数） | [1] | 显存需求参考 |
| 参数维度验证方法 | state_dict keys比对 | [1] | 确保权重与架构匹配 |

## 边界与分流
- 若权重文件不存在且无备选 → 记录WARNING并使用替代权重，需在报告中说明
- 若权重维度不匹配 → 停止加载并报错，避免静默使用错误权重
- 若使用替代权重（如annodpo_best.ckpt替代annodpo.ckpt） → 需验证替代权重的适用性

## 质量检查
- 权重加载后验证模型参数维度与配置一致
- 验证权重文件的MD5/SHA256哈希（如可用）
- 对比权重文件日期与模型版本发布时间

## 回退策略
- 主权重不存在时，检索同目录下model_best/model_final等变体
- 若所有checkpoint均不可用，使用随机初始化权重并标注
- 记录权重加载失败的原因和使用替代方案的决策

## 资源召回建议
- 当执行模型训练/推理任务且需要加载预训练权重时召回本卡
- 当发现权重加载失败或使用非标准权重时召回本卡
- 配套资源：bio-esm2-protein-language-model（ESM-2模型详情）

## 证据来源
[1] GOBeacon: An ensemble model for protein function prediction enhanced by contrastive learning, Protein Science, 2025, DOI: 10.1002/pro.70182
[2] GOBoost: leveraging long-tail gene ontology terms for accurate protein function prediction, Bioinformatics, 2025, DOI: 10.1093/bioinformatics/btaf267