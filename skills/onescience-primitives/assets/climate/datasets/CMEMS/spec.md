## content_principle
以 Copernicus Marine 数据为基础组织海洋状态变量，用于海洋时空预测和海气耦合特征建模。

## data_schema
metadata.json 给出 years=[2010,2011,2012]、variables 列表和 total_files=365；data/h5/newdata 存放年度 h5；stats/stats-new 存放统计量。

## storage_format
HDF5 .h5、JSON metadata、NumPy stats。

## scale_spec
metadata 记录 total_files=365；变量含 SST、SSH、10m u/v wind、23 层 eastward/northward velocity、salinity、potential temperature。

## coverage_spec
海洋表层和多深度三维变量，覆盖 CMEMS 指定年份和网格范围。

## label_spec
未来海洋状态作为监督标签；历史海洋/风场作为输入。

## split_strategy
推荐按时间连续划分 train/valid/test；metadata years 可作为小规模测试配置。
