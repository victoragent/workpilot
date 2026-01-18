"""Logger configuration"""

import logging
from pathlib import Path


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """配置并返回 logger 实例

    Args:
        name: logger 名称
        level: 日志级别

    Returns:
        配置好的 logger 实例
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level
    )
    return logging.getLogger(name)
