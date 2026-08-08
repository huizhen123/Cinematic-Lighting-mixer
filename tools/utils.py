"""
通用工具函数
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directory(dir_path: str) -> Path:
    """
    确保目录存在
    
    Args:
        dir_path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: str) -> float:
    """
    获取文件大小 (MB)
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小 (MB)
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def clean_cache(cache_dir: str) -> None:
    """
    清理缓存目录
    
    Args:
        cache_dir: 缓存目录路径
    """
    cache_path = Path(cache_dir)
    if cache_path.exists():
        for file in cache_path.glob('*'):
            file.unlink()
        logger.info(f"缓存已清理: {cache_dir}")
