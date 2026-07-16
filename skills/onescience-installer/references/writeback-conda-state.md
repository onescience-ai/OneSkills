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

## 规则

- 保留 `onescience.json` 中无关字段。
- 保持 JSON 合法。
- 安装失败或验证失败后不得写入成功状态。
