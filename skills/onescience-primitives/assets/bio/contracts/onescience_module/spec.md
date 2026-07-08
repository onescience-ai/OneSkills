# component_info

`onescience_module` 是 OneScience 模型基础类组件契约，对应 `Module` 基类。它为继承该类的模型记录可序列化构造参数，提供统一的 checkpoint 打包、加载、从 checkpoint 重建模型、registry 实例化和 torch 模型包装能力。对上述 5 个生信模型的检索中，`medgemma` 直接尝试从 `onescience.modules` 导入 `Module` 并继承该基类，其余 `diffdock`、`genscore`、`laproteina`、`targetdiff` 未在 `modules` 或 `flax_models` 中发现直接依赖。

# purpose

用于给模型原语提供通用生命周期能力：保存模型权重和构造参数、从 `.mdlus` checkpoint 恢复模型、通过 `ModelRegistry` 或模块路径动态实例化、获得模型所在设备、统计可学习参数数量，以及把已有 torch 模型包装成 OneScience `Module`。它适用于需要接入 OneScience 统一模型管理的生信模型，例如 MedGemma；不适合作为蛋白结构预测、分子生成、打分或对接算法的功能组件替代。

# input_schema

```text
Module.__init__:
  meta:
    type: ModelMetaData | None
    default: None
    usage: 存储模型名称、精度、导出、推理和自动微分等静态能力标记

instantiate:
  arg_dict:
    __name__: str
    __module__: str
    __args__: Dict[str, JSON-serializable]

save:
  file_name:
    type: str | None
    constraint: 如果提供，必须以 .mdlus 结尾
  verbose:
    type: bool

load:
  file_name:
    type: str
    constraint: 本地或远端可被 OneScience filesystem 工具解析的 checkpoint 路径
  map_location:
    type: str | torch.device | None
  strict:
    type: bool

from_checkpoint:
  file_name:
    type: str

from_torch:
  torch_model_class:
    type: torch.nn.Module class
  meta:
    type: ModelMetaData | None
```

# output_schema

```text
instantiate:
  Module-compatible model instance

save:
  side effect:
    writes .mdlus tar package containing:
      model.pt
      args.json
      metadata.json

load:
  side effect:
    loads model.pt into current module instance

from_checkpoint:
  Module-compatible model instance restored from checkpoint

from_torch:
  dynamically generated Module subclass

device:
  torch.device

num_parameters:
  int
```

# parameters

- `_file_extension`: 固定为 `.mdlus`，用于保存和加载 OneScience 模型包。
- `__model_checkpoint_version__`: 当前为 `0.1.0`，用于 checkpoint 版本兼容性检查。
- `meta`: `ModelMetaData`，默认名称为 `OnescienceModule`，包含推理、精度、导出和自动微分相关标记。
- `strict`: `load` 中控制 `state_dict` key 是否严格匹配，默认 `True`。
- `map_location`: 控制 checkpoint 权重加载设备，默认使用当前模型的 `device`。
- `verbose`: `save` 中控制是否写入 git hash 等额外元数据。

# key_dependencies

- `module.py`
- `__init__.py`
- `meta.py`
- `model_registry.py`
- `filesystem.py`
- `torch`
- `tarfile`
- `importlib`
- `inspect`

# usage_and_risks

典型使用方式是让模型类继承 `Module`，并保证构造函数参数可以 JSON 序列化；实例创建时 `__new__` 会捕获构造参数，`save` 会将权重、参数和元数据打包成 `.mdlus`，`from_checkpoint` 会解包后通过 `instantiate` 重建模型并加载权重。风险点包括：构造参数中包含不可序列化对象会导致保存或恢复失败；checkpoint 版本不一致会触发兼容性错误；动态 import 依赖 `__module__` 路径稳定；`load` 需要 checkpoint 内含 `args.json`、`metadata.json`、`model.pt`；顶层 `onescience.__init__.py` 会导出 `Module`，但 `medgemma` 当前写法是 `from onescience.modules import Module`，而 `modules/__init__.py` 的懒加载表未导出 `Module`，实际运行前应验证该导入是否可用，必要时改为 `from onescience import Module`、显式导入 `onescience.modules.module.Module`，或补充 `modules/__init__.py` 导出。

# code_references

- `{onescience_path}/onescience/src/onescience/modules`
- `{onescience_path}/onescience/src/onescience`
- `{onescience_path}/onescience/src/onescience/models/medgemma`
- `{onescience_path}/onescience/src/onescience/models`
- `{onescience_path}/onescience/src/onescience/registry`
- `{onescience_path}/onescience/src/onescience/utils`
