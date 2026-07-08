"""
SCNet Chat 配置文件管理模块
只支持从 ~/.scnet-chat.env 文件读取和写入配置
"""

import os
from pathlib import Path

# 默认配置文件路径
DEFAULT_ENV_PATH = Path.home() / ".scnet-chat.env"

# 配置项映射：环境变量名 -> 配置键名
CONFIG_MAPPING = {
    'SCNET_ACCESS_KEY': 'access_key',
    'SCNET_SECRET_KEY': 'secret_key',
    'SCNET_USER': 'user',
}

# 反向映射：配置键名 -> 环境变量名
REVERSE_MAPPING = {v: k for k, v in CONFIG_MAPPING.items()}

# 必需的配置项
REQUIRED_KEYS = ['access_key', 'secret_key', 'user']


def load_env_file(config_path=None):
    """
    从 .env 文件加载配置

    Args:
        config_path: 自定义配置文件路径，默认 ~/.scnet-chat.env

    Returns:
        dict: 配置字典
    """
    config = {}

    if config_path is None:
        config_path = DEFAULT_ENV_PATH
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        return config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')  # 去除引号

                    # 映射到标准配置键
                    if key in CONFIG_MAPPING:
                        config[CONFIG_MAPPING[key]] = value
    except Exception as e:
        print(f"⚠️  读取配置文件失败: {e}")

    return config


def write_env_file(config, config_path=None):
    """
    将配置写入 .env 文件

    Args:
        config: 配置字典
        config_path: 配置文件路径，默认 ~/.scnet-chat.env

    Returns:
        bool: 是否成功写入
    """
    if config_path is None:
        config_path = DEFAULT_ENV_PATH
    else:
        config_path = Path(config_path)

    try:
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有内容（保留注释）
        existing_lines = []
        existing_keys = set()
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        key = stripped.split('=', 1)[0].strip()
                        existing_keys.add(key)
                    existing_lines.append(line.rstrip('\n'))

        # 构建新内容
        lines = existing_lines if existing_lines else [
            "# SCNet Chat 配置文件",
            "# 存放位置: ~/.scnet-chat.env",
            "# 权限建议: chmod 600 ~/.scnet-chat.env",
            "",
            "# SCNet 访问密钥 (Access Key)",
        ]

        # 添加或更新配置项
        for key in REQUIRED_KEYS:
            env_var = REVERSE_MAPPING.get(key)
            value = config.get(key)
            if value and env_var:
                if env_var not in existing_keys:
                    # 添加新配置项
                    if env_var == 'SCNET_ACCESS_KEY':
                        lines.append("")
                        lines.append("# SCNet 访问密钥 (Access Key)")
                    elif env_var == 'SCNET_SECRET_KEY':
                        lines.append("")
                        lines.append("# SCNet 密钥 (Secret Key)")
                    elif env_var == 'SCNET_USER':
                        lines.append("")
                        lines.append("# SCNet 用户名")
                    lines.append(f"{env_var}={value}")

        # 写入文件
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

        # 设置文件权限为仅所有者可读写
        os.chmod(config_path, 0o600)
        return True

    except Exception as e:
        print(f"⚠️  写入配置文件失败: {e}")
        return False


def load_config(config_path=None):
    """
    加载配置（仅从 ~/.scnet-chat.env 读取）

    Args:
        config_path: 自定义 .env 配置文件路径

    Returns:
        dict: 配置字典
    """
    return load_env_file(config_path)


def check_config(config=None):
    """
    检查配置是否完整

    Args:
        config: 配置字典，如果为 None 则自动加载

    Returns:
        tuple: (is_valid: bool, missing_keys: list)
    """
    if config is None:
        config = load_config()

    missing_keys = [key for key in REQUIRED_KEYS if not config.get(key)]

    return len(missing_keys) == 0, missing_keys


def create_config_template(config_path=None):
    """
    创建配置文件模板

    Args:
        config_path: 配置文件路径，默认 ~/.scnet-chat.env

    Returns:
        str: 创建的配置文件路径
    """
    if config_path is None:
        config_path = DEFAULT_ENV_PATH
    else:
        config_path = Path(config_path)

    template_content = """# SCNet Chat 配置文件
# 存放位置: ~/.scnet-chat.env
# 权限建议: chmod 600 ~/.scnet-chat.env

# SCNet 访问密钥 (Access Key)
SCNET_ACCESS_KEY=your_access_key_here

# SCNet 密钥 (Secret Key)
SCNET_SECRET_KEY=your_secret_key_here

# SCNet 用户名
SCNET_USER=your_username_here
"""

    try:
        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        # 设置文件权限为仅所有者可读写
        os.chmod(config_path, 0o600)
        return str(config_path)
    except Exception as e:
        raise IOError(f"创建配置文件失败: {e}")


# 导出
__all__ = [
    'load_config',
    'load_env_file',
    'write_env_file',
    'check_config',
    'create_config_template',
    'DEFAULT_ENV_PATH',
    'CONFIG_MAPPING',
]
