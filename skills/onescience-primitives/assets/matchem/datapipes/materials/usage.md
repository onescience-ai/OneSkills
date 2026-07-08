# launch

该原语通常通过配置驱动的训练 pipeline 启动。实际启动时，需要在配置中声明数据源、采样、变换、批次构造和任务统计量，然后由训练程序实例化 dataset 与 dataloader。

CLI 示例：

``` sh
python -m onescience.examples.matchem.uma.demo.main --config-name oc20_ef_4dcu data.dataset_name=oc20 data.elem_refs="[0.0]" data.normalizer_rmsd=1.0 data.train_dataset.dataset_configs.oc20.format=ase_db data.train_dataset.dataset_configs.oc20.splits.train.src="${ONESCIENCE_DATASETS_DIR}/matchem/uma/oc20/train.aselmdb" data.val_dataset.dataset_configs.oc20.format=ase_db data.val_dataset.dataset_configs.oc20.splits.val.src="${ONESCIENCE_DATASETS_DIR}/matchem/uma/oc20/val.aselmdb" trainer.batch_size=2 trainer.num_workers=4
```

Python API 示例：

``` python
from omegaconf import OmegaConf
from onescience.datapipes.materials.custom_stack.storage.mt_concat_dataset import create_concat_dataset
from onescience.datapipes.materials.custom_stack.collaters.mt_collater import MTCollater
from onescience.datapipes.materials.uma.dataloader_builder import get_dataloader

dataset_configs = OmegaConf.create({
    "omat": {
        "format": "ase_db",
        "splits": {
            "train": {
                "src": "${ONESCIENCE_DATASETS_DIR}/matchem/uma/omat/train.aselmdb"
            }
        },
        "a2g_args": {
            "r_energy": True,
            "r_forces": True
        },
        "transforms": {
            "asedb_transform": {
                "dataset_name": "omat"
            }
        }
    }
})

combined_config = {
    "sampling": {
        "type": "explicit",
        "ratios": {
            "omat.train": 1.0
        }
    }
}

dataset = create_concat_dataset(dataset_configs, combined_config)
collate_fn = MTCollater()
dataloader = get_dataloader(
    dataset=dataset,
    batch_sampler_fn=batch_sampler_fn,
    collate_fn=collate_fn,
    num_workers=4,
)
```

# input_schema

使用时需要准备以下输入：

- 数据路径：训练、验证、测试对应的 ASE 数据库、ASE LMDB、结构文件目录、glob 或多帧文件。
- 数据格式声明：说明数据如何被读取，例如数据库型、单结构文件型或多结构文件型。
- 字段读取策略：说明是否从原始结构中读取能量、力、应力、电荷、自旋和其他附加标签。
- split 配置：定义每个数据集的 train、val、test 来源。
- 数据变换配置：声明是否补 dataset 标识、是否处理分子大真空盒、是否要求 charge/spin、是否 reshape stress。
- 字段映射配置：把数据源字段名映射成任务字段名。
- 采样配置：定义 max atoms、样本数、是否打乱、元数据筛选、多数据集采样比例。
- 任务统计量：元素参考能量、归一化常数和与 head/loss 对齐的任务字段。

典型任务输入准备：

- energy-only：数据至少提供结构和能量标签。
- EF：数据提供结构、能量和逐原子力。
- EFS：数据提供结构、能量、逐原子力和应力，并确认应力 shape。
- OMOL/分子：数据必须提供电荷、自旋，或在数据准备阶段明确生成。
- 晶体/表面/吸附：数据必须保留正确 cell、PBC、固定原子和 tags。

# runtime_interfaces

- 多数据集装配接口：接收多个数据集配置和采样配置，返回一个可索引的合并数据集。
- 单数据集创建接口：接收某个数据集的 split 配置，完成格式解析、样本索引、过滤和子集抽样。
- 原子结构读取接口：按样本 id 读取一个原子结构，并返回可转换为标准原子数据对象的结构记录。
- 数据变换接口：对单个标准原子数据对象执行字段补齐、分子处理、应力整理和字段映射。
- 批次拼接接口：把多个变长原子结构样本拼接为一个批次对象。
- 运行加载接口：将合并数据集、批采样策略和批次拼接逻辑组合为可迭代数据加载器。

# main_functions

- `create_concat_dataset`
- `create_dataset`
- `__getitem__`
- `get_atoms`
- `get_metadata`
- `sample_property_metadata`
- `common_transform`
- `omol_transform`
- `stress_reshape_transform`
- `asedb_transform`
- `__call__`
- `get_dataloader`

# execution_resources

- 该数据处理主要消耗 CPU、内存和磁盘 I/O。
- 大规模 ASE 数据库或 LMDB 读取建议使用多 worker、只读访问和稳定的本地存储。
- 若开启内存缓存，应只用于小数据集；大数据集会造成高内存占用。
- 多数据集均衡或温度采样会改变等效 epoch 长度，需要同步调整训练步数。
- 原子数过滤、最大原子 batch 采样和 metadata 策略依赖预先准备好的元数据。
- 分子大真空盒和应力整理会改变样本字段，应在训练前用小 batch 检查 shape、dtype 和物理语义。

# operation_limits

- 不支持把任意文本文件直接当作材料数据库读取。
- 不支持在缺少元数据时执行依赖元数据的过滤。
- 不支持在没有 charge/spin 的情况下直接运行严格分子电荷/自旋任务。
- 不保证自动修复应力单位、符号或坐标系；这些必须由数据准备阶段确认。
- 不应把不同 DFT 设置或不同归一化统计的数据集无说明地混合。
- 不应依赖默认 charge/spin 处理真实带电或自旋体系。
- 若批次内混合周期和非周期体系，必须确认下游构图逻辑是否支持。
