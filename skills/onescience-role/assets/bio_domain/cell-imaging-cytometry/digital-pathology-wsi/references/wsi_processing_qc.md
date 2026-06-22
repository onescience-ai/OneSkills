# WSI 处理 QC

## 必要元数据

- Slide id、case/patient id、stain、scanner、magnification、MPP、label、batch。
- Tile 坐标需保留 slide level、x/y、tile size 和 tissue fraction。

## 防止数据泄漏

病理图像的训练/验证/测试必须按 patient 或 case 划分。若一个患者有多张 slide 或多个 tile，不能分散到不同 split。

## 常见 QC

- 背景过多、离焦、折叠、气泡、pen mark、坏扫描区域。
- Stain normalization 需要记录 reference slide 和参数，不能改变标签相关形态。
- WSI 文件很大，交接物要说明 tile 缓存、并行读取和失败重试策略。
