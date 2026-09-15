# Step Handoff 示例（四个 domain）

本文档给出 orchestrator 调用本技能时四个 domain 的典型 `step_handoff` 与预期 `execution_result`。所有示例均可直接作为集成测试 fixture。

## 示例 1：climate / ERA5（Tier1，本地已有 raw）

### 输入

```yaml
step_handoff:
  step_id: standardize_era5
  execution_skill: onescience-data-standardizer
  step_goal: 将 ERA5 原始再分析数据转换为 AI-Ready 数据集
  task_context:
    user_goal: 训练全球天气预报模型，需要 AI-Ready ERA5
    dataset_name: ERA5
    domain: climate
    source_dir: /public/share/onestore/onedatasets/ERA5
    target_dir: /home/user/onedata/era5-ai-ready
    allow_download: false
  resource_bindings: []
  inputs: {}
  required_outputs:
    - AI-Ready ERA5 数据集
    - data_management.json 注册项
```

### 预期输出

```yaml
execution_result:
  skill: onescience-data-standardizer
  status: success
  artifacts:
    name: ERA5
    domain: climate
    source_dir: /public/share/onestore/onedatasets/ERA5
    target_dir: /home/user/onedata/era5-ai-ready
    handler: adapter:climate/era5
    dataset_card: /home/user/onedata/era5-ai-ready/dataset_card.json
    registry_path: /home/user/.onescience/data_management.json
    dataset_report_called: true
    dataset_report_payload:
      name: ERA5
      target_dir: /home/user/onedata/era5-ai-ready
      source_dir: /public/share/onestore/onedatasets/ERA5
  observation:
    summary: ERA5 raw NetCDF 已转换为按年 HDF5 + static + stats 结构
    tier: 1
    completed: [resolve_source, fetch_target_spec, select_converter, convert, validate, register, report]
    validation:
      format_valid: true
      required_files_present: [data/, dataset_card.json, README.md, static/, stats/]
      warnings: []
    source_resolution:
      method: explicit
      resolved_path: /public/share/onestore/onedatasets/ERA5
    dataset_report:
      available: true
      probe_method: host_tool
      called: true
    next_recommendation: 可交给下游天气模型训练技能消费；或调用 onescience-dataset-builder 任务2 做二次验证
```

## 示例 2：cfd / DeepCFD（Tier1，需下载）

### 输入

```yaml
step_handoff:
  step_id: standardize_deepcfd
  execution_skill: onescience-data-standardizer
  step_goal: 下载并标准化 DeepCFD 数据集
  task_context:
    user_goal: 复现 DeepCFD 论文，需要 AI-Ready 数据
    dataset_name: DeepCFD
    domain: cfd
    allow_download: true
    modelscope_repo_id: OneScience/DeepCFD
  execution_flags:
    autonomous_mode: true
```

### 预期输出（关键片段）

```yaml
execution_result:
  status: success
  artifacts:
    name: DeepCFD
    domain: cfd
    source_dir: /home/user/.onescience/datasets/DeepCFD/raw
    target_dir: /home/user/.onescience/datasets/DeepCFD-ai-ready
    handler: adapter:cfd/deepcfd
  observation:
    tier: 1
    source_resolution:
      method: modelscope_download
      download_details:
        repo_id: OneScience/DeepCFD
        repo_id_source: explicit
        method: sdk
        bytes_downloaded: 52428800
        files_count: 2
```

## 示例 3：bio / targetdiff（Tier1，本地探测命中）

### 输入

```yaml
step_handoff:
  step_id: standardize_targetdiff
  execution_skill: onescience-data-standardizer
  step_goal: 把 TargetDiff 口袋-配体数据转成 LMDB 图缓存
  task_context:
    user_goal: 训练结构基础生成模型
    dataset_name: targetdiff
    # domain 缺失，由 primitives 命名直查回填
```

### 预期输出（关键片段）

```yaml
execution_result:
  status: success
  artifacts:
    name: targetdiff
    domain: bio
    source_dir: /public/share/onestore/onedatasets/targetdiff/data
    target_dir: /home/user/.onescience/datasets/targetdiff-ai-ready
    handler: adapter:bio/targetdiff
  observation:
    tier: 1
    source_resolution:
      method: local_probe
      probed_paths:
        - {path: /public/share/onestore/onedatasets/targetdiff, hit: true}
```

## 示例 4：matchem / oc20（Tier1，多子集）

### 输入

```yaml
step_handoff:
  step_id: standardize_oc20
  execution_skill: onescience-data-standardizer
  step_goal: 将 OC20 S2EF extxyz 转为 ASE LMDB 分片
  task_context:
    user_goal: UMA 微调
    dataset_name: oc20
    domain: matchem
    source_dir: /public/share/onestore/onedatasets/matchem/oc20
    target_dir: /data/ai-ready/oc20
```

### 预期输出（关键片段）

```yaml
execution_result:
  status: success
  artifacts:
    handler: adapter:matchem/oc20
    target_dir: /data/ai-ready/oc20
  observation:
    tier: 1
    validation:
      format_valid: true
      required_files_present:
        - data/train/data.0000.aselmdb
        - data/val/data.0000.aselmdb
        - dataset_card.json
        - README.md
```

## 示例 5：matchem / dpa3（Tier2，LLM 合成）

### 输入

```yaml
step_handoff:
  step_id: standardize_dpa3
  execution_skill: onescience-data-standardizer
  step_goal: 标准化 DPA3 微调数据
  task_context:
    user_goal: DPA3 势函数微调
    dataset_name: dpa3
    domain: matchem
    source_dir: /public/share/onestore/onedatasets/matchem/dp/dpa3_finetune
```

### 预期输出（关键片段）

```yaml
execution_result:
  status: success
  artifacts:
    handler: llm_synth:v1
    target_dir: /home/user/.onescience/datasets/dpa3-ai-ready
  observation:
    tier: 2
    completed: [resolve_source, fetch_target_spec, probe_raw, synthesize_converter, validate_generated, convert, validate, register, report]
    converter_artifacts:
      script: /home/user/.onescience/datasets/dpa3-ai-ready/_converter/convert_dpa3.py
      prompt_snapshot: /home/user/.onescience/datasets/dpa3-ai-ready/_converter/prompt_snapshot.md
      raw_probe_report: /home/user/.onescience/datasets/dpa3-ai-ready/_converter/raw_probe_report.json
    next_recommendation: 若该数据集被反复使用，建议人工审校 _converter/convert_dpa3.py 后提升为 scripts/adapters/matchem/dpa3.py
```

## 示例 6：阻断 —— raw 未找到且不允许下载

### 输入

```yaml
task_context:
  dataset_name: merra2
  domain: climate
  allow_download: false
```

### 预期输出

```yaml
execution_result:
  status: blocked
  blocked_reason: raw_dataset_not_found
  blocked_details: |
    raw dataset 'merra2' not found locally. Probed paths:
      - ${ONESCIENCE_DATASETS_DIR}/merra2 (env not set)
      - ~/.onescience/datasets/merra2/raw
      - /public/share/onestore/onedatasets/merra2
      - ./merra2
    Suggested ModelScope repo: OneScience/merra2
    To proceed: set allow_download=true, or provide source_dir explicitly.
  artifacts: {}
  observation:
    source_resolution:
      method: none
      probed_paths: [...]
    next_recommendation: 用户确认下载或提供本地路径后重试
```

## 示例 7：阻断 —— primitives spec 缺失

### 输入

```yaml
task_context:
  dataset_name: my_custom_dataset
  domain: cfd
  source_dir: /data/my_custom
```

### 预期输出

```yaml
execution_result:
  status: blocked
  blocked_reason: target_spec_missing
  blocked_details: |
    onescience-primitives returned no matched_resources for keyword='my_custom_dataset' domain='cfd'.
    Cannot proceed without a target schema.
    Options:
      1) Add a primitives card at skills/onescience-primitives/assets/cfd/datasets/my_custom_dataset/
      2) Provide a custom spec via task_context.custom_spec_json
  observation:
    next_recommendation: 先在 primitives 中登记该数据集，或走自定义 spec 分支
```
