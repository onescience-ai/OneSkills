#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet Container Manager - 容器实例管理模块

功能：
1. 创建容器实例
2. 启动/停止/删除容器实例
3. 批量执行脚本
4. 查询容器实例列表/详情
5. 获取容器实例URL
6. 更新资源规格
7. 查询节点资源限额
8. 查询资源分组
9. 检查授权的挂载路径
10. 获取镜像列表

容器接口使用 aiUrl 作为服务器地址
"""

import requests
import json
from typing import Optional, Dict, Any, List


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
    
    # ============== 容器生命周期管理 ==============
    
    def create_container(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建容器实例
        
        API: POST /ai/openapi/v2/instance-service/task
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task")
        
        try:
            response = requests.post(url, headers=self.headers, json=config, timeout=60)
            return response.json()
        except Exception as e:
            print(f"❌ 创建容器失败: {e}")
            return None
    
    def start_container(self, instance_service_id: str) -> Optional[Dict[str, Any]]:
        """
        启动容器实例
        
        API: POST /ai/openapi/v2/instance-service/task/actions/restart
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/restart")
        params = {"instanceServiceId": instance_service_id}
        
        try:
            response = requests.post(url, headers=self.headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 启动容器失败: {e}")
            return None
    
    def stop_containers(self, ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        批量停止容器实例
        
        API: POST /ai/openapi/v2/instance-service/task/actions/stop
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/stop")
        params = [("ids", id) for id in ids]
        
        try:
            response = requests.post(url, headers=self.headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 停止容器失败: {e}")
            return None
    
    def delete_containers(self, ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        批量删除容器实例
        
        API: DELETE /ai/openapi/v2/instance-service/task
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task")
        params = [("ids", id) for id in ids]
        
        try:
            response = requests.delete(url, headers=self.headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 删除容器失败: {e}")
            return None
    
    def execute_script(self, instance_id: str, script_content: str, 
                       scope: str = "all") -> Optional[Dict[str, Any]]:
        """
        批量执行脚本
        
        API: POST /ai/openapi/v2/instance-service/task/actions/execute-script
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task/actions/execute-script")
        payload = {
            "id": instance_id,
            "startScriptContent": script_content,
            "startScriptActionScope": scope
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 执行脚本失败: {e}")
            return None
    
    # ============== 查询接口 ==============
    
    def list_containers(self, status: str = None, task_type: str = None,
                        instance_name: str = None, start: int = 0, 
                        limit: int = 20, sort: str = "desc") -> Optional[Dict[str, Any]]:
        """
        查询容器实例列表
        
        API: GET /ai/openapi/v2/instance-service/task
        """
        url = self._get_url("/ai/openapi/v2/instance-service/task")
        
        # 这个接口需要使用GET with body
        payload = {
            "start": start,
            "limit": limit,
            "sort": sort
        }
        if status:
            payload["status"] = status
        if task_type:
            payload["taskType"] = task_type
        if instance_name:
            payload["instanceServiceName"] = instance_name
        
        try:
            response = requests.get(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询容器列表失败: {e}")
            return None
    
    def get_container_detail(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        查询容器实例详情
        
        API: GET /ai/openapi/v2/instance-service/{id}/detail
        """
        url = self._get_url(f"/ai/openapi/v2/instance-service/{instance_id}/detail")
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询容器详情失败: {e}")
            return None
    
    def get_container_url(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        获取容器实例URL
        
        API: GET /ai/openapi/v2/instance-service/{id}/url
        """
        url = self._get_url(f"/ai/openapi/v2/instance-service/{instance_id}/url")
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 获取容器URL失败: {e}")
            return None
    
    # ============== 资源管理 ==============
    
    def update_resource_spec(self, instance_id: str, cpu_number: int, 
                             gpu_number: int, ram_size: int) -> Optional[Dict[str, Any]]:
        """
        更新资源规格
        
        API: POST /ai/openapi/v2/instance-service/resource-spec/actions/update
        """
        url = self._get_url("/ai/openapi/v2/instance-service/resource-spec/actions/update")
        payload = {
            "id": instance_id,
            "cpuNumber": cpu_number,
            "gpuNumber": gpu_number,
            "ramSize": ram_size
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 更新资源规格失败: {e}")
            return None
    
    def get_resource_limits(self, accelerator_type: str, resource_group: str) -> Optional[Dict[str, Any]]:
        """
        查询节点资源限额
        
        API: GET /ai/openapi/v2/instance-service/resources
        """
        url = self._get_url("/ai/openapi/v2/instance-service/resources")
        params = {
            "acceleratorType": accelerator_type,
            "resourceGroup": resource_group
        }
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询资源限额失败: {e}")
            return None
    
    def get_resource_groups(self) -> Optional[Dict[str, Any]]:
        """
        查询资源分组
        
        API: GET /ai/openapi/v2/instance-service/resource-group
        """
        url = self._get_url("/ai/openapi/v2/instance-service/resource-group")
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询资源分组失败: {e}")
            return None
    
    def get_allowed_mount_dirs(self) -> Optional[Dict[str, Any]]:
        """
        检查授权的挂载路径
        
        API: GET /ai/openapi/v2/instance-service/allowed-mount-dir
        """
        url = self._get_url("/ai/openapi/v2/instance-service/allowed-mount-dir")
        headers = {"token": self.token}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ 查询挂载路径失败: {e}")
            return None
    
    def get_images(self, name: str = None, image_type: str = None, 
                   accelerator_type: str = None, access: str = "public",
                   page: int = 1, size: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取镜像列表
        
        API: POST /ai/openapi/v2/image/images
        """
        url = self._get_url("/ai/openapi/v2/image/images")
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


# ============== 容器状态映射 ==============

CONTAINER_STATUS_MAP = {
    "Running": "运行中",
    "Deploying": "部署中",
    "Waiting": "等待中",
    "Terminated": "已终止",
    "Failed": "失败",
    "Completed": "已完成"
}


def format_container_status(status: str) -> str:
    """格式化容器状态"""
    return CONTAINER_STATUS_MAP.get(status, status)


# ============== 容器创建向导 ==============

class ContainerCreateWizard:
    """容器创建向导"""
    
    def __init__(self, manager: ContainerManager):
        self.manager = manager
        self.config = {}
    
    def preview_config(self) -> str:
        """预览配置"""
        lines = [
            "📋 容器配置预览:",
            "-" * 40,
            f"实例名称: {self.config.get('instanceServiceName', '未设置')}",
            f"任务类型: {self.config.get('taskType', '未设置')}",
            f"加速器类型: {self.config.get('acceleratorType', '未设置')}",
            f"镜像: {self.config.get('version', '未设置')}",
            f"CPU: {self.config.get('cpuNumber', '未设置')} 核",
            f"GPU: {self.config.get('gpuNumber', '未设置')} 个",
            f"内存: {self.config.get('ramSize', '未设置')} MB",
            f"资源分组: {self.config.get('resourceGroup', '未设置')}",
            f"实例数量: {self.config.get('taskNumber', 1)}",
            f"超时时间: {self.config.get('timeoutLimit', 'unlimited')}",
            "-" * 40,
        ]
        return "\n".join(lines)
    
    def create(self) -> Optional[str]:
        """创建容器"""
        result = self.manager.create_container(self.config)
        
        if result and result.get("code") == "0":
            return result.get("data")  # 返回任务ID
        return None


if __name__ == "__main__":
    print("Container Manager Module")
    print("请使用 SCNetClient 来初始化 ContainerManager")
