# PT-DiT / ProToken 执行要点

PT-DiT 依赖 ProToken embedding 和 checkpoint。`protoken_emb.pkl`、`aatype_emb.pkl`、PT-DiT checkpoint、ProToken checkpoint 必须成套。多设备 pmap 要求 batch 能被设备数整除；flash attention 对 NRES 有长度要求，保守时关闭或调整长度。

ProToken 的 `scripts/infer.py` 用 PDB 编码到 VQ code 并重建结构，`decode_structure.py` 用 token indexes 解码 PDB。重建结构是 tokenizer reconstruction，不代表结构预测置信度。
