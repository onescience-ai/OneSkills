# s02 模型权重加载与条件编码

## 输入契约

| 输入项 | 来源 | 格式 | 必填 | 说明 |
|--------|------|------|------|------|
| 模型权重 | 任务prompt或配置 | 文件路径 | 是 | 默认Base_ckpt.pt |
| 固定残基索引 | s01输出 | list[int] | 否 | 默认[10, 25] |
| 对称群 | 任务prompt | str | 否 | 默认C1 |
| 目标长度 | s01输出 | int | 是 | 骨架总长度 |

## 操作步骤

### 步骤1：权重文件验证

1. **文件名核对**：
   - 检查权重文件名是否为标准名称 `Base_ckpt.pt`
   - 若用户提供了其他文件名，记录变更并确认
   - 若未提供文件名，使用默认值 `Base_ckpt.pt`

2. **权重版本识别**：
   | 权重名称 | 文件名 | 适用场景 |
   |----------|--------|----------|
   | 基础权重 | Base_ckpt.pt | 默认功能位点约束生成 |
   | 超电权重 | Supercharge_ckpt.pt | 高电荷蛋白设计 |
   | 对称权重 | Symmetric_ckpt.pt | 对称寡聚体设计 |
   | 全原子权重 | AllAtom_ckpt.pt | 全原子结构生成 |

3. **文件完整性检查**：
   ```python
   import os
   import torch
   
   def validate_checkpoint(checkpoint_path):
       if not os.path.exists(checkpoint_path):
           raise FileNotFoundError(f"权重文件不存在: {checkpoint_path}")
       
       checkpoint = torch.load(checkpoint_path, map_location='cpu')
       
       required_keys = ['model_state_dict', 'config']
       for key in required_keys:
           if key not in checkpoint:
               raise KeyError(f"权重文件缺少必要键: {key}")
       
       return True
   ```

### 步骤2：模型加载

1. **权重加载**：
   ```python
   import torch
   from rfdiffusion.models import RFdiffusion
   
   def load_model(checkpoint_path):
       checkpoint = torch.load(checkpoint_path, map_location='cpu')
       model = RFdiffusion(checkpoint['config'])
       model.load_state_dict(checkpoint['model_state_dict'])
       model.eval()
       return model
   ```

2. **模型配置验证**：
   - 检查模型配置是否与任务匹配
   - 验证模型支持的输入维度

### 步骤3：条件编码

1. **固定残基编码**：
   ```python
   def encode_fixed_positions(fixed_residues, target_length):
       mask = torch.zeros(target_length)
       for res in fixed_residues:
           if 0 <= res < target_length:
               mask[res] = 1.0
       return mask
   ```

2. **对称性编码**：
   ```python
   def encode_symmetry(symmetry_group):
       symmetry_dict = {
           'C1': 1,
           'C2': 2,
           'C3': 3,
           'C4': 4,
           'D2': 2,
           'D3': 3,
           'D4': 4
       }
       return symmetry_dict.get(symmetry_group, 1)
   ```

3. **功能条件编码**：
   - 从基序PDB中提取原子坐标
   - 编码为模型输入特征

### 步骤4：输出生成

**条件特征**：
```json
{
  "fixed_positions_mask": [0, 0, ..., 1, ..., 0],
  "symmetry_code": 1,
  "motif_coordinates": [...]
}
```

**模型加载记录**：
```json
{
  "checkpoint_file": "Base_ckpt.pt",
  "model_version": "1.0",
  "load_status": "success",
  "config": {...}
}
```

## 输出产物

| 产物 | 格式 | 说明 |
|------|------|------|
| 条件特征 | Tensor/JSON | 固定残基掩码、对称性编码 |
| 固定残基掩码 | Tensor | 标记固定位置的掩码向量 |
| 模型加载记录 | JSON | 权重文件名、版本、加载状态 |
| 功能条件 | Tensor | 基序坐标编码 |

## 质量门禁

### 必须通过

- [ ] 权重文件名与标准一致（Base_ckpt.pt）或已记录变更
- [ ] 权重文件完整（无损坏）
- [ ] 模型配置与任务匹配
- [ ] 固定残基索引在目标长度范围内
- [ ] 条件特征无缺失

### 失败处理

| 失败类型 | 处理方式 |
|----------|----------|
| 文件不存在 | 提示用户提供正确文件 |
| 文件损坏 | 要求重新下载权重 |
| 配置不匹配 | 调整模型配置或选择正确权重 |
| 索引越界 | 调整固定残基索引 |

## 回退策略

- 权重文件名不符 → 使用标准名称，记录变更
- 权重文件损坏 → 尝试重新下载或使用备用权重
- 配置不匹配 → 调整模型配置参数

## 边界说明

**本任务负责**：
- 权重文件验证和加载
- 条件特征编码
- 模型加载记录生成

**本任务不负责**：
- 输入文件解析（s01）
- 候选结构生成（s03）
- 结果筛选和评估（s04）

## 证据来源

[1] Watson JL, et al. De novo design of protein structure and function with RFdiffusion. Nature, 2023, 620:1089-1100. DOI: 10.1038/s41586-023-06415-8
