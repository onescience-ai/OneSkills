# EEMD-TCN混合模型完整实现方法

## 适用范围

适用于基于集合经验模态分解（EEMD）和时间卷积网络（TCN）的混合时间序列预测任务，特别是ENSO指数的6-24个月概率预测。

## 输入

输入数据格式：
- 时间序列：形状为 `(batch_size, seq_len, features)` 的张量
- 典型特征：SST异常、热含量、风场等气候变量
- 时间步长：月/周/日

## 输出

输出产物：
- EEMD分解后的IMF（固有模态函数）分量：`(n_imfs, seq_len)`
- TCN预测结果：`(forecast_len,)` 或 `(forecast_len, n_quantiles)` （概率预测）
- 模型权重文件：`.pth` 或 `.h5` 格式

## 流程节点

### EEMD分解流程

```
原始信号 → 添加噪声（N次） → EMD分解 → IMF分量 → 集合平均 → 最终IMF
```

**详细步骤**：
1. **初始化**：设置噪声标准差（通常为信号标准差的0.2倍）
2. **添加白噪声**：向原始信号添加高斯白噪声，重复N次（通常N=100）
3. **EMD分解**：对每次添加噪声后的信号进行EMD分解
4. **集合平均**：对N次分解的IMF进行集合平均
5. **输出IMF**：得到分解后的固有模态函数分量

### TCN网络架构

```python
# 时间卷积网络核心组件
class TemporalBlock(nn.Module):
    def __init__(self, n_inputs, n_outputs, kernel_size, stride, dilation, padding, dropout=0.2):
        super().__init__()
        self.conv1 = weight_norm(nn.Conv1d(n_inputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp1 = Chomp1d(padding)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(dropout)
        self.conv2 = weight_norm(nn.Conv1d(n_outputs, n_outputs, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
        self.chomp2 = Chomp1d(padding)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(dropout)
        self.net = nn.Sequential(self.conv1, self.chomp1, self.relu1, self.dropout1,
                                 self.conv2, self.chomp2, self.relu2, self.dropout2)
        self.downsample = nn.Conv1d(n_inputs, n_outputs, 1) if n_inputs != n_outputs else None
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        out = self.net(x)
        res = x if self.downsample is None else self.downsample(x)
        return self.relu(out + res)

class TCN(nn.Module):
    def __init__(self, input_size, output_size, num_channels, kernel_size=2, dropout=0.2):
        super().__init__()
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            dilation_size = 2 ** i
            in_channels = input_size if i == 0 else num_channels[i-1]
            out_channels = num_channels[i]
            layers += [TemporalBlock(in_channels, out_channels, kernel_size, 
                                    stride=1, dilation=dilation_size,
                                    padding=(kernel_size-1) * dilation_size, dropout=dropout)]
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        # x shape: (batch, seq_len, features) -> (batch, features, seq_len)
        x = x.transpose(1, 2)
        y = self.network(x)
        return y[:, :, -1]  # 返回最后一个时间步的输出
```

### EEMD-TCN结合方式

```
原始信号 → EEMD分解 → [IMF1, IMF2, ..., IMF_n]
                            ↓
                    对每个IMF独立建模
                            ↓
                [TCN1(IMF1), TCN2(IMF2), ..., TCN_n(IMF_n)]
                            ↓
                      集合预测聚合
                            ↓
                      最终预测结果
```

**聚合方式**：
- **直接求和**：`prediction = Σ(TCN_i(IMF_i))`
- **加权求和**：`prediction = Σ(w_i * TCN_i(IMF_i))`
- **注意力加权**：使用注意力机制动态分配权重

### 模型训练流程

```python
# 训练代码示例
def train_eemd_tcn(model, train_loader, val_loader, epochs=100, lr=0.001):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    for epoch in range(epochs):
        model.train()
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            output = model(batch_X)
            loss = criterion(output, batch_y)
            loss.backward()
            optimizer.step()
        
        # 验证
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for val_X, val_y in val_loader:
                val_output = model(val_X)
                val_loss += criterion(val_output, val_y).item()
        
        print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}, Val Loss: {val_loss/len(val_loader):.4f}")
    
    return model
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| EEMD噪声标准差 | 0.2 × std(signal) | [Wu & Huang, 2009] | 控制噪声辅助分解的强度 |
| EEMD集成次数 | 100次 | [Wu & Huang, 2009] | 分解结果的稳定性 |
| TCN卷积核大小 | 2-8 | [Bai et al., 2018] | 因果卷积的感受野 |
| TCN膨胀率 | 2^i (i=0,1,...,L-1) | [Bai et al., 2018] | 指数增长的膨胀率 |
| TCN层数 | 3-8层 | [实践] | 根据序列长度调整 |
| Dropout率 | 0.1-0.3 | [实践] | 防止过拟合 |
| 学习率 | 1e-3 | [实践] | Adam优化器初始学习率 |

## 边界与分流

### 模型选择决策

```
IF (数据非线性强) → 使用EEMD-TCN
IF (数据线性强) → 使用简单ARIMA或线性回归
IF (数据周期性明显) → 考虑加入傅里叶分解
IF (数据噪声大) → 增加EEMD集成次数或使用CEEMDAN
```

### 训练异常处理
- **梯度爆炸**：使用梯度裁剪 `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)`
- **过拟合**：增加Dropout率、使用早停、增加数据增强
- **收敛慢**：调整学习率、使用学习率调度器

## 质量检查

| 检查项 | 标准 | 失败处理 |
|--------|------|----------|
| IMF物理意义 | 每个IMF应有明确的物理对应 | 调整噪声参数或集成次数 |
| 预测稳定性 | 多次运行结果方差小 | 增加模型集成或使用集成学习 |
| 训练收敛 | 损失函数稳定下降 | 调整学习率或网络架构 |

## 回退策略

- **EEMD实现失败**：使用CEEMDAN（完全自适应噪声集合经验模态分解）
- **TCN训练不收敛**：使用预训练模型或简化网络架构
- **计算资源不足**：减少EEMD集成次数或使用轻量级TCN变体

## 资源召回建议

当执行以下任务时应召回本卡片：
- ENSO指数预测
- 气候时间序列预测
- 混合分解-深度学习模型
- 概率预测任务

配套资源：`climate-enso-data-sources`, `climate-time-series-validation`

## 证据来源

[1] Wu, Z., & Huang, N. E. (2009). Ensemble Empirical Mode Decomposition: A Noise-Assisted Data Analysis Method. *Advances in Adaptive Data Analysis*, 1(1), 1-41. DOI: 10.1002/advs.201300412

[2] Bai, S., Kolter, J. Z., & Koltun, V. (2018). An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling. *arXiv preprint arXiv:1803.01271*.

[3] Trenberth, K. E. (1997). The Definition of El Niño. *Bulletin of the American Meteorological Society*, 78(12), 2771-2778.