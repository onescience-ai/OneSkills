#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Notebook Manager - Notebook实例管理模块

功能：
1. 创建Notebook实例
2. Notebook实例开机/关机/释放
3. 查询Notebook资源
4. 查询镜像列表/模型镜像列表
5. 修改Notebook实例名称
6. 查询Notebook实例详情/列表
7. 查询Jupyter服务地址/自定义服务地址
8. 启动Notebook实例自定义服务

所有Notebook接口使用 https://www.scnet.cn 作为基础URL
"""

import requests
import json
from typing import Optional, Dict, Any, List

# Notebook API 基础URL
NOTEBOOK_BASE_URL = "https://www.scnet.cn"


class NotebookManager:
    """Notebook管理器"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "token": token,
            "Content-Type": "application/json"
        }
    
    # ============== 实例管理 ==============
    
    def create_notebook(self, cluster_id: str, image_config: Dict[str, Any], 
                        accelerator_type: str = "DCU", accelerator_number: str = "1",
                        resource_group_code: str = None, mount_home: bool = True,
                        start_command: str = None, mount_info: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        创建Notebook实例
        
        API: POST /ac/openapi/v2/notebook/actions/create
        """
        url = f"{NOTEBOOK_BASE_URL}/ac/openapi/v2/notebook/actions/create"
        
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
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            return response.json()
        except Exception as e:
            print(f"❌ 创建Notebook失败: {e}")
            return None
    
    def start_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """
        Notebook实例开机
        
        API: POST /ac/openapi/v2/notebook/actions/start
        """
        url = f"{NOTEBOOK_BASE_URL}/ac/openapi/v2/notebook/actions/start"
        payload = {"notebookId": notebook_id}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 开机失败: {e}")
            return None
    
    def stop_notebook(self, notebook_id: str, save_env: bool = False) -> Optional[Dict[str, Any]]:
        """
        Notebook实例关机
        
        API: POST /ai/openapi/v2/notebook/actions/stop
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/actions/stop"
        payload = {
            "notebookId": notebook_id,
            "saveEnv": save_env
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 关机失败: {e}")
            return None
    
    def release_notebook(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """
        Notebook实例释放
        
        API: POST /ai/openapi/v2/notebook/actions/release
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/actions/release"
        payload = {"id": notebook_id}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 释放失败: {e}")
            return None
    
    def rename_notebook(self, notebook_id: str, new_name: str) -> Optional[Dict[str, Any]]:
        """
        修改Notebook实例名称
        
        API: POST /ai/openapi/v2/notebook/name
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/name"
        payload = {
            "id": notebook_id,
            "notebookName": new_name
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 重命名失败: {e}")
            return None
    
    # ============== 查询接口 ==============
    
    def list_notebooks(self, notebook_name: str = None, notebook_status: str = None,
                       page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """
        查询Notebook实例列表
        
        API: GET /ai/openapi/v2/notebook/list
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/list"
        params = {
            "page": page,
            "size": size
        }
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
        """
        查询Notebook实例详情
        
        API: GET /ai/openapi/v2/notebook/detail
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/detail"
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询详情失败: {e}")
            return None
    
    def get_notebook_url(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Jupyter服务地址
        
        API: GET /ai/openapi/v2/notebook/url
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/url"
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询URL失败: {e}")
            return None
    
    # ============== 资源与镜像 ==============
    
    def get_resources(self, cluster_ids: List[str], resource_id: str = None) -> Optional[Dict[str, Any]]:
        """
        查询Notebook资源
        
        API: GET /ac/openapi/v2/resources/accelerators
        """
        url = f"{NOTEBOOK_BASE_URL}/ac/openapi/v2/resources/accelerators"
        params = {
            "clusterIds": ",".join(cluster_ids)
        }
        if resource_id:
            params["resourceId"] = resource_id
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询资源失败: {e}")
            return None
    
    def get_images(self, name: str = None, image_type: str = None, 
                   accelerator_type: str = None, access: str = "public",
                   page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """
        查询镜像列表
        
        API: POST /ai/openapi/v2/image/images
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/image/images"
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
        """
        查询模型镜像列表
        
        API: POST /ai/openapi/v2/image/models
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/image/models"
        payload = {
            "page": page,
            "size": size
        }
        if accelerator_type:
            payload["acceleratorType"] = accelerator_type
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询模型镜像失败: {e}")
            return None
    
    # ============== 自定义服务 ==============
    
    def start_custom_service(self, notebook_id: str, port: str, 
                             command: str = None) -> Optional[Dict[str, Any]]:
        """
        启动Notebook实例自定义服务
        
        API: POST /ai/openapi/v2/notebook/customize-service/actions/start
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/customize-service/actions/start"
        payload = {
            "id": notebook_id,
            "customizePort": port
        }
        if command:
            payload["command"] = command
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 启动自定义服务失败: {e}")
            return None
    
    def get_custom_service_url(self, notebook_id: str) -> Optional[Dict[str, Any]]:
        """
        查询Notebook实例自定义服务地址
        
        API: GET /ai/openapi/v2/notebook/customize-service/url
        """
        url = f"{NOTEBOOK_BASE_URL}/ai/openapi/v2/notebook/customize-service/url"
        params = {"notebookId": notebook_id}
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询自定义服务URL失败: {e}")
            return None


# ============== Notebook状态映射 ==============

NOTEBOOK_STATUS_MAP = {
    "Creating": "创建中",
    "Restarting": "开机中",
    "Running": "运行中",
    "Terminated": "已关机",
    "Failed": "失败",
    "Shutting": "关机中"
}


def format_notebook_status(status: str) -> str:
    """格式化Notebook状态"""
    return NOTEBOOK_STATUS_MAP.get(status, status)


# ============== Notebook创建向导 ==============

class NotebookCreateWizard:
    """Notebook创建向导"""
    
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
            f"资源分组: {self.config.get('resource_group_code', '自动分配')}",
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


if __name__ == "__main__":
    # 测试代码
    print("Notebook Manager Module")
    print("请使用 SCNetClient 来初始化 NotebookManager")
