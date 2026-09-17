# Flow Matching 预处理与数据切分

## 适用范围

本任务处理参数条件与流场分布样本的预处理与数据切分，为 Flow matching model 训练准备标准化输入。适用于流匹配概率代理构建流程的第二阶段。核心原则：按物理意义（几何、工况、轨迹）分组切分，杜绝信息泄漏。

## 输入

- 数据契约（data_contract.json，来自阶段 1）
- 切分配置（{SPLIT_CONFIG}，默认 train/val/test = 0.7/0.15/0.15）
- 目标变量列表（{TARGET_FIELDS}）
- 无量纲化标志（{NONDIMENSIONALIZE}，默认 true）

## 输出

- train_manifest.json（训练集清单）
- validation_manifest.json（验证集清单）
- test_manifest.json（测试集清单）
- normalization.json（归一化统计量与可逆变换参数）

## 流程节点

1. 依据数据契约核验变量完整性
2. 执行质控（去噪、异常值处理）
3. 按需执行重采样或图构建
4. 应用掩膜（边界、孔洞等）
5. 计算归一化或无量纲化参数（仅用训练集）
6. 按几何、完整轨迹或物理工况为单位切分
7. 保存变换统计量与可逆变换参数
8. 输出三份切分清单与归一化配置

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | train/val/test |
| 分组依据 | geometry_or_trajectory | [场景需求书] | 按几何或轨迹分组 |
| 随机种子 | 42 | [场景需求书] | 可复现切分 |
| 无量纲化 | true | [场景需求书] | 默认开启 |

## 边界与分流

- 同一轨迹帧被打散：必须重新按轨迹分组，不得使用随机打散
- 变量缺失：返回 BLOCKED，列出缺失变量
- 无量纲化参数泄露（用全量数据计算）：必须仅用训练集重新计算
- 边界与掩膜语义破坏：检查掩膜一致性，必要时回退

## 质量检查

- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏
- 归一化参数可逆（可恢复原始物理量）

## 回退策略

- 切分泄漏：重新按轨迹分组切分
- 归一化参数错误：仅用训练集重新计算
- 掩膜不一致：检查并修复掩膜定义

## 资源召回建议

当用户需要为流匹配概率代理任务进行数据预处理时召回本卡片。前置步骤：cfd-flow-matching-data-intake-contract-validation。后续步骤：cfd-flow-matching-model-training。

## 证据来源

[1] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
[2] 场景需求书 CFD_S092 预处理步骤定义
