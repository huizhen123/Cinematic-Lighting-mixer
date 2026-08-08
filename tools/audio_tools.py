"""音频处理工具函数"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: str) -> float:
    """
    获取音频时长
    
    Args:
        audio_path: 音频文件路径
        
    Returns:
        时长 (秒)
    """
    # TODO: 使用librosa获取音频时长
    logger.info(f"获取音频时长: {audio_path}")
    return 0.0


def validate_audio_format(file_path: str) -> bool:
    """
    验证音频格式
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为支持的格式
    """
    supported_formats = ['mp3', 'wav', 'aac', 'flac', 'ogg']
    ext = file_path.split('.')[-1].lower()
    return ext in supported_formats
