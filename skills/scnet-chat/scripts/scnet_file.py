#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet File Manager - SCNet文件管理模块

功能：
1. 查询文件列表
2. 创建文件夹
3. 创建文件
4. 上传文件（普通上传和分片上传）
5. 下载文件
6. 删除文件/文件夹
7. 复制/移动文件
8. 重命名文件
9. 检查文件是否存在
10. 检查文件权限

所有文件操作接口使用efileUrls（从get_center_info获取）
"""

import hmac
import hashlib
import requests
import json
import time
import os
import sys
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

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
    timestamp = str(int(time.time()))
    signature = generate_signature(access_key, timestamp, user, secret_key)
    tokens_url = "https://api.scnet.cn/api/user/v3/tokens"
    headers = {"user": user, "accessKey": access_key, "signature": signature, "timestamp": timestamp}
    try:
        response = requests.post(tokens_url, headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ 获取token失败: {e}")
        return None


def get_center_info(token: str) -> Optional[Dict[str, Any]]:
    """获取授权区域信息"""
    urls = ["https://www.scnet.cn/ac/openapi/v2/center", "https://api.scnet.cn/ac/openapi/v2/center"]
    headers = {"token": token, "Content-Type": "application/json"}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except:
            continue
    return None


def get_efile_url(center_info: Dict[str, Any]) -> Optional[str]:
    """从授权区域信息中获取可用的efileUrl（文件服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    efile_urls = data.get("efileUrls", [])
    for url_info in efile_urls:
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_home_path(center_info: Dict[str, Any]) -> Optional[str]:
    """获取用户家目录路径"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    cluster_user_info = data.get("clusterUserInfo", {})
    return cluster_user_info.get("homePath")


# ============== 文件操作方法 ==============

def list_files(efile_url: str, token: str, path: Optional[str] = None, 
               limit: int = 100, start: int = 0) -> Optional[Dict[str, Any]]:
    """
    查询文件列表
    
    API: GET /efile/openapi/v2/file/list
    Note: efile_url 已经包含 /efile 后缀，不需要重复添加
    """
    url = f"{efile_url}/openapi/v2/file/list"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"limit": limit, "start": start, "order": "asc", "orderBy": "name"}
    if path:
        params["path"] = path
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ 查询文件列表失败: {e}")
        return None


def check_file_exists(efile_url: str, token: str, path: str) -> bool:
    """
    检查文件/文件夹是否存在
    
    API: POST /efile/openapi/v2/file/exist
    """
    url = f"{efile_url}/openapi/v2/file/exist"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"path": path}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return result.get("data", {}).get("exist", False)
        return False
    except Exception as e:
        print(f"❌ 检查文件存在性失败: {e}")
        return False


def create_folder(efile_url: str, token: str, path: str, create_parents: bool = True) -> bool:
    """
    创建文件夹
    
    API: POST /efile/openapi/v2/file/mkdir
    """
    url = f"{efile_url}/openapi/v2/file/mkdir"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": path, "createParents": str(create_parents).lower()}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        elif result.get("code") == "911021":
            # 文件夹已存在
            return True
        else:
            print(f"❌ 创建文件夹失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 创建文件夹失败: {e}")
        return False


def create_file(efile_url: str, token: str, file_path: str) -> bool:
    """
    创建空文件
    
    API: POST /efile/openapi/v2/file/touch
    """
    url = f"{efile_url}/openapi/v2/file/touch"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"fileAbsolutePath": file_path}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        elif result.get("code") == "911021":
            # 文件已存在
            return True
        else:
            print(f"❌ 创建文件失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")
        return False


def upload_file(efile_url: str, token: str, local_path: str, remote_path: str, 
                cover: str = "cover") -> bool:
    """
    上传文件（普通上传，适合小文件）
    
    API: POST /efile/openapi/v2/file/upload
    """
    url = f"{efile_url}/openapi/v2/file/upload"
    headers = {"token": token}
    
    try:
        with open(local_path, 'rb') as f:
            files = {"file": (os.path.basename(local_path), f)}
            data = {"path": remote_path, "cover": cover}
            response = requests.post(url, headers=headers, data=data, files=files, timeout=300)
            result = response.json()
            if result.get("code") == "0":
                return True
            else:
                print(f"❌ 上传文件失败: {result.get('msg', '未知错误')}")
                return False
    except Exception as e:
        print(f"❌ 上传文件失败: {e}")
        return False


def upload_file_chunked(efile_url: str, token: str, local_path: str, remote_path: str,
                        chunk_size: int = 5 * 1024 * 1024, cover: str = "cover") -> bool:
    """
    分片上传文件（适合大文件）
    
    API: POST /efile/openapi/v2/file/burst (分片上传)
         POST /efile/openapi/v2/file/merge (合并分片)
    """
    url_burst = f"{efile_url}/openapi/v2/file/burst"
    url_merge = f"{efile_url}/openapi/v2/file/merge"
    headers = {"token": token}
    
    file_size = os.path.getsize(local_path)
    filename = os.path.basename(local_path)
    total_chunks = (file_size + chunk_size - 1) // chunk_size
    identifier = f"{file_size}-{filename.replace('.', '')}"
    
    try:
        # 分片上传
        with open(local_path, 'rb') as f:
            for chunk_number in range(1, total_chunks + 1):
                chunk_data = f.read(chunk_size)
                current_chunk_size = len(chunk_data)
                
                files = {"file": (filename, chunk_data)}
                data = {
                    "chunkNumber": str(chunk_number),
                    "cover": cover,
                    "filename": filename,
                    "path": remote_path,
                    "relativePath": filename,
                    "totalChunks": str(total_chunks),
                    "totalSize": str(file_size),
                    "chunkSize": str(chunk_size),
                    "currentChunkSize": str(current_chunk_size),
                    "identifier": identifier
                }
                
                response = requests.post(url_burst, headers=headers, data=data, files=files, timeout=60)
                result = response.json()
                if result.get("code") != "0":
                    print(f"❌ 分片 {chunk_number}/{total_chunks} 上传失败: {result.get('msg', '未知错误')}")
                    return False
                
                print(f"  分片 {chunk_number}/{total_chunks} 上传完成")
        
        # 合并分片
        merge_data = {
            "cover": cover,
            "filename": filename,
            "path": remote_path,
            "relativePath": filename,
            "identifier": identifier
        }
        response = requests.post(url_merge, headers=headers, data=merge_data, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 合并分片失败: {result.get('msg', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 分片上传失败: {e}")
        return False


def download_file(efile_url: str, token: str, remote_path: str, local_path: str) -> bool:
    """
    下载文件
    
    API: GET /efile/openapi/v2/file/download
    """
    url = f"{efile_url}/openapi/v2/file/download"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": remote_path}
    
    try:
        response = requests.get(url, headers=headers, params=params, stream=True, timeout=300)
        if response.status_code == 200:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            print(f"❌ 下载文件失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载文件失败: {e}")
        return False


def delete_file(efile_url: str, token: str, path: str, recursive: bool = False) -> bool:
    """
    删除文件/文件夹
    
    API: POST /efile/openapi/v2/file/remove
    """
    url = f"{efile_url}/openapi/v2/file/remove"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"paths": path, "recursive": str(recursive).lower()}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 删除失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False


def rename_file(efile_url: str, token: str, file_path: str, new_name: str) -> bool:
    """
    重命名文件
    
    API: POST /efile/openapi/v2/file/rename
    """
    url = f"{efile_url}/openapi/v2/file/rename"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"fileAbsolutePath": file_path, "newName": new_name}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 重命名失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 重命名失败: {e}")
        return False


def copy_file(efile_url: str, token: str, source_paths: List[str], target_path: str, cover: str = "cover") -> bool:
    """
    复制文件
    
    API: POST /efile/openapi/v2/file/copy
    """
    url = f"{efile_url}/openapi/v2/file/copy"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "sourcePaths": ",".join(source_paths),
        "targetPath": target_path,
        "cover": cover
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 复制失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False


def move_file(efile_url: str, token: str, source_paths: List[str], target_path: str, cover: str = "cover") -> bool:
    """
    移动文件
    
    API: POST /efile/openapi/v2/file/move
    """
    url = f"{efile_url}/openapi/v2/file/move"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "sourcePaths": ",".join(source_paths),
        "targetPath": target_path,
        "cover": cover
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 移动失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 移动失败: {e}")
        return False


def check_permission(efile_url: str, token: str, path: str, action: str = "READ") -> bool:
    """
    检查文件权限
    
    API: POST /efile/openapi/v2/file/permission
    action: READ, WRITE, EXECUTE
    """
    url = f"{efile_url}/openapi/v2/file/permission"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"path": path, "permissionAction": action}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return result.get("data", {}).get("allowed", False)
        return False
    except Exception as e:
        print(f"❌ 检查权限失败: {e}")
        return False


# ============== 高级封装方法 ==============

class SCNetFileManager:
    """SCNet文件管理器类"""
    
    def __init__(self, access_key: str, secret_key: str, user: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.user = user
        self.tokens_cache = {}
        self.center_info_cache = {}
        self.efile_url_cache = {}
        self.home_path_cache = {}
    
    def get_cluster_token(self, cluster_name: str) -> Optional[str]:
        """获取指定计算中心的token"""
        if cluster_name in self.tokens_cache:
            return self.tokens_cache[cluster_name]
        
        tokens_data = get_tokens(self.access_key, self.secret_key, self.user)
        if not tokens_data or tokens_data.get("code") != "0":
            return None
        
        for token_info in tokens_data.get("data", []):
            name = token_info.get("clusterName", "")
            token = token_info.get("token", "")
            self.tokens_cache[name] = token
        
        return self.tokens_cache.get(cluster_name)
    
    def get_cluster_efile_url(self, cluster_name: str) -> Optional[str]:
        """获取指定计算中心的efileUrl"""
        if cluster_name in self.efile_url_cache:
            return self.efile_url_cache[cluster_name]
        
        token = self.get_cluster_token(cluster_name)
        if not token:
            return None
        
        center_info = get_center_info(token)
        if not center_info:
            return None
        
        efile_url = get_efile_url(center_info)
        home_path = get_home_path(center_info)
        
        if efile_url:
            self.efile_url_cache[cluster_name] = efile_url
        if home_path:
            self.home_path_cache[cluster_name] = home_path
        self.center_info_cache[cluster_name] = center_info
        
        return efile_url
    
    def get_cluster_home_path(self, cluster_name: str) -> Optional[str]:
        """获取指定计算中心的家目录"""
        if cluster_name in self.home_path_cache:
            return self.home_path_cache[cluster_name]
        
        # 触发缓存
        self.get_cluster_efile_url(cluster_name)
        return self.home_path_cache.get(cluster_name)
    
    def _get_efile_url_and_token(self, cluster_name: str) -> Tuple[Optional[str], Optional[str]]:
        """获取efileUrl和token"""
        efile_url = self.get_cluster_efile_url(cluster_name)
        token = self.get_cluster_token(cluster_name)
        return efile_url, token
    
    # ============== 便捷操作方法 ==============
    
    def list_dir(self, cluster_name: str, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """列出目录内容"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return None
        return list_files(efile_url, token, path)
    
    def mkdir(self, cluster_name: str, path: str, create_parents: bool = True) -> bool:
        """创建目录"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        return create_folder(efile_url, token, path, create_parents)
    
    def touch(self, cluster_name: str, file_path: str) -> bool:
        """创建空文件"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        return create_file(efile_url, token, file_path)
    
    def upload(self, cluster_name: str, local_path: str, remote_path: str, use_chunk: bool = False) -> bool:
        """上传文件"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        
        if use_chunk:
            return upload_file_chunked(efile_url, token, local_path, remote_path)
        else:
            return upload_file(efile_url, token, local_path, remote_path)
    
    def download(self, cluster_name: str, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        return download_file(efile_url, token, remote_path, local_path)
    
    def remove(self, cluster_name: str, path: str, recursive: bool = False) -> bool:
        """删除文件/目录"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        return delete_file(efile_url, token, path, recursive)
    
    def exists(self, cluster_name: str, path: str) -> bool:
        """检查文件是否存在"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            print(f"❌ 无法获取 {cluster_name} 的文件服务地址或token")
            return False
        return check_file_exists(efile_url, token, path)


# ============== 测试用例 ==============

def test_scenario_1():
    """
    测试用例1：完整文件操作流程
    
    1. 在昆山计算中心的家目录下创建文件夹 /claw_workspace/POSCAR
    2. 上传 /Users/apple/.openclaw/workspace/jobs 文件夹下的全部文件到 /claw_workspace/POSCAR/
    3. 在同级目录下创建 helloWord.txt
    4. 显示这个目录下的文件列表
    5. 将文件全部下载到本地路径 /Users/apple/.openclaw/workspace/jobs/download/
    """
    print("="*70)
    print("🧪 测试用例1: 完整文件操作流程")
    print("="*70)
    
    # 配置
    access_key = "72158c9f945243a7beab294a7a9bb0a6"
    secret_key = "4c05f5ce15d047cda84593844ac89793"
    user = "yiziqinx"
    cluster_name = "华东一区【昆山】"
    local_jobs_dir = "/Users/apple/.openclaw/workspace/jobs"
    local_download_dir = "/Users/apple/.openclaw/workspace/jobs/download"
    
    # 初始化文件管理器
    fm = SCNetFileManager(access_key, secret_key, user)
    
    # 获取家目录
    home_path = fm.get_cluster_home_path(cluster_name)
    if not home_path:
        print(f"❌ 无法获取 {cluster_name} 的家目录")
        return False
    print(f"🏠 家目录: {home_path}")
    
    # 步骤1: 创建文件夹 /claw_workspace/POSCAR
    remote_dir = f"{home_path}/claw_workspace/POSCAR"
    print(f"\n📁 步骤1: 创建远程目录 {remote_dir}")
    if fm.mkdir(cluster_name, remote_dir, create_parents=True):
        print(f"  ✅ 目录创建成功")
    else:
        print(f"  ❌ 目录创建失败")
        return False
    
    # 步骤2: 上传本地jobs文件夹下的所有文件
    print(f"\n📤 步骤2: 上传本地文件到远程目录")
    local_files = []
    if os.path.exists(local_jobs_dir):
        for item in os.listdir(local_jobs_dir):
            item_path = os.path.join(local_jobs_dir, item)
            if os.path.isfile(item_path):
                local_files.append(item_path)
                print(f"  📄 准备上传: {item}")
    
    if not local_files:
        # 创建测试文件
        test_file = os.path.join(local_jobs_dir, "test_upload.txt")
        with open(test_file, 'w') as f:
            f.write("This is a test file for SCNet upload.\n")
        local_files.append(test_file)
        print(f"  📝 创建测试文件: test_upload.txt")
    
    uploaded_files = []
    for local_file in local_files:
        filename = os.path.basename(local_file)
        print(f"  📤 正在上传: {filename}...")
        if fm.upload(cluster_name, local_file, remote_dir):
            print(f"    ✅ 上传成功")
            uploaded_files.append(filename)
        else:
            print(f"    ❌ 上传失败")
    
    # 步骤3: 在同级目录下创建 helloWord.txt
    parent_dir = os.path.dirname(remote_dir)
    hello_file = f"{parent_dir}/helloWord.txt"
    print(f"\n📄 步骤3: 创建文件 {hello_file}")
    if fm.touch(cluster_name, hello_file):
        print(f"  ✅ 文件创建成功")
    else:
        print(f"  ❌ 文件创建失败")
    
    # 步骤4: 显示目录文件列表
    print(f"\n📋 步骤4: 显示目录 {remote_dir} 的文件列表")
    result = fm.list_dir(cluster_name, remote_dir)
    if result and result.get("code") == "0":
        data = result.get("data", {})
        file_list = data.get("fileList", [])
        print(f"  📁 目录内容 (共 {len(file_list)} 项):")
        for item in file_list:
            item_type = "📁" if item.get("isDirectory") else "📄"
            item_name = item.get("name", "未知")
            item_size = item.get("size", 0)
            print(f"    {item_type} {item_name} ({item_size} bytes)")
    else:
        print(f"  ⚠️ 无法获取文件列表")
    
    # 显示父目录列表
    print(f"\n  📋 父目录 {parent_dir} 内容:")
    result = fm.list_dir(cluster_name, parent_dir)
    if result and result.get("code") == "0":
        data = result.get("data", {})
        file_list = data.get("fileList", [])
        for item in file_list:
            item_type = "📁" if item.get("isDirectory") else "📄"
            item_name = item.get("name", "未知")
            print(f"    {item_type} {item_name}")
    
    # 步骤5: 下载文件到本地
    print(f"\n📥 步骤5: 下载远程文件到本地 {local_download_dir}")
    os.makedirs(local_download_dir, exist_ok=True)
    
    # 获取远程目录文件列表并下载
    result = fm.list_dir(cluster_name, remote_dir)
    if result and result.get("code") == "0":
        data = result.get("data", {})
        file_list = data.get("fileList", [])
        
        for item in file_list:
            if not item.get("isDirectory"):
                remote_file_path = item.get("path")
                filename = item.get("name")
                local_file_path = os.path.join(local_download_dir, filename)
                
                print(f"  📥 正在下载: {filename}...")
                if fm.download(cluster_name, remote_file_path, local_file_path):
                    print(f"    ✅ 下载成功 -> {local_file_path}")
                else:
                    print(f"    ❌ 下载失败")
    
    print("\n" + "="*70)
    print("✅ 测试用例1完成")
    print("="*70)
    return True


if __name__ == "__main__":
    test_scenario_1()
