#!/usr/bin/env python3
"""
Windows 终端兼容模块

解决 Windows GBK 终端下输出 Unicode 字符（如 emoji、ANSI 颜色）时
触发 UnicodeEncodeError 导致脚本崩溃的问题。
"""

import sys


def setup_windows_console() -> None:
    """在 Windows 上启用 ANSI 并将 stdout/stderr 编码设为 utf-8"""
    if sys.platform != "win32":
        return

    # 启用 Windows 10+ 的 ANSI 颜色支持 - 使用 ctypes 替代 os.system("")
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

    # 将 stdout/stderr 重编码为 utf-8，无法编码的字符用替换符代替
    try:
        import io

        if hasattr(sys.stdout, "buffer"):
            # 避免重复包装
            if getattr(sys.stdout, "encoding", None) != "utf-8":
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer"):
            if getattr(sys.stderr, "encoding", None) != "utf-8":
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


# 模块导入时自动执行
setup_windows_console()
