# pipeline_responsibility

该数据处理原语的职责是把材料原子体系数据从“原始结构存储”转为“模型可直接消费的批次化原子数据对象”。它覆盖以下能力：

- 多数据源组织：从一个或多个材料数据集读取 train、val、test 等 split。
- 结构读取：把 ASE 数据库、ASE LMDB、单结构文件或多帧结构文件解析为原子结构对象。
- 样本筛选：按 split、样本数、原子数、元数据条件和随机种子控制样本范围。
- 数据变换：补齐材料势任务所需的 dataset、charge、spin、fixed、cell、stress、sid 等字段。
- 多任务采样：按显式比例、均衡策略、温度策略或权重策略混合不同数据集。
- 批次构造：把变长原子结构拼接为统一 batch，生成 batch 索引、每结构原子数、批量 cell、批量标签等字段。
- 运行加载：把 dataset、batch sampler 和 collate 逻辑组合成可迭代 dataloader。

该原语蒸馏后的主概念是“多数据集装配能力 + 单数据集创建能力 + 结构读取能力 + 数据变换能力 + 批次拼接能力 + 运行加载能力”共同完成材料数据 pipeline。

# pipeline_architecture

``` text
数据处理输入
  数据集配置
    数据集名称
    数据格式
    train / val / test 路径
    字段读取策略
    数据变换策略
    字段映射策略
    采样策略

多数据集装配
  读取每个数据集配置
    -> 按 split 生成单数据集视图
    -> 对每个 split 做样本过滤和采样
    -> 得到多个可索引样本集合
  多数据集合并
    -> 记录每个子数据集长度
    -> 按采样策略计算扩展比例
    -> 将全局样本索引映射回子数据集内部索引

单样本处理
  原始结构存储
    ASE DB / ASE LMDB / ASE-readable 文件
      -> 原子结构对象
      -> 可选原子 tag 修正
      -> 标准 AtomicData
      -> 数据变换
      -> 字段重命名
      -> 单样本输出

批次处理
  多个 AtomicData 样本
    -> 拼接所有原子坐标
    -> 拼接原子序数、固定标记、tags、forces
    -> 堆叠结构级 cell、pbc、energy、stress、charge、spin
    -> 生成 batch: 每个原子所属结构编号
    -> 生成 natoms: 每个结构原子数
    -> 批次 AtomicData

运行时加载
  dataset + batch_sampler + collate
    -> 可迭代 dataloader
    -> 训练、验证、测试或批量推理
```

# data_loading

该 pipeline 将原始数据读取抽象为“结构对象加载能力”，核心行为如下：

- 对数据库型材料数据，按数据源路径连接数据库，枚举可用样本 id，按需读取单条结构记录，并把数据库行中的附加信息合并进结构对象。
- 对普通结构文件，按目录、glob 或索引表枚举文件；单结构读取路径一次返回一个结构，多结构读取路径会把同一文件内的每一帧展开为独立样本。
- 对每个结构样本，先得到原子序数、坐标、晶胞、周期边界条件和附加属性，再根据字段读取策略提取能量、力、应力、电荷、自旋等监督信息。
- 对大规模数据库，样本 id 列表可以来自数据库自身索引；如果没有现成索引，则需要遍历数据库记录生成 id 列表。
- 对 metadata 可用的数据集，读取原子数等元数据，用于后续过滤和 batch 规划。

读取后的样本会进入统一转换流程：

``` text
原始存储记录
  -> 原子结构对象
  -> 原子结构到 AtomicData 的转换
  -> 任务字段补齐
  -> 字段映射
  -> 单样本 AtomicData
```

# sampling_strategy

采样策略分为单数据集内部采样和多数据集合并采样。

单数据集内部采样：

- split 选择：每个数据集可以为 train、val、test 配置不同数据源。
- 原子数过滤：当存在 natoms 元数据时，可剔除超过 `max_atoms` 的结构。
- 元数据过滤：可按指定 metadata 字段执行绝对值小于等于阈值或属于给定集合的筛选。
- 前 N 个样本：用于可复现调试或小规模 smoke test。
- 随机抽样 N 个样本：按随机种子打乱后取样，非训练 split 使用不同 seed 以避免与训练采样完全重合。
- 保序采样：用于已经预先排序或预先划分的数据集。

多数据集合并采样：

- 显式比例采样：每个数据集使用人工指定的扩展比例。
- 均衡采样：小数据集被重复采样，使各数据集等效长度接近最大数据集。
- 温度采样：按数据集规模的温度平滑分布确定采样比例，减弱大数据集支配效应。
- 权重采样：直接使用外部给定的采样权重。

索引行为：

``` text
全局样本索引
  -> 判断属于哪个子数据集
  -> 计算该子数据集内部样本索引
  -> 如果子数据集被扩展采样，对真实样本数取模
  -> 返回对应 AtomicData 样本
```

# data_transform

数据变换的目标是把不同材料数据源整理成 UMA 任务一致的样本协议。主要处理包括：

- 数据集标识补齐：把样本标记为所属 dataset，供多任务、dataset embedding 或任务路由使用。
- 电荷与自旋处理：若通用任务缺失 charge/spin，可补默认 0；若分子任务明确要求电荷和自旋，则必须从数据中读取，不能静默忽略。
- 能量张量化：将能量标签转换为浮点张量，并统一成一维结构级字段。
- 分子大真空盒处理：对非周期分子，重新居中结构并构造足够大的晶胞，使后续模型构图可在统一 cell 语义下运行。
- 固定原子标记：对需要 fixed 字段的任务补全固定标记；对表面/吸附体系则应尽量保留原始固定原子语义。
- 表面/吸附 tags 处理：当结构没有非零 tags 时，可自动补 tag，避免下游模型或构图逻辑无法识别有效原子分组。
- 应力形状规范化：将应力类字段整理为结构级九分量形式，便于 EFS head、loss 和 metric 使用。
- 样本 id 规范化：把结构 id 转为稳定字符串，便于日志、错误追踪和推理输出回写。
- 字段映射：当原始标签名和训练任务字段名不同，将原始字段重命名为任务期望字段。
- 二阶张量分解：对需要不可约表示标签的任务，可将 rank-2 张量拆为不同阶的分量字段。

# input_schema

配置输入应描述以下信息：

- 数据源名称：用于区分不同材料数据域或任务域。
- 数据源格式：数据库、单结构文件、多帧结构文件或其他已注册格式。
- split 路径：train、val、test 对应的文件、目录、glob 或路径列表。
- 字段读取策略：指定是否读取 energy、forces、stress、charge、spin 等字段。
- 数据变换策略：指定需要补齐或改写哪些字段，例如分子处理、应力 reshape、dataset 标识、sid 规范化。
- 字段映射策略：当原始字段名与训练任务字段名不一致时提供映射。
- 采样策略：包括 max_atoms、subset 条件、first_n、sample_n、no_shuffle、多数据集 sampling type 和 ratios。
- 任务统计量：元素参考能量、归一化常数、任务 head 和 loss/metric 所需字段。

原始样本应至少能提供：

- 原子种类或原子序数。
- 原子坐标。
- 晶胞和周期边界条件，周期体系必须准确。
- 能量、力、应力等任务标签，按任务需要提供。
- 分子任务所需电荷与自旋。
- 可选固定原子、表面标记、样本 id、frame id 和其他元数据。

# output_schema

单样本输出是标准原子数据对象，自然语言字段协议如下：

- 原子坐标：二维浮点数组，每行对应一个原子的三维坐标。
- 原子序数：一维整数数组，每个元素对应一个原子的元素编号。
- 晶胞：结构级三乘三浮点矩阵。
- 周期边界条件：结构级布尔标记，描述三个方向是否周期。
- 原子数：结构级整数，记录该样本原子数量。
- 数据集标识：字符串或可编码标识，表示样本所属数据域。
- 电荷与自旋：结构级数值字段，分子任务必须真实提供。
- 固定原子标记：原子级字段，表示哪些原子固定或属于特定物理角色。
- 表面/吸附 tags：原子级整数或类别字段。
- 能量：结构级浮点标签。
- 力：原子级三维向量标签。
- 应力：结构级三乘三或九分量浮点标签，EFS 任务通常使用九分量形式。
- 样本 id：可追踪的字符串标识。

批次输出是在单样本协议上的拼接形式：

``` text
Batch AtomicData
  pos: 所有结构原子坐标拼接
  atomic_numbers: 所有结构原子序数拼接
  batch: 每个原子对应的结构编号
  natoms: 每个结构的原子数
  cell: 每个结构的晶胞堆叠
  pbc: 每个结构的周期边界条件堆叠
  charge / spin: 每个结构的电荷与自旋
  energy: 每个结构的能量标签
  forces: 所有原子的力标签拼接
  stress: 每个结构的应力标签堆叠
```

# constraints

- 数据格式必须与读取策略一致，不能把普通结构文本直接声明成数据库格式。
- 元数据过滤依赖可用元数据；缺少元数据时不能使用原子数或其他 metadata 条件筛选。
- `first_n`、`sample_n`、`no_shuffle` 属于互斥采样控制。
- 多数据集显式采样要求每个子数据集都有对应比例。
- 温度采样要求温度参数不小于 1。
- 分子电荷/自旋任务必须真实提供 charge 和 spin。
- 应力标签必须在 shape、单位和符号上与训练任务一致。
- 元素参考能量和归一化常数必须来自同一数据统计上下文。
- 周期晶胞、PBC、固定原子和 tags 的语义会影响模型构图和物理量预测，不能随意补默认值。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/materials/custom_stack/core/atomic_data.py`
- `{onescience_path}/onescience/src/onescience/datapipes/materials/custom_stack/storage/ase_datasets.py`
- `{onescience_path}/onescience/src/onescience/datapipes/materials/custom_stack/storage/mt_concat_dataset.py`
- `{onescience_path}/onescience/src/onescience/datapipes/materials/custom_stack/collaters/mt_collater.py`
- `{onescience_path}/onescience/src/onescience/datapipes/materials/uma/dataloader_builder.py`
- `{onescience_path}/onescience/src/onescience/datapipes/materials/uma_transforms.py`
- `{onescience_path}/onescience/examples/matchem/uma/configs/uma_sm_finetune_template.yaml`
- `{onescience_path}/onescience/examples/matchem/uma/demo/configs/*.yaml`
