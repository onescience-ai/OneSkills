#!/usr/bin/env python3
"""
SCNet Skill - 统一入口
支持自然语言交互管理 SCNet 超算平台

使用方法:
    python scripts/scnet.py "用户对话内容"
    
示例:
    python scripts/scnet.py "查询作业"
    python scripts/scnet.py "提交作业 --cmd 'sleep 100' --queue debug"
    python scripts/scnet.py "删除作业 123"
    python scripts/scnet.py "查看文件列表 /public/home/user"
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Windows 终端兼容处理（避免 GBK 编码下 UnicodeEncodeError 崩溃）
if sys.platform == "win32":
    # 启用 ANSI 颜色支持（Windows 10+）- 使用 ctypes 替代 os.system("")
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass
    
    # 强制 stdout/stderr 使用 utf-8，无法编码的字符用替换符代替
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# 添加当前目录（scripts）到路径，以便导入其他模块
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# 导入配置
from config import AppTimeout, CACHE_PATH, CONFIG_PATH, get_cache_path

# 导入底层模块
from cache import switch_default_cluster, CacheManager, ConfigManager, Logger, CacheInitializer


class Colors:
    """终端颜色代码"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class IntentRecognizer:
    """意图识别器 - 支持自然语言理解"""
    
    # 中文数字映射
    CHINESE_NUMBERS = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
        '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        '两': 2,  # 支持"两页"
    }
    
    # 作业状态映射 - 支持中文状态到代码的转换（与 job.py 的 JOB_STATUS_MAP 对应）
    # 格式: 中文关键词 -> AC API状态代码
    JOB_STATUS_MAP = {
        'statR': ['运行', 'running', '执行中', '运行中'],
        'statQ': ['排队', 'queue', 'queued', '等待', '队列中'],
        'statH': ['保留', 'hold', '挂起保留'],
        'statS': ['挂起', 'suspend', '暂停', 'suspended'],
        'statE': ['退出', 'exit', 'exited', '已退出'],
        'statC': ['完成', 'completed', 'complete', '已完成', '成功'],
        'statW': ['等待', 'wait', 'waiting'],
        'statX': ['其他', 'other'],
        'statDE': ['取消', 'cancelled', '已取消', 'deleted'],
        'statD': ['失败', 'failed', '故障', 'error'],
        'statT': ['超时', 'timeout', 'timedout', '已超时'],
        'statN': ['节点异常', 'nodefail', '节点失败'],
        'statRQ': ['重新运行', 'rerun', '重跑', '再次运行'],
    }
    
    def _load_clusters(self) -> Dict[str, str]:
        """从用户缓存动态加载区域映射"""
        import json
        import re as _re
        clusters = {}
        try:
            cache_path = get_cache_path()
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                for cluster in cache.get('clusters', []):
                    name = cluster.get('clusterName')
                    if not name or len(name) < 2:
                        continue
                    # 跳过纯 ASCII 名称（如 "ac"），避免在路径中被误匹配
                    if _re.fullmatch(r'[A-Za-z0-9_\-]+', name):
                        continue
                    clusters[name] = name
                    # 提取别名，如 "华东一区【昆山】" → "华东一区", "昆山"
                    if '【' in name and '】' in name:
                        prefix = name.split('【')[0]
                        inner = name[name.find('【') + 1:name.find('】')]
                        if prefix and len(prefix) >= 2:
                            clusters[prefix] = name
                        if inner and len(inner) >= 2:
                            clusters[inner] = name
        except Exception:
            pass
        return clusters
    
    def recognize(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        识别用户意图并提取参数
        
        Returns:
            (intent, params) - intent 为意图类型，params 为提取的参数
        """
        text_lower = text.strip().lower()
        params = {"raw": text}
        
        # ========== 缓存管理 ==========
        if any(k in text_lower for k in ["刷新缓存", "初始化缓存", "更新缓存", "reload cache", "刷新全部缓存", "刷新所有缓存"]):
            return "cache_refresh", params
            
        # ========== 文件管理（提前检查，避免路径被误判为区域名）==========
        # 文件列表
        if any(k in text_lower for k in ["文件列表", "查看文件", "list files", "ls ", "目录内容"]):
            params["path"] = self._extract_path(text)
            return "file_list", params
            
        # 上传文件
        if any(k in text_lower for k in ["上传文件", "upload file", "上传"]):
            local_path, remote_path = self._extract_upload_paths(text)
            params["local_path"] = local_path
            params["remote_path"] = remote_path
            return "file_upload", params
            
        # 下载文件
        if any(k in text_lower for k in ["下载文件", "download file", "下载"]):
            remote_path, local_path = self._extract_download_paths(text)
            params["remote_path"] = remote_path
            params["local_path"] = local_path
            return "file_download", params
            
        # 创建目录
        if any(k in text_lower for k in ["创建目录", "新建目录", "mkdir", "make dir"]):
            params["path"] = self._extract_path(text)
            return "file_mkdir", params
            
        # 创建文件
        if any(k in text_lower for k in ["创建文件", "新建文件", "touch file", "新建空文件"]):
            params["path"] = self._extract_path(text)
            return "file_touch", params
            
        # 复制文件（放在删除之前检查）
        if any(k in text_lower for k in ["复制文件", "拷贝文件", "copy file", "cp "]):
            src, dst = self._extract_copy_params(text)
            params["src"] = src
            params["dst"] = dst
            return "file_copy", params
            
        # 删除文件
        if any(k in text_lower for k in ["删除文件", "删除目录", "remove file", "delete file"]) or \
           text_lower.startswith("rm ") or " rm " in text_lower:
            params["path"] = self._extract_path(text)
            return "file_delete", params
            
        # 移动文件（放在重命名之前，避免"移动文件"被误判为重命名）
        if any(k in text_lower for k in ["移动文件", "剪切文件", "move file", "mv "]):
            src, dst = self._extract_move_params(text)
            params["src"] = src
            params["dst"] = dst
            return "file_move", params
            
        # 重命名文件
        if any(k in text_lower for k in ["重命名", "改名", "rename"]):
            old_path, new_name = self._extract_rename_params(text)
            params["old_path"] = old_path
            params["new_name"] = new_name
            return "file_rename", params
            
        # 检查文件存在
        if any(k in text_lower for k in ["检查文件", "文件存在", "exists", "file exists"]):
            params["path"] = self._extract_path(text)
            return "file_exists", params
        
        # ========== 区域切换 ==========
        # 检查是否包含提交作业关键词（如"在山东提交作业"应优先处理提交）
        is_job_submit = any(k in text_lower for k in ["提交作业", "提交任务", "submit job", "run job", "运行作业"])
        
        if not is_job_submit:
            for key, name in self._load_clusters().items():
                if key in text_lower:
                    params["cluster_name"] = name
                    return "switch_cluster", params
        
        # ========== 用户信息查询 ==========
        # 注意：排除包含"作业"的情况（如"查询用户 xxx 的作业"应该匹配作业查询）
        if any(k in text_lower for k in ["用户信息", "我的信息", "账户信息", "余额", "我是谁", "user info"]) or \
           ("查询用户" in text_lower and "作业" not in text_lower):
            return "user_info", params
        
        # 查询作业统计信息
        if any(k in text_lower for k in ["作业统计", "统计信息", "作业状态统计", "job stats", "job statistics"]):
            return "job_stats", params
        
        # 查询机时
        if any(k in text_lower for k in ["机时", "剩余机时", "已用机时", "walltime", "机时信息"]):
            return "walltime", params
            
        # ========== 作业管理 ==========
        # 提交作业帮助（必须在提交作业之前检查）
        if any(k in text_lower for k in ["如何提交作业", "提交作业帮助", "作业提交帮助", "作业有哪些参数", "job submit help", "how to submit job", "我要提交作业"]):
            return "job_submit_help", params
            
        # 提交作业（支持 "在[中心]提交作业" 格式）
        if is_job_submit:
            params.update(self._extract_job_params(text))
            # 检查是否指定了区域（先去除路径文本，避免路径中子串误匹配）
            text_no_paths = re.sub(r'/[\w/.-]+', ' ', text_lower)
            text_no_paths = re.sub(r'[A-Z]:\\[\w\\. -]+', ' ', text_no_paths, flags=re.IGNORECASE)
            for key, name in self._load_clusters().items():
                if key in text_no_paths:
                    params["cluster_name"] = name
                    break
            return "job_submit", params
            
        # 删除作业
        if any(k in text_lower for k in ["删除作业", "取消作业", "终止作业", "杀掉作业", "delete job", "kill job"]):
            params["job_id"] = self._extract_job_id(text)
            return "job_delete", params
            
        # 查询队列
        if any(k in text_lower for k in ["查询队列", "可用队列", "队列列表", "queues", "queue list"]):
            return "job_queues", params
            
        # 集群信息
        if any(k in text_lower for k in ["集群信息", "调度器信息", "cluster info", "scheduler info"]):
            return "cluster_info", params
            
        # 历史作业查询（必须在作业详情之前，避免"历史作业详情"被误判为实时详情）
        if any(k in text_lower for k in ["历史作业", "历史任务", "history jobs", "completed jobs"]):
            params.update(self._extract_job_filter_params(text))
            params["job_id"] = self._extract_job_id(text)
            return "job_history", params

        # 作业详情
        if any(k in text_lower for k in ["作业详情", "查看作业", "job detail"]):
            params["job_id"] = self._extract_job_id(text)
            if params["job_id"]:
                return "job_detail", params

        # 明确的实时作业查询（用户明确提到"实时"、"运行中"等词）
        if any(k in text_lower for k in ["实时作业", "实时任务", "运行作业", "运行中", "running job", "running jobs", "active job", "active jobs", "当前作业"]):
            params.update(self._extract_job_filter_params(text))
            return "job_list", params

        # 通用作业查询（未明确指定历史或实时，同时查询两者）
        # 使用更严格的匹配：必须是完整的词，且不是文件路径的一部分
        job_keywords = ["作业", "任务", "jobs"]
        if any(k in text_lower for k in job_keywords) or \
           (" job " in text_lower or text_lower.startswith("job ") or text_lower.endswith(" job")):
            params.update(self._extract_job_filter_params(text))
            return "job_query", params
            
        # ========== 帮助 ==========
        if any(k in text_lower for k in ["帮助", "help", "怎么用", "使用说明"]):
            return "help", params
            
        return "unknown", params
    
    def _extract_job_id(self, text: str) -> Optional[str]:
        """从文本中提取作业ID"""
        # 先排除日期时间格式的数字（避免误识别 2024-01-01 中的 2024）
        # 移除日期时间格式: 2024-01-01, 2024-01-01 00:00:00, 00:00:00 等
        import re
        text_cleaned = text
        
        # 移除完整日期时间格式
        text_cleaned = re.sub(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', '', text_cleaned)
        # 移除日期格式
        text_cleaned = re.sub(r'\d{4}-\d{2}-\d{2}', '', text_cleaned)
        # 移除时间格式
        text_cleaned = re.sub(r'\d{2}:\d{2}:\d{2}', '', text_cleaned)
        text_cleaned = re.sub(r'\d{2}:\d{2}', '', text_cleaned)
        
        # 匹配数字ID
        patterns = [
            r'作业[\s]*([0-9]+)',  # 作业 123
            r'job[\s]*([0-9]+)',   # job 123
            r'#([0-9]+)',          # #123
            r'(?<!\d)([0-9]{3,})(?!\d)',  # 至少3位数字，前后非数字（兼容中文后的数字）
        ]
        for pattern in patterns:
            match = re.search(pattern, text_cleaned.lower())
            if match:
                return match.group(1)
        return None
    
    def _extract_path(self, text: str) -> Optional[str]:
        """从文本中提取路径"""
        # 匹配 Linux 风格路径
        patterns = [
            r'(/[\w\-/\.]+)',           # /public/home/user
            r'路径[\s]*([\w\-/\.]+)',    # 路径 /xxx
            r'path[\s]*([\w\-/\.]+)',    # path /xxx
            r'到[\s]*(/[\w\-/\.]+)',     # 到 /xxx
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                path = match.group(1)
                # 确保路径以 / 开头
                if path.startswith('/'):
                    return path
        return None

    def _extract_quoted_paths(self, text: str) -> List[str]:
        """提取带引号的路径片段，保留原始大小写与空格。"""
        matches = re.findall(r'["\']([^"\']+)["\']', text)
        return [m.strip() for m in matches if m and m.strip()]

    def _looks_like_remote_path(self, path: str) -> bool:
        """判断是否为远程 Linux 路径。"""
        return bool(path) and path.startswith('/')

    def _looks_like_local_path(self, path: str) -> bool:
        """判断是否为本地路径或本地文件名。"""
        if not path:
            return False
        return bool(
            re.match(r'^[A-Za-z]:[\\/]', path) or
            path.startswith('./') or
            path.startswith('.\\') or
            path.startswith('~/') or
            path.startswith('~\\') or
            re.match(r'^[^/\\\s]+\.[A-Za-z0-9]+$', path)
        )

    def _clean_local_path(self, path: Optional[str]) -> Optional[str]:
        """清理本地路径文本，但不随意改写为 ./。"""
        if not path:
            return None
        path = path.strip().strip('"').strip("'")
        return path or None

    def _clean_remote_path(self, path: Optional[str]) -> Optional[str]:
        """清理远程路径文本。"""
        if not path:
            return None
        path = path.strip().strip('"').strip("'")
        return path or None

    def _extract_upload_paths(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取上传的本地路径和远程路径"""
        local_path = None
        remote_path = None

        # 优先处理带引号的双路径输入，避免自然语言误解析
        quoted_paths = self._extract_quoted_paths(text)
        if len(quoted_paths) >= 2:
            first, second = quoted_paths[0], quoted_paths[1]
            if self._looks_like_local_path(first) and self._looks_like_remote_path(second):
                return self._clean_local_path(first), self._clean_remote_path(second)

        # 处理明确的“上传 <本地> 到 <远程>”格式，保留本地路径原文
        match = re.search(r'上传(?:文件)?\s+(.+?)\s+到\s+([\'"]?/[^\'"\s]+[\'"]?)', text, re.IGNORECASE)
        if not match:
            match = re.search(r'upload\s+(.+?)\s+to\s+([\'"]?/[^\'"\s]+[\'"]?)', text, re.IGNORECASE)
        if match:
            local_path = self._clean_local_path(match.group(1))
            remote_path = self._clean_remote_path(match.group(2))
            return local_path, remote_path

        local_path = self._extract_local_path(text)

        # 提取远程路径（查找"到"后面的路径）
        remote_match = re.search(r'到[\s]+([\'"]?/[^\'"\s]+[\'"]?)', text)
        if remote_match:
            remote_path = self._clean_remote_path(remote_match.group(1))

        return local_path, remote_path
    
    def _extract_download_paths(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取下载的远程路径和本地路径"""
        remote_path = None
        local_path = None
        
        # 匹配 "下载 xxx 到 xxx" 或 "download xxx to xxx"
        # 第一个路径是远程路径（服务器端），第二个是本地路径
        text_lower = text.lower()
        
        # 尝试匹配完整格式（标准路径）
        patterns = [
            r'下载[\s]+(/[\w\-/.]+)[\s]+到[\s]+([A-Za-z]:[\w\-/.\\\\]+|/~[\w\-/.]+|/[\w\-/.]+)',
            r'download[\s]+(/[\w\-/.]+)[\s]+to[\s]+([A-Za-z]:[\w\-/.\\\\]+|/~[\w\-/.]+|/[\w\-/.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                remote_path = match.group(1)
                local_path = match.group(2)
                return remote_path, local_path
        
        # 匹配带中文描述的格式
        # 先提取远程路径
        remote_match = re.search(r'下载[\s]+(/[\w\-/.]+)', text_lower)
        if not remote_match:
            remote_match = re.search(r'download[\s]+(/[\w\-/.]+)', text_lower)
        if remote_match:
            remote_path = remote_match.group(1)
        
        # 提取本地路径（支持中文描述）
        # 查找 "到" 之后的内容
        if '到' in text:
            parts = text.split('到')
            if len(parts) >= 2:
                local_desc = parts[-1].strip()
                local_path = self._convert_local_desc_to_path(local_desc)
        elif ' to ' in text_lower:
            parts = text_lower.split(' to ')
            if len(parts) >= 2:
                local_desc = parts[-1].strip()
                local_path = self._convert_local_desc_to_path(local_desc)
        
        if remote_path and local_path:
            return remote_path, local_path
        
        # 备用：查找所有绝对路径
        all_paths = re.findall(r'(/[\w\-/.]+)', text)
        if len(all_paths) >= 2:
            remote_path = all_paths[0]
            local_path = all_paths[1]
            return remote_path, local_path
        
        # 单独提取
        if not remote_path:
            remote_path = self._extract_path(text)
        if not local_path:
            local_path = self._extract_local_path(text)
        return remote_path, local_path
    
    def _convert_local_desc_to_path(self, desc: str) -> Optional[str]:
        """将中文描述的本地位置转换为实际路径"""
        import os
        desc = desc.strip().lower()
        
        # 桌面相关
        if any(k in desc for k in ['桌面', 'desktop', '我的桌面']):
            return os.path.expanduser('~/Desktop')
        
        # 下载目录
        if any(k in desc for k in ['下载', 'downloads', 'download']):
            return os.path.expanduser('~/Downloads')
        
        # 文档目录
        if any(k in desc for k in ['文档', 'documents', 'document', '我的文档']):
            return os.path.expanduser('~/Documents')
        
        # 当前目录
        if any(k in desc for k in ['当前目录', '当前文件夹', '这里', '.', 'current']):
            return './'
        
        # 家目录
        if any(k in desc for k in ['家目录', 'home', '用户目录', '主目录']):
            return os.path.expanduser('~/')
        
        # 如果是标准路径格式，直接返回
        if desc.startswith('/') or desc.startswith('~/') or desc.startswith('./'):
            return os.path.expanduser(desc)
        
        # 默认返回当前目录
        return './'
    
    def _extract_local_path(self, text: str) -> Optional[str]:
        """提取本地路径"""
        quoted_paths = self._extract_quoted_paths(text)
        for path in quoted_paths:
            if self._looks_like_local_path(path):
                return self._clean_local_path(path)

        # 匹配 ./ 或 ~/ 或 / 开头的完整路径，或文件名
        patterns = [
            r'([A-Za-z]:[/\\][^"\r\n]+)',     # Windows 路径，允许空格和中文
            r'(~/[\w\-/.]+)',                # ~/xxx
            r'(\./[\w\-/.]*)',               # ./xxx 或 ./
            r'([\w\-]+\.[\w]+)',             # 文件名如 file.txt
            r'(/[\w\-/.]+(?:/[\w\-/.]+)*)',   # Unix 绝对路径 /xxx/yyy
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                path = match.group(1)
                # 如果是文件名（不含/），加上./前缀表示当前目录
                if '/' not in path and '\\' not in path and not path.startswith('.'):
                    return './' + path
                return self._clean_local_path(path)
        return None
    
    def _extract_rename_params(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取重命名参数"""
        old_path = None
        new_name = None
        
        text_lower = text.lower()
        
        # 支持多种格式：
        # 1. 重命名文件 /path 为 newname
        # 2. 重命名 /path 为 newname
        # 3. 改名 /path 为 newname
        patterns = [
            r'重命名[\s]+文件[\s]+(/[\w\-/.]+)[\s]*为[\s]*([\w\-/.]+)',
            r'重命名[\s]+(/[\w\-/.]+)[\s]*为[\s]*([\w\-/.]+)',
            r'改名[\s]+(/[\w\-/.]+)[\s]*为[\s]*([\w\-/.]+)',
            r'rename[\s]+(/[\w\-/.]+)[\s]*to[\s]*([\w\-/.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                old_path = match.group(1)
                new_name = match.group(2)
                return old_path, new_name
        
        # 如果正则没匹配到，尝试用通用方法提取路径
        old_path = self._extract_path(text)
        
        # 尝试提取新名称（在"为"或"to"之后）
        separators = [' 为 ', ' 为', '为 ', ' to ', ' to', 'to ']
        for separator in separators:
            if separator in text:
                parts = text.split(separator)
                if len(parts) >= 2:
                    # 新名称是最后一部分，去掉空白
                    new_name = parts[-1].strip()
                    # 如果新名称包含路径，只取文件名
                    if '/' in new_name:
                        new_name = new_name.split('/')[-1]
                    return old_path, new_name
        
        return old_path, new_name
    
    def _extract_copy_params(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取复制/移动参数"""
        src = None
        dst = None
        
        patterns = [
            r'复制[\s]*(/[\w\-/.]+)[\s]*到[\s]*(/[\w\-/.]*)',
            r'移动[\s]*(/[\w\-/.]+)[\s]*到[\s]*(/[\w\-/.]*)',
            r'copy[\s]*(/[\w\-/.]+)[\s]*to[\s]*(/[\w\-/.]*)',
            r'move[\s]*(/[\w\-/.]+)[\s]*to[\s]*(/[\w\-/.]*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                src = match.group(1)
                dst = match.group(2)
                return src, dst
        
        # 尝试提取两个路径
        paths = re.findall(r'(/[\w\-/.]+)', text)
        if len(paths) >= 2:
            return paths[0], paths[1]
        elif len(paths) == 1:
            return paths[0], None
        return None, None
    
    def _extract_move_params(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取移动参数"""
        src = None
        dst = None
        
        text_lower = text.lower()
        
        # 匹配移动相关的模式
        patterns = [
            r'移动[\s]*文件[\s]*(/[\w\-/.]+)[\s]*到[\s]*(/[\w\-/.]*)',
            r'移动[\s]*(/[\w\-/.]+)[\s]*到[\s]*(/[\w\-/.]*)',
            r'move[\s]*(/[\w\-/.]+)[\s]*to[\s]*(/[\w\-/.]*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                src = match.group(1)
                dst = match.group(2)
                return src, dst
        
        # 尝试提取两个路径
        paths = re.findall(r'(/[\w\-/.]+)', text)
        if len(paths) >= 2:
            return paths[0], paths[1]
        elif len(paths) == 1:
            return paths[0], None
        return None, None
    
    def _extract_job_params(self, text: str) -> Dict[str, Any]:
        """提取作业提交参数"""
        params = {}
        
        # 提取命令（多种格式支持）
        cmd = None
        
        # 1. --cmd 参数格式。优先支持引号；若外层 shell/模型吞掉引号，
        #    未加引号的 cmd 必须在下一个 scnet 参数前截断，避免把
        #    "--queue/--work-dir/..." 拼进启动命令。
        cmd_match = re.search(
            r'--cmd\s+(?:"([^"]+)"|\'([^\']+)\'|(.+?)(?=\s+--(?:queue|work-dir|nnode|job-name|wall-time|nproc|ppn|ngpu|ndcu|job-mem)\b|$))',
            text,
            re.IGNORECASE
        )
        if cmd_match:
            cmd = next((g for g in cmd_match.groups() if g), "").strip()

        # 1b. 位置命令 + 显式参数格式：
        #     提交作业 bash run.sh --queue ... --work-dir ... --ppn ...
        # 先于区域名清理处理，避免“提交作业”被误删后无法提取 cmd。
        if not cmd:
            cmd_match = re.search(
                r'提交作业\s+(.+?)(?=\s+--(?:queue|work-dir|nnode|job-name|wall-time|nproc|ppn|ngpu|ndcu|job-mem)\b|$)',
                text,
                re.IGNORECASE
            )
            if cmd_match:
                cmd = cmd_match.group(1).strip()
        
        # 2. "命令行" 或 "命令行内容" 格式
        if not cmd:
            # 匹配 "命令行内容 xxx" 或 "命令行 xxx" 格式（捕获xxx部分）
            # 注意：要排除"命令行"这个词本身被捕获
            cmd_match = re.search(r'命令行(?:[\s]*内容)?[\s]*[:：]?\s+([^,，]+)', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
        
        # 3. "运行" 或 "执行" 格式（引号中的命令）
        if not cmd and ('运行' in text or '执行' in text):
            cmd_match = re.search(r'["\']([^"\']+)["\']', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
        
        # 4. "以 xxx 提交" 格式
        if not cmd and '以' in text and '提交' in text:
            cmd_match = re.search(r'以\s*(.+?)\s*提交', text)
            if cmd_match:
                cmd = cmd_match.group(1).strip()
        
        # 5. 简洁格式：提交作业 xxx（以参数关键词为边界截断）
        if not cmd:
            text_clean = text
            # 移除区域名称
            for key in self._load_clusters().keys():
                text_clean = text_clean.replace(key, '')
            # 尝试匹配 "提交作业 xxx"，以参数关键词为边界截断
            cmd_match = re.search(r'提交作业\s+(.+)', text_clean)
            if cmd_match:
                cmd = self._truncate_at_param_boundary(cmd_match.group(1).strip())
        
        if cmd:
            params["cmd"] = cmd
        
        # 提取队列
        queue_match = re.search(r'--queue[\s]*([\w]+)', text)
        if queue_match:
            params["queue"] = queue_match.group(1)
        else:
            # 匹配 "队列 xxx" / "队列：xxx" / "队列为 xxx" / "queue xxx"
            queue_match = re.search(r'队列\s*(?:为)?\s*[:：]?\s*([\w]+)', text)
            if queue_match:
                params["queue"] = queue_match.group(1)
        
        # 提取工作目录（支持 Linux 和 Windows 路径）
        # 路径模式：/public/home/... 或 D:/work/... 或 ~/... 等
        _path_pattern = r'(["\']?)([^"\'\s,，]+)\1'
        workdir_match = re.search(r'--work-dir[\s]*' + _path_pattern, text)
        if workdir_match:
            params["work_dir"] = workdir_match.group(2)
        else:
            workdir_match = re.search(r'工作目录[\s]*[:：]?\s*' + _path_pattern, text)
            if workdir_match:
                params["work_dir"] = workdir_match.group(2)
        
        # 提取节点数
        nnode_match = re.search(r'--nnode[\s]*(\d+)', text)
        if nnode_match:
            params["nnode"] = nnode_match.group(1)
        else:
            # 匹配 "节点数 2" / "节点 2" / "2个节点" / "2节点"
            nnode_match = re.search(r'节点数?[\s]*[:：]?\s*(\d+)', text)
            if not nnode_match:
                nnode_match = re.search(r'(\d+)[\s]*个?节点', text)
            if nnode_match:
                params["nnode"] = nnode_match.group(1)
        
        # 提取作业名（支持多种中文格式）
        if not params.get("job_name"):
            name_match = re.search(r'--job-name[\s]*["\']?([^"\']+)["\']?', text)
            if name_match:
                params["job_name"] = name_match.group(1).strip()
            else:
                # 匹配 "作业名 xxx" 或 "作业名称 xxx"
                name_match = re.search(r'作业名[\s]*称?[\s]*[:：]?\s*(.+)', text)
                if name_match:
                    raw_name = name_match.group(1).strip()
                    # 在下一个参数关键词处截断，避免吞入后续参数
                    truncated = self._truncate_at_param_boundary(raw_name)
                    params["job_name"] = (truncated or raw_name.split(',')[0].strip())
        
        # 提取运行时间（支持多种中文格式）
        if not params.get("wall_time"):
            walltime_match = re.search(r'--wall-time[\s]*["\']?([\d:]+)["\']?', text)
            if walltime_match:
                params["wall_time"] = walltime_match.group(1)
            else:
                # 匹配 "运行时间 xxx" 或 "最大运行时长 xxx"
                walltime_match = re.search(r'(?:运行时间|最大运行时长|运行时长)[\s]*[:：]?\s*([\d:]+)', text)
                if walltime_match:
                    params["wall_time"] = walltime_match.group(1)
                else:
                    # 匹配 "xx 小时"
                    walltime_match = re.search(r'(\d+)[\s]*小时', text)
                    if walltime_match:
                        params["wall_time"] = f"{walltime_match.group(1)}:00:00"
        
        # 提取每节点核心数。GAP_PPN 与 GAP_NPROC 是平台互斥参数，先识别 PPN，
        # 避免把“CPU核心/节点”误判为“总核心数”。
        if not params.get("ppn"):
            ppn_match = re.search(r'--ppn[\s]*(\d+)', text, re.IGNORECASE)
            if not ppn_match:
                ppn_match = re.search(r'(?:CPU\s*核心\s*/\s*节点|CPU核心/节点|每节点核心数?|PPN|每节点核?)[\s]*[:：]?\s*(\d+)', text, re.IGNORECASE)
            if ppn_match:
                params["ppn"] = ppn_match.group(1)

        # 提取总核心数。不要匹配“CPU核心/节点”，那是 PPN。
        if not params.get("nproc"):
            nproc_match = re.search(r'--nproc[\s]*(\d+)', text, re.IGNORECASE)
            if not nproc_match:
                nproc_match = re.search(r'(?:总核心数|核心数)[\s]*[:：]?\s*(\d+)', text)
            if nproc_match:
                params["nproc"] = nproc_match.group(1)
        
        return params

    def _truncate_at_param_boundary(self, text: str) -> Optional[str]:
        """
        在第一个参数关键词处截断文本，提取纯净的命令行内容。

        例如输入:
            "bash run.sh 队列 Agent0 核心数 8"
        返回:
            "bash run.sh"
        """
        # 参数关键词列表（按优先级排列，匹配最早的截断位置）
        boundaries = [
            # 中文关键词
            '工作目录', '作业名称', '作业名',
            '队列',
            '每节点核心数', '每节点核心', '核心数', '总核心数',
            '运行时间', '最大运行时长', '运行时长',
            '节点数', '节点个数',
            'GPU卡数', 'GPU卡', 'DCU卡数', 'DCU卡', '内存',
            # --flag 格式
            '--cmd', '--queue', '--work-dir', '--nnode',
            '--job-name', '--wall-time', '--nproc', '--ppn',
            '--ngpu', '--ndcu', '--job-mem',
        ]

        earliest_pos = len(text)
        for kw in boundaries:
            # 匹配关键词：前面是空白或开头，后面是空白/冒号
            pattern = re.compile(
                r'(?:^|(?<=\s))' + re.escape(kw) + r'[\s:：]',
                re.IGNORECASE
            )
            m = pattern.search(text)
            if m and m.start() < earliest_pos:
                earliest_pos = m.start()

        result = text[:earliest_pos].strip()
        # 去掉末尾的逗号/分号
        result = result.rstrip('，,；; ')
        return result if result else None

    def _chinese_to_number(self, text: str) -> Optional[int]:
        """将中文数字转换为阿拉伯数字"""
        # 先尝试直接匹配阿拉伯数字
        if text.isdigit():
            return int(text)
        # 尝试中文数字匹配
        return self.CHINESE_NUMBERS.get(text)
    
    def _extract_job_filter_params(self, text: str) -> Dict[str, Any]:
        """提取作业筛选参数（支持 AC 接口新参数）"""
        params = {}
        text_lower = text.lower()
        
        # 状态筛选 - 使用完整的 JOB_STATUS_MAP 映射
        # 优先匹配 "作业状态为XXX" 或 "状态为XXX" 格式
        status_pattern = r'(?:作业)?状态[\s]*为[\s]*([\u4e00-\u9fa5a-zA-Z]+)'
        status_match = re.search(status_pattern, text)
        if status_match:
            status_text = status_match.group(1)
            # 在 JOB_STATUS_MAP 中查找匹配的状态代码
            for status_code, keywords in self.JOB_STATUS_MAP.items():
                if any(keyword in status_text or status_text in keyword for keyword in keywords):
                    params["status"] = status_code
                    params["jobState"] = status_code  # 同时设置 jobState 用于历史作业查询
                    break
        
        # 如果没有匹配到 "状态为XXX" 格式，尝试关键词匹配
        if not params.get("status"):
            for status_code, keywords in self.JOB_STATUS_MAP.items():
                for keyword in keywords:
                    if keyword in text:
                        # 避免误匹配（如"等待"可能匹配到多个状态）
                        # 优先匹配更具体的状态描述
                        params["status"] = status_code
                        params["jobState"] = status_code
                        break
                if params.get("status"):
                    break
        
        # 队列筛选（兼容「队列：comp」「队列为 comp」）
        queue_match = re.search(r'队列\s*(?:为)?\s*[:：]?\s*([\w]+)', text)
        if queue_match:
            params["queue"] = queue_match.group(1)
        
        # 作业名筛选
        name_match = re.search(r'名称[\s]*["\']?([^"\']+)["\']?', text)
        if name_match:
            params["job_name"] = name_match.group(1)
        
        # 最近N天 - 支持中文数字
        days_match = re.search(r'最近[\s]*(\d+)[\s]*天', text)
        if days_match:
            params["days"] = int(days_match.group(1))
        else:
            # 尝试匹配中文数字
            days_ch_match = re.search(r'最近[\s]*([一二两三四五六七八九十]+)[\s]*天', text)
            if days_ch_match:
                days_num = self._chinese_to_number(days_ch_match.group(1))
                if days_num:
                    params["days"] = days_num
        
        # AC 接口新参数 - 分页
        # 支持 "第2页"、"第二页" 等格式
        page_match = re.search(r'第[\s]*(\d+)[\s]*页', text)
        if page_match:
            params["page"] = int(page_match.group(1))
        else:
            # 尝试匹配中文页码
            page_ch_match = re.search(r'第[\s]*([一二两三四五六七八九十]+)[\s]*页', text)
            if page_ch_match:
                page_num = self._chinese_to_number(page_ch_match.group(1))
                if page_num:
                    params["page"] = page_num
        
        size_match = re.search(r'每页[\s]*(\d+)[\s]*条', text)
        if size_match:
            params["size"] = int(size_match.group(1))
        
        # AC 接口新参数 - 区域ID
        cluster_id_match = re.search(r'区域[IDSid]*[\s]*[:：]?[\s]*([\w-]+)', text)
        if cluster_id_match:
            params["cluster_id"] = cluster_id_match.group(1)
        
        # AC 接口新参数 - 展示组所有成员作业
        if any(k in text for k in ["展示组作业", "显示组作业", "组作业", "show group"]):
            params["show_group_jobs"] = "true"
        
        # AC 接口新参数 - 返回所有字段
        if any(k in text for k in ["所有字段", "全部字段", "详细信息", "all data"]):
            params["show_all_data"] = True
        
        # AC 接口新参数 - 用户名筛选
        user_match = re.search(r'用户[\s]*[:：]?[\s]*([\w-]+)', text)
        if user_match:
            params["cluster_user_name"] = user_match.group(1)
        
        # 时间范围 - 支持格式: 2024-01-01 或 2024-01-01 00:00:00
        start_time_match = re.search(r'开始时间[\s]*[:：]?[\s]*([\d]{4}-[\d]{2}-[\d]{2}(?:[\s:]\d+){0,6})', text)
        if start_time_match:
            params["start_time"] = start_time_match.group(1).strip()
        
        end_time_match = re.search(r'结束时间[\s]*[:：]?[\s]*([\d]{4}-[\d]{2}-[\d]{2}(?:[\s:]\d+){0,6})', text)
        if end_time_match:
            params["end_time"] = end_time_match.group(1).strip()
        
        # 支持 "从XXX到XXX" 格式的时间范围（用于历史作业查询）
        # 格式: 从2026-04-01到2026-04-03 或 从 2026-04-01 到 2026-04-03
        date_range_match = re.search(
            r'从[\s]*([\d]{4}-[\d]{2}-[\d]{2})[\s]*到[\s]*([\d]{4}-[\d]{2}-[\d]{2})',
            text
        )
        if date_range_match:
            start_date = date_range_match.group(1)
            end_date = date_range_match.group(2)
            params["start_time"] = f"{start_date} 00:00:00"
            params["end_time"] = f"{end_date} 23:59:59"
        
        return params


# ============ 处理函数 ============

# 从配置文件导入超时时间
TIMEOUT_QUICK = AppTimeout.QUICK
TIMEOUT_NORMAL = AppTimeout.NORMAL
TIMEOUT_COMPLEX = AppTimeout.COMPLEX
TIMEOUT_TRANSFER = AppTimeout.TRANSFER

def run_subprocess(cmd: List[str], timeout: int = None, capture: bool = True) -> str:
    """运行子进程命令"""
    import subprocess
    # 默认使用普通超时
    if timeout is None:
        timeout = TIMEOUT_NORMAL
        
    try:
        if capture:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                encoding='utf-8', errors='replace',
                timeout=timeout
            )
            output = result.stdout or ""
            if result.stderr and result.returncode != 0:
                output += f"\n{result.stderr}" if output else result.stderr
            if not output:
                output = "执行完成"
            return output
        else:
            subprocess.run(cmd, timeout=timeout)
            return ""
    except subprocess.TimeoutExpired:
        return f"执行超时（超过 {timeout} 秒）"
    except Exception as e:
        return f"执行错误: {e}"


def check_config_exists() -> bool:
    """检查配置文件是否存在"""
    from config import CONFIG_PATH
    return CONFIG_PATH.exists()


def check_cache_exists() -> bool:
    """检查缓存文件是否存在"""
    from config import get_cache_path
    return get_cache_path().exists()


def ensure_cache_initialized() -> Tuple[bool, str]:
    """
    确保缓存已初始化
    
    Returns:
        (success, message) - success 为 True 表示缓存可用，False 表示需要用户手动初始化
    """
    # 1. 检查配置文件
    if not check_config_exists():
        config_path = CONFIG_PATH
        msg = f"""
{Colors.RED}✗ 配置文件不存在: {config_path}{Colors.END}

请创建配置文件，步骤如下：

1. 登录 SCNet 平台获取 Access Key 和 Secret Key:
   https://www.scnet.cn/ui/console/index.html#/personal/auth-manage

2. 创建配置文件:
   {Colors.CYAN}cat > {config_path} << 'EOF'
# SCNet Chat 配置文件
SCNET_LOGIN_URL=https://api.scnet.cn
SCNET_AC_URL=https://www.scnet.cn
SCNET_ACCESS_KEY=your_access_key_here
SCNET_SECRET_KEY=your_secret_key_here
SCNET_USER=your_username_here
SCNET_LOG_ENABLED=0
EOF{Colors.END}

3. 设置权限:
   {Colors.CYAN}chmod 600 {config_path}{Colors.END}

4. 初始化缓存:
   {Colors.CYAN}python {SCRIPTS_DIR}/cache.py{Colors.END}
"""
        return False, msg
    
    # 2. 检查缓存文件
    if not check_cache_exists():
        msg = f"""
{Colors.YELLOW}⚠ 缓存文件不存在{Colors.END}

正在自动初始化缓存...
"""
        return False, msg
    
    return True, ""


def handle_cache_refresh(params=None) -> str:
    """处理缓存刷新"""
    params = params or {}
    raw_text = params.get("raw", "")
    
    # 检查是否包含"全部"或"所有"关键词
    refresh_all = any(k in raw_text.lower() for k in ["全部", "所有", "all", "完整"])
    
    try:
        # 使用 CacheInitializer 来初始化缓存
        initializer = CacheInitializer(only_default=not refresh_all)
        success = initializer.run()
        if success:
            if refresh_all:
                return "✓ 所有区域缓存刷新成功"
            return "✓ 默认区域缓存刷新成功\n  (使用 \"刷新全部缓存\" 可刷新所有区域)"
        return "缓存刷新失败"
    except FileNotFoundError as e:
        return f"错误：{e}"
    except ValueError as e:
        return f"配置错误：{e}"
    except Exception as e:
        return f"错误：{e}"


def handle_switch_cluster(cluster_name: str) -> str:
    """处理切换区域"""
    if not cluster_name:
        return "错误：未指定区域"
    
    try:
        success = switch_default_cluster(cluster_name)
        if success:
            # 切换成功后，显示当前区域的账户信息
            result_msg = f"✓ 已切换到 {cluster_name}\n"
            user_info = handle_user_info()
            return result_msg + "\n" + user_info
        return f"切换失败"
    except Exception as e:
        return f"错误：{e}"


def handle_user_info() -> str:
    """处理用户信息查询"""
    return run_subprocess([sys.executable, str(SCRIPTS_DIR / "user.py")], timeout=TIMEOUT_QUICK)


def handle_job_stats(params: Dict[str, Any]) -> str:
    """处理作业统计信息查询"""
    return run_subprocess([sys.executable, str(SCRIPTS_DIR / "user.py"), "--stats"], timeout=TIMEOUT_NORMAL)


def handle_walltime(params: Dict[str, Any]) -> str:
    """处理机时查询"""
    return run_subprocess([sys.executable, str(SCRIPTS_DIR / "user.py"), "--walltime"], timeout=TIMEOUT_QUICK)


def handle_job_list(params: Dict[str, Any]) -> str:
    """处理实时作业查询"""
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py")]
    
    # 添加筛选参数
    if params.get("status"):
        cmd.extend(["--status", params["status"]])
    if params.get("queue"):
        cmd.extend(["--queue", params["queue"]])
    if params.get("job_name"):
        cmd.extend(["--job-name", params["job_name"]])
    
    # AC 接口新参数
    if params.get("page"):
        cmd.extend(["--page", str(params["page"])])
    if params.get("size"):
        cmd.extend(["--size", str(params["size"])])
    if params.get("cluster_id"):
        cmd.extend(["--cluster-id", params["cluster_id"]])
    if params.get("show_group_jobs"):
        cmd.extend(["--show-group-jobs", params["show_group_jobs"]])
    if params.get("cluster_user_name"):
        cmd.extend(["--cluster-user-name", params["cluster_user_name"]])
    if params.get("show_all_data"):
        cmd.append("--show-all-data")
    if params.get("start_time"):
        cmd.extend(["--start-time", params["start_time"]])
    if params.get("end_time"):
        cmd.extend(["--end-time", params["end_time"]])
    if params.get("days"):
        cmd.extend(["--days", str(params["days"])])
    
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_job_history(params: Dict[str, Any]) -> str:
    """处理历史作业查询"""
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--history"]
    
    # 添加筛选参数
    if params.get("job_id"):
        cmd.extend(["--job-id", params["job_id"]])
    if params.get("status"):
        cmd.extend(["--status", params["status"]])
    if params.get("queue"):
        cmd.extend(["--queue", params["queue"]])
    if params.get("job_name"):
        cmd.extend(["--job-name", params["job_name"]])
    if params.get("days"):
        cmd.extend(["--days", str(params["days"])])
    
    # AC 接口新参数
    if params.get("page"):
        cmd.extend(["--page", str(params["page"])])
    if params.get("size"):
        cmd.extend(["--size", str(params["size"])])
    if params.get("cluster_id"):
        cmd.extend(["--cluster-id", params["cluster_id"]])
    if params.get("show_group_jobs"):
        cmd.extend(["--show-group-jobs", params["show_group_jobs"]])
    if params.get("cluster_user_name"):
        cmd.extend(["--cluster-user-name", params["cluster_user_name"]])
    if params.get("show_all_data"):
        cmd.append("--show-all-data")
    if params.get("start_time"):
        cmd.extend(["--start-time", params["start_time"]])
    if params.get("end_time"):
        cmd.extend(["--end-time", params["end_time"]])
    
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_job_query(params: Dict[str, Any]) -> str:
    """处理通用作业查询 - 同时查询实时作业和历史作业"""
    import concurrent.futures

    results = {}

    def query_realtime():
        return handle_job_list(params.copy())

    def query_history():
        return handle_job_history(params.copy())

    # 并发查询实时作业和历史作业
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_realtime = executor.submit(query_realtime)
        future_history = executor.submit(query_history)

        results['realtime'] = future_realtime.result(timeout=TIMEOUT_NORMAL)
        results['history'] = future_history.result(timeout=TIMEOUT_NORMAL)

    # 合并输出
    output_parts = []
    output_parts.append("\n" + "=" * 70)
    output_parts.append("  📊 同时查询实时作业和历史作业")
    output_parts.append("=" * 70)
    output_parts.append("\n▶ 实时作业")
    output_parts.append(results['realtime'])
    output_parts.append("\n▶ 历史作业")
    output_parts.append(results['history'])

    return "\n".join(output_parts)


def handle_job_detail(params: Dict[str, Any]) -> str:
    """处理作业详情查询"""
    job_id = params.get("job_id")
    if not job_id:
        return "错误：请指定作业ID，例如：查询作业详情 123"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--job-id", job_id]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_job_submit(params: Dict[str, Any]) -> str:
    """处理作业提交"""
    # 检查是否提供了命令
    if not params.get("cmd"):
        return handle_job_submit_help()
    
    # 如果指定了区域，先切换
    cluster_name = params.get("cluster_name")
    if cluster_name:
        result = handle_switch_cluster(cluster_name)
        # 切换失败时返回错误
        if "错误" in result or "失败" in result:
            return result
    
    # 如果没有指定队列，从缓存获取默认队列
    if not params.get("queue"):
        try:
            import json
            with open(get_cache_path(), 'r', encoding='utf-8') as f:
                cache = json.load(f)
            clusters = cache.get('clusters', [])
            
            # 首先尝试从当前默认区域获取队列
            default_cluster = None
            for cluster in clusters:
                if cluster.get('default') or cluster.get('isDefault'):
                    default_cluster = cluster
                    break
            
            # 如果当前默认区域有队列，使用它
            if default_cluster:
                job_managers = default_cluster.get('JobManagers', [])
                if job_managers:
                    queues = job_managers[0].get('queues', [])
                    if queues:
                        params['queue'] = queues[0].get('queueName', '')
            
            # 如果当前默认区域没有队列，查找其他有队列的区域
            if not params.get("queue"):
                for cluster in clusters:
                    cluster_name = cluster.get('clusterName', '')
                    # 跳过 ac 区域
                    if cluster_name == 'ac':
                        continue
                    job_managers = cluster.get('JobManagers', [])
                    if job_managers:
                        queues = job_managers[0].get('queues', [])
                        if queues:
                            queue_name = queues[0].get('queueName', '')
                            if queue_name:
                                params['queue'] = queue_name
                                # 切换到这个有队列的区域
                                print(f"{Colors.YELLOW}⚠ 当前区域无可用队列，自动切换到 {cluster_name} 进行提交{Colors.END}")
                                switch_result = handle_switch_cluster(cluster_name)
                                if "错误" in switch_result or "失败" in switch_result:
                                    return f"切换区域失败: {switch_result}"
                                break
        except Exception as e:
            pass
    
    # 检查队列是否为空
    if not params.get("queue"):
        return f"错误：未指定队列，且无法从缓存获取默认队列。\n请使用 --queue 参数指定队列，或先刷新缓存获取可用队列。\n查询可用队列：python scripts/run \"查询队列\""

    # GAP_NPROC 与 GAP_PPN 是平台二选一参数。两者相同通常来自上层 skill
    # 同时传 ppn/nproc；保留 PPN，避免平台回退到 1 核。两者不同则拒绝提交。
    if params.get("ppn") and params.get("nproc"):
        if str(params["ppn"]) == str(params["nproc"]):
            params.pop("nproc", None)
        else:
            return "错误：--ppn 与 --nproc 对应平台 GAP_PPN/GAP_NPROC，必须二选一；若是单节点任务请只传 --ppn。"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--submit"]
    
    # 添加参数
    if params.get("cmd"):
        cmd.extend(["--cmd", params["cmd"]])
    if params.get("queue"):
        cmd.extend(["--queue", params["queue"]])
    if params.get("work_dir"):
        cmd.extend(["--work-dir", params["work_dir"]])
    if params.get("nnode"):
        cmd.extend(["--nnode", params["nnode"]])
    if params.get("job_name"):
        cmd.extend(["--job-name", params["job_name"]])
    if params.get("wall_time"):
        cmd.extend(["--wall-time", params["wall_time"]])
    if params.get("nproc"):
        cmd.extend(["--nproc", str(params["nproc"])])
    if params.get("ppn"):
        cmd.extend(["--ppn", str(params["ppn"])])
    
    return run_subprocess(cmd, timeout=TIMEOUT_COMPLEX)


def handle_job_submit_help() -> str:
    """显示作业提交帮助信息"""
    help_text = f"""
{Colors.BOLD}{Colors.CYAN}作业提交帮助{Colors.END}

{Colors.BOLD}1. 提交作业示例：{Colors.END}

  {Colors.GREEN}提交作业 sleep 900{Colors.END}

  {Colors.GREEN}提交作业 作业名：job_test，命令行内容：sleep 900，工作目录：家目录/job_test/，节点数：1，最大运行时长：24:00:00{Colors.END}

{Colors.BOLD}2. 常用参数（mapAppJobInfo）：{Colors.END}

  参数名              | 描述                                          | 示例
  ------------------- | --------------------------------------------- | --------------------------
  GAP_CMD_FILE        | 命令行内容（如需换行，请使用 \\n）              | sleep 500
  GAP_JOB_NAME        | 作业名称                                      | job_test
  GAP_QUEUE           | 队列名称                                      | debug
  GAP_WORK_DIR        | 工作路径                                      | /public/home/test/job_test
  GAP_NNODE           | 节点个数（与 GAP_NODE_STRING 二选一）         | 1
  GAP_NODE_STRING     | 指定节点（与 GAP_NNODE 二选一，另一个须为""） | 
  GAP_WALL_TIME       | 最大运行时长（HH:MM:ss）                      | 24:00:00
  GAP_SUBMIT_TYPE     | 提交类型，cmd 为命令行模式                    | cmd
  GAP_APPNAME         | 应用名称，BASE 为基础应用                     | BASE
  GAP_NPROC           | 总核心数（与 GAP_PPN 选其一填写）             | 8
  GAP_PPN             | CPU 核心/节点（与 GAP_NPROC 选其一填写）      | 4
  GAP_NGPU            | GPU 卡数/节点                                 | 1
  GAP_NDCU            | DCU 卡数/节点                                 | 1
  GAP_JOB_MEM         | 每个节点内存值，单位为 MB/GB                  | 16GB
  GAP_EXCLUSIVE       | 是否独占节点，1 为独占，空 为非独占           | 1
  GAP_MULTI_SUB       | 作业组长度，建议小于等于 50 的正整数          | 10
  GAP_STD_OUT_FILE    | 标准输出文件路径                              | /public/home/test/std.out.%j
  GAP_STD_ERR_FILE    | 标准错误文件路径                              | /public/home/test/std.err.%j

{Colors.YELLOW}自然语言交互提示：{Colors.END}
  你可以直接使用“参数名：值”的格式来提交作业，例如：
  {Colors.GREEN}提交作业 作业名：test，命令行内容：sleep 900，队列：debug，节点数：1{Colors.END}
  {Colors.GREEN}提交作业 命令行内容：mpirun -np 4 ./myapp，节点数：2，CPU核心/节点：4，最大运行时长：12:00:00{Colors.END}
  {Colors.GREEN}在山东提交作业 作业名：gpu_train，命令行内容：python train.py，队列：gpu，GPU卡数/节点：1，节点内存：32GB{Colors.END}

{Colors.BOLD}提交前准备：{Colors.END}
  1. 确保已在正确的区域（使用"切换到<中心名>"）
  2. 查询可用队列（使用"查询队列"）
  3. 确认工作目录存在且有权限

{Colors.BOLD}相关命令：{Colors.END}
  {Colors.CYAN}查询队列{Colors.END}     查看可用队列
  {Colors.CYAN}查询作业{Colors.END}     查看已提交作业状态
  {Colors.CYAN}删除作业 <ID>{Colors.END} 取消或删除作业
"""
    return help_text


def handle_job_delete(params: Dict[str, Any]) -> str:
    """处理作业删除"""
    job_id = params.get("job_id")
    if not job_id:
        return "错误：请指定作业ID，例如：删除作业 123"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--delete", "--job-id", job_id]
    return run_subprocess(cmd, timeout=TIMEOUT_COMPLEX)


def handle_job_queues() -> str:
    """处理队列查询"""
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--queues"]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_cluster_info() -> str:
    """处理集群信息查询"""
    cmd = [sys.executable, str(SCRIPTS_DIR / "job.py"), "--cluster-info"]
    return run_subprocess(cmd, timeout=TIMEOUT_QUICK)


def handle_file_list(params: Dict[str, Any]) -> str:
    """处理文件列表查询"""
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--list"]
    
    path = params.get("path")
    if path:
        cmd.append(path)
    
    return run_subprocess(cmd, timeout=TIMEOUT_QUICK)


def handle_file_upload(params: Dict[str, Any]) -> str:
    """处理文件上传"""
    local_path = params.get("local_path")
    remote_path = params.get("remote_path")
    
    if local_path and remote_path:
        cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--upload", local_path, remote_path]
        return run_subprocess(cmd, timeout=TIMEOUT_TRANSFER)
    else:
        return "请指定本地文件路径和远程目标路径\n用法: 上传文件 <本地文件> <远程目录>\n或: python scripts/file.py --upload <本地文件> <远程目录>"


def handle_file_download(params: Dict[str, Any]) -> str:
    """处理文件下载"""
    remote_path = params.get("remote_path")
    local_path = params.get("local_path")
    
    if remote_path and local_path:
        cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--download", remote_path, local_path]
        return run_subprocess(cmd, timeout=TIMEOUT_TRANSFER)
    else:
        return "请指定远程文件路径和本地目标路径\n用法: 下载文件 <远程文件> <本地目录>\n或: python scripts/file.py --download <远程文件> <本地目录>"


def handle_file_mkdir(params: Dict[str, Any]) -> str:
    """处理创建目录"""
    path = params.get("path")
    if not path:
        return "错误：请指定目录路径"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--mkdir", path]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_file_touch(params: Dict[str, Any]) -> str:
    """处理创建空文件"""
    path = params.get("path")
    if not path:
        return "错误：请指定文件路径"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--touch", path]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_file_delete(params: Dict[str, Any]) -> str:
    """处理删除文件"""
    path = params.get("path")
    if not path:
        return "错误：请指定文件路径"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--delete", path]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_file_rename(params: Dict[str, Any]) -> str:
    """处理重命名文件"""
    old_path = params.get("old_path")
    new_name = params.get("new_name")
    
    if not old_path or not new_name:
        return "错误：请指定原文件路径和新名称\n用法: 重命名 <原路径> 为 <新名称>"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--rename", old_path, new_name]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def _find_cluster_by_home_directory(path: str) -> Optional[str]:
    """
    根据路径查找包含该家目录的区域
    
    Args:
        path: 文件路径，如 /public/home/ac1npa3sf2/test.txt
    
    Returns:
        区域名称，如果未找到返回 None
    """
    try:
        import json
        cache_path = get_cache_path()
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        clusters = cache.get('clusters', [])
        
        # 提取路径中的家目录部分（如 /public/home/ac1npa3sf2）
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 3 and path_parts[0] in ['public', 'work'] and path_parts[1] == 'home':
            home_dir = f"/{path_parts[0]}/{path_parts[1]}/{path_parts[2]}"
        else:
            home_dir = path
        
        # 遍历所有区域，查找包含该家目录的区域
        for cluster in clusters:
            cluster_name = cluster.get('clusterName', '')
            if cluster_name == 'ac':
                continue
            
            # 检查 clusterUserInfo 中的 homeDir
            user_info = cluster.get('clusterUserInfo', {})
            home_dir_in_cluster = user_info.get('homeDir', '')
            
            # 如果路径包含该区域的家目录，返回该区域
            if home_dir_in_cluster and home_dir in home_dir_in_cluster:
                return cluster_name
            
            # 也检查 clusterUserName
            username = user_info.get('clusterUserName', '')
            if username and username in path:
                return cluster_name
        
        return None
    except Exception:
        return None


def handle_file_copy(params: Dict[str, Any]) -> str:
    """处理复制文件"""
    src = params.get("src")
    dst = params.get("dst")
    
    if not src or not dst:
        return "错误：请指定源文件和目标路径\n用法: 复制文件 <源文件> 到 <目标目录>"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--copy", src, dst]
    result = run_subprocess(cmd, timeout=TIMEOUT_NORMAL)
    
    # 如果失败且是文件不存在错误，尝试切换区域
    if "File does not exist" in result or "不存在" in result:
        # 尝试查找包含该家目录的区域
        target_cluster = _find_cluster_by_home_directory(src)
        
        if target_cluster:
            print(f"{Colors.YELLOW}⚠ 在当前区域未找到文件，自动切换到 {target_cluster} 重试...{Colors.END}")
            
            # 切换到目标区域
            switch_result = handle_switch_cluster(target_cluster)
            if "错误" not in switch_result and "失败" not in switch_result:
                # 重新执行复制操作
                return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)
            else:
                return f"切换区域失败: {switch_result}\n原始错误: {result}"
        else:
            # 尝试在缓存中查找有文件服务的区域
            try:
                import json
                with open(get_cache_path(), 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                clusters = cache.get('clusters', [])
                
                for cluster in clusters:
                    cluster_name = cluster.get('clusterName', '')
                    if cluster_name == 'ac':
                        continue
                    # 检查是否有 efileUrls（文件服务）
                    if cluster.get('efileUrls'):
                        print(f"{Colors.YELLOW}⚠ 在当前区域未找到文件，尝试切换到 {cluster_name}...{Colors.END}")
                        switch_result = handle_switch_cluster(cluster_name)
                        if "错误" not in switch_result and "失败" not in switch_result:
                            return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)
                        break
            except Exception:
                pass
    
    return result


def handle_file_move(params: Dict[str, Any]) -> str:
    """处理移动文件"""
    src = params.get("src")
    dst = params.get("dst")
    
    if not src or not dst:
        return "错误：请指定源文件和目标路径\n用法: 移动文件 <源文件> 到 <目标目录>"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--move", src, dst]
    return run_subprocess(cmd, timeout=TIMEOUT_NORMAL)


def handle_file_exists(params: Dict[str, Any]) -> str:
    """处理检查文件存在"""
    path = params.get("path")
    if not path:
        return "错误：请指定文件路径"
    
    cmd = [sys.executable, str(SCRIPTS_DIR / "file.py"), "--exists", path]
    return run_subprocess(cmd, timeout=TIMEOUT_QUICK)


def format_help() -> str:
    """生成帮助文本（供打印或返回给调用方，避免 help 意图下 result 为空）。"""
    return f"""
{Colors.BOLD}{Colors.CYAN}SCNet Skill - 自然语言命令帮助{Colors.END}

{Colors.BOLD}1. 缓存管理{Colors.END}
   - 刷新缓存 / 初始化缓存

{Colors.BOLD}2. 区域切换{Colors.END}
   - 切换到 [区域]
     可选: 昆山、山东、西安、四川、武汉、哈尔滨、分区一、分区二等

{Colors.BOLD}3. 用户信息查询{Colors.END}
   - 查询用户 / 账户信息 / 我的信息
   - 作业统计 / 统计信息 - 查询实时作业统计
   - 机时 / 剩余机时 / 已用机时 - 查询机时使用情况

{Colors.BOLD}4. 作业管理{Colors.END}
   - 查询作业 / 实时作业列表
   - 历史作业 / 查询历史作业
   - 提交作业 / 提交新任务 [--cmd "命令" --queue 队列名]
   - 删除作业 [作业ID] / 取消作业 [作业ID]
   - 作业详情 [作业ID]
   - 查询队列 / 可用队列
   - 集群信息 / 调度器信息

{Colors.BOLD}5. 文件管理{Colors.END}
   - 文件列表 [路径] / 查看文件 [路径]
   - 上传文件 <本地文件> 到 <远程目录>
   - 下载文件 <远程文件> 到 <本地目录>
   - 创建目录 <路径>
   - 创建文件 <路径>
   - 删除文件 <路径>
   - 重命名 <原路径> 为 <新名称>
   - 复制文件 <源文件> 到 <目标目录>
   - 移动文件 <源文件> 到 <目标目录>

{Colors.BOLD}使用示例:{Colors.END}
   python scripts/scnet.py "查询作业"
   python scripts/scnet.py "提交作业 --cmd 'sleep 100' --queue debug"
   python scripts/scnet.py "删除作业 123"
   python scnet.py "查看文件列表 /public/home/user"
"""


def print_help():
    """打印帮助信息"""
    print(format_help())


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='SCNet Skill - 自然语言交互管理 SCNet 超算平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/scnet.py "查询作业"
  python scripts/scnet.py "提交作业 --cmd 'sleep 100' --queue debug"
  python scripts/scnet.py "删除作业 123"
  python scnet.py "查看文件列表 /public/home/user"
  python scripts/scnet.py "上传文件 ./test.txt 到 /public/home/user/"

注意: 如果命令包含以 -- 开头的参数，需要用引号包裹整个命令
        """
    )
    parser.add_argument('text', nargs='?', help='自然语言命令')
    # 捕获所有剩余参数（处理 --work-dir 等参数）
    parser.add_argument('remainder', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    args = parser.parse_args()
    
    # 合并 text 和 remainder（处理 -- 开头的参数）
    if args.text:
        text = args.text
        if args.remainder:
            # 去掉 remainder 中的 '--' 标记，合并参数
            remainder = ' '.join(args.remainder)
            text = text + ' ' + remainder
    else:
        print("SCNet Skill | 输入自然语言命令，或 'quit' 退出，'help' 查看帮助")
        text = input("\n> ").strip()
        if text.lower() in ["quit", "exit", "q"]:
            return
        if text.lower() in ["help", "帮助", "?"]:
            print_help()
            return
    
    # 识别意图
    recognizer = IntentRecognizer()
    intent, params = recognizer.recognize(text)
    
    # 路由到对应处理函数
    handlers = {
        "cache_refresh": handle_cache_refresh,
        "switch_cluster": lambda p: handle_switch_cluster(p.get("cluster_name", "")),
        "user_info": lambda p: handle_user_info(),
        "job_stats": handle_job_stats,
        "walltime": handle_walltime,
        "job_list": handle_job_list,
        "job_history": handle_job_history,
        "job_query": handle_job_query,
        "job_detail": handle_job_detail,
        "job_submit": handle_job_submit,
        "job_submit_help": lambda p: handle_job_submit_help(),
        "job_delete": handle_job_delete,
        "job_queues": lambda p: handle_job_queues(),
        "cluster_info": lambda p: handle_cluster_info(),
        "file_list": handle_file_list,
        "file_upload": handle_file_upload,
        "file_download": handle_file_download,
        "file_mkdir": handle_file_mkdir,
        "file_touch": handle_file_touch,
        "file_delete": handle_file_delete,
        "file_rename": handle_file_rename,
        "file_copy": handle_file_copy,
        "file_move": handle_file_move,
        "file_exists": handle_file_exists,
        "help": lambda p: format_help(),
    }
    
    # 对于需要缓存的命令，先检查配置和缓存
    intents_requiring_cache = [
        "user_info", "job_list", "job_history", "job_query", "job_detail",
        "job_submit", "job_delete", "job_queues", "cluster_info",
        "file_list", "file_upload", "file_download", "file_mkdir",
        "file_touch", "file_delete", "file_rename", "file_copy", "file_move"
    ]
    
    if intent in intents_requiring_cache:
        cache_ok, msg = ensure_cache_initialized()
        if not cache_ok:
            print(msg)
            # 如果是缓存不存在但配置存在，尝试自动初始化
            if check_config_exists() and not check_cache_exists():
                result = handle_cache_refresh()
                print(result)
            return
    
    if intent in handlers:
        result = handlers[intent](params)
        if result:
            print(result)
        else:
            print(f"{Colors.YELLOW}命令执行完成，但没有输出结果{Colors.END}")
    else:
        print(f"{Colors.YELLOW}未能理解的命令: {text}{Colors.END}")
        print()
        print_help()


if __name__ == "__main__":
    main()
