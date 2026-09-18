# PyTorch模型保存与加载规范

## 适用范围

面向使用PyTorch框架的深度学习模型训练与推理任务，定义模型保存与加载的标准规范。适用于科学计算、网格优化、物理场预测等需要持久化模型权重的场景。本卡规定了checkpoint格式、state_dict使用方法和跨设备加载策略。

## 输入

- 训练完成的PyTorch模型（torch.nn.Module）
- 优化器状态（torch.optim.Optimizer）
- 训练元信息（epoch、loss等）

## 输出

- 标准化的checkpoint文件（.pt或.pth格式）
- 可复现的模型加载接口
- 跨设备兼容的权重文件

## 流程节点

1. **模型准备** → 确保模型处于正确状态（eval/train）
2. **state_dict提取** → 获取模型参数字典
3. **checkpoint组织** → 组装模型、优化器、元信息
4. **序列化保存** → 使用torch.save写入磁盘
5. **反序列化加载** → 使用torch.load读取文件
6. **模型恢复** → 加载state_dict到新模型实例

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 保存函数 | torch.save() | [D1] | PyTorch官方推荐 |
| 加载函数 | torch.load() | [D1] | 支持设备映射 |
| 推荐格式 | .pt或.pth | [D1] | PyTorch约定 |
| checkpoint格式 | .tar | [D1] | 多组件保存 |
| state_dict访问 | model.state_dict() | [D1] | 参数字典 |
| 加载方法 | model.load_state_dict() | [D1] | 参数恢复 |

### 校准数值（体系专属）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| weights_only参数 | True（推荐） | [D1] | 安全加载 |
| map_location参数 | 视设备而定 | [D1] | 跨设备加载 |
| strict参数 | True/False | [D1] | 部分加载控制 |

## 边界与分流

- 使用numpy格式保存（.npz）：不符合工作流契约，需转换为.pt格式
- 缺少model类定义：无法使用torch.save(model)方式，必须使用state_dict
- 跨设备加载失败：使用map_location参数指定目标设备
- 部分权重缺失：设置strict=False忽略不匹配的key

## 质量检查

- 验证checkpoint文件可被torch.load正确解析
- 检查state_dict中的key与模型结构匹配
- 验证权重形状与模型层参数一致
- 测试加载后模型可正常执行推理
- 检查文件扩展名是否为.pt/.pth/.tar

## 回退策略

- state_dict加载失败：尝试使用torch.load(model)加载完整模型
- 跨设备问题：使用map_location='cpu'或'map_location=device'
- 格式不兼容：使用旧格式参数_use_new_zipfile_serialization=False

## 资源召回建议

- 当任务涉及PyTorch模型训练、checkpoint保存、模型推理时召回本卡
- 配套资源：cfd-adaptive-mesh-data-contract（数据格式）、cfd-training-early-stopping-strategy（训练策略）

## 补充证据

[D1] Saving and Loading Models, PyTorch Contributors, 2023, URL: https://pytorch.org/tutorials/beginner/saving_loading_models.html（accessed_at: 2026-09-17，权威文档）

[D2] PyTorch Serialization Notes, PyTorch, v2.14, URL: https://pytorch.org/docs/stable/notes/serialization.html（accessed_at: 2026-09-17，权威文档）

## 证据来源

[1] PyTorch官方教程 - Saving and Loading Models, PyTorch Contributors, 2023, DOI: N/A