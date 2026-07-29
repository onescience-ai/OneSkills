# 工作流 - 写回 Conda 状态

仅在检测成功、安装成功且验证成功、或 Python 包安装成功且包验证成功后读取本工作流。

## 写回位置

只写 `onescience.json.runtime.conda`。

只更新 `runtime` 下的 `conda` 子字段，不修改 `onescience.json` 的其它信息。

## Conda 环境成功

```json
{
  "runtime": {
    "conda": {
      "enabled": true,
      "env_name": "onescience311",
      "activate_script": "source ~/.bashrc && conda activate onescience311"
    }
  }
}
```

- 将 `onescience311` 替换为实际 `env_name`

## 当前环境或预装包成功

```json
{
  "runtime": {
    "conda": {
      "enabled": false
    }
  }
}
```

## 写回模型路径（增量）

当 `workspace-model-path-discovery.md` 探测到有效的模型或数据集路径，且 `onescience.json.runtime.script.env_vars` 中对应字段为默认值或缺失时，写入：

```json
{
  "runtime": {
    "script": {
      "env_vars": {
        "ONESCIENCE_MODELS_DIR": "<探测到的模型路径>",
        "ONESCIENCE_DATASETS_DIR": "<探测到的数据集路径>"
      }
    }
  }
}
```

- `ONESCIENCE_MODELS_DIR` 默认值为 `/public/share/sugonhpcapp01/onestore/onemodels/`（来自 `onescience.default.json`），仅当现有值等于默认值或缺失时才写入探测值。
- `ONESCIENCE_DATASETS_DIR` 默认值为 `/public/share/sugonhpcapp01/onestore/onedatasets/`（来自 `onescience.default.json`），仅当现有值等于默认值或缺失时才写入探测值。
- 若现有值为非默认值（用户已显式设置），保留，不覆盖。
- 模型路径探测失败不阻断 conda 状态写回。

## 规则

- 保留 `onescience.json` 中无关字段。
- 保持 JSON 合法。
- 安装失败或验证失败后不得写入成功状态。
