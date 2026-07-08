#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Chat Skill - 查询SCNet账户信息、作业信息和文件管理

功能：
1. 获取SCNet账户的token列表
2. 查询账户余额
3. 查询实时作业列表
4. 查询历史作业列表
5. 文件管理（列表、创建目录、上传、下载、删除等）
6. 作业管理（提交作业、删除作业、查询队列等）

配置方式：
仅支持从 ~/.scnet-chat.env 文件读取配置

配置文件示例:
    SCNET_ACCESS_KEY=your_access_key_here
    SCNET_SECRET_KEY=your_secret_key_here
    SCNET_USER=your_username_here

如果配置文件不存在，启动时会交互式提示用户输入配置并自动保存
"""

import hmac
import hashlib
import requests
import json
import time
import os
import sys
import re
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

# 导入配置管理模块
from config_manager import (
    load_config, create_config_template, check_config,
    write_env_file, DEFAULT_ENV_PATH
)

# ============== 日志模块 ==============

class SCNetLogger:
    """SCNet Chat 日志记录器 - 按月轮转日志文件"""

    def __init__(self, log_dir: str = None):
        if log_dir is None:
            # 默认日志目录: ~/.openclaw/workspace/skills/scnet-chat/logs/
            self.log_dir = os.path.expanduser("~/.openclaw/workspace/skills/scnet-chat/logs")
        else:
            self.log_dir = log_dir

        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)

        # 当前日志文件路径
        self.current_log_file = None
        self.current_month = None

        # 初始化日志文件
        self._rotate_log_file()

    def _rotate_log_file(self):
        """按月轮转日志文件"""
        now = datetime.now()
        month_str = now.strftime("%Y-%m")

        # 如果月份变化，创建新日志文件
        if month_str != self.current_month:
            self.current_month = month_str
            self.current_log_file = os.path.join(self.log_dir, f"scnet-chat-{month_str}.log")

            # 写入文件头
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"# SCNet Chat Log Started at {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")

    def log(self, method: str, url: str, params: Any = None,
            response: Any = None, error: str = None, duration_ms: float = None):
        """记录API调用日志"""
        # 检查是否需要轮转
        self._rotate_log_file()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        lines = []
        lines.append(f"[{timestamp}] {method.upper()} {url}")

        # 记录请求参数
        if params:
            try:
                if isinstance(params, dict):
                    params_str = json.dumps(params, ensure_ascii=False, indent=2)
                else:
                    params_str = str(params)
                # 截断过长的参数
                if len(params_str) > 2000:
                    params_str = params_str[:2000] + "... (truncated)"
                lines.append(f"  Params: {params_str}")
            except:
                lines.append(f"  Params: {str(params)[:500]}")

        # 记录响应或错误
        if error:
            lines.append(f"  Error: {error}")
        elif response is not None:
            try:
                if isinstance(response, dict):
                    resp_str = json.dumps(response, ensure_ascii=False, indent=2)
                else:
                    resp_str = str(response)
                # 截断过长的响应
                if len(resp_str) > 2000:
                    resp_str = resp_str[:2000] + "... (truncated)"
                lines.append(f"  Response: {resp_str}")
            except:
                lines.append(f"  Response: {str(response)[:500]}")

        # 记录耗时
        if duration_ms is not None:
            lines.append(f"  Duration: {duration_ms:.2f}ms")

        lines.append("")  # 空行分隔

        # 写入日志文件
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
        except Exception as e:
            print(f"⚠️ 日志写入失败: {e}")

    def log_info(self, message: str):
        """记录信息日志"""
        self._rotate_log_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] INFO: {message}\n")
        except Exception as e:
            print(f"⚠️ 日志写入失败: {e}")

    def log_error(self, message: str):
        """记录错误日志"""
        self._rotate_log_file()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] ERROR: {message}\n")
        except Exception as e:
            print(f"⚠️ 日志写入失败: {e}")

# 全局日志实例
_logger = None

def get_logger() -> SCNetLogger:
    """获取全局日志实例"""
    global _logger
    if _logger is None:
        _logger = SCNetLogger()
    return _logger

def set_logger(logger: SCNetLogger):
    """设置全局日志实例"""
    global _logger
    _logger = logger

# ============== 基础认证和通用方法 ==============

def escape_json(s: Optional[str]) -> str:
    """转义JSON字符串"""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_signature(access_key: str, timestamp: str, user: str, secret_key: str) -> str:
    """生成HMAC-SHA256签名"""
    escaped_ak = escape_json(access_key)
    escaped_ts = escape_json(timestamp)
    escaped_user = escape_json(user)
    data_to_sign = f'{{"accessKey":"{escaped_ak}","timestamp":"{escaped_ts}","user":"{escaped_user}"}}'
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=data_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature.lower()


def get_tokens(access_key: str, secret_key: str, user: str) -> Optional[Dict[str, Any]]:
    """获取SCNet用户token列表"""
    logger = get_logger()
    timestamp = str(int(time.time()))
    signature = generate_signature(access_key, timestamp, user, secret_key)
    tokens_url = "https://api.scnet.cn/api/user/v3/tokens"
    headers = {"user": user, "accessKey": access_key, "signature": signature, "timestamp": timestamp}

    start_time = time.time()
    try:
        response = requests.post(tokens_url, headers=headers, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", tokens_url, headers, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", tokens_url, headers, error=str(e), duration_ms=duration_ms)
        print(f"❌ 获取token失败: {e}")
        return None


def get_center_info(token: str) -> Optional[Dict[str, Any]]:
    """获取授权区域信息"""
    logger = get_logger()
    urls = ["https://www.scnet.cn/ac/openapi/v2/center", "https://api.scnet.cn/ac/openapi/v2/center"]
    headers = {"token": token, "Content-Type": "application/json"}

    for url in urls:
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                duration_ms = (time.time() - start_time) * 1000
                logger.log("GET", url, headers, result, duration_ms=duration_ms)
                return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, headers, error=str(e), duration_ms=duration_ms)
            continue
    return None


def get_hpc_url(center_info: Dict[str, Any]) -> Optional[str]:
    """获取hpcUrl（作业服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    for url_info in data.get("hpcUrls", []):
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_efile_url(center_info: Dict[str, Any]) -> Optional[str]:
    """获取efileUrl（文件服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    for url_info in data.get("efileUrls", []):
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_home_path(center_info: Dict[str, Any]) -> Optional[str]:
    """获取用户家目录"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    return data.get("clusterUserInfo", {}).get("homePath")


def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """获取用户信息（包含账户余额）"""
    logger = get_logger()
    urls = ["https://www.scnet.cn/ac/openapi/v2/user", "https://api.scnet.cn/ac/openapi/v2/user"]
    headers = {"token": token, "Content-Type": "application/json"}
    for url in urls:
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                duration_ms = (time.time() - start_time) * 1000
                logger.log("GET", url, headers, result, duration_ms=duration_ms)
                return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, headers, error=str(e), duration_ms=duration_ms)
            continue
    return None


# ============== 作业操作方法 ==============

def get_cluster_info(hpc_url: str, token: str) -> Optional[Dict[str, Any]]:
    """查询集群信息"""
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/cluster"
    headers = {"token": token, "Content-Type": "application/json"}
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, headers, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, headers, error=str(e), duration_ms=duration_ms)
        return None


def query_user_queues(hpc_url: str, token: str, username: str, scheduler_id: str) -> Optional[Dict[str, Any]]:
    """
    查询用户可访问队列

    API: GET /hpc/openapi/v2/queuenames/users/{username}
    """
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/queuenames/users/{username}"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"strJobManagerID": scheduler_id}
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        print(f"❌ 查询队列失败: {e}")
        return None


def submit_job(hpc_url: str, token: str, scheduler_id: str, job_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    提交作业

    API: POST /hpc/openapi/v2/apptemplates/BASIC/BASE/job
    """
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/apptemplates/BASIC/BASE/job"
    headers = {"token": token, "Content-Type": "application/json"}

    # 构建请求体
    payload = {
        "strJobManagerID": scheduler_id,
        "mapAppJobInfo": {
            "GAP_CMD_FILE": job_config.get("cmd", "sleep 300"),
            "GAP_NNODE": str(job_config.get("nnodes", 1)),
            "GAP_NODE_STRING": job_config.get("node_string", ""),
            "GAP_SUBMIT_TYPE": job_config.get("submit_type", "cmd"),
            "GAP_JOB_NAME": job_config.get("job_name", "SCNetJob"),
            "GAP_WORK_DIR": job_config.get("work_dir", "~"),
            "GAP_QUEUE": job_config.get("queue", "debug"),
            "GAP_NPROC": str(job_config.get("nproc", 1)),
            "GAP_PPN": str(job_config.get("ppn", "")),
            "GAP_NGPU": str(job_config.get("ngpu", "")),
            "GAP_NDCU": str(job_config.get("ndcu", "")),
            "GAP_WALL_TIME": job_config.get("wall_time", "01:00:00"),
            "GAP_EXCLUSIVE": str(job_config.get("exclusive", "")),
            "GAP_APPNAME": job_config.get("appname", "BASE"),
            "GAP_MULTI_SUB": str(job_config.get("multi_sub", "")),
            "GAP_STD_OUT_FILE": job_config.get("stdout", f"{job_config.get('work_dir', '~')}/std.out.%j"),
            "GAP_STD_ERR_FILE": job_config.get("stderr", f"{job_config.get('work_dir', '~')}/std.err.%j"),
        }
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
        print(f"❌ 提交作业失败: {e}")
        return None


def delete_job(hpc_url: str, token: str, scheduler_id: str, username: str, job_id: str) -> Optional[Dict[str, Any]]:
    """
    删除作业

    API: DELETE /hpc/openapi/v2/jobs
    """
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/jobs"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "jobMethod": "5",
        "strJobInfoMap": f"{scheduler_id},{username}:{job_id}:"
    }
    start_time = time.time()
    try:
        response = requests.delete(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("DELETE", url, payload, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("DELETE", url, payload, error=str(e), duration_ms=duration_ms)
        print(f"❌ 删除作业失败: {e}")
        return None


def query_job_detail(hpc_url: str, token: str, scheduler_id: str, job_id: str) -> Optional[Dict[str, Any]]:
    """
    查询作业详情

    API: GET /hpc/openapi/v2/jobs/{job_id}
    """
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/jobs/{job_id}"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"strJobManagerID": scheduler_id}
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        print(f"❌ 查询作业详情失败: {e}")
        return None


def query_jobs(hpc_url: str, token: str, cluster_id: str, start: int = 0, limit: int = 100) -> Optional[Dict[str, Any]]:
    """查询实时作业列表"""
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/jobs"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"strClusterIDList": cluster_id, "start": start, "limit": limit}
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        return None


def query_history_jobs(hpc_url: str, token: str, cluster_id: str, start_time: str, end_time: str,
                       start: int = 0, limit: int = 100) -> Optional[Dict[str, Any]]:
    """查询历史作业列表"""
    logger = get_logger()
    url = f"{hpc_url}/hpc/openapi/v2/historyjobs"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {
        "strClusterNameList": cluster_id,
        "startTime": start_time,
        "endTime": end_time,
        "timeType": "CUSTOM",
        "isQueryByQueueTime": "false",
        "start": start,
        "limit": limit
    }
    req_start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()
        duration_ms = (time.time() - req_start_time) * 1000
        logger.log("GET", url, params, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - req_start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        return None


# ============== 文件操作方法 ==============

def list_files(efile_url: str, token: str, path: Optional[str] = None, limit: int = 100) -> Optional[Dict[str, Any]]:
    """查询文件列表"""
    url = f"{efile_url}/openapi/v2/file/list"
    headers = {"token": token, "Content-Type": "application/json"}
def list_files(efile_url: str, token: str, path: Optional[str] = None, limit: int = 100) -> Optional[Dict[str, Any]]:
    """查询文件列表"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/list"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"limit": limit, "start": 0, "order": "asc", "orderBy": "name"}
    if path:
        params["path"] = path
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, result, duration_ms=duration_ms)
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        return None


def create_folder(efile_url: str, token: str, path: str, create_parents: bool = True) -> bool:
    """创建文件夹"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/mkdir"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": path, "createParents": str(create_parents).lower()}
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        success = result.get("code") == "0" or result.get("code") == "911021"
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, params, result, duration_ms=duration_ms)
        return success
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, params, error=str(e), duration_ms=duration_ms)
        return False


def create_file(efile_url: str, token: str, file_path: str) -> bool:
    """创建空文件"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/touch"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"fileAbsolutePath": file_path}
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        success = result.get("code") == "0" or result.get("code") == "911021"
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, result, duration_ms=duration_ms)
        return success
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
        return False


def upload_file(efile_url: str, token: str, local_path: str, remote_path: str, cover: str = "cover") -> bool:
    """上传文件"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/upload"
    headers = {"token": token}
    start_time = time.time()
    try:
        with open(local_path, 'rb') as f:
            files = {"file": (os.path.basename(local_path), f)}
            data = {"path": remote_path, "cover": cover}
            response = requests.post(url, headers=headers, data=data, files=files, timeout=300)
            result = response.json()
            success = result.get("code") == "0"
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, {"path": remote_path, "cover": cover, "file": local_path}, result, duration_ms=duration_ms)
            return success
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, {"path": remote_path, "cover": cover, "file": local_path}, error=str(e), duration_ms=duration_ms)
        return False


def download_file(efile_url: str, token: str, remote_path: str, local_path: str) -> bool:
    """下载文件"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/download"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": remote_path}
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, stream=True, timeout=300)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, {"status": "success", "local_path": local_path}, duration_ms=duration_ms)
            return True
        else:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, {"status_code": response.status_code}, duration_ms=duration_ms)
            return False
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
        return False


def delete_file(efile_url: str, token: str, path: str, recursive: bool = False) -> bool:
    """删除文件/文件夹"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/remove"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"paths": path, "recursive": str(recursive).lower()}
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        success = result.get("code") == "0"
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, params, result, duration_ms=duration_ms)
        return success
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, params, error=str(e), duration_ms=duration_ms)
        return False


def check_file_exists(efile_url: str, token: str, path: str) -> bool:
    """检查文件是否存在"""
    logger = get_logger()
    url = f"{efile_url}/openapi/v2/file/exist"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"path": path}
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        exists = result.get("code") == "0" and result.get("data", {}).get("exist", False)
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, result, duration_ms=duration_ms)
        return exists
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
        return False


# ============== Notebook管理器类 ==============

class NotebookManager:
    """Notebook管理器"""

    def __init__(self, token: str, ai_url: str = "https://www.scnet.cn"):
        self.token = token
        self.ai_url = ai_url.rstrip('/')
        self.headers = {
            "token": token,
            "Content-Type": "application/json"
        }

    def _get_ai_url(self, endpoint: str) -> str:
        """构建完整的AI服务URL"""
        if endpoint.startswith('/'):
            return f"{self.ai_url}{endpoint}"
        return f"{self.ai_url}/{endpoint}"

    def create_notebook(self, cluster_id: str, image_config: Dict[str, Any],
                        accelerator_type: str = "DCU", accelerator_number: str = "1",
                        resource_group_code: str = None, mount_home: bool = True,
                        start_command: str = None, mount_info: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """创建Notebook实例"""
        logger = get_logger()
        url = self._get_ai_url("/ac/openapi/v2/notebook/actions/create")

        payload = {
            "clusterId": cluster_id,
            "imagePath": image_config.get("path"),
            "imageName": image_config.get("name"),
            "imageSize": image_config.get("size", ""),
            "acceleratorType": accelerator_type,
            "acceleratorNumber": accelerator_number,
            "mountHome": mount_home
        }

        if resource_group_code:
            payload["resourceGroupCode"] = resource_group_code
        if start_command:
            payload["startCommand"] = start_command
        if mount_info:
            payload["mountInfo"] = mount_info

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 创建Notebook失败: {e}")
            return None

    def start_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Notebook实例开机"""
        logger = get_logger()
        url = self._get_ai_url("/ac/openapi/v2/notebook/actions/start")
        payload = {"notebookId": notebook_id}

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 开机失败: {e}")
            return None

    def stop_notebook(self, notebook_id: str, save_env: bool = False) -> Optional[Dict[str, Any]]:
        """Notebook实例关机"""
        logger = get_logger()
        url = self._get_ai_url("/ai/openapi/v2/notebook/actions/stop")
        payload = {"notebookId": notebook_id, "saveEnv": save_env}

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 关机失败: {e}")
            return None

    def release_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """Notebook实例释放"""
        logger = get_logger()
        url = self._get_ai_url("/ai/openapi/v2/notebook/actions/release")
        payload = {"id": notebook_id}

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 释放失败: {e}")
            return None

    def rename_notebook(self, notebook_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        """修改Notebook实例名称"""
        logger = get_logger()
        url = self._get_ai_url("/ai/openapi/v2/notebook/name")
        payload = {"id": notebook_id, "notebookName": new_name}

        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 重命名失败: {e}")
            return None

    def list_notebooks(self, notebook_name: str = None, notebook_status: str = None,
                       page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """查询Notebook实例列表"""
        logger = get_logger()
        url = self._get_ai_url("/ai/openapi/v2/notebook/list")
        params = {"page": page, "size": size}
        if notebook_name:
            params["notebookName"] = notebook_name
        if notebook_status:
            params["notebookStatus"] = notebook_status

        headers = {"token": self.token}

        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询列表失败: {e}")
            return None

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询列表失败: {e}")
            return None

    def get_notebook_detail(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """查询Notebook实例详情"""
        url = self._get_ai_url("/ai/openapi/v2/notebook/detail")
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询详情失败: {e}")
            return None

    def get_notebook_url(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """查询Jupyter服务地址"""
        url = self._get_ai_url("/ai/openapi/v2/notebook/url")
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询URL失败: {e}")
            return None

    def get_images(self, name: str = None, image_type: str = None,
                   accelerator_type: str = None, access: str = "public",
                   page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """查询镜像列表"""
        url = self._get_ai_url("/ai/openapi/v2/image/images")
        payload = {
            "access": access,
            "start": (page - 1) * size,
            "limit": size,
            "sort": "DESC",
            "orderBy": "create_time"
        }
        if name:
            payload["name"] = name
        if image_type:
            payload["type"] = image_type
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询镜像失败: {e}")
            return None

    def get_model_images(self, page: int = 1, size: int = 20,
                         accelerator_type: str = None) -> Optional[Dict[str, Any]]:
        """查询模型镜像列表"""
        url = self._get_ai_url("/ai/openapi/v2/image/models")
        payload = {"page": page, "size": size}
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询模型镜像失败: {e}")
            return None

    def get_resources(self, cluster_ids: List[str], resource_id: str = None) -> Optional[Dict[str, Any]]:
        """查询Notebook资源"""
        url = self._get_ai_url("/ac/openapi/v2/resources/accelerators")
        params = {"clusterIds": ",".join(cluster_ids)}
        if resource_id:
            params["resourceId"] = resource_id
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询资源失败: {e}")
            return None
        """查询Notebook实例列表"""
        url = f"{self.NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/list"
        params = {"page": page, "size": size}
        if notebook_name:
            params["notebookName"] = notebook_name
        if notebook_status:
            params["notebookStatus"] = notebook_status

        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询列表失败: {e}")
            return None

    def get_notebook_detail(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """查询Notebook实例详情"""
        url = f"{self.NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/detail"
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询详情失败: {e}")
            return None

    def get_notebook_url(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """查询Jupyter服务地址"""
        url = f"{self.NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/url"
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询URL失败: {e}")
            return None

    def get_images(self, name: str = None, image_type: str = None,
                   accelerator_type: str = None, access: str = "public",
                   page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """查询镜像列表"""
        url = self._get_ai_url("/ai/openapi/v2/image/images")
        payload = {
            "access": access,
            "start": (page - 1) * size,
            "limit": size,
            "sort": "DESC",
            "orderBy": "create_time"
        }
        if name:
            payload["name"] = name
        if image_type:
            payload["type"] = image_type
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询镜像失败: {e}")
            return None

    def get_model_images(self, page: int = 1, size: int = 20,
                         accelerator_type: str = None) -> Optional[Dict[str, Any]]:
        """查询模型镜像列表"""
        url = self._get_ai_url("/ai/openapi/v2/image/models")
        payload = {"page": page, "size": size}
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询模型镜像失败: {e}")
            return None

    def get_resources(self, cluster_ids: List[str], resource_id: str = None) -> Optional[Dict[str, Any]]:
        """查询Notebook资源"""
        url = self._get_ai_url("/ac/openapi/v2/resources/accelerators")
        params = {"clusterIds": ",".join(cluster_ids)}
        if resource_id:
            params["resourceId"] = resource_id
        headers = {"token": self.token}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询资源失败: {e}")
            return None


# ============== 容器管理器类 ==============

class ContainerManager:
    """容器管理器"""

    def __init__(self, token: str, ai_url: str = "https://www.scnet.cn"):
        self.token = token
        self.ai_url = ai_url.rstrip('/')
        self.headers = {
            "token": token,
            "Content-Type": "application/json"
        }

    def _get_url(self, endpoint: str) -> str:
        """构建完整的AI服务URL"""
        if endpoint.startswith('/'):
            return f"{self.ai_url}{endpoint}"
        return f"{self.ai_url}/{endpoint}"

    def create_container(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建容器实例"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task")
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=config, timeout=60)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, config, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, config, error=str(e), duration_ms=duration_ms)
            print(f"❌ 创建容器失败: {e}")
            return None

    def start_container(self, instance_service_id: str) -> Optional[Dict[str, Any]]:
        """启动容器实例"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/restart")
        params = {"instanceServiceId": instance_service_id}
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, params, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, params, error=str(e), duration_ms=duration_ms)
            print(f"❌ 启动容器失败: {e}")
            return None

    def stop_containers(self, ids: List[str]) -> Optional[Dict[str, Any]]:
        """批量停止容器实例"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/stop")
        params = [("ids", id) for id in ids]
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, {"ids": ids}, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, {"ids": ids}, error=str(e), duration_ms=duration_ms)
            print(f"❌ 停止容器失败: {e}")
            return None

    def delete_containers(self, ids: List[str]) -> Optional[Dict[str, Any]]:
        """批量删除容器实例"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task")
        params = [("ids", id) for id in ids]
        start_time = time.time()
        try:
            response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("DELETE", url, {"ids": ids}, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("DELETE", url, {"ids": ids}, error=str(e), duration_ms=duration_ms)
            print(f"❌ 删除容器失败: {e}")
            return None

    def execute_script(self, instance_id: str, script_content: str, scope: str = "all") -> Optional[Dict[str, Any]]:
        """批量执行脚本"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/execute-script")
        payload = {
            "id": instance_id,
            "startScriptContent": script_content,
            "startScriptActionScope": scope
        }
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 执行脚本失败: {e}")
            return None

    def list_containers(self, status: str = None, task_type: str = None,
                        instance_name: str = None, start: int = 0,
                        limit: int = 20, sort: str = "desc") -> Optional[Dict[str, Any]]:
        """查询容器实例列表"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/task/list")
        params = {"start": start, "limit": limit, "sort": sort}
        if status:
            params["status"] = status
        if task_type:
            params["taskType"] = task_type
        if instance_name:
            params["instanceServiceName"] = instance_name
        start_time = time.time()
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询容器列表失败: {e}")
            return None

    def get_container_detail(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """查询容器实例详情"""
        logger = get_logger()
        url = self._get_url(f"/ai/openapi/v2/instance-service/{instance_id}/detail")
        headers = {"token": self.token}
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询容器详情失败: {e}")
            return None

    def get_container_url(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """获取容器实例URL"""
        logger = get_logger()
        url = self._get_url(f"/ai/openapi/v2/instance-service/{instance_id}/url")
        headers = {"token": self.token}
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, error=str(e), duration_ms=duration_ms)
            print(f"❌ 获取容器URL失败: {e}")
            return None

    def update_resource_spec(self, instance_id: str, cpu_number: int,
                             gpu_number: int, ram_size: int) -> Optional[Dict[str, Any]]:
        """更新资源规格"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/resource-spec/actions/update")
        payload = {"id": instance_id, "cpuNumber": cpu_number, "gpuNumber": gpu_number, "ramSize": ram_size}
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 更新资源规格失败: {e}")
            return None

    def get_resource_limits(self, accelerator_type: str, resource_group: str) -> Optional[Dict[str, Any]]:
        """查询节点资源限额"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/resources")
        params = {"acceleratorType": accelerator_type, "resourceGroup": resource_group}
        headers = {"token": self.token}
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询资源限额失败: {e}")
            return None

    def get_resource_groups(self) -> Optional[Dict[str, Any]]:
        """查询资源分组"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/resource-group")
        headers = {"token": self.token}
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询资源分组失败: {e}")
            return None

    def get_allowed_mount_dirs(self) -> Optional[Dict[str, Any]]:
        """检查授权的挂载路径"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/instance-service/allowed-mount-dir")
        headers = {"token": self.token}
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("GET", url, None, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询挂载路径失败: {e}")
            return None

    def get_images(self, name: str = None, image_type: str = None,
                   accelerator_type: str = None, access: str = "public",
                   page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """获取镜像列表"""
        logger = get_logger()
        url = self._get_url("/ai/openapi/v2/image/images")
        payload = {"access": access, "start": (page - 1) * size, "limit": size, "sort": "DESC", "orderBy": "create_time"}
        if name:
            payload["name"] = name
        if image_type:
            payload["type"] = image_type
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type
        start_time = time.time()
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = response.json()
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, result, duration_ms=duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.log("POST", url, payload, error=str(e), duration_ms=duration_ms)
            print(f"❌ 查询镜像失败: {e}")
            return None
        if image_type:
            payload["type"] = image_type
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询镜像失败: {e}")
            return None


# ============== SCNet客户端类 ==============

class SCNetClient:
    """SCNet统一客户端"""

    def __init__(self, access_key: str, secret_key: str, user: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.user = user
        self.tokens_data = None
        self._tokens_cache = {}
        self._center_info_cache = {}
        self._hpc_url_cache = {}
        self._efile_url_cache = {}
        self._home_path_cache = {}
        self._cluster_id_cache = {}
        self._notebook_manager = None
        self._container_manager = None

    def init_tokens(self) -> bool:
        """初始化token列表"""
        self.tokens_data = get_tokens(self.access_key, self.secret_key, self.user)
        if self.tokens_data and self.tokens_data.get("code") == "0":
            for token_info in self.tokens_data.get("data", []):
                name = token_info.get("clusterName", "")
                self._tokens_cache[name] = token_info.get("token", "")
                self._cluster_id_cache[name] = token_info.get("clusterId", "")
            # 初始化NotebookManager和ContainerManager（使用第一个token和aiUrl）
            first_token = list(self._tokens_cache.values())[0] if self._tokens_cache else None
            first_cluster = list(self._tokens_cache.keys())[0] if self._tokens_cache else None
            if first_token and first_cluster:
                ai_url = self._get_ai_url(first_cluster)
                if ai_url:
                    self._notebook_manager = NotebookManager(first_token, ai_url)
                    self._container_manager = ContainerManager(first_token, ai_url)
                else:
                    self._notebook_manager = NotebookManager(first_token)
                    self._container_manager = ContainerManager(first_token)
            return True
        return False

    def get_notebook_manager(self) -> Optional[NotebookManager]:
        """获取Notebook管理器"""
        return self._notebook_manager

    def get_container_manager(self) -> Optional[ContainerManager]:
        """获取容器管理器"""
        return self._container_manager

    def get_cluster_id(self, cluster_name: str) -> Optional[str]:
        """获取计算中心ID（用于Notebook创建）"""
        return self._cluster_id_cache.get(cluster_name)

    def get_token(self, cluster_name: str) -> Optional[str]:
        """获取指定计算中心的token"""
        return self._tokens_cache.get(cluster_name)

    def _get_center_info(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """获取计算中心信息（带缓存）"""
        if cluster_name in self._center_info_cache:
            return self._center_info_cache[cluster_name]
        token = self.get_token(cluster_name)
        if not token:
            return None
        info = get_center_info(token)
        if info:
            self._center_info_cache[cluster_name] = info
        return info

    def get_hpc_url(self, cluster_name: str) -> Optional[str]:
        """获取hpcUrl（作业服务）"""
        if cluster_name in self._hpc_url_cache:
            return self._hpc_url_cache[cluster_name]
        info = self._get_center_info(cluster_name)
        url = get_hpc_url(info) if info else None
        if url:
            self._hpc_url_cache[cluster_name] = url
        return url

    def get_efile_url(self, cluster_name: str) -> Optional[str]:
        """获取efileUrl（文件服务）"""
        if cluster_name in self._efile_url_cache:
            return self._efile_url_cache[cluster_name]
        info = self._get_center_info(cluster_name)
        url = get_efile_url(info) if info else None
        if url:
            self._efile_url_cache[cluster_name] = url
        return url

    def get_home_path(self, cluster_name: str) -> Optional[str]:
        """获取家目录"""
        if cluster_name in self._home_path_cache:
            return self._home_path_cache[cluster_name]
        info = self._get_center_info(cluster_name)
        path = get_home_path(info) if info else None
        if path:
            self._home_path_cache[cluster_name] = path
        return path

    def _get_ai_url(self, cluster_name: str) -> Optional[str]:
        """获取AI服务URL（用于Notebook）"""
        info = self._get_center_info(cluster_name)
        if not info or info.get("code") != "0":
            return None
        data = info.get("data", {})
        ai_urls = data.get("aiUrls", [])
        for url_info in ai_urls:
            if url_info.get("enable") == "true":
                return url_info.get("url")
        return None

    def find_cluster_by_name(self, name_hint: str) -> Optional[str]:
        """根据名称提示查找计算中心"""
        name_hint = name_hint.lower()
        for cluster_name in self._tokens_cache.keys():
            if name_hint in cluster_name.lower():
                return cluster_name
        return None

    def get_scheduler_id(self, cluster_name: str) -> Optional[str]:
        """获取调度器ID"""
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        if not hpc_url or not token:
            return None
        cluster_info = get_cluster_info(hpc_url, token)
        if cluster_info and cluster_info.get("code") == "0":
            clusters = cluster_info.get("data", [])
            if clusters:
                return str(clusters[0].get("id", ""))
        return None

    # ============== 账户操作 ==============

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """获取账户信息"""
        logger = get_logger()
        logger.log_info("获取账户信息")
        if not self.tokens_data:
            if not self.init_tokens():
                logger.log_error("获取账户信息失败: 无法初始化token")
                return None
        first_token = list(self._tokens_cache.values())[0] if self._tokens_cache else None
        if first_token:
            result = get_user_info(first_token)
            if result and result.get("code") == "0":
                logger.log_info("获取账户信息成功")
            else:
                logger.log_error(f"获取账户信息失败: {result}")
            return result
        logger.log_error("获取账户信息失败: 无可用token")
        return None

    # ============== 作业操作 ==============

    def get_user_queues(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """获取用户可访问队列"""
        logger = get_logger()
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        scheduler_id = self.get_scheduler_id(cluster_name)
        if not hpc_url or not token or not scheduler_id:
            logger.log_error(f"获取队列失败: 计算中心 {cluster_name} 配置不完整")
            return None
        logger.log_info(f"获取计算中心 {cluster_name} 的队列")
        return query_user_queues(hpc_url, token, self.user, scheduler_id)

    def submit_job(self, cluster_name: str, job_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """提交作业"""
        logger = get_logger()
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        scheduler_id = self.get_scheduler_id(cluster_name)
        if not hpc_url or not token or not scheduler_id:
            logger.log_error(f"提交作业失败: 计算中心 {cluster_name} 配置不完整")
            return None
        logger.log_info(f"提交作业到 {cluster_name}: {job_config.get('job_name', '未命名')}")
        return submit_job(hpc_url, token, scheduler_id, job_config)

    def delete_job(self, cluster_name: str, job_id: str) -> Optional[Dict[str, Any]]:
        """删除作业"""
        logger = get_logger()
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        scheduler_id = self.get_scheduler_id(cluster_name)
        if not hpc_url or not token or not scheduler_id:
            logger.log_error(f"删除作业失败: 计算中心 {cluster_name} 配置不完整")
            return None
        logger.log_info(f"删除作业 {job_id} 从 {cluster_name}")
        return delete_job(hpc_url, token, scheduler_id, self.user, job_id)

    def get_job_detail(self, cluster_name: str, job_id: str) -> Optional[Dict[str, Any]]:
        """查询作业详情"""
        logger = get_logger()
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        scheduler_id = self.get_scheduler_id(cluster_name)
        if not hpc_url or not token or not scheduler_id:
            logger.log_error(f"查询作业详情失败: 计算中心 {cluster_name} 配置不完整")
            return None
        return query_job_detail(hpc_url, token, scheduler_id, job_id)

    def get_running_jobs(self, cluster_name: str) -> Optional[Dict[str, Any]]:
        """查询实时作业"""
        logger = get_logger()
        hpc_url = self.get_hpc_url(cluster_name)
        token = self.get_token(cluster_name)
        cluster_id = self.get_cluster_id(cluster_name)
        if not hpc_url or not token or not cluster_id:
            logger.log_error(f"查询作业失败: 计算中心 {cluster_name} 配置不完整")
            return None
        return query_jobs(hpc_url, token, cluster_id)

    def get_all_jobs(self, days: int = 7) -> Dict[str, Any]:
        """获取所有计算中心的作业"""
        logger = get_logger()
        logger.log_info(f"获取所有计算中心 {days} 天内的作业")
        if not self.tokens_data:
            if not self.init_tokens():
                logger.log_error("获取作业失败: 无法初始化token")
                return {"active_jobs": [], "history_jobs": []}

        all_active = []
        all_history = []

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        for cluster_name, token in self._tokens_cache.items():
            hpc_url = self.get_hpc_url(cluster_name)
            if not hpc_url:
                continue

            cluster_info = get_cluster_info(hpc_url, token)
            if not cluster_info or cluster_info.get("code") != "0":
                continue

            for cluster in cluster_info.get("data", []):
                scheduler_id = str(cluster.get("id", ""))
                if not scheduler_id:
                    continue

                jobs_data = query_jobs(hpc_url, token, scheduler_id)
                if jobs_data and jobs_data.get("code") == "0":
                    for job in jobs_data.get("data", {}).get("list", []):
                        job["_cluster_name"] = cluster_name
                        all_active.append(job)

                history_data = query_history_jobs(hpc_url, token, scheduler_id, start_str, end_str)
                if history_data and history_data.get("code") == "0":
                    for job in history_data.get("data", {}).get("list", []):
                        job["_cluster_name"] = cluster_name
                        all_history.append(job)

        logger.log_info(f"获取作业完成: {len(all_active)} 个活跃作业, {len(all_history)} 个历史作业")
        return {"active_jobs": all_active, "history_jobs": all_history}

    # ============== 文件操作 ==============

    def list_dir(self, cluster_name: str, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """列出目录"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"列出目录失败: 计算中心 {cluster_name} 配置不完整")
            return None
        logger.log_info(f"列出目录 {cluster_name}:{path or '/'}")
        return list_files(efile_url, token, path)

    def mkdir(self, cluster_name: str, path: str, create_parents: bool = True) -> bool:
        """创建目录"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"创建目录失败: 计算中心 {cluster_name} 配置不完整")
            return False
        logger.log_info(f"创建目录 {cluster_name}:{path}")
        return create_folder(efile_url, token, path, create_parents)

    def touch(self, cluster_name: str, file_path: str) -> bool:
        """创建空文件"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"创建文件失败: 计算中心 {cluster_name} 配置不完整")
            return False
        logger.log_info(f"创建文件 {cluster_name}:{file_path}")
        return create_file(efile_url, token, file_path)

    def upload(self, cluster_name: str, local_path: str, remote_path: str) -> bool:
        """上传文件"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"上传文件失败: 计算中心 {cluster_name} 配置不完整")
            return False
        logger.log_info(f"上传文件 {local_path} -> {cluster_name}:{remote_path}")
        return upload_file(efile_url, token, local_path, remote_path)

    def download(self, cluster_name: str, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"下载文件失败: 计算中心 {cluster_name} 配置不完整")
            return False
        logger.log_info(f"下载文件 {cluster_name}:{remote_path} -> {local_path}")
        return download_file(efile_url, token, remote_path, local_path)

    def remove(self, cluster_name: str, path: str, recursive: bool = False) -> bool:
        """删除文件/目录"""
        logger = get_logger()
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            logger.log_error(f"删除文件失败: 计算中心 {cluster_name} 配置不完整")
            return False
        logger.log_info(f"删除 {cluster_name}:{path} (recursive={recursive})")
        return delete_file(efile_url, token, path, recursive)

    def exists(self, cluster_name: str, path: str) -> bool:
        """检查文件是否存在"""
        efile_url = self.get_efile_url(cluster_name)
        token = self.get_token(cluster_name)
        if not efile_url or not token:
            return False
        return check_file_exists(efile_url, token, path)


# ============== 自然语言意图解析 ==============

class IntentParser:
    """自然语言意图解析器"""

    CLUSTER_KEYWORDS = {
        "昆山": "华东一区【昆山】",
        "华东一区": "华东一区【昆山】",
        "哈尔滨": "东北一区【哈尔滨】",
        "东北": "东北一区【哈尔滨】",
        "东北一区": "东北一区【哈尔滨】",
        "乌镇": "华东三区【乌镇】",
        "华东三区": "华东三区【乌镇】",
        "西安": "西北一区【西安】",
        "西北": "西北一区【西安】",
        "西北一区": "西北一区【西安】",
        "雄衡": "华北一区【雄衡】",
        "华北": "华北一区【雄衡】",
        "华北一区": "华北一区【雄衡】",
        "山东": "华东四区【山东】",
        "华东四区": "华东四区【山东】",
        "四川": "西南一区【四川】",
        "西南": "西南一区【四川】",
        "西南一区": "西南一区【四川】",
        "核心": "核心节点【分区一】",
        "核心节点": "核心节点【分区一】",
        "分区一": "核心节点【分区一】",
        "分区二": "核心节点【分区二】",
    }

    @classmethod
    def parse_cluster(cls, text: str) -> Optional[str]:
        """从文本中解析计算中心名称"""
        text_lower = text.lower()
        for keyword, cluster_name in cls.CLUSTER_KEYWORDS.items():
            if keyword in text_lower:
                return cluster_name
        return None

    @classmethod
    def parse_path(cls, text: str) -> Optional[str]:
        """从文本中解析路径"""
        patterns = [
            r'(/public/home/[^\s\,\;\,]+)',
            r'(/work/home/[^\s\,\;\,]+)',
            r'(/home/[^\s\,\;\,]+)',
            r'(~/[^\s\,\;\,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @classmethod
    def parse_local_path(cls, text: str) -> Optional[str]:
        """从文本中解析本地路径"""
        patterns = [
            r'(/Users/[^\s\,\;\,]+)',
            r'(~/[^\s\,\;\,]+)',
            r'(\.[^\s\,\;\,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @classmethod
    def is_account_query(cls, text: str) -> bool:
        """是否是查询账户信息"""
        keywords = ["余额", "账户", "account", "balance", "多少钱", "欠费", "我的账户", "我的余额"]
        # 匹配"我的账户余额是多少"、"我的余额"等句式
        patterns = [
            r'我的\s*(账户)?\s*余额\s*(是)?\s*(多少|几|剩)',
            r'账户\s*余额\s*(是)?\s*(多少|几|剩)',
            r'余额\s*(是)?\s*(多少|几|剩)',
        ]
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            return True
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def parse_job_id(cls, text: str) -> Optional[str]:
        """从文本中解析8位数字作业号
        
        匹配格式:
        - 纯8位数字: 24254669
        - 带前缀: 作业号24254669, job_id 24254669, job id 24254669
        - 带描述: 作业24254669的状态
        """
        # 先尝试匹配带关键词的作业号
        patterns_with_keyword = [
            r'作业号\s*[:：]?\s*(\d{8})',
            r'作业\s*[iI][dD]\s*[:：]?\s*(\d{8})',
            r'[jJ][oO][bB][_\s]*[iI][dD]\s*[:：]?\s*(\d{8})',
            r'[jJ][oO][bB]\s*[iI][dD]\s*[:：]?\s*(\d{8})',
            r'作业\s*[:：]?\s*(\d{8})',
        ]
        for pattern in patterns_with_keyword:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        # 然后匹配独立的8位数字（但排除时间、日期等常见格式）
        # 要求数字前后是边界或非数字字符
        standalone_pattern = r'(?:^|\s|\D)(\d{8})(?:\s|\D|$)'
        matches = re.findall(standalone_pattern, text)
        for m in matches:
            # 排除可能是日期或时间的数字（如20251231, 12345678等）
            if not (m.startswith('20') or m.startswith('19')):  # 排除年份格式
                return m
        # 如果没有更好的匹配，返回第一个8位数字
        if matches:
            return matches[0]
        return None

    @classmethod
    def is_job_query(cls, text: str) -> bool:
        """是否是查询作业"""
        keywords = ["查询作业", "查看作业", "作业状态", "job list", "作业列表", "我有哪些作业", "我的作业"]
        patterns = [
            r'我\s*有\s*(哪些|什么)\s*作业',
            r'我的\s*作业\s*(有)?\s*(哪些|什么)?',
            r'作业\s*(有)?\s*(哪些|什么)',
            r'看看\s*作业',
            r'查[一下询]*\s*作业',
        ]
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            return True
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def is_job_detail_query(cls, text: str) -> bool:
        """是否是查询作业详情（包含作业号）"""
        # 如果解析到8位作业号，认为是查询作业详情
        return cls.parse_job_id(text) is not None

    @classmethod
    def is_job_submit(cls, text: str) -> bool:
        """是否是提交作业"""
        keywords = ["提交作业", "submit", "提交任务", "运行作业", "跑作业", "投递作业", "创建作业", "新建作业", "作业提交"]
        patterns = [
            r'投递\s*作业',
            r'创建\s*作业',
            r'新建\s*作业',
            r'提交\s*作业',
            r'作业\s*提交',
        ]
        text_lower = text.lower()
        if any(kw in text_lower for kw in keywords):
            return True
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def is_job_delete(cls, text: str) -> bool:
        """是否是删除作业"""
        keywords = ["删除作业", "cancel", "terminate", "停止作业", "取消作业"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_file_list(cls, text: str) -> bool:
        """是否是列出文件"""
        keywords = ["列出", "显示", "查看", "ls", "list", "目录", "文件列表"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_mkdir(cls, text: str) -> bool:
        """是否是创建目录"""
        keywords = ["创建文件夹", "创建目录", "mkdir", "新建文件夹", "新建目录"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_upload(cls, text: str) -> bool:
        """是否是上传"""
        keywords = ["上传", "upload", "发送文件", "传到"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_download(cls, text: str) -> bool:
        """是否是下载"""
        keywords = ["下载", "download", "下载到", "拉取"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_delete(cls, text: str) -> bool:
        """是否是删除"""
        keywords = ["删除", "remove", "delete", "rm", "删掉"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_create_file(cls, text: str) -> bool:
        """是否是创建文件"""
        keywords = ["创建文件", "新建文件", "touch", "生成文件"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_create(cls, text: str) -> bool:
        """是否是创建Notebook"""
        keywords = ["创建notebook", "新建notebook", "创建实例", "新建实例", "create notebook"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_start(cls, text: str) -> bool:
        """是否是开机Notebook"""
        keywords = ["notebook开机", "启动notebook", "开启notebook", "start notebook", "开机"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_stop(cls, text: str) -> bool:
        """是否是关机Notebook"""
        keywords = ["notebook关机", "停止notebook", "关闭notebook", "stop notebook", "关机"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_release(cls, text: str) -> bool:
        """是否是释放Notebook"""
        keywords = ["释放notebook", "删除notebook", "销毁notebook", "release notebook"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_list(cls, text: str) -> bool:
        """是否是查询Notebook列表"""
        keywords = ["notebook列表", "查询notebook", "查看notebook", "notebook list", "我的notebook"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_detail(cls, text: str) -> bool:
        """是否是查询Notebook详情"""
        keywords = ["notebook详情", "notebook状态", "notebook信息", "notebook detail"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_notebook_url(cls, text: str) -> bool:
        """是否是查询Notebook URL"""
        keywords = ["notebook地址", "notebook url", "notebook链接", "访问notebook"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_create(cls, text: str) -> bool:
        """是否是创建容器"""
        keywords = ["创建容器", "新建容器", "create container", "启动容器实例"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_start(cls, text: str) -> bool:
        """是否是启动容器"""
        keywords = ["启动容器", "开启容器", "start container", "容器开机"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_stop(cls, text: str) -> bool:
        """是否是停止容器"""
        keywords = ["停止容器", "关闭容器", "stop container", "容器关机"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_delete(cls, text: str) -> bool:
        """是否是删除容器"""
        keywords = ["删除容器", "移除容器", "delete container", "销毁容器"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_list(cls, text: str) -> bool:
        """是否是查询容器列表"""
        keywords = ["容器列表", "查询容器", "查看容器", "container list", "我的容器"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_detail(cls, text: str) -> bool:
        """是否是查询容器详情"""
        keywords = ["容器详情", "容器状态", "容器信息", "container detail"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_url(cls, text: str) -> bool:
        """是否是查询容器URL"""
        keywords = ["容器地址", "容器url", "容器链接", "访问容器"]
        return any(kw in text.lower() for kw in keywords)

    @classmethod
    def is_container_execute(cls, text: str) -> bool:
        """是否是执行脚本"""
        keywords = ["执行脚本", "运行脚本", "execute script", "容器脚本"]
        return any(kw in text.lower() for kw in keywords)


# ============== 作业提交向导 ==============

class JobSubmitWizard:
    """作业提交向导"""

    DEFAULTS = {
        "nnodes": "1",
        "ppn": "1",
        "wall_time": "01:00:00",
        "work_dir": "~/claw_workspace",
        "submit_type": "cmd",
        "appname": "BASE",
    }

    def __init__(self, client: SCNetClient, cluster_name: str):
        self.client = client
        self.cluster_name = cluster_name
        self.job_config = {}

    def get_available_queues(self) -> List[Dict[str, Any]]:
        """获取可用队列"""
        result = self.client.get_user_queues(self.cluster_name)
        if result and result.get("code") == "0":
            return result.get("data", [])
        return []

    def build_job_config(self, **kwargs) -> Dict[str, Any]:
        """构建作业配置"""
        config = self.DEFAULTS.copy()
        config.update(kwargs)

        # 确保工作目录存在
        work_dir = config.get("work_dir", "~/claw_workspace")
        if work_dir.startswith("~"):
            home = self.client.get_home_path(self.cluster_name) or "/public/home/yiziqinx"
            work_dir = work_dir.replace("~", home)
            config["work_dir"] = work_dir

        # 设置输出文件路径
        config["stdout"] = config.get("stdout", f"{work_dir}/std.out.%j")
        config["stderr"] = config.get("stderr", f"{work_dir}/std.err.%j")

        return config

    def preview_job_config(self, config: Dict[str, Any]) -> str:
        """预览作业配置"""
        lines = [
            "📋 作业配置预览:",
            "-" * 40,
            f"作业名称: {config.get('job_name', '未设置')}",
            f"运行命令: {config.get('cmd', '未设置')}",
            f"节点数: {config.get('nnodes', 1)}",
            f"每节点核数: {config.get('ppn', 1)}",
            f"运行时长: {config.get('wall_time', '01:00:00')}",
            f"队列: {config.get('queue', '未设置')}",
            f"工作目录: {config.get('work_dir', '~')}",
            f"标准输出: {config.get('stdout', '')}",
            f"错误输出: {config.get('stderr', '')}",
            "-" * 40,
        ]
        return "\n".join(lines)

    def submit(self, config: Dict[str, Any], auto_confirm: bool = False) -> Optional[str]:
        """
        提交作业

        参数:
            config: 作业配置
            auto_confirm: 是否自动确认（不询问用户）
        
        返回:
            作业ID 或 None
        """
        # 如果没有自动确认，先展示配置并请求确认
        if not auto_confirm:
            # 展示完整的作业配置
            preview = self.preview_job_config(config)
            print("\n" + preview)
            
            # 检查队列是否已设置，如果没有或不确定是否有效，列出可用队列
            queue = config.get('queue', '')
            if not queue:
                print("\n⚠️  未指定队列，正在获取可用队列...")
                queues = self.get_available_queues()
                if queues:
                    print("\n📋 可用队列列表:")
                    print("-" * 40)
                    for i, q in enumerate(queues, 1):
                        queue_name = q.get('queueName', '未知')
                        status = q.get('status', '未知')
                        # 显示队列状态和基本信息
                        status_icon = "🟢" if status == "open" else "🔴" if status == "closed" else "⚪"
                        print(f"  {i}. {queue_name} {status_icon} [{status}]")
                        # 显示队列详细信息（如果有）
                        max_nodes = q.get('maxNodes', '')
                        max_time = q.get('maxWallTime', '')
                        if max_nodes or max_time:
                            details = []
                            if max_nodes:
                                details.append(f"最大节点: {max_nodes}")
                            if max_time:
                                details.append(f"最大时长: {max_time}")
                            print(f"     ({', '.join(details)})")
                    print("-" * 40)
                    print("请设置队列后重新提交")
                    return None
                else:
                    print("❌ 无法获取可用队列列表")
                    return None
            else:
                # 验证队列是否有效
                queues = self.get_available_queues()
                queue_names = [q.get('queueName') for q in queues]
                if queue not in queue_names:
                    print(f"\n⚠️  队列 '{queue}' 可能不可用或您无权访问")
                    if queues:
                        print("\n📋 您可用的队列:")
                        print("-" * 40)
                        for i, q in enumerate(queues, 1):
                            queue_name = q.get('queueName', '未知')
                            status = q.get('status', '未知')
                            status_icon = "🟢" if status == "open" else "🔴"
                            print(f"  {i}. {queue_name} {status_icon}")
                        print("-" * 40)
                    print("\n是否继续提交? (队列不可用可能导致提交失败)")
            
            # 请求用户确认
            print("\n⚠️  请确认以上作业配置是否正确")
            print("   输入 'yes' 或 'y' 确认提交")
            print("   输入 'no' 或 'n' 取消提交")
            print("   或直接按 Enter 取消")
            
            try:
                user_input = input("\n确认提交? [y/N]: ").strip().lower()
                if user_input not in ['yes', 'y', '是']:
                    print("❌ 已取消提交")
                    return None
            except (KeyboardInterrupt, EOFError):
                print("\n❌ 已取消提交")
                return None
        
        # 执行提交
        print(f"\n🚀 正在提交作业到 {self.cluster_name}...")
        result = self.client.submit_job(self.cluster_name, config)
        if result and result.get("code") == "0":
            job_id = result.get("data")
            print(f"✅ 作业提交成功! 作业ID: {job_id}")
            return job_id
        else:
            error_msg = result.get("message", "未知错误") if result else "请求失败"
            print(f"❌ 作业提交失败: {error_msg}")
            return None


class NotebookCreateWizard:
    """Notebook创建向导"""

    STATUS_MAP = {
        "Creating": "创建中",
        "Restarting": "开机中",
        "Running": "运行中",
        "Terminated": "已关机",
        "Failed": "失败",
        "Shutting": "关机中"
    }

    def __init__(self, manager: NotebookManager):
        self.manager = manager
        self.config = {}

    def preview_config(self) -> str:
        """预览配置"""
        lines = [
            "📋 Notebook配置预览:",
            "-" * 40,
            f"实例名称: {self.config.get('name', '未设置')}",
            f"计算中心ID: {self.config.get('cluster_id', '未设置')}",
            f"镜像: {self.config.get('image_name', '未设置')}",
            f"加速器类型: {self.config.get('accelerator_type', 'DCU')}",
            f"加速器数量: {self.config.get('accelerator_number', '1')}",
            f"挂载主目录: {self.config.get('mount_home', True)}",
            f"启动命令: {self.config.get('start_command', '默认')}",
            "-" * 40,
        ]
        return "\n".join(lines)

    def create(self) -> Optional[str]:
        """创建Notebook"""
        image_config = {
            "path": self.config.get("image_path"),
            "name": self.config.get("image_name"),
            "size": self.config.get("image_size", "")
        }

        result = self.manager.create_notebook(
            cluster_id=self.config.get("cluster_id"),
            image_config=image_config,
            accelerator_type=self.config.get("accelerator_type", "DCU"),
            accelerator_number=self.config.get("accelerator_number", "1"),
            resource_group_code=self.config.get("resource_group_code"),
            mount_home=self.config.get("mount_home", True),
            start_command=self.config.get("start_command"),
            mount_info=self.config.get("mount_info")
        )

        if result and result.get("code") == "0":
            data = result.get("data", {})
            return data.get("notebookId")
        return None

    @classmethod
    def format_status(cls, status: str) -> str:
        """格式化状态"""
        return cls.STATUS_MAP.get(status, status)

def main():
    """主函数"""
    # 从 ~/.scnet-chat.env 加载配置
    config = load_config()
    is_valid, missing_keys = check_config(config)

    if not is_valid:
        print("❌ 错误: 缺少必要的配置项")
        print(f"\n缺失的配置项: {', '.join(missing_keys)}")
        print(f"\n配置文件未找到: {DEFAULT_ENV_PATH}")
        print(f"\n请提供以下配置信息:")

        # 交互式获取配置
        print("\n请输入 SCNet 配置信息:")
        access_key = input("SCNET_ACCESS_KEY: ").strip()
        secret_key = input("SCNET_SECRET_KEY: ").strip()
        user = input("SCNET_USER: ").strip()

        if not all([access_key, secret_key, user]):
            print("❌ 配置信息不完整，退出")
            sys.exit(1)

        # 保存配置到文件
        config = {
            'access_key': access_key,
            'secret_key': secret_key,
            'user': user
        }
        if write_env_file(config):
            print(f"\n✅ 配置已保存到: {DEFAULT_ENV_PATH}")
        else:
            print(f"\n⚠️  配置保存失败，但会继续使用当前配置")
    else:
        print(f"✅ 已从 {DEFAULT_ENV_PATH} 加载配置")

    access_key = config.get('access_key')
    secret_key = config.get('secret_key')
    user = config.get('user')

    client = SCNetClient(access_key, secret_key, user)

    print("🔑 正在初始化SCNet客户端...")
    if not client.init_tokens():
        print("❌ 初始化失败")
        sys.exit(1)

    print(f"✅ 已连接到 {len(client._tokens_cache)} 个计算中心")


if __name__ == "__main__":
    main()
