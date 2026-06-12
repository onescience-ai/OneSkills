# Earth System Domain Knowledge

| 字段 | 摘要 |
| --- | --- |
| 适用领域 | 气象、海洋、气候和地球系统论文。 |
| 召回信号 | weather、climate、ocean、atmosphere、forecast、reanalysis、grid、lead time、rollout、climatology、pressure-level、surface variables。 |
| 核心用途 | 提示变量/层级/网格/forcing/static/lead time/气候态/评估指标等字段的提取与审计。 |
| 注意事项 | 只作为检查清单；只有论文或用户材料出现的内容才能写成确定要求。 |

用于气象、海洋、气候和地球系统论文的提取提示。这里只提供检查清单，不提供论文事实。

## 常见数据对象

- pressure-level / height-level / surface / static / forcing / target-only variables。
- 经纬度网格、reduced Gaussian grid、cubed sphere、icosahedral grid、非结构网格。
- lead time、forecast range、rollout、hindcast、nowcast、climatology。

## 提取时重点检查

- pressure-level 变量必须拆清变量名、层数和通道数。
- surface、forcing、static、output-only 变量要分组记录，避免变量数和 scalar channel 数混用。
- 训练 rollout horizon、推理 horizon、评估 lead time 分开记录。
- 面积权重、气候态、ACC/RMSE、区域/层级/变量平均方式要标注证据。
- 非均匀网格的面积权重优先查论文或数据协议；没有证据时写 `ASSUMPTION:`。

## 常见评估提示

- RMSE、MAE、ACC、CRPS、spread/skill。
- lead-time curves、regional scores、vertical-level scores。
- extreme events、precipitation、tropical cyclone、storm track、energy spectrum。
- operational baseline、reanalysis baseline、climatology baseline。

只有论文实际出现或用户材料提供的指标才能写成确定评估要求。
