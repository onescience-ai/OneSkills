## access

优先使用 `${ONESCIENCE_DATASETS_DIR}/Carbon/finetune/random-promoter-dream-2022`；未设置该变量时回退到 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/random-promoter-dream-2022`。



已绑定的资源入口：

- `Carbon/finetune/random-promoter-dream-2022/supervised`
- `Carbon/finetune/random-promoter-dream-2022/challenge_test_sequences`
- `Carbon/finetune/random-promoter-dream-2022/test_subset_membership`
- `Carbon/finetune/random-promoter-dream-2022/public_leaderboard_ids`

## data_schema

supervised：`sequence:string,activity:float,sequence_length:int32,source_file:string,row_id:int64`。challenge_test_sequences 相同但没有 activity。两个 ID 配置为 `subset,item_id,row_id,source_member,line_number,raw_line`，不是序列样本；item_id 非数字时 row_id 可为 -1，不能当作有效连接键。

## task_usage

回归训练选 supervised；提交预测选 challenge；分组评测选对应 ID 清单并先验证连接协议。

## integration_paths

选择 config → 验证 schema 和标识 → 回归或无标签预测 adapter → 按已验证 ID 规则分组评测。

## preparation_requirements

检查 activity 有限值、sequence_length、split、source_file/row_id 唯一性；对 ID 表先确认 0/1-based、来源成员与非数字 ID 的处理。

## consumption_interfaces

监督任务消费 sequence+activity+来源键；challenge 消费无标签 sequence；ID 配置只供样本分组或提交索引。

## operation_limits

只读访问源数据；转换、缓存和索引写入独立输出目录，并记录源路径与配置。

多个 config 的行号命名空间不同。不得用 labeled test 调参或把 challenge 的存储 train 文件混入 supervised train。README 声明 CC BY 4.0，引用源挑战数据。
