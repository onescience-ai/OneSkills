# 流固耦合逆向设计任务验收与适用域判定

## 适用范围
流固耦合逆向设计的第五步，评估统计误差、关键物理约束、泛化能力和计算收益，产出验收结论和适用域报告。适用于任何需要对流固耦合逆向设计结果进行验收和适用域判定的任务。

## 输入
- 验收指标（{METRICS}）：统计和物理指标
- 相对误差门限（{MAX_RELATIVE_L2}）：测试集放行阈值
- 是否外推测试（{RUN_OOD_TEST}）：测试域外工况

## 输出
- 评估报告（evaluation.json）
- 最差样本（worst_cases.csv）
- 适用域报告（applicability_report.md）
- 验收结论（PASS_REJECT_BLOCKED.txt）

## 流程节点
```
s05 任务验收与适用域判定
  │  1. 按{METRICS}评价s04结果
  │  2. 至少报告逐变量误差、边界误差、守恒或方程残差
  │  3. 报告最差样本和推理成本
  │  4. 使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
  │  5. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域
  │  6. 不得仅凭平均误差宣称工程可用
  │  质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | 统计与物理指标同时报告 | 场景需求书s05 | 不能仅凭平均误差 |
| 最差样本 | 可追溯 | 场景需求书s05 | 需要详细分析 |
| 适用域限制 | 结论中必须包含 | 场景需求书s05 | 域外工况需CFD复核 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对误差门限 | 0.1 | 场景需求书s05 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 外推测试 | 默认true | 场景需求书s05 | |

## 边界与分流
- 未通过验收时输出REJECT并附详细原因
- 域外工况需CFD复核
- 统计指标不达标时REJECT
- 物理约束不满足时REJECT

## 质量检查
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议
- 验收结论明确（PASS/REJECT/BLOCKED）

## 回退策略
- 未通过验收时返回s04调整优化策略
- 适用域不足时扩大训练数据范围
- 物理约束不满足时检查模型物理一致性

## 资源召回建议
- 本卡片为任务级卡片，可被以下需求召回：FSI任务验收、流固耦合适用域判定、任务验收与适用域判定
- 配套工作流卡片：cfd-differentiable-physics-fsi-inverse-design-workflow
- 配套场景卡片：cfd-differentiable-physics-fsi-inverse-design-scenario

## 证据来源
[1] PRDP_ Progressively Refined Differentiable Physics
[2] PETAL_ Physics Emulation Through Averaged Linearizations for Solving Inverse Problems