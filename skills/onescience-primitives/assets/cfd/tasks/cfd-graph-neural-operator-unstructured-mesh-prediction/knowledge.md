# 图神经算子任意域非结构网格流场预测任务

## 适用范围

本任务卡适用于在任意几何域的非结构网格CFD数据上执行图神经算子（Graph Neural Operator）或MeshGraphNet模型的流场预测任务。任务覆盖从数据接入、预处理、模型训练、推理到评估的完整流程，适用于空气动力学、结构力学、流体-结构耦合等领域的复杂几何流场预测。

## 输入

| 变量 | 类型 | 必填 | 说明 |
|------|------|------|------|
| DATASET_PATH | doc | 是 | 非结构网格CFD数据集路径（HDF5、NetCDF或VTK格式） |
| DATASET_NAME | str | 是 | 数据集名称与版本 |
| DATA_CONTRACT | object | 否 | 变量、单位、网格拓扑定义 |
| MODEL_NAME | str | 是 | 模型名称（Graph Neural Operator或MeshGraphNet） |
| TRAIN_CONFIG | object | 是 | 训练配置（框架、轮数、批大小、学习率等） |

## 输出

| 文件 | 说明 |
|------|------|
| best_checkpoint.pt | 最佳模型权重 |
| train_config.json | 训练配置记录 |
| training_metrics.csv | 训练过程指标 |
| predictions/ | 推理结果目录 |
| evaluation.json | 评估结果 |
| applicability_report.md | 适用域报告 |

## 流程节点

1. **数据接入与契约核验**
   - 读取非结构网格CFD数据集
   - 建立数据清单，核验网格拓扑、变量定义、单位坐标
   - 检查训练测试泄漏
   - 输出：dataset_manifest.json, data_contract.json, data_audit.md

2. **预处理与数据切分**
   - 构建图结构（节点特征、边特征、邻接关系）
   - 按几何或工况切分数据集
   - 归一化或无量纲化处理
   - 输出：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

3. **模型配置与训练**
   - 配置Graph Neural Operator或MeshGraphNet模型
   - 执行消息传递训练
   - 保存最佳检查点
   - 输出：best_checkpoint.pt, train_config.json, training_metrics.csv

4. **批量推理与物理恢复**
   - 加载模型权重进行推理
   - 反归一化恢复物理单位
   - 输出：predictions/, inference_manifest.json

5. **任务验收与适用域判定**
   - 计算统计误差和物理约束指标
   - 执行外推测试
   - 生成适用域报告
   - 输出：evaluation.json, applicability_report.md

## 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 模型类型 | Graph Neural Operator, MeshGraphNet | 核心模型架构 |
| 图构建方式 | 非结构网格 → 图结构 | 节点=网格单元，边=邻接关系 |
| 消息传递轮数 | 10-15 | 控制信息传播范围 |
| 切分策略 | 按几何或工况切分 | 避免数据泄漏 |
| 验收指标 | relative_L2, RMSE, conservation_residual | 统计和物理指标 |

## 边界与分流

- **数据格式不支持**：尝试格式转换或返回BLOCKED
- **网格拓扑异常**：检查网格质量，过滤退化单元
- **训练发散**：降低学习率或增加正则化
- **外推测试失败**：在适用域报告中明确标注域外边界

## 质量检查

| 检查项 | 判据 | 失败处理 |
|--------|------|----------|
| 数据完整性 | 所有变量存在且无NaN | BLOCKED |
| 图构建正确性 | 节点数=网格单元数 | 重新构建 |
| 训练收敛 | 损失函数下降 | 调整超参数 |
| 推理结果 | 无NaN且形状正确 | 重新推理 |

## 回退策略

- 数据格式不支持时，尝试VTK或HDF5转换工具
- 训练发散时，使用学习率调度或早停
- 推理失败时，检查模型兼容性和设备配置

## 资源召回建议

当需要在非结构网格CFD数据上执行图神经算子流场预测时召回本卡。配合场景卡（cfd-graph-neural-operator-arbitrary-domain-unstructured-mesh-flow-scenario）和工作流卡（graph-neural-operator-unstructured-flow-prediction）使用可获得完整执行指南。

## 证据来源
[1] Pfaff et al., "Learning Mesh-Based Simulation with Graph Networks", ICLR 2021, arXiv:2010.03409
[2] Nabian et al., "X-MeshGraphNet: Scalable Multi-Scale Graph Neural Networks for Physics Simulation", arXiv:2411.17164, 2024
[3] Schmöcker et al., "Generalization capabilities of MeshGraphNets to unseen geometries for fluid dynamics", arXiv:2408.06101, 2024