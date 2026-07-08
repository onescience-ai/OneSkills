# launch
Python API 示例：

``` python
from onescience.modules.head.uma_head import MLP_Energy_Head

head = MLP_Energy_Head(backbone=backbone, reduce="sum")
outputs = head(data_dict=batch, emb={"node_embedding": node_embedding})
```

Hydra/训练入口中通常通过 class path 或 registry 配置，命令示例：

``` sh
python examples/matchem/uma/train.py --config-name=uma_finetune --data.heads.energy._target_=onescience.modules.head.uma_head.MLP_Energy_Head --data.heads.energy.reduce=sum --tasks.energy.property=energy --tasks.energy.loss_fn=mae --trainer.max_epochs=10 --optim.batch_size=2 --model.backbone.regress_forces=true --model.backbone.regress_stress=false
```

# input_schema
运行输入组织：

backbone 输出
  node_embedding: (NumAtoms, SphFeatureSize, SphereChannels)
    l=0 分量
      -> energy head
    l=1 分量
      -> direct force head
    l=2 分量
      -> stress anisotropic part

batch 字段
  batch: (NumAtoms,)
    -> 原子到构型聚合
  natoms: (NumGraphs,)
    -> sum/mean reduce
  pos / pos_original
    -> gradient forces
  cell + displacement
    -> stress
  dataset
    -> dataset-specific wrapper

# runtime_interfaces
- `MLP_EFS_Head.forward(data, emb)`：输出能量，并可通过梯度输出 forces/stress。
- `MLP_Energy_Head.forward(data_dict, emb)`：MLP 能量读出。
- `Linear_Energy_Head.forward(data_dict, emb)`：线性能量读出。
- `Linear_Force_Head.forward(data_dict, emb)`：直接力读出。
- `MLP_Stress_Head.forward(data_dict, emb)`：应力读出。
- `DatasetSpecificMoEWrapper.forward(data, emb)`：按 dataset 路由 MoE head 输出。
- `DatasetSpecificSingleHeadWrapper.forward(data, emb)`：按 dataset 生成专用输出 key。
- `compose_tensor(trace, l2_symmetric)`：由 trace 和 l=2 对称分量组成 rank-2 stress 张量。

# main_functions
- `forward`
- `compose_tensor`

# execution_resources
- head 计算通常轻于 backbone，但 gradient-based EFS head 会触发额外 autograd。
- direct force head 更省导数开销，但需 backbone 学到矢量力表示。
- dataset-specific MoE wrapper 会增加线性层替换和专家混合开销。
- 模型并行环境下需要 `gp_utils` 归约或 gather。

# operation_limits
- `emb["node_embedding"]` 的球谐布局必须与 head 假设一致。
- gradient-based forces 要求 `data["pos"]` 在 forward 中可求导。
- stress 输出格式必须与 UMA loss/task 配置一致。
- dataset 名称缺失或不在 `dataset_names` 中会导致 wrapper 报错。
- `wrap_property=False` 时 loss/metric 必须读取裸 tensor。
