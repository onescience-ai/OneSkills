# 离线环境科学计算资源获取

## 适用范围
- 触发条件：执行环境网络受限或完全离线时
- 适用场景：无法直接访问GitHub、PyPI等外部资源的计算环境
- 不适用场景：网络畅通的常规开发环境

## 输入
- 网络限制信息（端口封锁、SSL证书问题、代理需求）
- 目标资源列表（Python包、模型权重、数据集）

## 输出
- 可访问的本地资源仓库
- 配置好的镜像源或代理

## 流程节点

### 1. 网络诊断
- 操作：测试关键资源的可达性
- 命令：
```bash
# 测试GitHub
curl -I https://github.com --connect-timeout 10
# 测试PyPI
curl -I https://pypi.org --connect-timeout 10
# 测试OpenAlex（学术检索）
curl -I https://api.openalex.org --connect-timeout 10
```
- 质量门禁：明确哪些资源可访问、哪些被封锁

### 2. 镜像源配置
- 操作：配置国内镜像源
- PyPI镜像：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```
- Conda镜像：
```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
```
- 质量门禁：`pip config list` 显示正确镜像配置

### 3. 代理配置
- 操作：设置HTTP/HTTPS代理
- 环境变量：
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```
- pip配置：
```bash
pip config set global.proxy http://proxy.example.com:8080
```
- 质量门禁：通过代理成功下载包

### 4. 离线资源包准备
- 操作：在有网络环境预下载资源
- Python包：
```bash
pip download rdkit-pypi torch pyg -d ./wheels
```
- 模型权重：直接下载文件或使用git clone --mirror
- 数据集：使用wget/curl批量下载
- 质量门禁：资源包完整性校验

### 5. 本地资源仓库搭建
- 操作：搭建简易PyPI镜像
- 工具：pypiserver、devpi
- 命令：
```bash
pip install pypiserver
pypi-server run -p 8080 ./wheels/
```
- 质量门禁：`pip install --index-url http://localhost:8080/ rdkit-pypi` 成功

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| PyPI清华镜像 | https://pypi.tuna.tsinghua.edu.cn/simple | [通用知识] | 国内常用镜像 |
| Conda清华镜像 | https://mirrors.tuna.tsinghua.edu.cn/anaconda/ | [通用知识] | Anaconda镜像 |
| 代理超时 | 10秒 | [通用知识] | 连接超时阈值 |
| 离线包目录 | ./wheels/ | [通用知识] | 预下载包存储位置 |

## 边界与分流
- **SSL证书问题**：可能需要`--trusted-host`参数或更新CA证书
- **代理认证**：部分代理需要用户名密码，格式为`http://user:pass@proxy:port`
- **包依赖冲突**：离线安装时需确保所有依赖包都已下载

## 质量检查
- 验证网络诊断结果
- 验证镜像源配置生效
- 验证离线安装成功
- 验证模型权重可加载

## 回退策略
- 如镜像不可用：尝试其他镜像源（阿里云、豆瓣）
- 如代理失败：联系网络管理员获取正确代理配置
- 如完全离线：使用预打包的Docker镜像

## 资源召回建议
- 何时召回：执行环境网络受限、安装失败、下载超时时
- 配套资源：bokdiff-model-weights-setup、rdkit-molecular-dependency

## 证据来源
[1] Khodabandeh Yalabadi A, Yazdani-Jahromi M, Garibay OO. BoKDiff: best-of-K diffusion alignment for target-specific 3D molecule generation. Bioinformatics Advances. 2025;5(1):vbaf137. DOI: 10.1093/bioadv/vbaf137
