#!/usr/bin/env python3
"""
SCNet 作业管理工具

支持查询、删除和提交作业，通过命令行参数识别操作意图。

使用方法:
    # 查询作业
    python scripts/job.py                          # 查询实时作业列表
    python scripts/job.py --history                # 查询历史作业列表
    python scripts/job.py --job-id 123             # 查询实时作业详情
    python scripts/job.py --history --job-id 123   # 查询历史作业详情
    python scripts/job.py --days 7                 # 查询最近7天的历史作业
    python scripts/job.py --status running         # 按状态筛选实时作业
    
    # 删除作业
    python scripts/job.py --delete --job-id 123    # 删除指定作业
    
    # 提交作业（需要指定 --cmd 参数）
    python scripts/job.py --submit --cmd "sleep 100" --queue comp
    
    # 高级筛选
    python scripts/job.py --queue debug --status running
    python scripts/job.py --job-name "test*"
    python scripts/job.py --start-time "2024-01-01 00:00:00" --end-time "2024-01-31 23:59:59"

注意：建议使用自然语言入口 scnet.py 进行作业提交，使用更方便：
    python scripts/scnet.py "提交作业 sleep 100 --queue comp"
    python scripts/scnet.py "提交作业帮助"
"""

import json
import sys
import ssl
import time
import urllib.request
import urllib.error
import urllib.parse
import base64
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Windows 终端兼容处理
import compat

# 导入公共工具模块
from utils import (
    Colors, print_header, print_section, print_item,
    print_success, print_warning, print_error, print_info,
    load_cache, get_cached_cache_path
)

# 导入配置文件
from config import (
    CONFIG_PATH, CACHE_PATH, get_cache_path, get_cached_cache_path as _get_cached_cache_path,
    JobTimeout, DEFAULT_JOB_NNODE, DEFAULT_JOB_WALL_TIME,
    DEFAULT_JOB_APPNAME, DEFAULT_SUBMIT_TYPE
)

# SSL 上下文
SSL_CONTEXT = ssl.create_default_context()

# 作业状态映射
JOB_STATUS_MAP = {
    'statR': '运行',
    'statQ': '排队',
    'statH': '保留',
    'statS': '挂起',
    'statE': '退出',
    'statC': '完成',
    'statW': '等待',
    'statX': '其他',
    'statDE': '取消',
    'statD': '失败',
    'statT': '超时',
    'statN': '节点异常',
    'statRQ': '重新运行',
    'running': 'statR',
    'queue': 'statQ',
    'queued': 'statQ',
    'hold': 'statH',
    'suspend': 'statS',
    'exit': 'statE',
    'completed': 'statC',
    'complete': 'statC',
    'wait': 'statW',
    'waiting': 'statW',
    'other': 'statX',
    'cancelled': 'statDE',
    'failed': 'statD',
    'timeout': 'statT',
    'nodefail': 'statN',
    'rerun': 'statRQ',
}


def _refresh_cache() -> bool:
    """
    调用 cache.py 刷新缓存
    
    Returns:
        True 表示刷新成功，False 表示刷新失败
    """
    import subprocess
    import sys
    
    try:
        # 获取 scripts 目录路径
        scripts_dir = Path(__file__).parent
        cache_script = scripts_dir / "cache.py"
        
        if not cache_script.exists():
            print_error(f"缓存脚本不存在: {cache_script}")
            return False
        
        # 运行缓存初始化脚本
        # 超时设置为子查询超时总和: 35秒
        result = subprocess.run(
            [sys.executable, str(cache_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=35
        )
        
        if result.returncode == 0:
            print_success("缓存刷新成功")
            return True
        else:
            print_error(f"缓存刷新失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("缓存刷新超时（超过 2 分钟）")
        return False
    except Exception as e:
        print_error(f"缓存刷新异常: {e}")
        return False


def load_config_username() -> Optional[str]:
    """从配置文件加载用户名"""
    if not CONFIG_PATH.exists():
        print_error(f"配置文件不存在: {CONFIG_PATH}")
        return None
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == 'SCNET_USER':
                        return value.strip()
        print_error("配置文件中未找到 SCNET_USER")
        return None
    except Exception as e:
        print_error(f"读取配置文件失败: {e}")
        return None


def get_default_cluster(cache: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """获取默认区域"""
    clusters = cache.get('clusters', [])
    for cluster in clusters:
        if cluster.get('default') is True:
            return cluster
    # 如果没有设置默认，返回第一个非 ac 的区域
    for cluster in clusters:
        if cluster.get('clusterName') != 'ac':
            return cluster
    return None


def get_compute_user(token: str) -> str:
    """从 token 解码获取 computeUser"""
    try:
        parts = token.split('.')
        if len(parts) == 3:
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            token_data = json.loads(decoded)
            return token_data.get('computeUser', '')
    except Exception:
        pass
    return ''


def get_ac_cluster_token(cache: Dict[str, Any]) -> Optional[str]:
    """从缓存中获取 clusterName 为 'ac' 的 token"""
    for cluster in cache.get('clusters', []):
        if cluster.get('clusterName') == 'ac':
            return cluster.get('token')
    return None


def format_datetime(time_str: str, is_end_time: bool = False) -> str:
    """
    格式化时间字符串，确保包含时分秒
    
    支持的输入格式:
        - 2024-01-01
        - 2024-01-01 00:00
        - 2024-01-01 00:00:00
    
    输出格式:
        - 开始时间: 2024-01-01 00:00:00
        - 结束时间: 2024-01-31 23:59:59
    
    Args:
        time_str: 输入的时间字符串
        is_end_time: 是否为结束时间，如果是则补全为 23:59:59
    """
    if not time_str:
        return time_str
    
    time_str = time_str.strip()
    
    # 如果已经是完整格式，直接返回
    if len(time_str) == 19 and ':' in time_str:
        return time_str
    
    # 只有日期部分 (2024-01-01)
    if len(time_str) == 10 and time_str.count('-') == 2:
        if is_end_time:
            return time_str + " 23:59:59"
        else:
            return time_str + " 00:00:00"
    
    # 日期 + 时分 (2024-01-01 00:00)
    if len(time_str) == 16 and time_str.count(':') == 1:
        if is_end_time:
            return time_str + ":59"
        else:
            return time_str + ":00"
    
    return time_str


def get_ac_url_from_config() -> str:
    """从配置文件中获取 SCNET_AC_URL，默认为 https://www.scnet.cn"""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == 'SCNET_AC_URL':
                            return value.strip().rstrip('/')
    except Exception:
        pass
    return 'https://www.scnet.cn'


class JobAPI:
    """作业查询 API 客户端"""
    
    def __init__(self, cluster: Dict[str, Any], cache: Dict[str, Any]):
        self.cluster = cluster
        self.cache = cache
        self.token = cluster.get('token', '')
        self.hpc_url = self._get_hpc_url()
        self.job_manager_id = self._get_job_manager_id()
        self.cluster_id = self._get_cluster_id()
        self.compute_user = get_compute_user(self.token)
        self.cluster_name = cluster.get('clusterName', '')
        # AC 接口相关配置
        self.ac_url = get_ac_url_from_config()
        self.job_api_url = 'https://api.scnet.cn/api/job'
        self.ac_token = get_ac_cluster_token(cache) or self.token
    
    def _get_hpc_url(self) -> str:
        """获取 HPC 服务 URL"""
        hpc_urls = self.cluster.get('hpcUrls', [])
        if hpc_urls and len(hpc_urls) > 0:
            return hpc_urls[0].get('url', '')
        return ''
    
    def _get_job_manager_id(self) -> str:
        """获取 JobManager ID"""
        job_managers = self.cluster.get('JobManagers', [])
        if job_managers and len(job_managers) > 0:
            return str(job_managers[0].get('id', ''))
        return ''
    
    def _get_cluster_id(self) -> str:
        """获取当前区域/集群 ID。"""
        cluster_id = self.cluster.get('clusterId') or self.cluster.get('id') or ''
        return str(cluster_id) if cluster_id else ''
    
    # 从配置文件导入超时时间
    TIMEOUT_QUERY_REALTIME_JOBS = JobTimeout.QUERY_REALTIME_JOBS
    TIMEOUT_QUERY_REALTIME_JOB_DETAIL = JobTimeout.QUERY_REALTIME_JOB_DETAIL
    TIMEOUT_QUERY_HISTORY_JOBS = JobTimeout.QUERY_HISTORY_JOBS
    TIMEOUT_QUERY_HISTORY_JOB_DETAIL = JobTimeout.QUERY_HISTORY_JOB_DETAIL
    TIMEOUT_DELETE_JOB = JobTimeout.DELETE_JOB
    TIMEOUT_SUBMIT_JOB = JobTimeout.SUBMIT_JOB
    TIMEOUT_USER_QUEUES = JobTimeout.USER_QUEUES
    TIMEOUT_CLUSTER_INFO = JobTimeout.CLUSTER_INFO
    
    # 兼容性保留
    TIMEOUT_QUICK = JobTimeout.QUICK
    TIMEOUT_NORMAL = JobTimeout.NORMAL
    TIMEOUT_COMPLEX = JobTimeout.COMPLEX
    TIMEOUT_SUBMIT_OLD = JobTimeout.SUBMIT_OLD
    
    def _make_request(self, url: str, headers: Dict[str, str], data: Optional[bytes] = None, 
                      method: str = 'GET', params: Optional[Dict[str, Any]] = None,
                      timeout: int = None) -> Optional[Dict[str, Any]]:
        """发起 HTTP 请求"""
        # 默认使用普通查询超时
        if timeout is None:
            timeout = self.TIMEOUT_NORMAL
            
        # 实现带重试的请求
        max_retries = 2
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                # 如果有查询参数，添加到 URL
                request_url = url
                if params:
                    query_string = urllib.parse.urlencode(params)
                    request_url = f"{url}?{query_string}"
                
                req = urllib.request.Request(
                    request_url,
                    data=data,
                    headers=headers,
                    method=method
                )
                
                # 每次重试都创建新的 SSL 上下文
                ssl_context = ssl.create_default_context()
                
                with urllib.request.urlopen(req, context=ssl_context, timeout=timeout) as response:
                    response_body = response.read().decode('utf-8')
                    return json.loads(response_body)
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8')
                try:
                    return json.loads(error_body)
                except:
                    return {"code": e.code, "msg": error_body}
                    
            except Exception as e:
                last_error = str(e)
                error_msg = str(e).lower()
                
                # 检查是否是可重试的错误
                if any(err in error_msg for err in ['ssl', 'eof', 'connection', 'reset', 'timeout']):
                    retry_count += 1
                    if retry_count <= max_retries:
                        import time
                        time.sleep(0.5 * retry_count)  # 递增延迟
                        continue
                
                # 非可重试错误或重试次数用尽
                return {"code": -1, "msg": last_error}
        
        # 所有重试都失败
        return {"code": -1, "msg": f"请求失败（已重试{max_retries}次）: {last_error}"}
    
    def _refresh_ac_token(self) -> bool:
        """刷新 AC token，用于 v3 聚合作业接口 auth_fail 后重试。"""
        try:
            from scnet_chat import get_tokens

            config_values: Dict[str, str] = {}
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        key, value = line.split('=', 1)
                        config_values[key.strip()] = value.strip()

            access_key = config_values.get('SCNET_ACCESS_KEY')
            secret_key = config_values.get('SCNET_SECRET_KEY')
            username = config_values.get('SCNET_USER')
            if not (access_key and secret_key and username):
                return False

            token_response = None
            for _ in range(3):
                token_response = get_tokens(access_key, secret_key, username)
                if isinstance(token_response, dict) and str(token_response.get('code')) == '0':
                    break
                time.sleep(0.5)
            if not isinstance(token_response, dict) or str(token_response.get('code')) != '0':
                return False

            new_token = None
            for item in token_response.get('data', []) or []:
                if item.get('clusterName') == 'ac' and item.get('token'):
                    new_token = item['token']
                    break
            if not new_token:
                return False

            self.ac_token = new_token
            # 写回缓存，避免后续新进程继续使用过期 AC token。
            try:
                for cluster in self.cache.get('clusters', []) or []:
                    if cluster.get('clusterName') == 'ac':
                        cluster['token'] = new_token
                        break
                cache_path = get_cached_cache_path()
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _build_v3_job_list_body(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """构建 v3 作业列表请求体；page/size 是 v3 必填参数。"""
        body: Dict[str, Any] = {
            'page': max(int(params.get('page') or 1), 1),
            'size': min(max(int(params.get('size') or 10), 1), 100),
        }

        optional_mapping = {
            'cluster_id': 'clusterId',
            'queue': 'queue',
            'status': 'state',
            'cluster_user_name': 'clusterUserName',
            'job_name': 'name',
        }
        for src, dst in optional_mapping.items():
            value = params.get(src)
            if value not in (None, ''):
                body[dst] = value

        if params.get('start_time'):
            body['startTime'] = format_datetime(params['start_time'], is_end_time=False)
        if params.get('end_time'):
            body['endTime'] = format_datetime(params['end_time'], is_end_time=True)
        if params.get('days') and not params.get('start_time'):
            end = datetime.now()
            start = end - timedelta(days=params['days'])
            body['startTime'] = start.strftime('%Y-%m-%d %H:%M:%S')
            body['endTime'] = end.strftime('%Y-%m-%d %H:%M:%S')

        return body

    def _normalize_v3_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """补齐旧展示函数依赖的字段名，同时保留 v3 原始字段。"""
        if not isinstance(job, dict):
            return job
        normalized = dict(job)
        aliases = {
            'jobId': job.get('jobId') or job.get('id'),
            'jobName': job.get('jobName') or job.get('name'),
            'jobStatus': job.get('jobStatus') or job.get('state'),
            'jobState': job.get('jobState') or job.get('state'),
            'jobStartTime': job.get('jobStartTime') or job.get('startTime'),
            'jobEndTime': job.get('jobEndTime') or job.get('endTime'),
            'jobRunTime': job.get('jobRunTime') or job.get('runTime'),
            'jobWalltimeUsed': job.get('jobWalltimeUsed') or job.get('runTime'),
            'jobExitStatus': job.get('jobExitStatus') or job.get('exitCode'),
            'jobProcNum': job.get('jobProcNum') or job.get('usedProcNum') or job.get('reqProcNum'),
            'procNumUsed': job.get('procNumUsed') or job.get('usedProcNum') or job.get('reqProcNum'),
            'nodeUsed': job.get('nodeUsed') or job.get('execHost') or job.get('usedNodeNum'),
            'nodect': job.get('nodect') or job.get('usedNodeNum') or job.get('reqNodeNum'),
            'workdir': job.get('workdir') or job.get('workDir'),
            'userName': job.get('userName') or job.get('clusterUserName'),
            'user': job.get('user') or job.get('clusterUserName'),
        }
        for key, value in aliases.items():
            if normalized.get(key) in (None, '') and value not in (None, ''):
                normalized[key] = value
        return normalized

    def _normalize_v3_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self._normalize_v3_job(job) for job in jobs or []]

    def _query_v3_jobs(self, endpoint: str, params: Dict[str, Any], timeout: int) -> Tuple[Optional[List[Dict]], int, str]:
        if not self.ac_token:
            return None, 0, "AC 认证 token 不可用"

        url = f"{self.job_api_url}/v3/jobs/{endpoint}"
        headers = {'token': self.ac_token, 'Content-Type': 'application/json'}
        data = json.dumps(self._build_v3_job_list_body(params), ensure_ascii=False).encode('utf-8')
        result = self._make_request(url, headers, data=data, method='POST', timeout=timeout)
        if result and (str(result.get('code')) == '402' or str(result.get('msg')).lower() == 'auth_fail'):
            if self._refresh_ac_token():
                headers['token'] = self.ac_token
                result = self._make_request(url, headers, data=data, method='POST', timeout=timeout)

        if result and str(result.get('code')) == '0':
            data_obj = result.get('data', {})
            if isinstance(data_obj, dict):
                job_list = data_obj.get('records', []) or data_obj.get('list', []) or data_obj.get('items', [])
                total = data_obj.get('total', len(job_list))
            elif isinstance(data_obj, list):
                job_list = data_obj
                total = len(job_list)
            else:
                job_list = []
                total = 0
            return self._normalize_v3_jobs(job_list), total, ""
        return None, 0, (result or {}).get('msg', '查询失败')

    def query_brief_jobs(self, jobs: List[Dict[str, Any]]) -> Tuple[Optional[List[Dict]], str]:
        """批量查询作业简要信息。jobs 按 clusterId/managerId 分组提交 ids。"""
        if not self.ac_token:
            return None, "AC 认证 token 不可用"
        grouped: Dict[Tuple[Any, Any], List[str]] = {}
        for job in jobs or []:
            cluster_id = job.get('clusterId') or job.get('cluster_id')
            manager_id = job.get('managerId') or job.get('jobManagerId') or job.get('jobmanagerId')
            job_id = job.get('id') or job.get('jobId') or job.get('job_id')
            if cluster_id and manager_id and job_id:
                grouped.setdefault((cluster_id, manager_id), []).append(str(job_id))
        if not grouped:
            return [], ""

        payload = {
            'jobs': [
                {'clusterId': int(cluster_id), 'managerId': int(manager_id), 'ids': ids[:100]}
                for (cluster_id, manager_id), ids in grouped.items()
            ]
        }
        url = f"{self.job_api_url}/v3/jobs/brief-job"
        headers = {'token': self.ac_token, 'Content-Type': 'application/json'}
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        result = self._make_request(url, headers, data=data, method='POST', timeout=self.TIMEOUT_NORMAL)
        if result and (str(result.get('code')) == '402' or str(result.get('msg')).lower() == 'auth_fail'):
            if self._refresh_ac_token():
                headers['token'] = self.ac_token
                result = self._make_request(url, headers, data=data, method='POST', timeout=self.TIMEOUT_NORMAL)
        if result and str(result.get('code')) == '0':
            data_obj = result.get('data', [])
            return self._normalize_v3_jobs(data_obj if isinstance(data_obj, list) else []), ""
        return None, (result or {}).get('msg', '查询失败')

    def _query_v3_job_detail(self, job_id: str, source: str = 'all') -> Tuple[Optional[Dict], str]:
        if not self.ac_token:
            return None, "AC 认证 token 不可用"
        if not self.cluster_id or not self.job_manager_id:
            return None, "当前区域缺少 clusterId 或 JobManager ID"
        source = source if source in ('active', 'history', 'all') else 'all'
        url = (
            f"{self.job_api_url}/v3/job/{urllib.parse.quote(str(self.cluster_id))}/"
            f"{urllib.parse.quote(str(self.job_manager_id))}/{source}/{urllib.parse.quote(str(job_id))}"
        )
        headers = {'token': self.ac_token, 'Content-Type': 'application/json'}
        result = self._make_request(url, headers, timeout=self.TIMEOUT_QUERY_REALTIME_JOB_DETAIL)
        if result and (str(result.get('code')) == '402' or str(result.get('msg')).lower() == 'auth_fail'):
            if self._refresh_ac_token():
                headers['token'] = self.ac_token
                result = self._make_request(url, headers, timeout=self.TIMEOUT_QUERY_REALTIME_JOB_DETAIL)
        if result and str(result.get('code')) == '0':
            data_obj = result.get('data')
            return (self._normalize_v3_job(data_obj), "") if data_obj else (None, "")
        return None, (result or {}).get('msg', '查询失败')

    def query_realtime_jobs(self, params: Dict[str, Any]) -> Tuple[Optional[List[Dict]], int, str]:
        """
        查询实时作业列表。
        v3: POST https://api.scnet.cn/api/job/v3/jobs/active-job
        """
        return self._query_v3_jobs('active-job', params, self.TIMEOUT_QUERY_REALTIME_JOBS)

    def query_realtime_job_detail(self, job_id: str) -> Tuple[Optional[Dict], str]:
        """
        查询实时作业详情。
        v3: GET /v3/job/{clusterId}/{managerId}/active/{id}
        """
        return self._query_v3_job_detail(job_id, source='active')
    
    def query_user_queues(self, username: str, raw_response: bool = False) -> Tuple[Optional[List[str]], str, Optional[Dict]]:
        """
        查询用户可访问队列
        GET /hpc/openapi/v2/queuenames/users/{username}
        
        Args:
            username: 用户名
            raw_response: 是否返回原始响应数据
        
        Returns: (queues_list, error_message, raw_data)
        """
        if not self.hpc_url or not self.job_manager_id:
            return None, "HPC 服务不可用", None
        
        url = f"{self.hpc_url}/hpc/openapi/v2/queuenames/users/{urllib.parse.quote(username)}"
        
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        params = {'strJobManagerID': self.job_manager_id}
        
        result = self._make_request(url, headers, params=params, timeout=self.TIMEOUT_USER_QUEUES)
        
        if result and str(result.get('code')) == '0':
            data = result.get('data', [])
            # 处理两种可能的数据结构：
            # 1. data 是列表（直接返回队列列表）
            # 2. data 是字典，包含 list 字段
            if isinstance(data, list):
                queues = data
            elif isinstance(data, dict):
                queues = data.get('list', [])
            else:
                queues = []
            if raw_response:
                return queues, "", result
            return queues, "", None
        else:
            if raw_response:
                return None, result.get('msg', '查询失败'), result
            return None, result.get('msg', '查询失败'), None
    
    def get_cluster_info(self) -> Tuple[Optional[List[Dict]], str]:
        """
        查询集群信息
        GET /hpc/openapi/v2/cluster
        
        Returns: (job_managers_list, error_message)
        """
        if not self.hpc_url:
            return None, "HPC 服务不可用"
        
        url = f"{self.hpc_url}/hpc/openapi/v2/cluster"
        
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        result = self._make_request(url, headers, timeout=self.TIMEOUT_CLUSTER_INFO)
        
        if result and str(result.get('code')) == '0':
            data = result.get('data', [])
            return data, ""
        else:
            return None, result.get('msg', '查询失败')
    
    def query_history_jobs(self, params: Dict[str, Any]) -> Tuple[Optional[List[Dict]], int, str]:
        """
        查询历史作业列表。
        v3: POST https://api.scnet.cn/api/job/v3/jobs/history-job
        """
        return self._query_v3_jobs('history-job', params, self.TIMEOUT_QUERY_HISTORY_JOBS)

    def query_history_job_detail(self, job_id: str, acct_time: str = None) -> Tuple[Optional[Dict], str]:
        """
        查询历史作业详情。
        v3: GET /v3/job/{clusterId}/{managerId}/history/{id}
        acct_time 为旧接口参数，v3 不再使用。
        """
        return self._query_v3_job_detail(job_id, source='history')

    def query_job_detail(self, job_id: str) -> Tuple[Optional[Dict], str]:
        """
        在当前区域中查询作业详情，source=all 同时覆盖实时和历史作业。
        """
        return self._query_v3_job_detail(job_id, source='all')
    
    def delete_job(self, job_id: str, username: str) -> Tuple[bool, str]:
        """
        删除作业
        DELETE /hpc/openapi/v2/jobs
        
        Args:
            job_id: 作业ID
            username: 用户名（从配置文件读取）
        
        Returns: (success, message)
        """
        if not self.hpc_url or not self.job_manager_id:
            return False, "HPC 服务不可用"
        
        url = f"{self.hpc_url}/hpc/openapi/v2/jobs"
        
        # 构建 strJobInfoMap: 调度器ID,用户名:作业号:
        str_job_info_map = f"{self.job_manager_id},{username}:{job_id}:"
        
        # 构建请求体数据
        payload = {
            'jobMethod': '5',
            'strJobInfoMap': str_job_info_map
        }
        
        # 编码数据为 application/x-www-form-urlencoded 格式
        data = urllib.parse.urlencode(payload).encode('utf-8')
        
        headers = {
            'token': self.token,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        result = self._make_request(url, headers, data=data, method='DELETE', timeout=self.TIMEOUT_DELETE_JOB)
        
        if result and str(result.get('code')) == '0':
            return True, result.get('msg', '删除成功')
        else:
            return False, result.get('msg', '删除失败')
    
    def submit_job(self, job_params: Dict[str, str]) -> Tuple[Optional[str], str]:
        """
        提交作业
        POST /hpc/openapi/v2/apptemplates/BASIC/BASE/job
        
        Args:
            job_params: 作业参数字典，包含 mapAppJobInfo 中的各个字段
        
        Returns: (job_id, message)
        """
        if not self.hpc_url or not self.job_manager_id:
            return None, "HPC 服务不可用"
        
        url = f"{self.hpc_url}/hpc/openapi/v2/apptemplates/BASIC/BASE/job"
        
        # 构建 mapAppJobInfo
        map_app_job_info = {}
        
        # 生成带时间戳的默认作业名称
        default_job_name = datetime.now().strftime('job-%Y-%m-%d-%H-%M-%S')
        
        # 必填参数（有默认值或必须提供）
        map_app_job_info['GAP_CMD_FILE'] = job_params.get('cmd', 'sleep 60')
        map_app_job_info['GAP_NNODE'] = job_params.get('nnode', '1')
        map_app_job_info['GAP_NODE_STRING'] = job_params.get('node_string', '')
        map_app_job_info['GAP_SUBMIT_TYPE'] = job_params.get('submit_type', 'cmd')
        map_app_job_info['GAP_JOB_NAME'] = job_params.get('job_name', default_job_name)
        
        # 工作目录
        work_dir = job_params.get('work_dir', '')
        map_app_job_info['GAP_WORK_DIR'] = work_dir
        map_app_job_info['GAP_QUEUE'] = job_params.get('queue', '')
        map_app_job_info['GAP_WALL_TIME'] = job_params.get('wall_time', '24:00:00')
        map_app_job_info['GAP_APPNAME'] = job_params.get('appname', 'BASE')
        
        # 标准输出和错误文件路径（如果未指定，自动生成）
        std_out = job_params.get('std_out', '')
        std_err = job_params.get('std_err', '')
        if work_dir:
            if not std_out:
                std_out = f"{work_dir}/std.out.%j"
            if not std_err:
                std_err = f"{work_dir}/std.err.%j"
        map_app_job_info['GAP_STD_OUT_FILE'] = std_out
        map_app_job_info['GAP_STD_ERR_FILE'] = std_err
        
        # 可选参数
        if job_params.get('nproc'):
            map_app_job_info['GAP_NPROC'] = job_params['nproc']
        if job_params.get('ppn'):
            map_app_job_info['GAP_PPN'] = job_params['ppn']
        if job_params.get('ngpu'):
            map_app_job_info['GAP_NGPU'] = job_params['ngpu']
        if job_params.get('ndcu'):
            map_app_job_info['GAP_NDCU'] = job_params['ndcu']
        if job_params.get('job_mem'):
            map_app_job_info['GAP_JOB_MEM'] = job_params['job_mem']
        if job_params.get('exclusive'):
            map_app_job_info['GAP_EXCLUSIVE'] = job_params['exclusive']
        if job_params.get('multi_sub'):
            map_app_job_info['GAP_MULTI_SUB'] = job_params['multi_sub']
        
        # 构建请求体
        payload = {
            'strJobManagerID': self.job_manager_id,
            'mapAppJobInfo': map_app_job_info
        }
        
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        result = self._make_request(url, headers, data=data, method='POST', timeout=self.TIMEOUT_SUBMIT_JOB)
        
        if result and str(result.get('code')) == '0':
            return result.get('data'), result.get('msg', '提交成功')
        else:
            return None, result.get('msg', '提交失败')


def parse_status(status: str) -> str:
    """解析作业状态"""
    return JOB_STATUS_MAP.get(status.lower(), status)


def format_job_status(status_code: str) -> str:
    """格式化作业状态显示"""
    status_map = {
        'statR': ('运行', Colors.GREEN),
        'statQ': ('排队', Colors.YELLOW),
        'statH': ('保留', Colors.CYAN),
        'statS': ('挂起', Colors.RED),
        'statE': ('退出', Colors.RED),
        'statC': ('完成', Colors.GREEN),
        'statW': ('等待', Colors.YELLOW),
        'statX': ('其他', Colors.DIM),
        'statDE': ('取消', Colors.YELLOW),
        'statD': ('失败', Colors.RED),
        'statT': ('超时', Colors.RED),
        'statN': ('节点异常', Colors.RED),
        'statRQ': ('重新运行', Colors.CYAN),
    }
    name, color = status_map.get(status_code, (status_code, Colors.END))
    return f"{color}{name}{Colors.END}"


def resolve_realtime_status(job: Dict) -> str:
    """
    解析实时作业的真实状态。
    平台顶层 jobStatus 有时会延迟同步（如 statC 实际已失败），
    此时优先以 jobInitAttr.JobState 或 reason 字段为准。
    """
    status = job.get('jobStatus', 'N/A')
    init_attr = job.get('jobInitAttr') or {}
    inner_state = init_attr.get('JobState', '')
    reason = job.get('reason', '')
    
    # statC 完成状态下，若底层调度器状态为 FAILED 或 reason 为非零退出码，则真实状态为失败(statD)
    if status == 'statC' and (inner_state == 'FAILED' or reason == 'NonZeroExitCode'):
        return 'statD'
    return status


def display_query_params(api: JobAPI, params: Dict[str, Any], is_history: bool = False, is_ac_api: bool = True):
    """显示查询条件参数
    
    Args:
        api: JobAPI 实例
        params: 查询参数
        is_history: 是否为历史作业查询
        is_ac_api: 是否为AC接口（实时/历史作业列表），如果是则显示"所有区域"
    """
    print_section("🔍 查询条件")
    
    # AC接口查询所有区域，其他接口查询当前区域
    if is_ac_api:
        print_item("区域", "所有区域（AC聚合查询）")
        print_item("AC Token", f"{api.ac_token[:20]}..." if api.ac_token else "N/A")
    else:
        print_item("区域", api.cluster_name)
        print_item("JobManager ID", api.job_manager_id)
    
    print_item("查询类型", "历史作业" if is_history else "实时作业")
    
    if params.get('job_id'):
        print_item("作业ID", params['job_id'])
    if params.get('job_name'):
        print_item("作业名称", params['job_name'])
    if params.get('queue'):
        print_item("队列", params['queue'])
    if params.get('status'):
        print_item("状态", params['status'])
    if params.get('cluster_id'):
        print_item("区域ID", params['cluster_id'])
    # if params.get('page') and params.get('page') != 1:
    print_item("页码", params['page'])
    # if params.get('size') and params.get('size') != 10:
    print_item("每页条数", params['size'])
    if params.get('days'):
        print_item("时间范围", f"最近 {params['days']} 天")
    elif params.get('start_time') and params.get('end_time'):
        print_item("开始时间", params['start_time'])
        print_item("结束时间", params['end_time'])
    else:
        # 显示默认时间范围（最近7天）
        print_item("时间范围", "最近 7 天（默认）")
    
    print()


def display_realtime_jobs(jobs: List[Dict], total: int, group_by_cluster: bool = True):
    """显示实时作业列表
    
    Args:
        jobs: 作业列表
        total: 作业总数
        group_by_cluster: 是否按区域分组显示（AC聚合查询时启用）
    """
    if not jobs:
        print_warning("未找到实时作业")
        return
    
    if group_by_cluster:
        # 按区域分组
        from collections import defaultdict
        cluster_jobs = defaultdict(list)
        for job in jobs:
            cluster_name = job.get('clusterName', '未知区域')
            cluster_jobs[cluster_name].append(job)
        
        print_section(f"📋 实时作业列表 (共 {total} 条)")
        print()
        
        # 按区域名称排序显示
        for cluster_name, cluster_job_list in sorted(cluster_jobs.items()):
            print(f"  {Colors.BOLD}{Colors.CYAN}▶ {cluster_name} ({len(cluster_job_list)} 条){Colors.END}")
            print(f"  {Colors.CYAN}{'─' * 50}{Colors.END}")
            
            for i, job in enumerate(cluster_job_list, 1):
                job_id = job.get('jobId', 'N/A')
                job_name = job.get('jobName', 'N/A')
                status = job.get('jobStatus', 'N/A')
                queue = job.get('queue', 'N/A')
                nodes = job.get('nodeUsed', 'N/A')
                cpus = job.get('procNumUsed', 0)
                runtime = job.get('jobRunTime', 'N/A')
                
                real_status = resolve_realtime_status(job)
                status_display = format_job_status(real_status)
                
                print(f"\n    {Colors.BOLD}{i}. 作业 {job_id}{Colors.END}")
                print(f"       名称: {Colors.CYAN}{job_name}{Colors.END}")
                print(f"       状态: {status_display}")
                print(f"       队列: {queue}")
                print(f"       节点: {nodes}")
                print(f"       CPU: {cpus} 核")
                print(f"       运行时间: {runtime}")
            
            print()  # 区域之间空行
    else:
        print_section(f"📋 实时作业列表 (共 {total} 条)")
        
        for i, job in enumerate(jobs, 1):
            job_id = job.get('jobId', 'N/A')
            job_name = job.get('jobName', 'N/A')
            status = job.get('jobStatus', 'N/A')
            queue = job.get('queue', 'N/A')
            nodes = job.get('nodeUsed', 'N/A')
            cpus = job.get('procNumUsed', 0)
            runtime = job.get('jobRunTime', 'N/A')
            
            real_status = resolve_realtime_status(job)
            status_display = format_job_status(real_status)
            
            print(f"\n  {Colors.BOLD}{i}. 作业 {job_id}{Colors.END}")
            print(f"     名称: {Colors.CYAN}{job_name}{Colors.END}")
            print(f"     状态: {status_display}")
            print(f"     队列: {queue}")
            print(f"     节点: {nodes}")
            print(f"     CPU: {cpus} 核")
            print(f"     运行时间: {runtime}")


def display_realtime_job_detail(job: Dict):
    """显示实时作业详情"""
    print_section("📄 实时作业详情")
    
    real_status = resolve_realtime_status(job)
    print_item("作业ID", job.get('jobId', 'N/A'))
    print_item("作业名称", job.get('jobName', 'N/A'))
    print_item("状态", format_job_status(real_status))
    print_item("队列", job.get('queue', 'N/A'))
    print_item("用户", job.get('user', 'N/A'))
    print_item("工作目录", job.get('workDir', 'N/A'))
    print_item("启动时间", job.get('jobStartTime', 'N/A'))
    print_item("运行时间", job.get('jobRunTime', 'N/A'))
    print_item("使用节点", job.get('nodeUsed', 'N/A'))
    print_item("CPU核数", f"{job.get('procNumUsed', 0)} 核")
    print_item("标准输出", job.get('outputPath', 'N/A'))
    print_item("错误输出", job.get('errorPath', 'N/A'))
    
    # 调度器信息
    print(f"\n  {Colors.BOLD}调度器信息:{Colors.END}")
    print_item("调度器", job.get('jobmanagerName', 'N/A'), indent=1)
    print_item("类型", job.get('jobmanagerType', 'N/A'), indent=1)


def display_history_jobs(jobs: List[Dict], total: int, group_by_cluster: bool = True):
    """显示历史作业列表
    
    Args:
        jobs: 作业列表
        total: 作业总数
        group_by_cluster: 是否按区域分组显示（AC聚合查询时启用）
    """
    if not jobs:
        print_warning("未找到历史作业")
        return
    
    if group_by_cluster:
        # 按区域分组
        from collections import defaultdict
        cluster_jobs = defaultdict(list)
        for job in jobs:
            cluster_name = job.get('clusterName', '未知区域')
            cluster_jobs[cluster_name].append(job)
        
        print_section(f"📋 历史作业列表 (共 {total} 条)")
        print()
        
        # 按区域名称排序显示
        for cluster_name, cluster_job_list in sorted(cluster_jobs.items()):
            print(f"  {Colors.BOLD}{Colors.CYAN}▶ {cluster_name} ({len(cluster_job_list)} 条){Colors.END}")
            print(f"  {Colors.CYAN}{'─' * 50}{Colors.END}")
            
            for i, job in enumerate(cluster_job_list, 1):
                job_id = job.get('jobId', 'N/A')
                job_name = job.get('jobName', 'N/A')
                status = job.get('jobState', 'N/A')
                queue = job.get('queue', 'N/A')
                start_time = job.get('jobStartTime', 'N/A')
                end_time = job.get('jobEndTime', 'N/A')
                walltime = job.get('jobWalltimeUsed', 'N/A')
                
                status_display = format_job_status(status)
                
                print(f"\n    {Colors.BOLD}{i}. 作业 {job_id}{Colors.END}")
                print(f"       名称: {Colors.CYAN}{job_name}{Colors.END}")
                print(f"       状态: {status_display}")
                print(f"       队列: {queue}")
                print(f"       开始: {start_time}")
                print(f"       结束: {end_time}")
                print(f"       运行时长: {walltime} 秒")
            
            print()  # 区域之间空行
    else:
        print_section(f"📋 历史作业列表 (共 {total} 条)")
        
        for i, job in enumerate(jobs, 1):
            job_id = job.get('jobId', 'N/A')
            job_name = job.get('jobName', 'N/A')
            status = job.get('jobState', 'N/A')
            queue = job.get('queue', 'N/A')
            start_time = job.get('jobStartTime', 'N/A')
            end_time = job.get('jobEndTime', 'N/A')
            walltime = job.get('jobWalltimeUsed', 'N/A')
            
            status_display = format_job_status(status)
            
            print(f"\n  {Colors.BOLD}{i}. 作业 {job_id}{Colors.END}")
            print(f"     名称: {Colors.CYAN}{job_name}{Colors.END}")
            print(f"     状态: {status_display}")
            print(f"     队列: {queue}")
            print(f"     开始: {start_time}")
            print(f"     结束: {end_time}")
            print(f"     运行时长: {walltime} 秒")


def display_history_job_detail(job: Dict):
    """显示历史作业详情"""
    print_section("📄 历史作业详情")
    
    print_item("作业ID", job.get('jobId', 'N/A'))
    print_item("作业名称", job.get('jobName', 'N/A'))
    print_item("状态", format_job_status(job.get('jobState', 'N/A')))
    print_item("队列", job.get('queue', 'N/A'))
    print_item("用户", job.get('userName', 'N/A'))
    print_item("工作目录", job.get('workdir', 'N/A'))
    print_item("入队时间", job.get('jobQueueTime', 'N/A'))
    print_item("开始时间", job.get('jobStartTime', 'N/A'))
    print_item("结束时间", job.get('jobEndTime', 'N/A'))
    print_item("等待时间", f"{job.get('jobWaitTime', 0)} 秒")
    print_item("运行时长", f"{job.get('jobWalltimeUsed', 0)} 秒")
    print_item("退出码", job.get('jobExitStatus', 'N/A'))
    
    # 资源使用
    print(f"\n  {Colors.BOLD}资源使用:{Colors.END}")
    print_item("CPU核数", f"{job.get('jobProcNum', 0)} 核", indent=1)
    print_item("节点数", f"{job.get('nodect', 0)} 个", indent=1)
    print_item("CPU时间", f"{job.get('jobCpuTime', 0)} 秒", indent=1)
    print_item("内存使用", f"{job.get('jobMemUsed', 0)} KB", indent=1)
    
    # 计费信息
    if job.get('cpuNuclearHour'):
        print(f"\n  {Colors.BOLD}计费信息:{Colors.END}")
        print_item("CPU核时", f"{job.get('cpuNuclearHour', 0)} 小时", indent=1)
        print_item("GPU卡时", f"{job.get('gpuCardHour', 0)} 小时", indent=1)


def display_user_queues(queues: List[str]):
    """显示用户可访问队列"""
    if not queues:
        print_warning("未找到可访问队列")
        return
    
    print_section(f"📋 用户可访问队列 (共 {len(queues)} 个)")
    
    for i, queue in enumerate(queues, 1):
        queue_name = queue if isinstance(queue, str) else queue.get('queueName', str(queue))
        print(f"  {Colors.BOLD}{i}.{Colors.END} {Colors.CYAN}{queue_name}{Colors.END}")


def display_cluster_info(job_managers: List[Dict]):
    """显示集群信息"""
    if not job_managers:
        print_warning("未找到集群信息")
        return
    
    print_section(f"📋 集群信息 (共 {len(job_managers)} 个调度器)")
    
    for i, jm in enumerate(job_managers, 1):
        jm_id = jm.get('id', 'N/A')
        jm_name = jm.get('text', 'N/A')
        jm_type = jm.get('jobmanagerType', 'N/A')
        
        print(f"\n  {Colors.BOLD}{i}. 调度器 {jm_name}{Colors.END}")
        print(f"     ID: {jm_id}")
        print(f"     类型: {jm_type}")
        
        # 显示队列信息（如果有）
        queues = jm.get('queues', [])
        if queues:
            print(f"     队列: {', '.join([q.get('queueName', str(q)) for q in queues[:5]])}")
            if len(queues) > 5:
                print(f"           ... 等共 {len(queues)} 个队列")


def display_delete_result(success: bool, job_id: str, message: str):
    """显示删除结果"""
    if success:
        print_success(f"作业 {job_id} 删除成功")
        print(f"\n{Colors.GREEN}响应信息: {message}{Colors.END}")
    else:
        print_error(f"作业 {job_id} 删除失败")
        print(f"\n{Colors.RED}错误信息: {message}{Colors.END}")


def get_default_job_name() -> str:
    """生成带时间戳的默认作业名称"""
    return datetime.now().strftime('job-%Y-%m-%d-%H-%M-%S')


# 作业参数定义（按重要程度排序）
JOB_PARAM_DEFINITIONS = [
    # (参数名, 环境变量名, 描述, 是否必填, 默认值)
    ('cmd', 'GAP_CMD_FILE', '命令行内容', True, None),
    ('job_name', 'GAP_JOB_NAME', '作业名称', True, None),  # 默认值为动态生成: job-{Y-m-d-H-i-s}
    ('queue', 'GAP_QUEUE', '队列名称', True, None),
    ('work_dir', 'GAP_WORK_DIR', '工作目录', True, None),
    ('wall_time', 'GAP_WALL_TIME', '最大运行时长 (HH:MM:SS)', True, '24:00:00'),
    ('nnode', 'GAP_NNODE', '节点个数', False, '1'),
    ('submit_type', 'GAP_SUBMIT_TYPE', '提交类型 (cmd/...)', False, 'cmd'),
    ('appname', 'GAP_APPNAME', '应用名称', False, 'BASE'),
    ('nproc', 'GAP_NPROC', '总核心数 (与ppn二选一)', False, ''),
    ('ppn', 'GAP_PPN', 'CPU核心/节点 (与nproc二选一)', False, ''),
    ('ngpu', 'GAP_NGPU', 'GPU卡数/节点', False, ''),
    ('ndcu', 'GAP_NDCU', 'DCU卡数/节点', False, ''),
    ('job_mem', 'GAP_JOB_MEM', '每个节点内存值 (MB/GB)', False, ''),
    ('exclusive', 'GAP_EXCLUSIVE', '是否独占节点 (1=独占)', False, ''),
    ('node_string', 'GAP_NODE_STRING', '指定节点 (指定时nnode必须为"")', False, ''),
    ('std_out', 'GAP_STD_OUT_FILE', '标准输出文件路径', False, ''),
    ('std_err', 'GAP_STD_ERR_FILE', '标准错误文件路径', False, ''),
]


def get_param_priority_index(param_name: str) -> int:
    """获取参数的重要程度排序索引"""
    for i, (name, _, _, _, _) in enumerate(JOB_PARAM_DEFINITIONS):
        if name == param_name:
            return i
    return 999


def collect_job_params_interactive(args) -> Dict[str, str]:
    """
    交互式收集作业参数
    按重要程度排序展示，允许用户修改
    """
    params = {}
    
    print_section("📋 作业参数配置")
    print(f"{Colors.DIM}请按重要程度顺序确认或修改作业参数，直接回车表示使用默认值{Colors.END}\n")
    
    # 从命令行参数预填充
    param_values = {
        'cmd': args.cmd,
        'job_name': args.job_name,
        'queue': args.queue,
        'work_dir': args.work_dir,
        'wall_time': args.wall_time,
        'nnode': args.nnode,
        'submit_type': args.submit_type,
        'appname': args.appname,
        'nproc': args.nproc,
        'ppn': args.ppn,
        'ngpu': args.ngpu,
        'ndcu': args.ndcu,
        'job_mem': args.job_mem,
        'exclusive': args.exclusive,
        'node_string': args.node_string,
        'std_out': args.std_out,
        'std_err': args.std_err,
    }
    
    # 生成动态的默认作业名称
    dynamic_job_name = get_default_job_name()
    
    for param_name, env_name, description, is_required, default in JOB_PARAM_DEFINITIONS:
        current_value = param_values.get(param_name) or ''
        
        # 对 job_name 使用动态生成的默认值
        if param_name == 'job_name' and not current_value:
            default = dynamic_job_name
        
        # 确定提示值
        if current_value:
            prompt_value = current_value
        elif default:
            prompt_value = default
        else:
            prompt_value = ''
        
        # 构建提示字符串
        required_mark = f"{Colors.RED}* {Colors.END}" if is_required else "  "
        default_hint = f" {Colors.DIM}(默认: {default}){Colors.END}" if default and not current_value else ""
        
        try:
            print(f"{required_mark}{Colors.BOLD}{description}:{Colors.END}{default_hint}")
            user_input = input(f"  当前值 [{Colors.CYAN}{prompt_value}{Colors.END}]: ").strip()
            
            # 如果用户输入了值，使用用户输入；否则使用当前值或默认值
            if user_input:
                params[param_name] = user_input
            elif current_value:
                params[param_name] = current_value
            elif default:
                params[param_name] = default
            elif is_required:
                # 必填参数但没有值
                print_error(f"{description} 是必填参数，必须提供值")
                return {}
            
        except (KeyboardInterrupt, EOFError):
            print("\n")
            print_warning("已取消参数输入")
            return {}
    
    # 自动设置标准输出和错误文件路径（如果未指定）
    if params.get('work_dir') and not params.get('std_out'):
        params['std_out'] = f"{params['work_dir']}/std.out.%j"
    if params.get('work_dir') and not params.get('std_err'):
        params['std_err'] = f"{params['work_dir']}/std.err.%j"
    
    return params


def display_job_params(params: Dict[str, str]):
    """按重要程度排序显示作业参数"""
    print_section("📋 作业参数确认")
    
    # 按重要程度排序
    sorted_params = sorted(params.items(), key=lambda x: get_param_priority_index(x[0]))
    
    for param_name, value in sorted_params:
        # 查找参数定义
        desc = param_name
        for name, _, d, is_required, _ in JOB_PARAM_DEFINITIONS:
            if name == param_name:
                desc = d
                if is_required:
                    desc = f"{desc} {Colors.RED}*{Colors.END}"
                break
        
        # 截断过长的值
        display_value = value if len(value) < 50 else value[:47] + "..."
        print_item(desc, display_value)


def confirm_submit() -> bool:
    """询问用户确认提交作业"""
    print()
    print_warning("请确认以上作业参数是否正确")
    
    try:
        response = input(f"{Colors.BOLD}请输入 'yes' 确认提交，或输入参数名修改，或其他键取消: {Colors.END}").strip().lower()
        if response == 'yes':
            return True
        elif response:
            # 返回参数名表示需要修改
            return response
        return False
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return False


def edit_param(params: Dict[str, str], param_name: str) -> Dict[str, str]:
    """编辑指定参数"""
    # 查找参数定义
    desc = param_name
    for name, _, d, _, _ in JOB_PARAM_DEFINITIONS:
        if name == param_name:
            desc = d
            break
    
    current_value = params.get(param_name, '')
    print(f"\n{Colors.BOLD}修改 {desc}:{Colors.END}")
    print(f"  当前值: {Colors.CYAN}{current_value}{Colors.END}")
    
    try:
        new_value = input(f"  新值: ").strip()
        if new_value:
            params[param_name] = new_value
            print_success(f"已更新 {desc}")
        else:
            print_warning("未输入新值，保持原值")
    except (KeyboardInterrupt, EOFError):
        print("\n")
    
    return params


def interactive_submit_job(api: JobAPI) -> Tuple[Optional[str], str]:
    """
    交互式提交作业
    按重要程度排序展示参数，允许用户修改后确认提交
    """
    # 第一次收集参数
    params = collect_job_params_interactive(type('Args', (), {p[0]: '' for p in JOB_PARAM_DEFINITIONS})())
    if not params:
        return None, "参数收集失败"
    
    while True:
        # 显示当前参数
        display_job_params(params)
        
        # 确认提交
        confirm = confirm_submit()
        
        if confirm is True:
            # 确认提交
            break
        elif confirm is False:
            # 取消
            return None, "用户取消提交"
        elif isinstance(confirm, str) and confirm in [p[0] for p in JOB_PARAM_DEFINITIONS]:
            # 修改指定参数
            params = edit_param(params, confirm)
        else:
            print_warning("无效的输入，请重新确认")
    
    # 执行提交
    print(f"\n{Colors.CYAN}正在提交作业...{Colors.END}")
    return api.submit_job(params)


def display_submit_result(job_id: Optional[str], message: str):
    """显示提交结果"""
    if job_id:
        print_success(f"作业提交成功！作业ID: {Colors.BOLD}{job_id}{Colors.END}")
        print(f"\n{Colors.GREEN}响应信息: {message}{Colors.END}")
    else:
        print_error("作业提交失败")
        print(f"\n{Colors.RED}错误信息: {message}{Colors.END}")
        
        # 提供常见错误解决方案
        if "Access/permission denied" in message or "access restricted" in message:
            print(f"\n{Colors.YELLOW}可能原因:{Colors.END}")
            print(f"  1. 您的账户在当前区域没有作业提交权限")
            print(f"  2. 请联系区域管理员开通权限")
            print(f"  3. 或尝试切换到其他您有权限的区域")
        elif "Required partition not available" in message:
            print(f"\n{Colors.YELLOW}可能原因:{Colors.END}")
            print(f"  1. 指定的队列当前不可用（维护或已满）")
            print(f"  2. 请尝试其他队列")
            print(f"  3. 使用 --queues 查看可用队列")
        elif "Invalid account" in message:
            print(f"\n{Colors.YELLOW}可能原因:{Colors.END}")
            print(f"  1. 账户/队列组合无效")
            print(f"  2. 您的账户可能没有该队列的使用权限")
            print(f"  3. 请联系管理员确认账户权限")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SCNet 作业管理工具 - 查询、删除和提交作业',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
查询示例:
  python scripts/job.py                          # 查询实时作业列表
  python scripts/job.py --history                # 查询历史作业列表
  python scripts/job.py --job-id 123             # 查询实时作业详情
  python scripts/job.py --history --job-id 123   # 查询历史作业详情
  python scripts/job.py --days 7                 # 查询最近7天历史作业
  python scripts/job.py --status running         # 查询运行中的作业
  python scripts/job.py --queue debug            # 查询指定队列的作业
  python scripts/job.py --job-name "test*"       # 按作业名称筛选
  python scripts/job.py --delete --job-id 123    # 删除指定作业

提交作业示例:
  python scripts/job.py --submit                 # 交互式提交作业
  python scripts/job.py --submit --cmd "sleep 100" --queue debug  # 带参数提交

队列和集群信息:
  python scripts/job.py --queues                 # 查询用户可访问队列
  python scripts/job.py --cluster-info           # 查询集群信息
        """
    )
    
    # 查询类型
    parser.add_argument('--history', action='store_true', help='查询历史作业（默认查询实时作业）')
    
    # 删除操作
    parser.add_argument('--delete', action='store_true', help='删除作业（需要配合 --job-id 使用）')
    
    # 提交作业
    parser.add_argument('--submit', action='store_true', help='提交新作业（需要配合 --cmd 参数使用）')
    
    # 队列和集群信息
    parser.add_argument('--queues', action='store_true', help='查询用户可访问队列')
    parser.add_argument('--cluster-info', action='store_true', help='查询集群信息')
    
    # 作业ID（用于详情查询或删除）
    parser.add_argument('--job-id', type=str, help='作业ID，指定则查询详情或删除作业')
    
    # 筛选条件
    parser.add_argument('--job-name', type=str, help='作业名称（支持模糊匹配）')
    parser.add_argument('--queue', type=str, help='队列名称')
    parser.add_argument('--status', type=str, 
                       choices=['running', 'queue', 'queued', 'hold', 'suspend', 'exit', 'completed', 'wait', 'waiting', 'other',
                               'statR', 'statQ', 'statH', 'statS', 'statE', 'statC', 'statW', 'statX', 'statDE', 'statD', 'statT', 'statN', 'statRQ'],
                       help='作业状态：running/statR(运行), queue/statQ(排队), hold/statH(保留), suspend/statS(挂起), exit/statE(退出), completed/statC(完成), wait/statW(等待), other/statX(其他), statDE(取消), statD(失败), statT(超时), statN(节点异常), statRQ(重新运行)')
    parser.add_argument('--owner', type=str, help='作业所有者用户名（实时作业）')
    parser.add_argument('--user', type=str, help='用户名（历史作业）')
    
    # 时间范围（历史作业）
    parser.add_argument('--days', type=int, default=30, help='查询最近N天的历史作业（默认30天）')
    parser.add_argument('--start-time', type=str, help='开始时间，格式：YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--end-time', type=str, help='结束时间，格式：YYYY-MM-DD HH:MM:SS')
    
    # 分页（旧版 HPC 接口）
    parser.add_argument('--start', type=int, default=0, help='起始位置（分页，旧版接口）')
    parser.add_argument('--limit', type=int, default=20, help='每页条数（默认20，旧版接口）')
    
    # AC 接口查询参数（新版）
    parser.add_argument('--page', type=int, default=1, help='页码（AC接口，默认1）')
    parser.add_argument('--size', type=int, default=10, help='每页条数（AC接口，默认10）')
    parser.add_argument('--cluster-id', type=str, help='区域ID（AC接口）')
    parser.add_argument('--show-group-jobs', type=str, help='展示组所有成员作业：true 为展示（AC接口）')
    parser.add_argument('--show-all-data', action='store_true', help='是否返回所有字段（AC接口，默认false）')
    parser.add_argument('--cluster-user-name', type=str, help='用户名（AC接口，默认为空）')
    
    # 提交作业参数
    
    # 提交作业参数
    parser.add_argument('--cmd', type=str, help='命令行内容（GAP_CMD_FILE）')
    parser.add_argument('--nnode', type=str, help='节点个数（GAP_NNODE，默认1）')
    parser.add_argument('--node-string', type=str, help='指定节点（GAP_NODE_STRING）')
    parser.add_argument('--submit-type', type=str, help='提交类型（GAP_SUBMIT_TYPE，默认cmd）')
    parser.add_argument('--work-dir', type=str, help='工作目录（GAP_WORK_DIR）')
    parser.add_argument('--wall-time', type=str, help='最大运行时长 HH:MM:SS（GAP_WALL_TIME，默认24:00:00）')
    parser.add_argument('--appname', type=str, help='应用名称（GAP_APPNAME，默认BASE）')
    parser.add_argument('--nproc', type=str, help='总核心数（GAP_NPROC）')
    parser.add_argument('--ppn', type=str, help='CPU核心/节点（GAP_PPN）')
    parser.add_argument('--ngpu', type=str, help='GPU卡数/节点（GAP_NGPU）')
    parser.add_argument('--ndcu', type=str, help='DCU卡数/节点（GAP_NDCU）')
    parser.add_argument('--job-mem', type=str, help='每个节点内存值 MB/GB（GAP_JOB_MEM）')
    parser.add_argument('--exclusive', type=str, help='是否独占节点 1=独占（GAP_EXCLUSIVE）')
    parser.add_argument('--std-out', type=str, help='标准输出文件路径（GAP_STD_OUT_FILE）')
    parser.add_argument('--std-err', type=str, help='标准错误文件路径（GAP_STD_ERR_FILE）')
    
    args = parser.parse_args()
    
    # 加载缓存
    cache = load_cache(auto_init=False)
    if not cache:
        sys.exit(1)
    
    # 获取默认区域
    cluster = get_default_cluster(cache)
    if not cluster:
        print_error("未找到默认区域")
        sys.exit(1)
    
    # 创建 API 客户端
    api = JobAPI(cluster, cache)
    
    if not api.ac_token:
        print_error("AC 认证 token 不可用，请检查缓存是否正确初始化")
        sys.exit(1)
    
    # 处理查询用户队列
    if args.queues:
        if not api.job_manager_id:
            print_error("未找到 JobManager ID")
            sys.exit(1)
        
        queues, error, raw_data = api.query_user_queues(api.compute_user or "", raw_response=True)
        
        # 直接输出原始 API 响应
        if raw_data:
            print(json.dumps(raw_data, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"code": -1, "msg": error or "未知错误"}, ensure_ascii=False, indent=2))
        
        sys.exit(0 if not error else 1)
    
    # 处理查询集群信息
    if args.cluster_info:
        print_header(f"集群信息 - {cluster.get('clusterName', 'N/A')}")
        
        job_managers, error = api.get_cluster_info()
        if error:
            print_error(f"查询失败: {error}")
            sys.exit(1)
        
        display_cluster_info(job_managers)
        
        # 底部提示
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
        print(f"  提示: 当前默认 JobManager ID: {api.job_manager_id}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")
        return
    
    if not api.job_manager_id:
        print_error("当前区域未配置 JobManager")
        sys.exit(1)
    
    # 构建查询参数
    params = {
        'start': args.start,
        'limit': args.limit,
        'job_id': args.job_id,
        'job_name': args.job_name,
        'queue': args.queue,
        'status': args.status,
        'owner': args.owner or api.compute_user,
        'user': args.user or api.compute_user,
        'start_time': args.start_time,
        'end_time': args.end_time,
        # AC接口分页参数
        'page': args.page,
        'size': args.size,
        'cluster_id': args.cluster_id,
        'show_group_jobs': args.show_group_jobs,
        'cluster_user_name': args.cluster_user_name,
        'show_all_data': args.show_all_data
    }
    
    # 只有当明确指定了 --days 参数时才加入（区分默认值）
    if '--days' in sys.argv:
        params['days'] = args.days
    
    # 处理提交作业
    if args.submit:
        print_header(f"提交作业 - {cluster.get('clusterName', 'N/A')}")
        
        # 检查是否提供了 --cmd 参数
        if not args.cmd:
            print_error("提交作业需要指定 --cmd 参数")
            print(f"\n{Colors.YELLOW}用法示例:{Colors.END}")
            print(f'  python scripts/job.py --submit --cmd "sleep 100" --queue comp')
            print(f"\n{Colors.CYAN}使用自然语言入口更方便:{Colors.END}")
            print(f'  python scripts/scnet.py "提交作业 sleep 100 --queue comp"')
            print(f'  python scripts/scnet.py "提交作业帮助"')
            sys.exit(1)
        
        # 设置默认工作目录（用户家目录）
        default_work_dir = f"/public/home/{api.compute_user}" if api.compute_user else ""
        
        job_params = {
            'cmd': args.cmd,
            'queue': args.queue or '',
            'nnode': args.nnode or '1',
            'node_string': args.node_string or '',
            'submit_type': args.submit_type or 'cmd',
            'job_name': args.job_name or datetime.now().strftime('job-%Y-%m-%d-%H-%M-%S'),
            'work_dir': args.work_dir or default_work_dir,
            'wall_time': args.wall_time or '24:00:00',
            'appname': args.appname or 'BASE',
            'nproc': args.nproc or '',
            'ppn': args.ppn or '',
            'ngpu': args.ngpu or '',
            'ndcu': args.ndcu or '',
            'job_mem': args.job_mem or '',
            'exclusive': args.exclusive or '',
            'std_out': args.std_out or '',
            'std_err': args.std_err or ''
        }
        print(f"{Colors.CYAN}正在提交作业...{Colors.END}")
        job_id, message = api.submit_job(job_params)
        display_submit_result(job_id, message)
        
        if not job_id:
            sys.exit(1)
        
        return
    
    # 打印标题
    # 判断是否为AC接口查询（实时/历史作业列表）
    # AC接口查询所有区域，其他接口查询当前区域
    # 如果指定了job_id且没有时间范围参数，则查询作业详情（非AC列表接口）
    has_time_range = bool(args.start_time or args.end_time or '--days' in sys.argv)
    is_job_detail_query = bool(args.job_id and not has_time_range)
    is_ac_list_query = not is_job_detail_query
    
    if is_ac_list_query:
        print_header("作业查询 - 所有区域（AC聚合）")
    else:
        cluster_name = cluster.get('clusterName', 'N/A')
        print_header(f"作业查询 - {cluster_name}")
    
    # 显示查询条件
    display_query_params(api, params, is_history=args.history, is_ac_api=is_ac_list_query)
    
    # 处理删除作业
    if args.delete:
        if not args.job_id:
            print_error("删除作业需要指定 --job-id 参数")
            sys.exit(1)
        
        # 从配置文件读取用户名
        config_username = load_config_username()
        if not config_username:
            sys.exit(1)
        
        # 先查询作业详情
        job, error = api.query_realtime_job_detail(args.job_id)
        if error or not job:
            print_warning(f"未找到作业 {args.job_id}，无法删除")
            sys.exit(1)
        
        # 执行删除
        print(f"{Colors.CYAN}正在删除作业 {args.job_id}...{Colors.END}")
        success, message = api.delete_job(args.job_id, config_username)
        display_delete_result(success, args.job_id, message)
        
        if not success:
            sys.exit(1)
        
        return
    
    # 根据参数决定查询类型
    if args.history:
        # 历史作业查询
        # 如果有时间范围参数，优先执行列表查询（即使有 job_id 也认为是过滤条件）
        has_time_range = bool(args.start_time or args.end_time or args.days != 30)
        if args.job_id and not has_time_range:
            # 历史作业详情
            job, error = api.query_history_job_detail(args.job_id)
            if error:
                print_error(f"查询失败: {error}")
                sys.exit(1)
            if job:
                display_history_job_detail(job)
            else:
                print_warning("未找到该历史作业")
        else:
            # 历史作业列表
            jobs, total, error = api.query_history_jobs(params)
            if error:
                print_error(f"查询失败: {error}")
                sys.exit(1)
            display_history_jobs(jobs, total, group_by_cluster=is_ac_list_query)
    else:
        # 实时作业查询
        # 如果有时间范围参数，优先执行列表查询（即使有 job_id 也认为是过滤条件）
        has_time_range = bool(args.start_time or args.end_time or args.days != 30)
        if args.job_id and not has_time_range:
            job, error = api.query_job_detail(args.job_id)
            if job:
                if job.get('source') == 'history':
                    display_history_job_detail(job)
                else:
                    display_realtime_job_detail(job)
            else:
                if error:
                    print_error(f"查询失败: {error}")
                    sys.exit(1)
                print_warning("未找到该作业")
        else:
            # 实时作业列表
            jobs, total, error = api.query_realtime_jobs(params)
            if error:
                print_error(f"查询失败: {error}")
                sys.exit(1)
            display_realtime_jobs(jobs, total, group_by_cluster=is_ac_list_query)
    

if __name__ == "__main__":
    main()
