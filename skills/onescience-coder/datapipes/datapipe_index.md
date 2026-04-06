# Datapipe Index

## 目标

本文件用于登记当前已补充到 `oneskills` 的数据处理与 `DataLoader` 知识。

它与 `models/`、`contracts/` 的分工不同：

- `models/`
  - 解决整模型结构、输入输出组织、组件链路
- `contracts/`
  - 解决模块如何初始化、`style` 写什么、shape 如何对齐
- `datapipes/`
  - 解决数据如何读取、按什么粒度存储、如何构造样本、如何组织 `DataLoader`

## 建议使用方式

推荐在以下情况优先读取本文件：

1. 用户要求设计数据读取流程或 `DataLoader`
2. 任务涉及年份选择、变量选择、时间窗口切片
3. 任务需要确认原始数据是按年份存储还是按时刻存储
4. 任务需要确认 datapipe 输出给模型的张量格式

推荐检索顺序：

1. 若任务主要是模型结构改造，先看 `models/` 与 `contracts/`
2. 若任务已经涉及数据组织，再看本文件
3. 先读具体 datapipe 卡片
4. 契约仍不足时，再回到 `./onescience/` 中的 datapipe 源码

## 当前已登记 Datapipe

| Datapipe | 数据类型 | 数据组织方式 | 样本粒度 | 主要配置 | 状态 | 文档 |
|---|---|---|---|---|---|---|
| ERA5Datapipe | 全球大气再分析数据 | 每年一个 HDF5 文件 | 连续时间窗样本 | `dataset_dir`, `used_years`, `used_variables`, `input_steps`, `output_steps`, `normalize` | `stable` | `./datapipes/era5.md` |
| CMEMSDatapipe | 全球海洋再分析/预报数据 | 按年份目录、按时刻 HDF5 文件 | 连续时间窗样本 | `data_dir`, `channels`, `train_ratio/val_ratio/test_ratio`, `input_steps`, `output_steps` | `stable` | `./datapipes/cmems.md` |

## Datapipe 层的核心问题

优先用 datapipe 卡片解决下面这些问题：

- 数据按什么粒度存储
- 年份或时间范围如何选择
- 变量名如何映射到通道索引
- 一个训练样本由几个时间步组成
- 返回给模型的张量形状是什么
- 是否包含额外物理量，例如太阳天顶角
- `DataLoader` 在 train / val / test 阶段的行为是什么

## 新增 Datapipe 文档的维护建议

新增 datapipe 时，建议至少完成以下内容：

1. 复制 `./datapipes/TEMPLATE.md`
2. 填写数据目录结构、输入配置、样本构造方式、风险点和源码锚点
3. 在本文件中登记
4. 检查 `README.md`、`task/SKILL.md`、`DEVELOPER_MANUAL.md` 是否需要同步更新
