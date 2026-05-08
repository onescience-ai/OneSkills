# New Dataset Workflow

本文件用于补充 `onescience-coder` 在处理“仓库中尚未登记的新数据集”时的最小设计流程。

## 适用场景

- 用户提供新的数据集 README
- 用户提供样例文件或目录结构
- 用户要求把一个未登记数据集接入现有 OneScience 训练流程

## 最小执行步骤

1. 先判断任务是 `datapipe-only` 还是 `full-adaptation`
2. 明确最接近的参考 datapipe 与参考 example
3. 明确新数据集的：
   - 目录结构
   - 样本切分方式
   - 输入输出字段
   - 时间 / 空间 / 变量组织方式
4. 明确是否需要桥接现有训练脚本的 batch 协议
5. 优先保持模型主体和训练主循环不变
6. 先在 datapipe、配置或调用层做最小改动

## 第一轮规格必须输出

- 参考 datapipe
- 参考 example
- 新 datapipe 文件名
- 新 datapipe 类名
- 输入输出结构
- batch 协议
- 最小桥接方案
- 是否需要修改 config / loss / metrics / inference

## 默认命名建议

- 文件名：`<DatasetName>.py`
- 数据集类：`<DatasetName>Dataset`
- 数据管道类：`<DatasetName>Datapipe`

## 约束

- 若用户没有明确要求改主库，优先输出到目标 `case` 目录
- 不要默认直接修改 `onescience/src/`
- 不要在未核对 batch 协议时假设可直接复用已有训练流程
