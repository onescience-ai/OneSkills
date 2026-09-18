# HDF5/NumPy/JSON数据接口兼容性

## 适用范围

面向科学计算数据处理中HDF5(h5py)、NumPy与JSON三种数据格式间的接口兼容性问题。适用于涉及HDF5文件读写、numpy数组序列化为JSON的跨领域数据处理场景，包括CFD流场数据、生信基因数据、材料模拟数据等。

**不适用场景**：
- 纯Python原生类型操作（无需格式转换）
- 仅使用HDF5内部存储（无需JSON序列化）

## 输入

- 需要写入HDF5的Python对象（dict、list、numpy数组）
- 需要序列化为JSON的numpy数组或包含numpy类型的dict
- HDF5文件中的Group/Dataset对象

## 输出

- 兼容性检查报告
- 类型转换后的安全数据结构
- 错误率=0的HDF5/JSON操作

## 流程节点

### Step 1：h5py attrs类型检查
- **操作**：检查待写入attrs的值类型，确认是否为标量/数组
- **参数**：允许类型=str/int/float/numpy.ndarray，禁止类型=dict/list/自定义对象
- **工具**：isinstance检查
- **质量门禁**：所有attrs值均为标量或numpy数组

### Step 2：numpy类型到Python原生类型转换
- **操作**：将numpy.int32/float64等类型转换为Python原生int/float
- **参数**：转换方法=.item()或int()/float()强制转换
- **工具**：numpy.ndarray.item()方法
- **质量门禁**：转换后类型为Python原生类型，可被JSON序列化

### Step 3：HDF5 Group vs Dataset API区分
- **操作**：确认操作对象是Group还是Dataset，使用正确的API
- **参数**：Group有.keys()/.values()/.items()，Dataset无这些方法
- **工具**：isinstance(obj, h5py.Group)检查
- **质量门禁**：不调用Dataset的.keys()方法

### Step 4：JSON序列化安全检查
- **操作**：确认待序列化对象中无numpy类型
- **参数**：递归检查dict/list中的所有值
- **工具**：自定义NumpyEncoder或预处理
- **质量门禁**：json.dumps()不抛TypeError

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| h5py attrs允许类型 | 标量/numpy数组 | [D1] | attrs不支持Python dict/list |
| h5py attrs大小限制 | 通常<64KB | [D2] | 大属性需特殊处理 |
| numpy到Python转换方法 | .item()或int()/float() | [D6] | .item()返回Python原生类型 |
| JSON默认序列化支持 | dict/list/str/int/float/bool/None | [D5] | numpy类型不在默认支持列表中 |
| HDF5 Group API | .keys()/.values()/.items()/.get() | [D3] | 类似Python dict接口 |
| HDF5 Dataset API | .shape/.dtype/.resize()/.read_direct() | [D4] | 类似numpy array接口 |
| numpy dtype "O"支持 | 不支持，不计划实现 | [D1] | HDF5无Python object等价类型 |
| numpy "U"字符串支持 | 不支持 | [D1] | HDF5无固定宽度UTF-16/32等价类型 |

### 校准数值（体系专属）

以下数值来自某CFD数据处理任务（h5py+numpy+JSON），供量级校准；其他任务需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 错误类型1 | h5py.attrs赋值dict→TypeError | [1] | Object dtype has no native HDF5 equivalent |
| 错误类型2 | json.dump(numpy.int32)→TypeError | [1] | numpy int32不可直接JSON序列化 |
| 错误类型3 | Dataset.keys()→AttributeError | [1] | Dataset无.keys()方法 |
| 错误类型4 | os.path.dirname('')→空字符串 | [1] | 导致FileNotFoundError |

## 边界与分流

- **h5py attrs需存储dict**：拆分为多个独立标量属性，或将dict序列化为JSON字符串存储
- **numpy类型需JSON序列化**：使用json.dumps(obj, default=lambda o: o.item())或自定义NumpyEncoder
- **需遍历HDF5对象**：先isinstance检查是Group还是Dataset，再调用对应API
- **numpy dtype "O"需HDF5存储**：转为字符串或使用h5py.vlen_dtype()特殊类型
- **大属性>64KB**：启用track_order=True并使用h5py.Empty或分块存储

## 质量检查

- 所有h5py.attrs赋值操作不抛TypeError
- 所有json.dumps操作不抛TypeError（含numpy类型的数据）
- 所有HDF5遍历操作使用正确的Group/Dataset API
- 生成的HDF5文件可被h5py正常读取
- 生成的JSON文件可被json.loads正常解析

## 回退策略

- h5py attrs存储dict失败：降级为JSON字符串存储（牺牲可读性）
- numpy JSON序列化失败：使用.tolist()预转换（可能丢失精度）
- HDF5 Group/Dataset API混淆：使用try/except捕获AttributeError并降级

## 资源召回建议

当任务涉及HDF5文件读写、numpy数组处理、JSON序列化时召回本卡片。配套资源：onescience-coder的编码步骤。

## 补充证据（开源文档）

[D1] "h5py FAQ - What datatypes are supported?", h5py Project, version 3.16, URL: https://docs.h5py.org/en/stable/faq.html（accessed 2026-09-17，交叉验证）
[D2] "h5py Attributes Documentation", h5py Project, version 3.16, URL: https://docs.h5py.org/en/stable/high/attr.html（accessed 2026-09-17，交叉验证）
[D3] "h5py Groups Documentation", h5py Project, version 3.16, URL: https://docs.h5py.org/en/stable/high/group.html（accessed 2026-09-17，交叉验证）
[D4] "h5py Datasets Documentation", h5py Project, version 3.16, URL: https://docs.h5py.org/en/stable/high/dataset.html（accessed 2026-09-17，交叉验证）
[D5] "Python json module documentation", Python Software Foundation, version 3.14, URL: https://docs.python.org/3/library/json.html（accessed 2026-09-17，交叉验证）
[D6] "NumPy ndarray.tolist documentation", NumPy Developers, version 2.5, URL: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.tolist.html（accessed 2026-09-17，交叉验证）

## 证据来源

[1] CFD_S006归因报告：code_generation_multiple_errors issue，s01数据接入脚本执行时遭遇4次连续错误：h5py.attrs赋值dict、numpy.int32 JSON序列化、HDF5 Dataset无.keys()方法、os.path.dirname('')返回空字符串
