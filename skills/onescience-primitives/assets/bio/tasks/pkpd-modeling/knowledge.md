# 药代动力学/药效动力学建模 (pkpd-modeling)

## 任务目标
从浓度-时间数据推导暴露指标、拟合结构模型、构建或审查群体 PK、评估给药方案与达标率、刻画暴露-效应、比较制剂、缩放到新人群；九个 Python 脚本仅报告数字与 findings，不下临床结论。技能存在意义在于防止十类常见误用（λz 用普通 r² 挑、AUCinf 外推占比过高、AIC 单独选房室、BLQ 留在 DV、2x2 上做参考标度 BE、新生儿缺成熟度项等）。

## 适用范围 / 不适用场景
适用：NCA、房室拟合与模型选择、群体 PK 数据集审查、方案模拟与达标率、暴露-效应（Emax/C-QTc 筛查）、生物等效性（ABE/ABEL/RSABE 与样本量）、异速缩放与首次人体（MRSD/MABEL）、ICH M12 静态 DDI、MAP Bayesian TDM。
不适用：不做 BE 判定、不为试验选剂量、不为患者推荐剂量、不下"无 QT 风险"结论、不替代合格药理计量师/临床药理学家/监管审查；`tdm_bayes.py` 仅为建模辅助，改方案是主治临床的决定；Python 端不重实现 NLME，估算交给 NONMEM/Monolix/nlmixr2/Pharmpy 等外部工具。

## 实体槽（Entity Slots）
- slot:analysis_type:nca / compartmental / popk-check / simulate / er / be / allometry / ddi / tdm
- slot:route:iv-bolus / extravascular
- slot:auc_method:linup-logdown（默认）
- slot:weighting:1-over-y2（默认，恒定 CV；同质方差 PD 不适用）
- slot:be_design:2x2 / replicate
- slot:be_scaling:abe / abel / rsabe / both（`--scaling` 在 2x2 上拒跑）
- slot:format:table / tsv / json

## 输入输出契约
输入：CSV 数据（`profile.csv`、`nmdata.csv`、`er.csv`、`qt.csv`、`be.csv` 等）；关键选择走命令行参数：`--dose`、`--route`、`--auc-method`、`--blq-rule`、`--lambda-z-points` 或 `--lambda-z-window`、`--partial-auc`、`--compare`、`--covariates`、`--time-varying`、`--design`、`--metric`、`--scaling`、`--simulate`、`--omega-cl`、`--omega-v`、`--target-trough`、`--pma-weeks`、`--noael`、`--safety-factor`、`--ki/--imax/--fu/--fm/--fg`、`--level conc@time`、`--target-auc24` 等。
输出：所有脚本支持 `--format table|tsv|json`；数据到 stdout，provenance 与 findings 到 stderr，`> out.tsv` 可分离；退出码 0=无发现，1=有 findings，2=输入错误，可直接作工作流闸门。

## 方法路线（可替换）
- 结构模型：`fit_compartmental.py --compare 1cmt,2cmt,3cmt`，同时看 AIC / BIC / F 检验、RSE 与参数间相关性；参数在 log 尺度估计（不为负、CI 非对称），权重默认 `1/y2`。
- 群体 PK：`check_popk_dataset.py` 只做数据集审查；NLME 估算走 NONMEM 7.6（新增 ADVAN16/17、NUTS、SAEM 存个体样本）/ nlmixr2（要求 rxode2 ≥ 5.0.0，配 babelmixr2、monolix2rx 翻译）/ Pharmpy 2.1.1（19 个 `run_*`：`run_amd`、`run_modelsearch`、`run_covsearch`、`run_structsearch`、`run_pdsearch`、`run_modelrank`、`run_vpc`、`run_qa`）/ Monolix；细节见 `references/population-pk.md`（含 BLQ M1–M7、协变量建模、VPC 与可接受性诊断）。
- 方案模拟：`simulate_regimen.py`；线性模型解析求解并叠加（精确），`--nonlinear` 切集成米氏消除后叠加不再成立、多剂行为不能从单剂推。
- 暴露-效应：`exposure_response.py --emax --sigmoid`（Emax/EC50，报 `fraction_of_emax_reached` 并在平台超出数据时 flag）；`--cqtc --cmax 250` 用**双侧 90% CI 上界**对 10 ms 阈值（ICH E14 真问题），内置为普通线性回归用于筛查，提交级需带随机截距与斜率的混合模型。
- 生物等效性：`bioequivalence.py --design 2x2 --metric AUC` 走 ABE（90% CI 落在 80.00–125.00%）；`--design replicate --scaling both` 走 EMA ABEL（按 CVwR 放宽，上限 69.84–143.19%，点估计仍在 80–125%）与 FDA RSABE（Hyslop 线性化界，非区间）；样本量 `--power --cv 0.30 --gmr 0.95 --target-power 0.80`，按估计标准差的抽样分布积分而非把 SE 当已知。
- 缩放与 FIH：`allometry_and_fih.py --scale --cl --weight-from --weight-to --pma-weeks` 走 CL 指数 0.75、V 指数 1，`--pma-weeks` 触发 Anderson-Holford 成熟度项（V 不成熟化）；`--fih --noael rat=,dog= --safety-factor 10` 走 FDA 2005 BSA 转换，同时始终提示激动性免疫调节剂需用 `--mabel` 计算 MABEL 并取较低值。
- DDI：`ddi_static.py --basic --ki --imax --fu --dose` 或 `--msm ... --fm --fg`；ICH M12 cutoff：R1 ≥ 1.02（肝）、≥ 11（肠）、R2 ≥ 1.25（TDI）、R3 ≤ 0.8（诱导），转运体按部位；basic 结果保守（阴性有意义、阳性只是触发进一步工作，不是量级预测），MSM 会同时报 ceiling（fm=0.9 时受害药 AUC 上限 10 倍）。
- TDM：`tdm_bayes.py --model vancomycin-adult --weight --crcl --dose --interval --level 18.2@11.5 --level 42@2 --target-auc24 500`；MAP Bayesian 数据信息足时跟随数据、不足时向群体先验收缩，优于"单谷浓度对群体参数"或"两点 log-线性回归"。

## 操作序列（Operations）
1. `cd skills/pkpd-modeling/scripts`；开工前先固定暴露指标（AUC(0-t)/AUC(0-inf)/AUC(0-tau)/Cavg、`auc_inf_obs` vs `auc_inf_pred`）与分析人群，看到数字后再改答案就是把阴性做成阳性。
2. NCA：`python3 nca.py -i profile.csv --dose 100 --route extravascular --partial-auc 0-24`；λz 从最后 3 个可定量点起向前扩，仅当**校正** r² 提升 >0.0001 才保留更长窗；Tmax 及之前的点永不入选（含 Tmax 会把吸收尾拟进来，压低 t½、Vz、AUCinf）。
3. 房室拟合：`python3 fit_compartmental.py -i profile.csv --dose 500 --route iv-bolus --compare 1cmt,2cmt,3cmt`；把结构、变异、协变量当三件事诊断，别用加房室吸收未建模的 BOV，别用加协变量掩盖错设的吸收。
4. 群体 PK 前检查：`python3 check_popk_dataset.py -i nmdata.csv --covariates WT,CRCL --time-varying WT`；重点抓沉默缺陷。
5. 方案模拟：`python3 simulate_regimen.py --cl 5 --v 40 --dose 500 --interval 12 --n-doses 10 --steady-state`；再叠 `--simulate 2000 --omega-cl 0.35 --omega-v 0.25 --target-trough 4.0` 看 p5/p25/median/p75/p95、几何均值与 `fraction_attaining`。
6. ER：`python3 exposure_response.py --emax -i er.csv --sigmoid` 或 `--cqtc -i qt.csv --cmax 250`；跨分位数 ER 仍是观察性（患者按剂量随机不按暴露随机），可能反映清除率协变量。
7. BE：2x2 只跑 ABE；`--scaling` 需 `--design replicate`；样本量假设 GMR 比 CV 主导，把 GMR 从 0.95 改到 1.00 会让 N 大约减半，是欠功效的常见原因。
8. 缩放：`--pma-weeks` 提供成熟度项；<20 kg 未提供会 raise finding；FIH：NOAEL 派生的 MRSD 对激动性免疫调节剂不充分，须再算 MABEL 取小。
9. DDI：`ddi_static.py --basic ...` 出 R1/R2/R3；`--msm ... --fm 0.9 --fg 0.7` 出机理静态预测与 ceiling。
10. TDM：多点浓度才够；单点会 raise finding（无法分离 CL 与 V）；内置 vancomycin 参数化明确标为示例，须换本人群验证过的模型才有意义。

## 验证契约（Validations）
- 收敛 ≠ 可识别：RSE 200% 或两参数相关 0.99 说明数据无法分离，脚本会 flag；只看参数表在这种情况下"看着挺好"。
- AIC 单独不够：AIC 每参数只罚 2，样本小时会挑过参数化模型（源示例中 3cmt 被 AIC 选中，但 BIC 与 F 检验都拒绝），须联看 BIC/F 并检查 `Q3 98% RSE`、`V3 71% RSE` 这类 finding。
- 残差诊断：符号非随机（runs test p=0.0036）→ **结构错设**，重新加权无效；符号随机但异方差 → **权重错**；两者混同会掩盖问题。
- NCA findings：`pct_auc_extrap` 高于 20%（示例 25.2%）说明 AUCinf 由 λz 拟合而非数据驱动；`lambda_z 窗口跨 <2.0 半衰期`（示例 0.58）说明末端相可能未达；稳态下应报 AUC(0-tau) 而非 AUCinf（脚本仍会算 AUCinf 并提示别信）。
- NCA 系统偏差：无噪声一室口服模拟（CL/F=5, V/F=20, ka=1.2）中 CL/F 高估约 0.6%，是梯形法则在稀疏吸收相的不可约偏差，也是 NCA 与房室 CL 估计不会完全一致的原因。
- ER：`fraction_of_emax_reached` 低（示例最高暴露只到 Emax 的 1/3）时 Emax 与 EC50 是外推且强相关，不可当独立估计报；此时"线性 ER"只是同一曲线的低浓度肢。
- C-QTc：必须用双侧 90% CI 上界对 10 ms，点估计或 95% CI 都答错问题。
- 数据集沉默缺陷：NM-TRAN 不拒绝非数值 DV，把 `BLQ` 读成 0 浓度；空白协变量变 0（0 kg 患者）；`ADDL` 缺 `II` 不加剂；同 timestamp 记录按文件顺序执行，前后剂取决于行序；`check_popk_dataset.py` 会出 error/warning。
- 缩放：新生儿只用体重外推会把 CL 高估数倍，因清除受酶/肾成熟限制而非体型；示例中体重项给 0.79 L/h，加 44 周 PMA 成熟度后降到 0.24 L/h（3.3 倍差），V 不成熟化。
- MSM ceiling：`fm=0.9` 时无抑制剂的受害药 AUC 上限 10 倍；预测接近 ceiling 说明 fm 出力大于抑制常数；fm 与 Fg 主导答案但常是最不确定的输入。
- TDM：单个 level 会 raise finding（无法分离 CL 与 V）；模型输出仅在本人群验证过的参数化下才有意义。

## 资源引用（Resources）
- 脚本（`skills/pkpd-modeling/scripts`）：`nca.py`、`fit_compartmental.py`、`simulate_regimen.py`、`check_popk_dataset.py`、`exposure_response.py`、`bioequivalence.py`、`allometry_and_fih.py`、`ddi_static.py`、`tdm_bayes.py`。
- 私有共享模块：`_models.py`（线性 mammillary 解析解 + 集成米氏、TMDD、间接反应结构）、`_common.py`（I/O 与报告）；写新脚本请 import 而不是重推 Bateman。
- 参考：`references/nca-conventions.md`、`structural-models.md`（含 NONMEM ADVAN/TRANS 映射）、`population-pk.md`、`pd-and-exposure-response.md`、`tmdd-and-biologics.md`、`pbpk.md`、`bioequivalence.md`、`special-populations.md`、`dataset-standards.md`（CDISC PC/PP、ADPC/ADPP、NONMEM 数据项）、`ddi-and-qt.md`（ICH M12、E14/S7B）、`antimicrobial-and-tdm.md`（PK/PD 指数、PTA/CFR、万古霉素 AUC 引导、MIPD）、`software-ecosystem.md`、`regulatory-guidance.md`、`source-ledger.md`。
- 资产：`assets/popk-analysis-plan.md`、`assets/nca-reporting-checklist.md`。

## 前后置任务（Task Graph）
无强制前后置。常见内部顺序：NCA → 房室拟合与模型选择 → 群体 PK 数据集检查 → 群体估算（外部 NONMEM/nlmixr2/Pharmpy/Monolix，非本技能）→ 方案模拟与达标率 → 暴露-效应 / 生物等效性 / 缩放与 FIH / DDI / TDM 视问题选用；退出码 0/1/2 可作为工作流闸门串联。

## 缺口与降级（Fallback / Gap）
- Python 端无监管级 NCA/NLME 包：本技能自带经验证的 NCA 与房室拟合而非包装外部包；NLME 估算与 VPC 等诊断交外部工具，见 `references/software-ecosystem.md`。
- 环境：Python 3.11+，仅 numpy 与 scipy；无网络、无专有软件；NONMEM/Monolix/Phoenix/Simcyp/GastroPlus 单独授权，脚本从不调用它们。
- Pharmpy 2.1.1 破坏性变更：2.0.0（2026-02-12）数据集行索引改为从 1 起；2.1.0（2026-05-08）`add_placebo_model` 改名 `set_placebo_model` 且要求 numpy ≥ 2；升级前先跑一次回归。
- NONMEM 7.6 相对 7.5 新增：ADVAN16（RADAR5 隐式 Runge-Kutta，刚性延迟微分）、ADVAN17（刚性延迟微分代数）、NUTS 贝叶斯采样、SAEM 存个体样本。
- PKPy 仅在 GitHub、**不在 PyPI**，`uv pip install pkpy` 会失败；贝叶斯 PKPD 可用 `chi-drm` 1.0.3（PyPI）。
- PBPK：OSP Suite v12（PK-Sim/MoBi）开源；Simcyp、GastroPlus 商业；`ospsuite` 仅 R 且需 .NET 8。
- 非线性消除：多剂行为不能从单剂叠加推，`--nonlinear` 切米氏；否则报典型患者而漏掉群体尾部。
- 数据坑兜底：进 `check_popk_dataset.py` 前先自查 DV 非数值、协变量空白、`ADDL` 无 `II`、同 timestamp 记录顺序；这些缺陷都不会中止运行，只会静默污染结果。
