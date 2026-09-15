# 化学信息学性质建模 (cheminformatics-property-modeling)

## 任务目标

从 SMILES/SDF 分子输入出发，经结构标准化、描述符/指纹特征化，训练回归或分类模型预测分子性质（溶解度、毒性、ADMET、结合亲和力等），输出经过 scaffold split 验证的预测性能指标。

## 适用范围 / 不适用场景

适用：小分子有机化合物性质预测、ADMET/毒性分类、MoleculeNet 基准复现、基于指纹或描述符的 QSAR 建模、scaffold split 数据划分、虚拟筛选排序。
不适用：蛋白/核酸序列建模、晶体材料带隙预测（需 CGCNN 等专用模型）、分子生成/逆合成、需要 3D 力场精度的自由能计算。

## 实体槽（Entity Slots）

| 槽位 | 说明 | 约束 |
|------|------|------|
| molecular_input | SMILES 字符串或 SDF 文件 | 必须可被 RDKit 解析 |
| target_property | 待预测性质列名 | 回归值为连续量，分类值为 0/1 |
| featurization_method | 特征化方式 | circular-fingerprint / descriptors / graph-convolution |
| model_family | 模型族 | RandomForest / XGBoost / GCN / AttentiveFP / MultitaskRegressor / 迁移学习 |
| split_strategy | 数据划分策略 | scaffold（默认）/ random / stratified / butina |
| evaluation_metric | 评价指标 | 回归: RMSE, MAE; 分类: ROC-AUC, balanced_accuracy, PRC-AUC |

## 输入输出契约

- 输入：含 SMILES 列的 CSV/SDF 文件 + 对应目标性质列；或 MoleculeNet 内置数据集名（Tox21, BBBP, Delaney 等）。
- 中间产物：特征矩阵 X（指纹向量 / 描述符 DataFrame / 分子图）、scaffold 划分的 train/test 集。
- 输出：训练好的模型对象、测试集性能指标、对新分子的预测值数组。
- 格式要求：特征矩阵为 numpy array 或 scipy sparse；目标值归一化由 `NormalizationTransformer(transform_y=True)` 处理。

## 方法路线（可替换）

1. **基线路线**：datamol ECFP4 指纹（`dm.to_fp(mol)`）→ scikit-learn RandomForest → scaffold split 评估。快速、可解释、数据量 <5K 时首选。
2. **描述符路线**：`dm.descriptors.batch_compute_many_descriptors(mols, n_jobs=-1)` → XGBoost/LightGBM → 特征重要性分析。适合需要物理解释的场景。
3. **GNN 路线**：deepchem `GraphConvModel` / `GCNModel` / `AttentiveFPModel` → 端到端学习。需 >10K 样本方优于指纹基线。
4. **迁移学习路线**：ChemBERTa / GROVER / MolFormer 预训练模型 → 小数据微调（5-20 epochs）。适合 <1K 样本或新骨架。

## 操作序列（Operations）

1. **分子加载与标准化**：`dm.to_mol(smiles)` 解析 → `dm.standardize_mol(mol, disconnect_metals=True, normalize=True, reionize=True)` → 过滤 None。
2. **特征计算**：指纹 `dm.to_fp(mol, fp_type="ecfp4")` 或描述符批量计算；deepchem 侧用 `dc.feat.CircularFingerprint()` / `dc.feat.ConvMolFeaturizer()`。
3. **数据集构建**：`dc.data.NumpyDataset(X, y, w, ids)` 或小规模直接用 pandas；大规模用 `dc.data.DiskDataset.from_numpy()`。
4. **数据划分**：`dc.splits.ScaffoldSplitter().train_test_split(dataset)` — 分子任务必须用 scaffold split 防止泄漏。
5. **模型训练**：sklearn `model.fit(X_train, y_train)` 或 deepchem `model.fit(train_dataset, nb_epoch=50)`。
6. **评估与预测**：`dc.metrics.Metric(dc.metrics.roc_auc_score)` 评估；`model.predict(X_test)` 输出预测。

## 验证契约（Validations）

- 必须使用 scaffold split 而非 random split，避免相似分子同时出现在 train/test。
- 回归任务报告 RMSE + MAE；分类任务报告 ROC-AUC + balanced_accuracy（不平衡数据）。
- 检查 `dm.to_mol()` 返回 None 的比例；超过 10% 需排查输入质量或尝试 `dm.fix_mol()`。
- GNN 模型若不如指纹基线，检查：样本量是否 >10K、epochs 是否充足（50-100）、架构选择（AttentiveFP > GCN）。
- 不平衡分类使用 `dc.trans.BalancingTransformer(dataset=train)` 或 `balanced_accuracy_score`。
- 特征归一化：`NormalizationTransformer(transform_y=True, dataset=train)` 对 train 拟合后同时 transform test。

## 资源引用（Resources）

- datamol 文档：https://docs.datamol.io/ （Apache-2.0 许可，版本 0.12.x）
- deepchem 文档：https://deepchem.readthedocs.io/ （MIT 许可，版本 2.8.0，Python 3.7-3.11）
- MoleculeNet 基准数据集：通过 `dc.molnet.load_*()` 系列函数加载。
- 安装：`uv pip install datamol`；`uv pip install 'deepchem[torch]'`（GNN 需先装 PyTorch）。

## 前后置任务（Task Graph）

无强制前后置。可选上游：分子结构准备（SMILES 清洗、3D 构象生成）；可选下游：虚拟筛选、先导化合物优化、ADMET 风险评估报告。

## 缺口与降级（Fallback / Gap）

- Butina 聚类限于 ~1000 分子（全距离矩阵内存瓶颈）→ 大规模改用 `dm.pick_diverse()` 或分层聚类。
- GNN 在小数据集过拟合 → 降级为 RandomForest + ECFP4 指纹，或用 GROVER/ChemBERTa 迁移学习。
- deepchem 导入报 `No module named 'torch'` → 先装 PyTorch CUDA 版再装 `deepchem[torch]` extra；zsh 中需引号包裹。
- Conda + PyTorch 出现 `undefined symbol: iJIT_NotifyEvent` → 执行 `conda install "mkl<2025"` 固定 MKL 版本。
- 远程文件访问失败 → 安装对应 fsspec 后端（`uv pip install s3fs` 或 `gcsfs`）并验证凭据。
