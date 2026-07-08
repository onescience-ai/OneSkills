#!/usr/bin/env python3
"""
SCNet 用户信息查看工具

从缓存中获取并显示当前区域的详细信息，以及其他可用区域列表。
支持动态查询作业统计信息。

使用方法:
    python scripts/user.py
"""

import argparse
import json
import sys
import ssl
import time
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    CONFIG_PATH, CACHE_PATH, get_cache_path, CACHE_MAX_AGE,
    ClusterTimeout, CACHE_INITIALIZER_TIMEOUT,
    ASYNC_CONCURRENCY_LIMIT
)

# 从 utils 导入通用功能
from utils import Colors, print_header, print_section, print_item, print_success, print_warning, print_error, load_cache

# SSL 上下文
SSL_CONTEXT = ssl.create_default_context()


def format_bytes(size_bytes: float) -> str:
    """将字节转换为人类可读的格式"""
    if size_bytes <= 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def _refresh_cache() -> bool:
    """
    调用 cache.py 刷新缓存
    
    Returns:
        True 表示刷新成功，False 表示刷新失败
    """
    try:
        # 获取 scripts 目录路径
        scripts_dir = Path(__file__).parent
        cache_script = scripts_dir / "cache.py"
        
        if not cache_script.exists():
            print_error(f"缓存脚本不存在: {cache_script}")
            return False
        
        print(f"{Colors.CYAN}正在连接 SCNet API 获取凭证...{Colors.END}")
        
        # 运行缓存初始化脚本
        # 超时设置为子查询超时总和
        result = subprocess.run(
            [sys.executable, str(cache_script)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=CACHE_INITIALIZER_TIMEOUT
        )
        
        if result.returncode == 0:
            print_success("缓存刷新成功")
            return True
        else:
            error_msg = result.stderr if result.stderr else "未知错误"
            print_error(f"缓存刷新失败: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("缓存刷新超时（超过 2 分钟）")
        return False
    except Exception as e:
        print_error(f"缓存刷新异常: {e}")
        return False


def get_default_cluster(clusters: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """获取默认区域"""
    # 首先查找标记为默认的区域
    for cluster in clusters:
        if cluster.get('default') is True or cluster.get('isDefault') is True:
            return cluster
    
    # 其次查找有完整配置（有 walltime 数据）的区域
    for cluster in clusters:
        if cluster.get('clusterName') != 'ac' and cluster.get('walltime') is not None:
            return cluster
    
    # 最后返回第一个非 ac 的区域
    for cluster in clusters:
        if cluster.get('clusterName') != 'ac':
            return cluster
    return None


def get_other_clusters(clusters: List[Dict[str, Any]], current_id: str) -> List[Dict[str, Any]]:
    """获取其他区域（排除 ac 和当前区域）"""
    others = []
    for cluster in clusters:
        name = cluster.get('clusterName', '')
        cid = cluster.get('clusterId', '')
        # 排除 ac 和当前区域
        if name != 'ac' and cid != current_id:
            others.append(cluster)
    return others


class ClusterAPI:
    """区域 API 客户端 - 动态查询作业统计信息"""
    
    # 从配置文件导入超时时间
    TIMEOUT_QUERY_JOB_STATE = ClusterTimeout.QUERY_JOB_STATE
    TIMEOUT_QUERY_CORE_STATE = ClusterTimeout.QUERY_CORE_STATE
    TIMEOUT_QUERY_QUEUE_JOBS = ClusterTimeout.QUERY_QUEUE_JOBS
    
    # 兼容性保留
    TIMEOUT_QUICK = ClusterTimeout.QUICK
    TIMEOUT_NORMAL = ClusterTimeout.NORMAL
    
    def __init__(self, cluster: Dict[str, Any]):
        self.cluster = cluster
        self.token = cluster.get('token', '')
        self.hpc_url = self._get_hpc_url()
        self.job_manager_id = self._get_job_manager_id()
        self.username = self._get_username()
        self.compute_user = self._get_compute_user()  # 调度系统用户名
    
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
    
    def _get_username(self) -> str:
        """获取平台用户名"""
        user_info = self.cluster.get('clusterUserInfo', {})
        return user_info.get('userName', '')
    
    def _get_compute_user(self) -> str:
        """获取调度系统用户名（从 token 解码）"""
        import base64
        try:
            parts = self.token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                # 添加 padding
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload)
                token_data = json.loads(decoded)
                return token_data.get('computeUser', '')
        except Exception:
            pass
        return ''
    
    def _make_request(self, url: str, headers: Dict[str, str], timeout: int = None) -> Optional[Dict[str, Any]]:
        """发起 HTTP GET 请求"""
        # 默认使用普通查询超时
        if timeout is None:
            timeout = self.TIMEOUT_NORMAL
            
        try:
            req = urllib.request.Request(
                url,
                headers=headers,
                method='GET'
            )
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=timeout) as response:
                response_body = response.read().decode('utf-8')
                return json.loads(response_body)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                return json.loads(error_body)
            except:
                return {"code": e.code, "msg": error_body}
        except Exception as e:
            return {"code": -1, "msg": str(e)}
    
    def query_job_state(self) -> Optional[Dict[str, Any]]:
        """
        查询作业状态统计信息
        GET /hpc/openapi/v2/view/jobs/state?userName={compute_user}
        注意：需要使用调度系统用户名(computeUser)
        """
        if not self.hpc_url or not self.compute_user:
            return None
        
        url = f"{self.hpc_url}/hpc/openapi/v2/view/jobs/state?userName={urllib.parse.quote(self.compute_user)}"
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        result = self._make_request(url, headers, timeout=self.TIMEOUT_QUERY_JOB_STATE)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None
    
    def query_core_state(self) -> Optional[Dict[str, Any]]:
        """
        查询核心数状态统计信息
        GET /hpc/openapi/v2/view/cpucore/state
        """
        if not self.hpc_url:
            return None
        
        url = f"{self.hpc_url}/hpc/openapi/v2/view/cpucore/state"
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        result = self._make_request(url, headers, timeout=self.TIMEOUT_QUERY_CORE_STATE)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None
    
    def query_queue_jobs(self) -> Optional[Dict[str, Any]]:
        """
        查询队列作业统计信息
        GET /hpc/openapi/v2/view/queue/jobs?userName={compute_user}
        注意：需要使用调度系统用户名(computeUser)
        """
        if not self.hpc_url or not self.compute_user:
            return None
        
        url = f"{self.hpc_url}/hpc/openapi/v2/view/queue/jobs?userName={urllib.parse.quote(self.compute_user)}"
        headers = {
            'token': self.token,
            'Content-Type': 'application/json'
        }
        
        result = self._make_request(url, headers, timeout=self.TIMEOUT_QUERY_QUEUE_JOBS)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None


class AsyncClusterAPI:
    """异步区域 API 客户端 - 并行查询作业统计信息"""
    
    def __init__(self, cluster: Dict[str, Any]):
        self.cluster = cluster
        self.token = cluster.get('token', '')
        self.hpc_url = self._get_hpc_url()
        self.compute_user = self._get_compute_user()
        self.ssl_context = ssl.create_default_context()
        # 信号量控制并发数
        self.semaphore = asyncio.Semaphore(ASYNC_CONCURRENCY_LIMIT)
    
    def _get_hpc_url(self) -> str:
        """获取 HPC 服务 URL"""
        hpc_urls = self.cluster.get('hpcUrls', [])
        if hpc_urls and len(hpc_urls) > 0:
            return hpc_urls[0].get('url', '')
        return ''
    
    def _get_compute_user(self) -> str:
        """获取调度系统用户名（从 token 解码）"""
        import base64
        try:
            parts = self.token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload)
                token_data = json.loads(decoded)
                return token_data.get('computeUser', '')
        except Exception:
            pass
        return ''
    
    async def _make_request(self, session: aiohttp.ClientSession, url: str, 
                           timeout: int = 5) -> Optional[Dict[str, Any]]:
        """发起异步 HTTP GET 请求"""
        async with self.semaphore:
            try:
                headers = {
                    'token': self.token,
                    'Content-Type': 'application/json'
                }
                async with session.get(
                    url, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    ssl=self.ssl_context
                ) as response:
                    response_body = await response.text()
                    return json.loads(response_body)
            except Exception:
                return None
    
    async def query_job_state(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """查询作业状态统计信息"""
        if not self.hpc_url or not self.compute_user:
            return None
        url = f"{self.hpc_url}/hpc/openapi/v2/view/jobs/state?userName={urllib.parse.quote(self.compute_user)}"
        result = await self._make_request(session, url, timeout=ClusterAPI.TIMEOUT_QUERY_JOB_STATE)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None
    
    async def query_core_state(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """查询核心数状态统计信息"""
        if not self.hpc_url:
            return None
        url = f"{self.hpc_url}/hpc/openapi/v2/view/cpucore/state"
        result = await self._make_request(session, url, timeout=ClusterAPI.TIMEOUT_QUERY_CORE_STATE)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None
    
    async def query_queue_jobs(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """查询队列作业统计信息"""
        if not self.hpc_url or not self.compute_user:
            return None
        url = f"{self.hpc_url}/hpc/openapi/v2/view/queue/jobs?userName={urllib.parse.quote(self.compute_user)}"
        result = await self._make_request(session, url, timeout=ClusterAPI.TIMEOUT_QUERY_QUEUE_JOBS)
        if result and str(result.get('code')) == '0':
            return result.get('data')
        return None
    
    async def query_all_stats(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """并行查询所有统计信息"""
        async with aiohttp.ClientSession() as session:
            job_state, core_state, queue_jobs = await asyncio.gather(
                self.query_job_state(session),
                self.query_core_state(session),
                self.query_queue_jobs(session),
                return_exceptions=True
            )
            
            # 处理异常
            if isinstance(job_state, Exception):
                job_state = None
            if isinstance(core_state, Exception):
                core_state = None
            if isinstance(queue_jobs, Exception):
                queue_jobs = None
                
            return {
                'job_state': job_state,
                'core_state': core_state,
                'queue_jobs': queue_jobs
            }


def display_user_info(user_info: Dict[str, Any]):
    """显示用户信息"""
    print_section("👤 用户信息")
    
    username = user_info.get('userName', 'N/A')
    fullname = user_info.get('fullName', 'N/A')
    account_status = user_info.get('accountStatus', 'N/A')
    balance = user_info.get('accountBalance', 'N/A')
    
    # 账户状态显示优化
    status_map = {
        'Normal': f"{Colors.GREEN}正常{Colors.END}",
        'Disabled': f"{Colors.RED}禁用{Colors.END}",
        'Suspended': f"{Colors.YELLOW}暂停{Colors.END}"
    }
    status_display = status_map.get(account_status, account_status)
    
    print_item("用户名", f"{Colors.CYAN}{username}{Colors.END}")
    print_item("姓名", fullname)
    print_item("账户状态", status_display)
    print_item("账户余额", f"{Colors.YELLOW}¥{balance}{Colors.END}" if balance != 'N/A' else 'N/A')
    
    # 其他信息
    email = user_info.get('email') or '未设置'
    mobile = user_info.get('mobilephoneNum') or '未设置'
    institution = user_info.get('institution') or '未设置'
    
    print_item("邮箱", email)
    print_item("手机", mobile)
    print_item("机构", institution)


def get_home_path(cluster: Dict[str, Any]) -> str:
    """获取家目录路径"""
    # 首先尝试从 parastors 获取路径
    parastors = cluster.get('parastors', [])
    if parastors:
        for item in parastors:
            path = item.get('path', '')
            if path and 'home' in path:
                return path
    
    # 如果没有配额数据，尝试根据用户名构造常见家目录格式
    user_info = cluster.get('clusterUserInfo', {})
    username = user_info.get('userName', '')
    if username:
        # 常见的家目录格式
        return f"/public/home/{username} 或 /work/home/{username}"
    
    return "未获取"


def display_home_and_quota(cluster: Dict[str, Any]):
    """显示家目录和存储配额"""
    print_section("💾 存储信息")
    
    # 显示家目录
    home_path = get_home_path(cluster)
    print_item("家目录", f"{Colors.CYAN}{home_path}{Colors.END}")
    
    # 显示存储配额详情
    parastors = cluster.get('parastors', [])
    if parastors:
        print(f"\n  {Colors.BOLD}存储配额详情:{Colors.END}")
        for i, item in enumerate(parastors, 1):
            path = item.get('path', 'N/A')
            threshold = item.get('threshold', 0)
            usage = item.get('usage', 0)
            
            # 转换单位 (GB)
            threshold_gb = float(threshold) if threshold else 0
            usage_gb = float(usage) if usage else 0
            
            # 计算使用率
            usage_percent = (usage_gb / threshold_gb * 100) if threshold_gb > 0 else 0
            
            # 进度条
            bar_length = 20
            filled = int(bar_length * usage_percent / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # 颜色判断
            if usage_percent >= 90:
                color = Colors.RED
            elif usage_percent >= 70:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
            
            print(f"\n    {i}. {Colors.BOLD}路径:{Colors.END} {path}")
            print(f"       配额: {threshold_gb:.2f} GB")
            print(f"       已用: {usage_gb:.2f} GB ({color}{usage_percent:.1f}%{Colors.END})")
            print(f"       {color}[{bar}]{Colors.END}")
    else:
        print(f"\n  {Colors.YELLOW}⚠ 暂无存储配额数据{Colors.END}")


def display_cluster_info(cluster: Dict[str, Any]):
    """显示集群信息"""
    job_managers = cluster.get('JobManagers', [])
    if not job_managers:
        return
    
    print_section("🖥️  集群信息")
    
    for i, jm in enumerate(job_managers, 1):
        name = jm.get('text', 'N/A')
        addr = jm.get('JobManagerAddr', 'N/A')
        jtype = jm.get('JobManagerType', 'N/A')
        port = jm.get('JobManagerPort', 'N/A')
        jm_id = jm.get('id', 'N/A')
        
        print(f"\n  {Colors.BOLD}集群 {i}: {Colors.CYAN}{name}{Colors.END}{Colors.END}")
        print(f"    类型: {jtype}")
        print(f"    地址: {addr}:{port}")
        print(f"    ID: {jm_id}")
        
        # 队列信息
        queues = jm.get('queues', [])
        if queues:
            print(f"    {Colors.BOLD}可用队列:{Colors.END}")
            for q in queues:
                qname = q.get('queueName', 'N/A')
                qname_display = qname if qname else 'default'
                free_cpus = q.get('queFreeNcpus', 'N/A')
                total_cpus = q.get('queNcpus', 'N/A')
                nodes = q.get('queNodes', 'N/A')
                
                print(f"      • {Colors.GREEN}{qname_display}{Colors.END}: "
                      f"{free_cpus}/{total_cpus} CPU 空闲, {nodes} 节点")





async def _display_dynamic_stats_async(cluster: Dict[str, Any]):
    """异步显示动态查询的作业统计信息"""
    # 检查是否有 HPC URL
    hpc_urls = cluster.get('hpcUrls', [])
    if not hpc_urls:
        return
    
    print_section("📊 实时作业统计")
    print(f"  {Colors.DIM}正在并行查询实时数据...{Colors.END}")
    
    # 创建异步 API 客户端
    api = AsyncClusterAPI(cluster)
    
    # 并行查询所有统计信息
    stats = await api.query_all_stats()
    
    # 作业状态名称映射
    job_state_map = {
        'jobview_status_run': '运行',
        'jobview_status_queue': '排队',
        'jobview_status_reserve': '保留',
        'jobview_status_hung': '挂起',
        'jobview_status_other': '其他',
        '运行': '运行',
        '排队': '排队',
        '保留': '保留',
        '挂起': '挂起',
        '其他': '其他'
    }
    
    # CPU状态名称映射
    core_state_map = {
        'jobview_used_label': '已使用',
        'jobview_unused_label': '未使用',
        'jobview_unavailable_label': '不可用',
        '已使用': '已使用',
        '未使用': '未使用',
        '不可用': '不可用'
    }
    
    # 1. 显示作业状态统计
    job_state_data = stats.get('job_state')
    if job_state_data:
        print(f"\n  {Colors.BOLD}作业状态分布:{Colors.END}")
        for item in job_state_data:
            name = item.get('name', 'N/A')
            count = item.get('y', 0)
            display_name = job_state_map.get(name, name)
            # 状态颜色
            if display_name == '运行':
                color = Colors.GREEN
            elif display_name == '排队':
                color = Colors.YELLOW
            elif display_name == '挂起':
                color = Colors.RED
            else:
                color = Colors.CYAN
            print(f"    • {display_name}: {color}{count}{Colors.END}")
    
    # 2. 显示核心数状态统计
    core_state_data = stats.get('core_state')
    if core_state_data:
        print(f"\n  {Colors.BOLD}CPU核心状态:{Colors.END}")
        for item in core_state_data:
            name = item.get('name', 'N/A')
            count = item.get('y', 0)
            display_name = core_state_map.get(name, name)
            # 状态颜色
            if '已使用' in display_name:
                color = Colors.GREEN
            elif '未使用' in display_name:
                color = Colors.BLUE
            else:
                color = Colors.YELLOW
            print(f"    • {display_name}: {color}{count}{Colors.END} 核")
    
    # 3. 显示队列作业统计
    queue_jobs_data = stats.get('queue_jobs')
    if queue_jobs_data:
        print(f"\n  {Colors.BOLD}队列作业统计:{Colors.END}")
        for queue in queue_jobs_data:
            qname = queue.get('name', 'N/A')
            values = queue.get('values', [])
            
            # 统计该队列的作业数
            running = 0
            queued = 0
            for v in values:
                metric = v.get('metricName', '')
                val = v.get('metricValue', 0)
                if metric == 'R':
                    running = val
                elif metric == 'Q':
                    queued = val
            
            total = running + queued
            if total > 0 or True:  # 显示所有队列，即使作业数为0
                print(f"    • {Colors.CYAN}{qname}{Colors.END}: "
                      f"{Colors.GREEN}{running} 运行{Colors.END}, "
                      f"{Colors.YELLOW}{queued} 排队{Colors.END}")


def _display_dynamic_stats_sync(cluster: Dict[str, Any]):
    """同步方式显示动态查询的作业统计信息 (回退方案)"""
    # 检查是否有 HPC URL
    hpc_urls = cluster.get('hpcUrls', [])
    if not hpc_urls:
        return
    
    print_section("📊 实时作业统计")
    print(f"  {Colors.DIM}正在查询实时数据...{Colors.END}")
    
    # 创建 API 客户端
    api = ClusterAPI(cluster)
    
    # 作业状态名称映射
    job_state_map = {
        'jobview_status_run': '运行',
        'jobview_status_queue': '排队',
        'jobview_status_reserve': '保留',
        'jobview_status_hung': '挂起',
        'jobview_status_other': '其他',
        '运行': '运行',
        '排队': '排队',
        '保留': '保留',
        '挂起': '挂起',
        '其他': '其他'
    }
    
    # CPU状态名称映射
    core_state_map = {
        'jobview_used_label': '已使用',
        'jobview_unused_label': '未使用',
        'jobview_unavailable_label': '不可用',
        '已使用': '已使用',
        '未使用': '未使用',
        '不可用': '不可用'
    }
    
    # 1. 查询作业状态统计
    job_state_data = api.query_job_state()
    if job_state_data:
        print(f"\n  {Colors.BOLD}作业状态分布:{Colors.END}")
        for item in job_state_data:
            name = item.get('name', 'N/A')
            count = item.get('y', 0)
            display_name = job_state_map.get(name, name)
            # 状态颜色
            if display_name == '运行':
                color = Colors.GREEN
            elif display_name == '排队':
                color = Colors.YELLOW
            elif display_name == '挂起':
                color = Colors.RED
            else:
                color = Colors.CYAN
            print(f"    • {display_name}: {color}{count}{Colors.END}")
    
    # 2. 查询核心数状态统计
    core_state_data = api.query_core_state()
    if core_state_data:
        print(f"\n  {Colors.BOLD}CPU核心状态:{Colors.END}")
        for item in core_state_data:
            name = item.get('name', 'N/A')
            count = item.get('y', 0)
            display_name = core_state_map.get(name, name)
            # 状态颜色
            if '已使用' in display_name:
                color = Colors.GREEN
            elif '未使用' in display_name:
                color = Colors.BLUE
            else:
                color = Colors.YELLOW
            print(f"    • {display_name}: {color}{count}{Colors.END} 核")
    
    # 3. 查询队列作业统计
    queue_jobs_data = api.query_queue_jobs()
    if queue_jobs_data:
        print(f"\n  {Colors.BOLD}队列作业统计:{Colors.END}")
        for queue in queue_jobs_data:
            qname = queue.get('name', 'N/A')
            values = queue.get('values', [])
            
            # 统计该队列的作业数
            running = 0
            queued = 0
            for v in values:
                metric = v.get('metricName', '')
                val = v.get('metricValue', 0)
                if metric == 'R':
                    running = val
                elif metric == 'Q':
                    queued = val
            
            total = running + queued
            if total > 0 or True:  # 显示所有队列，即使作业数为0
                print(f"    • {Colors.CYAN}{qname}{Colors.END}: "
                      f"{Colors.GREEN}{running} 运行{Colors.END}, "
                      f"{Colors.YELLOW}{queued} 排队{Colors.END}")


def display_dynamic_stats(cluster: Dict[str, Any]):
    """显示动态查询的作业统计信息 (自动选择同步/异步方式)"""
    if AIOHTTP_AVAILABLE:
        # 使用异步并行查询
        asyncio.run(_display_dynamic_stats_async(cluster))
    else:
        # 回退到同步方式
        _display_dynamic_stats_sync(cluster)


def display_walltime(cluster: Dict[str, Any]):
    """显示已用机时"""
    walltime = cluster.get('walltime')
    if walltime is None:
        return
    
    cluster_name = cluster.get('clusterName', '未知区域')
    print_section(f"⏱️  {cluster_name}")
    
    hours = float(walltime) if walltime else 0
    
    # 显示为小时数（原始数据就是小时）
    print(f"  本月已用: {Colors.YELLOW}{hours:.2f}{Colors.END} 小时")


def display_other_clusters(others: List[Dict[str, Any]]):
    """显示其他区域"""
    if not others:
        return
    
    print_section(f"📋 其他区域 ({len(others)}个)")
    
    for i, cluster in enumerate(others, 1):
        name = cluster.get('clusterName', 'N/A')
        cid = cluster.get('clusterId', 'N/A')
        
        # 检查服务状态
        has_hpc = bool(cluster.get('hpcUrls'))
        has_ai = bool(cluster.get('aiUrls'))
        has_efile = bool(cluster.get('efileUrls'))
        
        services = []
        if has_hpc:
            services.append("HPC")
        if has_ai:
            services.append("AI")
        if has_efile:
            services.append("文件")
        
        service_str = ', '.join(services) if services else f"{Colors.YELLOW}服务暂不可用{Colors.END}"
        
        print(f"  {i}. {Colors.CYAN}{name}{Colors.END}")
        print(f"     可用服务: {service_str}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='SCNet 用户信息查看工具')
    parser.add_argument('--stats', action='store_true', help='显示作业统计信息')
    parser.add_argument('--walltime', action='store_true', help='显示机时使用信息')
    args = parser.parse_args()
    
    # 加载缓存（禁用自动初始化，由 scnet.py 统一处理）
    cache = load_cache(auto_init=False)
    if not cache:
        sys.exit(1)
    
    clusters = cache.get('clusters', [])
    if not clusters:
        print_error("缓存中没有区域数据")
        sys.exit(1)
    
    # 获取当前默认区域
    current = get_default_cluster(clusters)
    if not current:
        print_error("未找到默认区域")
        sys.exit(1)
    
    # 根据参数显示不同信息
    if args.stats:
        # 显示作业统计信息
        display_dynamic_stats(current)
    elif args.walltime:
        # 显示机时使用信息（显示所有有数据的区域）
        has_walltime_data = False
        for cluster in clusters:
            if cluster.get('walltime') is not None and cluster.get('clusterName') != 'ac':
                if not has_walltime_data:
                    print_header("⏱️  机时使用情况")
                    has_walltime_data = True
                display_walltime(cluster)
        if not has_walltime_data:
            print_warning("暂无机时使用数据")
    else:
        # 默认显示完整用户信息
        # 打印主标题
        cluster_name = current.get('clusterName', 'N/A')
        cluster_id = current.get('clusterId', '')
        print_header(f"当前区域: {cluster_name}")
        
        # 用户信息
        user_info = current.get('clusterUserInfo', {})
        if user_info:
            display_user_info(user_info)
        
        # 家目录和存储配额
        display_home_and_quota(current)
        
        # 集群信息
        display_cluster_info(current)
        
if __name__ == "__main__":
    main()
