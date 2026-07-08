#!/usr/bin/env python3
"""
公共工具模块
提供跨脚本共享的工具函数和类
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache

from config import get_cache_path, CACHE_MAX_AGE


# =============================================================================
# 终端颜色代码
# =============================================================================

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


# =============================================================================
# 打印函数
# =============================================================================

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN} {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.END}\n")


def print_section(title: str):
    """打印小节标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}▶ {title}{Colors.END}")
    print(f"{Colors.BLUE}{'─' * 60}{Colors.END}")


def print_item(label: str, value: str, indent: int = 0):
    """打印键值对"""
    prefix = "  " * indent
    print(f"{prefix}{Colors.BOLD}{label}:{Colors.END} {value}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


# =============================================================================
# 缓存管理
# =============================================================================

@lru_cache(maxsize=1)
def get_cached_cache_path() -> Path:
    """获取缓存路径（结果会被缓存，避免重复读取配置文件）"""
    return get_cache_path()


def load_cache(auto_init: bool = True) -> Optional[Dict[str, Any]]:
    """
    加载缓存文件
    
    Args:
        auto_init: 缓存不存在或过期时是否自动初始化
    
    Returns:
        缓存数据，如果加载失败则返回 None
    """
    cache_path = get_cached_cache_path()
    
    # 检查缓存文件是否存在
    if not cache_path.exists():
        print_warning(f"缓存文件不存在: {cache_path}")
        
        if auto_init:
            print_info("正在自动初始化缓存...")
            if _refresh_cache():
                # 重新加载缓存
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print_error(f"加载新缓存失败: {e}")
                    return None
            else:
                print_error("自动初始化缓存失败")
                return None
        else:
            print(f"\n请先运行缓存初始化命令:")
            print(f"  python scripts/cache.py")
            return None
    
    # 加载缓存文件
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"缓存文件解析失败: {e}")
        if auto_init:
            print_info("正在自动刷新缓存...")
            if _refresh_cache():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e2:
                    print_error(f"加载新缓存失败: {e2}")
                    return None
            else:
                print_error("自动刷新缓存失败")
                return None
        return None
    except Exception as e:
        print_error(f"读取缓存文件失败: {e}")
        if auto_init:
            print_info("正在自动刷新缓存...")
            if _refresh_cache():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e2:
                    print_error(f"加载新缓存失败: {e2}")
                    return None
            else:
                print_error("自动刷新缓存失败")
                return None
        return None
    
    # 检查缓存是否过期（token 有效期通常为 12 小时）
    meta = cache.get('_meta', {})
    updated_at = meta.get('updated_at', 0)
    current_time = int(time.time())
    
    if current_time - updated_at > CACHE_MAX_AGE:
        print_warning(f"缓存已过期（上次更新: {datetime.fromtimestamp(updated_at).strftime('%Y-%m-%d %H:%M:%S')}）")
        
        if auto_init:
            print_info("正在自动刷新缓存...")
            if _refresh_cache():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print_error(f"加载新缓存失败: {e}")
                    return cache  # 即使刷新失败，也返回过期缓存
            else:
                print_warning("自动刷新缓存失败，尝试使用现有缓存")
                return cache
        else:
            print(f"\n请手动刷新缓存:")
            print(f"  python scripts/cache.py")
            return cache  # 返回过期缓存（可能还能用）
    
    return cache


def _refresh_cache() -> bool:
    """调用 cache.py 刷新缓存"""
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "cache.py")],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except Exception as e:
        print_error(f"刷新缓存失败: {e}")
        return False


# =============================================================================
# 异常处理工具
# =============================================================================

class SCNetError(Exception):
    """SCNet 基础异常"""
    pass


class ConfigError(SCNetError):
    """配置错误"""
    pass


class APIError(SCNetError):
    """API 调用错误"""
    def __init__(self, message: str, code: int = None, response: dict = None):
        super().__init__(message)
        self.code = code
        self.response = response


class CacheError(SCNetError):
    """缓存错误"""
    pass


class NetworkError(SCNetError):
    """网络错误"""
    pass


def handle_exception(e: Exception, context: str = "") -> str:
    """
    统一异常处理
    
    Args:
        e: 异常对象
        context: 错误上下文
    
    Returns:
        错误信息字符串
    """
    if isinstance(e, APIError):
        return f"{context} API错误: {e}"
    elif isinstance(e, ConfigError):
        return f"{context} 配置错误: {e}"
    elif isinstance(e, NetworkError):
        return f"{context} 网络错误: {e}"
    elif isinstance(e, json.JSONDecodeError):
        return f"{context} JSON解析错误: {e}"
    elif isinstance(e, FileNotFoundError):
        return f"{context} 文件不存在: {e}"
    elif isinstance(e, PermissionError):
        return f"{context} 权限错误: {e}"
    elif isinstance(e, TimeoutError):
        return f"{context} 操作超时"
    else:
        return f"{context} 错误: {e}"
