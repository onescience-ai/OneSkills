# s03 候选结构生成与参数记录

## 输入契约

| 输入项 | 来源 | 格式 | 必填 | 说明 |
|--------|------|------|------|------|
| 模型 | s02输出 | RFdiffusion模型 | 是 | 已加载权重的模型 |
| 条件特征 | s02输出 | Tensor | 是 | 固定残基掩码、对称性编码 |
| 设计数量 | 任务prompt或默认 | int | 是 | 默认64，范围1-5000 |
| 采样温度 | 任务prompt或默认 | float | 否 | 默认0.2，范围0.01-2 |
| 随机种子 | 任务prompt或默认 | int | 否 | 默认17，范围0-2147483647 |

## 操作步骤

### 步骤1：参数验证

1. **设计数量验证**：
   ```python
   def validate_num_designs(num_designs):
       if num_designs < 1:
           raise ValueError("设计数量必须≥1")
       if num_designs > 5000:
           raise ValueError("设计数量不能超过5000")
       if num_designs < 64:
           print(f"警告: 设计数量{num_designs}低于标准64，可能影响筛选效果")
       return True
   ```

2. **采样温度验证**：
   ```python
   def validate_temperature(temperature):
       if temperature < 0.01 or temperature > 2.0:
           raise ValueError("采样温度必须在0.01-2.0范围内")
       return True
   ```

3. **随机种子验证**：
   ```python
   def validate_seed(seed):
       if seed < 0 or seed > 2147483647:
           raise ValueError("随机种子必须在0-2147483647范围内")
       return True
   ```

### 步骤2：生成执行

1. **命令行调用**：
   ```bash
   python scripts/run_inference.py \
       --input_pdb motif_5tpn.pdb \
       --num_designs 64 \
       --temperature 0.2 \
       --random_seed 17 \
       --fixed_residues 10,25 \
       --target_length 256 \
       --output_dir ./output
   ```

2. **API调用**：
   ```python
   import torch
   
   def generate_candidates(model, conditions, num_designs, temperature, seed):
       torch.manual_seed(seed)
       
       candidates = []
       for i in range(num_designs):
           with torch.no_grad():
               candidate = model.sample(
                   conditions=conditions,
                   temperature=temperature
               )
               candidates.append(candidate)
       
       return candidates
   ```

### 步骤3：参数记录

1. **生成日志记录**：
   ```json
   {
     "num_designs_generated": 64,
     "temperature": 0.2,
     "random_seed": 17,
     "timestamp": "2026-09-16T11:44:00Z",
     "input_pdb": "motif_5tpn.pdb",
     "fixed_residues": [10, 25],
     "target_length": 256
   }
   ```

2. **输出文件命名**：
   - 每个候选结构：`{prefix}_{i}.pdb`（i从1开始）
   - 生成日志：`generation_log.json`

### 步骤4：输出验证

1. **候选数量验证**：
   ```python
   def verify_candidate_count(output_dir, expected_count):
       pdb_files = glob.glob(os.path.join(output_dir, "*.pdb"))
       actual_count = len(pdb_files)
       if actual_count != expected_count:
           raise ValueError(f"期望{expected_count}个候选，实际生成{actual_count}个")
       return True
   ```

2. **参数完整性验证**：
   - 检查生成日志是否包含所有必要参数
   - 验证参数值与输入一致

## 输出产物

| 产物 | 格式 | 说明 |
|------|------|------|
| 设计候选 | PDB文件（多个） | 生成的蛋白骨架结构 |
| 采样分数 | JSON | 每个候选的采样分数 |
| 生成日志 | JSON | 包含所有采样参数 |
| 参数记录 | JSON | 温度、种子、数量等 |

## 质量门禁

### 必须通过

- [ ] 生成数量≥64
- [ ] 随机种子已记录
- [ ] 采样温度在合理范围（0.01-2.0）
- [ ] 生成日志完整
- [ ] 固定残基未改变

### 失败处理

| 失败类型 | 处理方式 |
|----------|----------|
| 生成数量不足 | 增加num_designs参数重试 |
| 参数未记录 | 补充记录缺失参数 |
| 固定残基改变 | 检查条件编码，重新生成 |

## 回退策略

- 生成数量不足 → 增加数量参数，重新生成
- 参数记录不完整 → 补充记录缺失参数
- 生成失败 → 检查模型加载和条件编码

## 边界说明

**本任务负责**：
- 生成参数验证和执行
- 候选结构生成
- 参数记录和日志生成

**本任务不负责**：
- 输入文件解析（s01）
- 模型权重加载（s02）
- 结果筛选和评估（s04）

## 证据来源

[1] Watson JL, et al. De novo design of protein structure and function with RFdiffusion. Nature, 2023, 620:1089-1100. DOI: 10.1038/s41586-023-06415-8
