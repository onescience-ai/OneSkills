#!/usr/bin/env python3
"""
SCNet Chat 缓存系统
用于初始化和管理 API token 及业务数据缓存

使用方法:
    python scripts/cache.py

配置文件位置:
    ~/.scnet-chat.env
    (路径可通过 config.CONFIG_PATH 修改)

缓存文件位置:
    ~/.scnet-chat-cache.json
    (路径可通过 config.get_cache_path() 获取)
"""

import aiohttp
import os
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import urllib.request
import urllib.error
import ssl

# Windows 终端兼容处理
import compat

# 异步HTTP支持
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# 导入配置文件
from config import (
    CONFIG_PATH, CACHE_PATH, get_cache_path,
    EXPIRY_PARASTORS, EXPIRY_WALLTIME, CACHE_MAX_AGE,
    APITimeout, ASYNC_CONCURRENCY_LIMIT
)


class Logger:
    """日志管理器"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
    
    def log(self, message: str):
        """输出日志"""
        if self.enabled:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def info(self, message: str):
        """信息日志"""
        self.log(f"[INFO] {message}")
    
    def error(self, message: str):
        """错误日志"""
        self.log(f"[ERROR] {message}")
    
    def warning(self, message: str):
        """警告日志"""
        self.log(f"[WARN] {message}")
    
    def success(self, message: str):
        """成功日志"""
        self.log(f"[SUCCESS] {message}")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.config: Dict[str, str] = {}
        self._load_config()
    
    def _load_config(self):
        """从配置文件加载配置"""
        if not CONFIG_PATH.exists():
            self.logger.error(f"配置文件不存在: {CONFIG_PATH}")
            print(f"\n错误: 配置文件不存在: {CONFIG_PATH}")
            print("\n请创建配置文件，格式如下:")
            print("""
# SCNet Chat 配置文件
# 存放位置: ~/.scnet-chat.env
# 权限建议: chmod 600 ~/.scnet-chat.env

# 登录接口的域名
SCNET_LOGIN_URL=https://api.scnet.cn

# AC接口的域名
SCNET_AC_URL=https://www.scnet.cn

# SCNet 访问密钥 (Access Key)
SCNET_ACCESS_KEY=your_access_key_here

# SCNet 密钥 (Secret Key)
SCNET_SECRET_KEY=your_secret_key_here

# SCNet 用户名
SCNET_USER=your_username_here

# 日志开关（1=启用，0或不设置=禁用）
SCNET_LOG_ENABLED=1
""")
            raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
        
        self.logger.info(f"正在读取配置文件: {CONFIG_PATH}")
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = value.strip()
        
        # 验证必要配置
        required_keys = ['SCNET_ACCESS_KEY', 'SCNET_SECRET_KEY', 'SCNET_USER']
        missing = [k for k in required_keys if k not in self.config]
        if missing:
            raise ValueError(f"配置文件缺少必要项: {', '.join(missing)}")
        
        # 设置默认值
        self.config.setdefault('SCNET_LOGIN_URL', 'https://api.scnet.cn')
        self.config.setdefault('SCNET_AC_URL', 'https://www.scnet.cn')
        self.config.setdefault('SCNET_LOG_ENABLED', '0')
        
        self.logger.success("配置文件加载成功")
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置项"""
        return self.config.get(key, default)
    
    @property
    def access_key(self) -> str:
        return self.config['SCNET_ACCESS_KEY']
    
    @property
    def secret_key(self) -> str:
        return self.config['SCNET_SECRET_KEY']
    
    @property
    def username(self) -> str:
        return self.config['SCNET_USER']
    
    @property
    def login_url(self) -> str:
        return self.config['SCNET_LOGIN_URL'].rstrip('/')
    
    @property
    def ac_url(self) -> str:
        return self.config['SCNET_AC_URL'].rstrip('/')
    
    @property
    def log_enabled(self) -> bool:
        return self.config.get('SCNET_LOG_ENABLED', '0') == '1'


def escape_json(s: str) -> str:
    """转义 JSON 字符串中的特殊字符"""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


class APIManager:
    """API 请求管理器"""
    
    # 从配置文件导入超时时间
    TIMEOUT_GET_TOKENS = APITimeout.GET_TOKENS
    TIMEOUT_GET_CENTER_INFO = APITimeout.GET_CENTER_INFO
    TIMEOUT_GET_USER_INFO = APITimeout.GET_USER_INFO
    TIMEOUT_GET_CLUSTER_INFO = APITimeout.GET_CLUSTER_INFO
    TIMEOUT_GET_USER_QUEUES = APITimeout.GET_USER_QUEUES
    TIMEOUT_GET_USER_QUOTA = APITimeout.GET_USER_QUOTA
    TIMEOUT_GET_USED_TIME = APITimeout.GET_USED_TIME
    
    # 兼容性保留
    TIMEOUT_QUICK = APITimeout.QUICK
    TIMEOUT_NORMAL = APITimeout.NORMAL
    TIMEOUT_COMPLEX = APITimeout.COMPLEX
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
        # 创建 SSL 上下文，允许我们处理可能的证书问题
        self.ssl_context = ssl.create_default_context()
        # 在开发/测试环境中可能需要禁用 SSL 验证
        # self.ssl_context.check_hostname = False
        # self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _generate_signature(self, access_key: str, timestamp: str, user: str, secret_key: str) -> str:
        """
        生成 HMAC-SHA256 签名
        
        构造待签名 JSON 字符串并生成 HMAC-SHA256 签名
        JSON 字段按字典序排列: accessKey, timestamp, user
        
        Args:
            access_key: AK
            timestamp: 时间戳（秒，字符串）
            user: 用户名
            secret_key: SK
        
        Returns:
            签名（小写十六进制字符串）
        """
        # 转义 JSON 特殊字符
        escaped_ak = escape_json(access_key)
        escaped_ts = escape_json(timestamp)
        escaped_user = escape_json(user)
        
        # 按字典序拼接 JSON：accessKey, timestamp, user
        data_to_sign = f'{{"accessKey":"{escaped_ak}","timestamp":"{escaped_ts}","user":"{escaped_user}"}}'
        
        # 计算 HMAC-SHA256 签名
        signature = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=data_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return signature.lower()
    
    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        # 默认使用普通超时
        if timeout is None:
            timeout = self.TIMEOUT_NORMAL
        """发起 HTTP 请求"""
        
        req_headers = headers or {}
        req_headers.setdefault('Accept', 'application/json')
        if data:
            req_headers.setdefault('Content-Type', 'application/json')
        
        self.logger.info(f"请求: {method} {url}")
        self.logger.info(f"请求头: {json.dumps(req_headers, ensure_ascii=False)}")
        
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers=req_headers,
                method=method
            )
            
            with urllib.request.urlopen(
                req, 
                context=self.ssl_context,
                timeout=timeout
            ) as response:
                response_body = response.read().decode('utf-8')
                self.logger.info(f"响应: {response_body[:200]}...")
                return json.loads(response_body)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            self.logger.error(f"HTTP 错误 {e.code}: {error_body}")
            try:
                error_json = json.loads(error_body)
                return {"success": False, "error": error_json, "code": e.code, "msg": error_json.get('msg', 'HTTP Error')}
            except json.JSONDecodeError:
                return {"success": False, "error": error_body, "code": e.code}
        except Exception as e:
            self.logger.error(f"请求异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_tokens(self) -> Dict[str, Any]:
        """
        获取访问凭证
        POST /api/user/v3/tokens
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-user-tokens-aksk.html
        """
        url = f"{self.config.login_url}/api/user/v3/tokens"
        
        # 获取时间戳（秒）
        timestamp = str(int(time.time()))
        
        # 生成签名
        signature = self._generate_signature(
            self.config.access_key,
            timestamp,
            self.config.username,
            self.config.secret_key
        )
        headers = {
            'user': self.config.username,
            'accessKey': self.config.access_key,
            'signature': signature,
            'timestamp': timestamp
        }
        
        self.logger.info("正在获取访问凭证...")
        start_time = time.time()
        result = self._make_request("POST", url, headers, timeout=self.TIMEOUT_GET_TOKENS)
        duration_ms = (time.time() - start_time) * 1000
        self.logger.info(f"请求耗时: {duration_ms:.2f}ms")
        
        # 接口返回成功: code 可以是数字 200 或字符串 "0"
        code = result.get('code')
        is_success = (code == 200 or code == '0' or code == 0 or result.get('success'))
        
        if is_success:
            self.logger.success("访问凭证获取成功")
        
        return result
    
    def get_center_info(self, token: str) -> Dict[str, Any]:
        """
        获取授权区域信息
        GET /ac/openapi/v2/center
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/safecertification/get-center-info.html
        """
        url = f"{self.config.ac_url}/ac/openapi/v2/center"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_CENTER_INFO)
    
    def get_cluster_info(self, base_url: str, token: str) -> Dict[str, Any]:
        """
        获取集群信息
        GET /hpc/openapi/v2/cluster
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/list-cluster.html
        """
        url = f"{base_url}/hpc/openapi/v2/cluster"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_CENTER_INFO)
    
    def get_user_queues(self, base_url: str, token: str, username: str, job_manager_id: str) -> Dict[str, Any]:
        """
        查询用户可访问队列
        GET /hpc/openapi/v2/queuenames/users/{username}?strJobManagerID={job_manager_id}
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-user-queue.html
        """
        url = f"{base_url}/hpc/openapi/v2/queuenames/users/{urllib.parse.quote(username)}?strJobManagerID={urllib.parse.quote(job_manager_id)}"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_USER_QUEUES)
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        获取用户信息
        GET /ac/openapi/v2/user
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/userresource/get-common-user.html
        """
        url = f"{self.config.ac_url}/ac/openapi/v2/user"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_USER_INFO)
    
    def get_user_quota(self, base_url: str, token: str) -> Dict[str, Any]:
        """
        获取用户共享存储配额及使用量
        GET /hpc/openapi/v2/parastors
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-user-quota.html
        """
        username = self.config.username
        url = f"{base_url}/hpc/openapi/v2/parastor/quota/usernames/{username}"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_USER_QUOTA)
    
    def get_used_time(self, base_url: str, token: str) -> Dict[str, Any]:
        """
        获取已用机时
        GET /hpc/openapi/v2/walltime
        文档: https://www.scnet.cn/ac/openapi/doc/2.0/api/jobmanager/query-used-time.html
        """ 
        username = self.config.username
        url = f"{base_url}/hpc/openapi/v2/view/walltime/users/{username}"
        
        headers = {
            'token': token,
            'Content-Type': 'application/json'
        }
        
        return self._make_request("GET", url, headers, timeout=self.TIMEOUT_GET_USED_TIME)


class AsyncAPIManager:
    """
    异步API请求管理器
    用于并行执行多个API请求以加速缓存初始化
    """
    
    def __init__(self, config: ConfigManager, logger: Logger):
        self.config = config
        self.logger = logger
        # SSL上下文（用于aiohttp）
        self.ssl_context = ssl.create_default_context()
        # 信号量控制并发数，避免服务端限流
        self.semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)
    
    async def _make_request(self, session: aiohttp.ClientSession, method: str, 
                           url: str, headers: Dict[str, str], 
                           data: Optional[bytes] = None,
                           timeout: int = 5) -> Dict[str, Any]:
        """发起异步HTTP请求"""
        async with self.semaphore:  # 控制并发数
            try:
                self.logger.info(f"异步请求: {method} {url}")
                
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=self.ssl_context
                ) as response:
                    response_body = await response.text()
                    self.logger.info(f"响应: {response_body[:200]}...")
                    return json.loads(response_body)
                    
            except asyncio.TimeoutError:
                self.logger.error(f"请求超时: {url}")
                return {"success": False, "error": "Timeout", "code": -1}
            except Exception as e:
                self.logger.error(f"请求异常: {str(e)}")
                return {"success": False, "error": str(e), "code": -1}
    
    async def get_center_info(self, session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
        """获取授权区域信息"""
        url = f"{self.config.ac_url}/ac/openapi/v2/center"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers, 
                                       timeout=APIManager.TIMEOUT_GET_CENTER_INFO)
    
    async def get_user_info(self, session: aiohttp.ClientSession, token: str) -> Dict[str, Any]:
        """获取用户信息"""
        url = f"{self.config.ac_url}/ac/openapi/v2/user"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers,
                                       timeout=APIManager.TIMEOUT_GET_USER_INFO)
    
    async def get_cluster_info(self, session: aiohttp.ClientSession, base_url: str, 
                               token: str) -> Dict[str, Any]:
        """获取集群信息"""
        url = f"{base_url}/hpc/openapi/v2/cluster"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers,
                                       timeout=APIManager.TIMEOUT_GET_CLUSTER_INFO)
    
    async def get_user_queues(self, session: aiohttp.ClientSession, base_url: str, 
                              token: str, username: str, job_manager_id: str) -> Dict[str, Any]:
        """查询用户可访问队列"""
        url = f"{base_url}/hpc/openapi/v2/queuenames/users/{urllib.parse.quote(username)}"
        url += f"?strJobManagerID={urllib.parse.quote(job_manager_id)}"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers,
                                       timeout=APIManager.TIMEOUT_GET_USER_QUEUES)
    
    async def get_user_quota(self, session: aiohttp.ClientSession, base_url: str, 
                             token: str) -> Dict[str, Any]:
        """获取用户共享存储配额"""
        username = self.config.username
        url = f"{base_url}/hpc/openapi/v2/parastor/quota/usernames/{username}"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers,
                                       timeout=APIManager.TIMEOUT_GET_USER_QUOTA)
    
    async def get_used_time(self, session: aiohttp.ClientSession, base_url: str, 
                            token: str) -> Dict[str, Any]:
        """获取已用机时"""
        username = self.config.username
        url = f"{base_url}/hpc/openapi/v2/view/walltime/users/{username}"
        headers = {'token': token, 'Content-Type': 'application/json'}
        return await self._make_request(session, "GET", url, headers,
                                       timeout=APIManager.TIMEOUT_GET_USED_TIME)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        # 缓存文件直接存放在用户主目录下，无需创建目录
    
    def load(self, auto_refresh: bool = True) -> Optional[Dict[str, Any]]:
        """加载缓存文件
        
        Args:
            auto_refresh: 当缓存文件解析失败时是否自动刷新缓存
        
        Returns:
            缓存字典，如果缓存不存在或解析失败则返回 None
        """
        if not get_cache_path().exists():
            self.logger.info("缓存文件不存在，将创建新缓存")
            return None
        
        try:
            with open(get_cache_path(), 'r', encoding='utf-8') as f:
                cache = json.load(f)
            self.logger.info(f"已加载缓存文件: {get_cache_path()}")
            return cache
        except json.JSONDecodeError as e:
            self.logger.error(f"缓存文件解析失败: {e}")
            if auto_refresh:
                self.logger.info("尝试自动刷新缓存...")
                return self._refresh_cache()
            return None
        except Exception as e:
            self.logger.error(f"加载缓存文件失败: {e}")
            if auto_refresh:
                self.logger.info("尝试自动刷新缓存...")
                return self._refresh_cache()
            return None
    
    def _refresh_cache(self) -> Optional[Dict[str, Any]]:
        """自动刷新缓存
        
        Returns:
            刷新后的缓存字典，如果刷新失败则返回 None
        """
        try:
            # 备份损坏的缓存文件
            if get_cache_path().exists():
                backup_path = get_cache_path().with_suffix('.json.bak')
                try:
                    get_cache_path().rename(backup_path)
                    self.logger.info(f"已备份损坏的缓存文件到: {backup_path}")
                except Exception as e:
                    self.logger.warning(f"备份缓存文件失败: {e}")
                    # 如果备份失败，直接删除
                    try:
                        get_cache_path().unlink()
                    except Exception:
                        pass
            
            print("\n⚠️  缓存文件损坏，正在自动刷新缓存...")
            # 创建初始化器并运行
            initializer = CacheInitializer()
            success = initializer.run()
            if success:
                print("✓ 缓存自动刷新成功")
                # 重新加载缓存（禁用自动刷新避免递归）
                return self.load(auto_refresh=False)
            else:
                print("✗ 缓存自动刷新失败，请手动运行: python scripts/cache.py")
                return None
        except Exception as e:
            self.logger.error(f"自动刷新缓存失败: {e}")
            print(f"✗ 自动刷新缓存失败: {e}")
            print("  请手动运行: python scripts/cache.py")
            return None
    
    def save(self, cache: Dict[str, Any]):
        """保存缓存文件"""
        try:
            with open(get_cache_path(), 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            self.logger.success(f"缓存已保存到: {get_cache_path()}")
        except Exception as e:
            self.logger.error(f"保存缓存文件失败: {e}")
            raise
    
    def get_default_cluster_id(self, cache: Optional[Dict[str, Any]]) -> Optional[str]:
        """获取当前默认的 clusterId"""
        if not cache or 'clusters' not in cache:
            return None
        
        for cluster in cache['clusters']:
            if cluster.get('default') is True:
                return cluster.get('clusterId')
        return None
    
    def is_expired(self, data: Dict[str, Any], expiry_key: str) -> bool:
        """检查数据是否过期"""
        if '_expiry' not in data:
            return True
        
        expiry = data['_expiry'].get(expiry_key, 0)
        return time.time() > expiry
    
    def set_expiry(self, data: Dict[str, Any], expiry_key: str, seconds: int):
        """设置数据过期时间"""
        if '_expiry' not in data:
            data['_expiry'] = {}
        
        data['_expiry'][expiry_key] = int(time.time() + seconds)


class CacheInitializer:
    """缓存初始化器"""
    
    def __init__(self, only_default: bool = True, target_cluster_id: str = None):
        """
        初始化缓存初始化器
        
        Args:
            only_default: 是否只初始化默认区域的详细信息（默认为 True）
            target_cluster_id: 指定要刷新的区域 ID（如果设置，优先于 only_default）
        """
        # 先创建 logger，配置加载后再更新 enabled 状态
        self.logger = Logger(enabled=False)
        self.config = ConfigManager(self.logger)
        self.logger.enabled = self.config.log_enabled
        self.api = APIManager(self.config, self.logger)
        self.cache_mgr = CacheManager(self.logger)
        self.only_default = only_default
        self.target_cluster_id = target_cluster_id
        
        # 初始化异步API管理器（如果可用）
        if AIOHTTP_AVAILABLE:
            self.async_api = AsyncAPIManager(self.config, self.logger)
        else:
            self.async_api = None
    
    def _extract_domain_and_port(self, url: str) -> str:
        """
        从 URL 中提取域名和端口部分
        例如: https://ksefile.hpccube.com:65241/efile -> https://ksefile.hpccube.com:65241
              https://ksefile.hpccube.com:65241/ -> https://ksefile.hpccube.com:65241
        """
        if not url:
            return url
        try:
            parsed = urllib.parse.urlparse(url)
            # 重新组合 scheme://netloc
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return url
    
    def _filter_enabled_urls(self, urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """过滤出 enable=true 的 URL 列表，并处理 url 只保留域名和端口"""
        result = []
        for u in urls:
            if str(u.get('enable', '')).lower() == 'true':
                # 复制一份，避免修改原始数据
                url_item = dict(u)
                # 处理 url 字段，只保留域名和端口
                if 'url' in url_item:
                    url_item['url'] = self._extract_domain_and_port(url_item['url'])
                result.append(url_item)
        return result
    
    def _get_base_url_from_cache(self, cluster: Dict[str, Any], api_name: str) -> Optional[str]:
        """
        从缓存中获取 API 的基础 URL
        
        规则:
        - /ac/ 开头: 使用 SCNET_AC_URL
        - /{name}/ 开头: 使用 {name}Urls[0].url
        """
        urls_key = f"{api_name}Urls"
        if urls_key in cluster and cluster[urls_key]:
            urls = self._filter_enabled_urls(cluster[urls_key])
            if urls:
                return urls[0].get('url')
        return None
    
    def _init_clusters_base(self, tokens_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """初始化 clusters 基础信息"""
        clusters = []
        
        data = tokens_response.get('data', [])
        if not data:
            self.logger.error("获取访问凭证响应中没有 data 字段")
            raise ValueError("获取访问凭证响应无效")
        
        for i, item in enumerate(data):
            cluster = {
                "clusterId": item.get("clusterId"),
                "clusterName": item.get("clusterName"),
                "token": item.get("token"),
                "default": i == 0  # 第一个设为默认
            }
            clusters.append(cluster)
        
        return clusters
    
    async def _init_cluster_details_async(self, cluster: Dict[str, Any]):
        """
        异步初始化单个 cluster 的详细信息
        使用并行请求加速缓存初始化过程
        """
        if not AIOHTTP_AVAILABLE or not self.async_api:
            # 如果aiohttp不可用，回退到同步方法
            self._init_cluster_details_sync(cluster)
            return
            
        cluster_id = cluster.get('clusterId')
        cluster_name = cluster.get('clusterName')
        token = cluster.get('token')
        
        self.logger.info(f"正在异步初始化区域: {cluster_name} (ID: {cluster_id})")
        
        # 特殊区域 ac 不调用某些接口
        if cluster_name == 'ac':
            self.logger.info(f"跳过特殊区域: {cluster_name}")
            return
        
        async with aiohttp.ClientSession() as session:
            # Phase 1: 并行获取基础信息 (无依赖)
            self.logger.info(f"[{cluster_name}] Phase 1: 并行获取基础信息...")
            center_info, user_info = await asyncio.gather(
                self.async_api.get_center_info(session, token),
                self.async_api.get_user_info(session, token),
                return_exceptions=True
            )
            
            # 处理 center_info
            if isinstance(center_info, Exception):
                self.logger.error(f"[{cluster_name}] 获取授权区域信息异常: {center_info}")
            elif str(center_info.get('code')) in ['200', '0'] and 'data' in center_info:
                data = center_info['data']
                for key in ['hpcUrls', 'aiUrls', 'efileUrls']:
                    if key in data:
                        cluster[key] = self._filter_enabled_urls(data[key])
            else:
                self.logger.warning(f"[{cluster_name}] 获取授权区域信息失败: {center_info.get('message', '未知错误')}")
            
            # 处理 user_info
            if isinstance(user_info, Exception):
                self.logger.error(f"[{cluster_name}] 获取用户信息异常: {user_info}")
            elif str(user_info.get('code')) in ['200', '0'] and 'data' in user_info:
                cluster['clusterUserInfo'] = user_info['data']
            else:
                self.logger.warning(f"[{cluster_name}] 获取用户信息失败: {user_info.get('message', '未知错误')}")
            
            # Phase 2: 并行获取集群、配额、机时 (依赖 hpc_url)
            hpc_url = self._get_base_url_from_cache(cluster, 'hpc')
            if hpc_url:
                self.logger.info(f"[{cluster_name}] Phase 2: 并行获取集群、配额、机时...")
                
                cluster_info, quota_info, walltime_info = await asyncio.gather(
                    self.async_api.get_cluster_info(session, hpc_url, token),
                    self.async_api.get_user_quota(session, hpc_url, token),
                    self.async_api.get_used_time(session, hpc_url, token),
                    return_exceptions=True
                )
                
                # 处理 cluster_info
                if isinstance(cluster_info, Exception):
                    self.logger.error(f"[{cluster_name}] 获取集群信息异常: {cluster_info}")
                elif str(cluster_info.get('code')) in ['200', '0'] and 'data' in cluster_info:
                    cluster['JobManagers'] = cluster_info['data']
                else:
                    self.logger.warning(f"[{cluster_name}] 获取集群信息失败: {cluster_info.get('message', '未知错误')}")
                
                # 处理 quota_info
                if isinstance(quota_info, Exception):
                    self.logger.error(f"[{cluster_name}] 获取配额信息异常: {quota_info}")
                elif str(quota_info.get('code')) in ['200', '0'] and 'data' in quota_info:
                    cluster['parastors'] = quota_info['data']
                    self.cache_mgr.set_expiry(cluster, 'parastors', EXPIRY_PARASTORS)
                elif quota_info.get('code') == 404:
                    self.logger.info(f"[{cluster_name}] 配额接口暂不可用 (404)")
                else:
                    self.logger.warning(f"[{cluster_name}] 获取配额信息失败: {quota_info.get('msg', quota_info.get('message', '未知错误'))}")
                
                # 处理 walltime_info
                if isinstance(walltime_info, Exception):
                    self.logger.error(f"[{cluster_name}] 获取已用机时异常: {walltime_info}")
                elif str(walltime_info.get('code')) in ['200', '0'] and 'data' in walltime_info:
                    cluster['walltime'] = walltime_info['data']
                    self.cache_mgr.set_expiry(cluster, 'walltime', EXPIRY_WALLTIME)
                elif walltime_info.get('code') == 404:
                    self.logger.info(f"[{cluster_name}] 机时接口暂不可用 (404)")
                else:
                    self.logger.warning(f"[{cluster_name}] 获取已用机时失败: {walltime_info.get('msg', walltime_info.get('message', '未知错误'))}")
                
                # Phase 3: 并行获取所有 JobManager 的队列
                if cluster.get('clusterUserInfo', {}).get('userName') and 'JobManagers' in cluster:
                    username = cluster['clusterUserInfo']['userName']
                    job_managers = cluster['JobManagers']
                    
                    if job_managers:
                        self.logger.info(f"[{cluster_name}] Phase 3: 并行获取 {len(job_managers)} 个 JobManager 的队列...")
                        
                        queue_tasks = []
                        for jm in job_managers:
                            job_manager_id = jm.get('id')
                            if job_manager_id:
                                task = self.async_api.get_user_queues(
                                    session, hpc_url, token, username, str(job_manager_id)
                                )
                                queue_tasks.append((jm, task))
                        
                        # 并行执行所有队列查询
                        if queue_tasks:
                            results = await asyncio.gather(
                                *[task for _, task in queue_tasks],
                                return_exceptions=True
                            )
                            
                            # 处理结果
                            for (jm, _), queues_info in zip(queue_tasks, results):
                                if isinstance(queues_info, Exception):
                                    self.logger.error(f"[{cluster_name}] 获取队列异常: {queues_info}")
                                elif str(queues_info.get('code')) in ['200', '0'] and 'data' in queues_info:
                                    jm['queues'] = queues_info.get('data', [])
            else:
                self.logger.warning(f"[{cluster_name}] 无法获取 HPC 服务地址，跳过集群信息获取")
        
        self.logger.success(f"区域 {cluster_name} 异步初始化完成")
    
    def _init_cluster_details_sync(self, cluster: Dict[str, Any]):
        """同步方式初始化单个 cluster 的详细信息 (原始实现)"""
        cluster_id = cluster.get('clusterId')
        cluster_name = cluster.get('clusterName')
        token = cluster.get('token')
        
        self.logger.info(f"正在初始化区域: {cluster_name} (ID: {cluster_id}) [同步模式]")
        
        # 特殊区域 ac 不调用某些接口
        if cluster_name == 'ac':
            self.logger.info(f"跳过特殊区域: {cluster_name}")
            return
        
        # 1. 获取授权区域信息 (/ac/openapi/v2/center)
        self.logger.info(f"[{cluster_name}] 获取授权区域信息...")
        center_info = self.api.get_center_info(token)
        
        if str(center_info.get('code')) in ['200', '0'] and 'data' in center_info:
            data = center_info['data']
            for key in ['hpcUrls', 'aiUrls', 'efileUrls']:
                if key in data:
                    cluster[key] = self._filter_enabled_urls(data[key])
        else:
            self.logger.warning(f"[{cluster_name}] 获取授权区域信息失败: {center_info.get('message', '未知错误')}")
        
        # 2. 获取用户信息 (/ac/openapi/v2/user)
        self.logger.info(f"[{cluster_name}] 获取用户信息...")
        user_info = self.api.get_user_info(token)
        
        if str(user_info.get('code')) in ['200', '0'] and 'data' in user_info:
            cluster['clusterUserInfo'] = user_info['data']
        else:
            self.logger.warning(f"[{cluster_name}] 获取用户信息失败: {user_info.get('message', '未知错误')}")
        
        # 3. 获取集群信息 (/hpc/openapi/v2/cluster) - 需要 hpcUrls
        hpc_url = self._get_base_url_from_cache(cluster, 'hpc')
        if hpc_url:
            self.logger.info(f"[{cluster_name}] 获取集群信息...")
            cluster_info = self.api.get_cluster_info(hpc_url, token)
            
            if str(cluster_info.get('code')) in ['200', '0'] and 'data' in cluster_info:
                cluster['JobManagers'] = cluster_info['data']
                
                # 4. 获取用户可访问队列 (每个 JobManager 分别获取)
                if cluster.get('clusterUserInfo', {}).get('userName') and 'JobManagers' in cluster:
                    username = cluster['clusterUserInfo']['userName']
                    for jm in cluster['JobManagers']:
                        job_manager_id = jm.get('id')
                        if job_manager_id:
                            self.logger.info(f"[{cluster_name}] 获取用户可访问队列 (JobManager: {jm.get('text', job_manager_id)})...")
                            queues_info = self.api.get_user_queues(hpc_url, token, username, str(job_manager_id))
                            
                            if str(queues_info.get('code')) in ['200', '0'] and 'data' in queues_info:
                                jm['queues'] = queues_info.get('data', [])
            else:
                self.logger.warning(f"[{cluster_name}] 获取集群信息失败: {cluster_info.get('message', '未知错误')}")
        else:
            self.logger.warning(f"[{cluster_name}] 无法获取 HPC 服务地址，跳过集群信息获取")
        
        # 5. 获取配额信息 (带过期时间)
        if hpc_url:
            self.logger.info(f"[{cluster_name}] 获取存储配额...")
            quota_info = self.api.get_user_quota(hpc_url, token)
            
            if str(quota_info.get('code')) in ['200', '0'] and 'data' in quota_info:
                cluster['parastors'] = quota_info['data']
                self.cache_mgr.set_expiry(cluster, 'parastors', EXPIRY_PARASTORS)
            elif quota_info.get('code') == 404:
                self.logger.info(f"[{cluster_name}] 配额接口暂不可用 (404)")
            else:
                self.logger.warning(f"[{cluster_name}] 获取配额信息失败: {quota_info.get('msg', quota_info.get('message', '未知错误'))}")
        
        # 6. 获取已用机时 (带过期时间)
        if hpc_url:
            self.logger.info(f"[{cluster_name}] 获取已用机时...")
            walltime_info = self.api.get_used_time(hpc_url, token)
            
            if str(walltime_info.get('code')) in ['200', '0'] and 'data' in walltime_info:
                cluster['walltime'] = walltime_info['data']
                self.cache_mgr.set_expiry(cluster, 'walltime', EXPIRY_WALLTIME)
            elif walltime_info.get('code') == 404:
                self.logger.info(f"[{cluster_name}] 机时接口暂不可用 (404)")
            else:
                self.logger.warning(f"[{cluster_name}] 获取已用机时失败: {walltime_info.get('msg', walltime_info.get('message', '未知错误'))}")
        
        self.logger.success(f"区域 {cluster_name} 初始化完成")
    
    def _init_cluster_details(self, cluster: Dict[str, Any]):
        """
        初始化单个 cluster 的详细信息
        自动选择异步或同步方式
        """
        if AIOHTTP_AVAILABLE and self.async_api:
            try:
                # 使用异步方式
                asyncio.run(self._init_cluster_details_async(cluster))
            except RuntimeError as e:
                # 如果事件循环已存在（如在某些IDE/Jupyter环境中），回退到同步方式
                self.logger.warning(f"异步初始化失败（{e}），回退到同步方式")
                self._init_cluster_details_sync(cluster)
        else:
            # 回退到同步方式
            self._init_cluster_details_sync(cluster)
    
    def _preserve_default_setting(self, new_clusters: List[Dict[str, Any]], old_cache: Optional[Dict[str, Any]]):
        """保留之前的 default 设置"""
        if not old_cache or 'clusters' not in old_cache:
            return
        
        # 获取之前的 default clusterId
        old_default_id = None
        for cluster in old_cache['clusters']:
            if cluster.get('default') is True:
                old_default_id = cluster.get('clusterId')
                break
        
        if not old_default_id:
            return
        
        # 重置所有 default 为 false
        for cluster in new_clusters:
            cluster['default'] = False
        
        # 恢复之前的 default
        for cluster in new_clusters:
            if cluster.get('clusterId') == old_default_id:
                cluster['default'] = True
                self.logger.info(f"保留默认区域: {cluster.get('clusterName')} (ID: {old_default_id})")
                break
    
    def _init_all_clusters(self, clusters: List[Dict[str, Any]]):
        """初始化所有区域的详细信息"""
        print(f"\n▶ 初始化所有区域详细信息...")
        self.logger.info("步骤 3/6: 初始化所有区域详细信息...")
        initialized_count = 0
        failed_count = 0
        
        for cluster in clusters:
            cluster_name = cluster.get('clusterName', 'Unknown')
            try:
                self._init_cluster_details(cluster)
                initialized_count += 1
            except Exception as e:
                self.logger.error(f"初始化区域 {cluster_name} 失败: {e}")
                print(f"✗ 区域 {cluster_name} 初始化失败: {e}")
                failed_count += 1
        
        print(f"✓ 区域详细信息初始化完成 ({initialized_count} 成功, {failed_count} 失败)")
    
    def run(self):
        """执行缓存初始化流程"""
        print("=" * 60)
        print("SCNet Chat 缓存初始化")
        print("=" * 60)
        
        # 1. 加载旧缓存（禁用自动刷新，避免递归）
        old_cache = self.cache_mgr.load(auto_refresh=False)
        
        # 2. 获取访问凭证
        self.logger.info("步骤 1/6: 获取访问凭证...")
        tokens_response = self.api.get_tokens()
        
        # 接口返回成功: code 可以是数字 200 或字符串 "0"
        code = tokens_response.get('code')
        is_success = (code == 200 or code == '0' or code == 0)
        
        if not is_success or 'data' not in tokens_response:
            error_msg = tokens_response.get('message', tokens_response.get('error', '未知错误'))
            self.logger.error(f"获取访问凭证失败: {error_msg}")
            print(f"\n错误: 获取访问凭证失败 - {error_msg}")
            print("\n可能原因:")
            print("1. AK/SK 配置错误")
            print("2. 网络连接问题")
            print("3. SCNet 服务异常")
            return False
        
        print(f"✓ 访问凭证获取成功")
        
        # 3. 初始化 clusters 基础信息
        self.logger.info("步骤 2/6: 初始化区域基础信息...")
        clusters = self._init_clusters_base(tokens_response)
        print(f"✓ 发现 {len(clusters)} 个区域")
        
        # 4. 保留之前的 default 设置
        self._preserve_default_setting(clusters, old_cache)
        
        # 5. 初始化 cluster 的详细信息
        # 根据模式决定初始化哪些区域
        if self.target_cluster_id:
            # 模式1: 刷新指定区域
            target_cluster = None
            for cluster in clusters:
                if cluster.get('clusterId') == self.target_cluster_id:
                    target_cluster = cluster
                    break
            
            if target_cluster:
                cluster_name = target_cluster.get('clusterName', 'Unknown')
                print(f"\n▶ 正在刷新区域: {cluster_name}")
                self.logger.info(f"步骤 3/6: 刷新指定区域 {cluster_name}...")
                try:
                    self._init_cluster_details(target_cluster)
                    print(f"✓ 区域 {cluster_name} 刷新完成")
                except Exception as e:
                    self.logger.error(f"刷新区域 {cluster_name} 失败: {e}")
                    print(f"✗ 区域 {cluster_name} 刷新失败: {e}")
            else:
                print(f"⚠ 未找到指定区域 (ID: {self.target_cluster_id})")
                print("  将初始化所有区域")
                self._init_all_clusters(clusters)
        elif self.only_default:
            # 模式2: 只初始化默认区域
            default_cluster = None
            for cluster in clusters:
                if cluster.get('default') is True:
                    default_cluster = cluster
                    break
            
            # 如果没有默认区域，使用第一个非 ac 的区域
            if not default_cluster:
                for cluster in clusters:
                    if cluster.get('clusterName') != 'ac':
                        default_cluster = cluster
                        cluster['default'] = True
                        break
            
            if default_cluster:
                cluster_name = default_cluster.get('clusterName', 'Unknown')
                print(f"\n▶ 仅初始化默认区域: {cluster_name}")
                print(f"  (其他区域将在切换时自动刷新)")
                self.logger.info(f"步骤 3/6: 初始化默认区域 {cluster_name}...")
                try:
                    self._init_cluster_details(default_cluster)
                    print(f"✓ 默认区域 {cluster_name} 初始化完成")
                except Exception as e:
                    self.logger.error(f"初始化区域 {cluster_name} 失败: {e}")
                    print(f"✗ 区域 {cluster_name} 初始化失败: {e}")
            else:
                print("⚠ 未找到默认区域，将初始化所有区域")
                self._init_all_clusters(clusters)
        else:
            # 模式3: 初始化所有区域
            self._init_all_clusters(clusters)
        
        # 6. 构建新缓存
        self.logger.info("步骤 4/6: 构建缓存数据...")
        new_cache = {
            "clusters": clusters,
            "_meta": {
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "version": "1.0"
            }
        }
        
        # 保留旧的 _expiry 信息（如果有）
        if old_cache and '_expiry' in old_cache:
            new_cache['_expiry'] = old_cache['_expiry']
        
        print("✓ 缓存数据构建完成")
        
        # 7. 保存缓存
        self.logger.info("步骤 5/6: 保存缓存文件...")
        self.cache_mgr.save(new_cache)
        print("✓ 缓存文件保存成功")
        
        # 8. 输出摘要
        self.logger.info("步骤 6/6: 生成摘要...")
        print("\n" + "=" * 60)
        print("缓存初始化完成")
        print("=" * 60)
        print(f"\n缓存文件位置: {get_cache_path()}")
        print(f"\n区域列表:")
        for cluster in clusters:
            default_mark = " [默认]" if cluster.get('default') else ""
            print(f"  - {cluster.get('clusterName')} (ID: {cluster.get('clusterId')}){default_mark}")
            
            # 显示缓存的数据项
            cached_items = []
            if 'hpcUrls' in cluster:
                cached_items.append("HPC")
            if 'aiUrls' in cluster:
                cached_items.append("AI")
            if 'efileUrls' in cluster:
                cached_items.append("文件")
            if 'clusterUserInfo' in cluster:
                cached_items.append("用户")
            if 'JobManagers' in cluster:
                cached_items.append("集群")
            if 'parastors' in cluster:
                cached_items.append("配额")
            if 'walltime' in cluster:
                cached_items.append("机时")
            
            if cached_items:
                print(f"    已缓存: {', '.join(cached_items)}")
        
        print("\n提示:")
        print("- 配额和机时数据将在 1 小时后过期")
        print("- 如需刷新缓存，请重新运行此脚本")
        print(f"- 缓存文件权限建议: chmod 600 {get_cache_path()}")
        
        return True


def switch_default_cluster(cluster_name: str) -> bool:
    """
    切换默认区域
    
    Args:
        cluster_name: 区域名称，如 "华东四区【山东】"
    
    Returns:
        bool: 是否成功
    """
    print("=" * 60)
    print("切换默认区域")
    print("=" * 60)
    
    # 加载缓存
    cache_path = get_cache_path()
    if not cache_path.exists():
        print(f"\n错误: 缓存文件不存在: {cache_path}")
        print("\n请先运行缓存初始化:")
        print("  python scripts/cache.py")
        return False
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except Exception as e:
        print(f"\n错误: 读取缓存文件失败: {e}")
        return False
    
    clusters = cache.get('clusters', [])
    if not clusters:
        print("\n错误: 缓存中没有区域数据")
        return False
    
    # 查找目标区域
    target_found = False
    target_id = None
    
    for cluster in clusters:
        if cluster.get('clusterName') == cluster_name:
            target_found = True
            target_id = cluster.get('clusterId')
            cluster['default'] = True
        else:
            cluster['default'] = False
    
    if not target_found:
        print(f"\n错误: 未找到区域: {cluster_name}")
        print("\n可用的区域:")
        for cluster in clusters:
            name = cluster.get('clusterName', '')
            if name != 'ac':
                current_mark = " (当前默认)" if cluster.get('default') else ""
                print(f"  - {name}{current_mark}")
        return False
    
    # 检查目标区域是否需要刷新（没有详细信息）
    target_cluster = None
    for cluster in clusters:
        if cluster.get('clusterId') == target_id:
            target_cluster = cluster
            break
    
    needs_refresh = False
    if target_cluster:
        # 检查是否有 hpcUrls、aiUrls、efileUrls 等详细信息
        has_details = any(key in target_cluster for key in ['hpcUrls', 'aiUrls', 'efileUrls', 'clusterUserInfo'])
        if not has_details:
            needs_refresh = True
            print(f"\n▶ 区域 {cluster_name} 详细信息未加载，正在刷新...")
    
    if needs_refresh and target_cluster:
        try:
            # 仅刷新目标区域的详细信息，保留其他区域的数据
            print(f"\n▶ 正在刷新区域 {cluster_name} 的详细信息...")
            
            # 创建初始化器用于刷新指定区域
            initializer = CacheInitializer(target_cluster_id=target_id)
            
            # 获取访问凭证（token可能已过期）
            tokens_response = initializer.api.get_tokens()
            code = tokens_response.get('code')
            is_success = (code == 200 or code == '0' or code == 0)
            
            if is_success and 'data' in tokens_response:
                # 更新目标区域的 token
                data = tokens_response.get('data', [])
                for item in data:
                    if item.get('clusterId') == target_id:
                        target_cluster['token'] = item.get('token')
                        break
                
                # 初始化目标区域的详细信息
                initializer._init_cluster_details(target_cluster)
                print(f"✓ 区域 {cluster_name} 刷新完成")
            else:
                print(f"⚠ 获取访问凭证失败，将使用现有数据")
        except Exception as e:
            print(f"⚠ 刷新区域失败: {e}")
            print(f"  将使用现有数据")
    
    # 保存缓存
    try:
        cache['_meta'] = cache.get('_meta', {})
        cache['_meta']['updated_at'] = int(time.time())
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 成功切换默认区域为: {cluster_name}")
        print(f"  区域 ID: {target_id}")
        
        print("\n区域列表:")
        for cluster in clusters:
            name = cluster.get('clusterName', '')
            default_mark = " [默认]" if cluster.get('default') else ""
            if name != 'ac':
                print(f"  - {name}{default_mark}")
        
        return True
        
    except Exception as e:
        print(f"\n错误: 保存缓存文件失败: {e}")
        return False


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SCNet Chat 缓存系统 - 初始化和管理 API token 及业务数据缓存',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/cache.py                    # 初始化默认区域缓存（快速）
  python scripts/cache.py --all              # 初始化所有区域缓存（完整）
  python scripts/cache.py --switch "华东四区【山东】"  # 切换默认区域
  python scripts/cache.py --list             # 列出所有区域
        """
    )
    
    parser.add_argument(
        '--switch',
        metavar='NAME',
        type=str,
        help='切换默认区域，指定区域名称'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有可用的区域'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='初始化所有区域的详细信息（默认只初始化默认区域）'
    )
    
    args = parser.parse_args()
    
    # 处理切换默认区域
    if args.switch:
        try:
            success = switch_default_cluster(args.switch)
            exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            exit(1)
        except Exception as e:
            print(f"\n错误: {e}")
            exit(1)
    
    # 处理列出区域
    if args.list:
        try:
            cache_path = get_cache_path()
            if not cache_path.exists():
                print(f"错误: 缓存文件不存在: {cache_path}")
                print("\n请先运行缓存初始化:")
                print("  python scripts/cache.py")
                exit(1)
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            clusters = cache.get('clusters', [])
            
            print("=" * 60)
            print("区域列表")
            print("=" * 60)
            
            for cluster in clusters:
                name = cluster.get('clusterName', '')
                cid = cluster.get('clusterId', '')
                default_mark = " [默认]" if cluster.get('default') else ""
                if name != 'ac':
                    print(f"  - {name} (ID: {cid}){default_mark}")
            
            exit(0)
            
        except Exception as e:
            print(f"错误: {e}")
            exit(1)
    
    # 默认：运行缓存初始化
    try:
        # 根据 --all 参数决定是初始化所有区域还是仅默认区域
        initializer = CacheInitializer(only_default=not args.all)
        success = initializer.run()
        exit(0 if success else 1)
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        exit(1)
    except ValueError as e:
        print(f"\n配置错误: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        exit(1)
    except Exception as e:
        print(f"\n未知错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
