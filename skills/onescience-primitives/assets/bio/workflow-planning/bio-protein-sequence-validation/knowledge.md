# 蛋白质序列输入验证

## 适用范围

面向蛋白质结构预测、同源建模、分子对接等任务的输入序列预处理与验证。覆盖 FASTA 格式校验、序列字符合法性、链标识唯一性、多链复合体输入格式检查，适用于 AlphaFold2、OpenFold、ESMFold 等主流预测工具。

## 输入

- FASTA 格式序列文件（单体或多链）
- 序列元数据（蛋白名称、物种、链标识）
- 目标预测工具的输入规范

## 输出

- 标准化输入文件
- 序列验证报告（通过/失败 + 错误详情）
- 实体清单（链标识、序列长度、分子类型）

## 流程节点

### 1. FASTA 格式校验

操作：验证文件格式符合 FASTA 标准

检查项：
- 每条序列以 `>` 开头
- 序列行只包含有效字符
- 无空行或格式异常

工具：正则表达式匹配

质量门禁：格式错误数 = 0

### 2. 序列字符合法性检查

操作：验证序列字符为标准氨基酸编码

有效字符集：
```
ACDEFGHIKLMNPQRSTVWY (标准 20 种)
B (Asx/Asp或Asn)
Z (Glx/Glu或Gln)
X (未知氨基酸)
U (硒代半胱氨酸)
O (吡咯赖氨酸)
```

工具：字符集匹配

质量门禁：非法字符数 = 0

### 3. 链标识唯一性检查

操作：确保多链输入中每条链有唯一标识

检查项：
- 单文件多序列：自动分配链标识 A, B, C...
- 多文件输入：文件名作为链标识
- 链标识不重复

工具：链标识解析器

质量门禁：链标识唯一性验证通过

### 4. 序列长度验证

操作：检查序列长度在模型支持范围内

参数：
- 最小长度：通常 ≥10 残基
- 最大长度：取决于 GPU 显存（参考 `general-gpu-compute-requirements`）
- 多聚体总长度：需考虑复合体总残基数

工具：长度计算

质量门禁：序列长度在允许范围内

### 5. 实体清单生成

操作：生成标准化输入和实体清单

输出格式：
```yaml
entities:
  - chain_id: A
    sequence: "MKTLLIAA..."
    length: 234
    molecule_type: protein
  - chain_id: B
    sequence: "GIVEQCCTS..."
    length: 51
    molecule_type: protein
```

工具：清单生成器

质量门禁：清单完整，无遗漏链

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 有效氨基酸字符 | ACDEFGHIKLMNPQRSTVWYBXZUO | [D1] | 标准 + 扩展 |
| FASTA 头行格式 | `>identifier description` | [D1] | identifier 必填 |
| 链标识格式 | 单字母（A-Z）或字符串 | [D1] | 唯一即可 |
| 最小序列长度 | ≥10 残基 | [D1] | 推荐值 |

### 校准数值

以下数值来自 OpenFold 实践，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| OpenFold 输入格式 | FASTA 目录 | [D1] | 每文件一序列 |
| 模板目录要求 | MMCIF 文件 | [D1] | 即使无模板也需提供 |
| 多聚体输入 | 多序列 FASTA | [D1] | 自动识别为复合体 |

## 边界与分流

- **前提 1**：输入为标准 FASTA 格式 → 否则需格式转换
- **前提 2**：序列字符合法 → 否则需清理或过滤
- **前提 3**：链标识唯一 → 否则需重新分配标识
- **前提 4**：序列长度在模型范围内 → 否则需截断或分段

## 质量检查

| 验证点 | 阈值 | 失败处理 |
|--------|------|----------|
| FASTA 格式正确 | 0 错误 | 修复格式问题 |
| 序列字符合法 | 0 非法字符 | 过滤或替换非法字符 |
| 链标识唯一 | 0 重复 | 重新分配链标识 |
| 序列长度有效 | 在模型范围内 | 截断或报错 |

## 回退策略

1. 格式错误 → 自动修复常见格式问题（如缺失换行符）
2. 非法字符 → 替换为 X（未知氨基酸）
3. 链标识重复 → 自动分配新标识
4. 序列过长 → 启用长序列模式或分段处理

## 资源召回建议

- 当任务开始时召回本卡执行输入验证
- 当执行日志显示输入格式错误时召回本卡
- 配套资源：`bio-openfold-ablation-workflow`（OpenFold 工作流）

## 补充证据

[D1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html (accessed_at, 官方文档)

## 证据来源

[1] OpenFold Inference Documentation, OpenFold Team, 2024, URL: https://openfold.readthedocs.io/en/latest/Inference.html
[2] FASTA Format Specification, NCBI, URL: https://www.ncbi.nlm.nih.gov/genbank/fastaformat/
