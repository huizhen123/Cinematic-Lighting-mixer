"""视频处理工具函数"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def get_video_info(video_path: str) -> dict:
    """
    获取视频信息
    
    Args:
        video_path: 视频文件路径
        
    Returns:
        视频信息字典
    """
    # TODO: 使用ffprobe获取视频信息
    logger.info(f"获取视频信息: {video_path}")
    return {}


def validate_video_format(file_path: str) -> bool:
    """
    验证视频格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为支持的格式
    """
    supported_formats = ['mp4', 'mov', 'webm', 'mkv', 'flv', 'avi']
    ext = file_path.split('.')[-1].lower()
    return ext in supported_formats
