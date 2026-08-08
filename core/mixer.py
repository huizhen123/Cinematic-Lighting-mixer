"""核心混剪引擎"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

from .video_editor import VideoEditor
from .audio_editor import AudioEditor
from tools.lighting_tools import LightingEffects
from config.settings import MIXER_PRESETS, QUALITY_PRESETS

logger = logging.getLogger(__name__)


class TransitionType(Enum):
    """转场类型"""
    CROSSFADE = 'crossfade'
    FADE_TO_BLACK = 'fade_to_black'
    SLIDE_LEFT = 'slide_left'
    SLIDE_RIGHT = 'slide_right'
    WIPE_UP = 'wipe_up'
    WIPE_DOWN = 'wipe_down'
    ZOOM_IN = 'zoom_in'
    ZOOM_OUT = 'zoom_out'


@dataclass
class VideoClip:
    """视频片段"""
    file_path: str
    start_time: float = 0.0
    duration: Optional[float] = None
    volume: float = 1.0
    opacity: float = 1.0


@dataclass
class AudioClip:
    """音频片段"""
    file_path: str
    start_time: float = 0.0
    duration: Optional[float] = None
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0


class CinematicMixer:
    """电影级灯光混剪系统 - 为诡秘之主打造"""
    
    def __init__(self, style: str = 'cinematic_lighting', theme: str = 'secretive_lord'):
        """
        初始化混剪器
        
        Args:
            style: 灯光风格 (cinematic_lighting, secretive_lord, portfolio_showcase)
            theme: 主题 (secretive_lord)
        """
        self.style = style
        self.theme = theme
        self.preset = MIXER_PRESETS.get(style, MIXER_PRESETS['cinematic_lighting'])
        
        # 初始化编辑器
        self.video_editor = VideoEditor()
        self.audio_editor = AudioEditor()
        self.lighting_effects = LightingEffects()
        
        # 存储片段
        self.video_clips: List[VideoClip] = []
        self.audio_clips: List[AudioClip] = []
        self.transitions: List[Dict] = []
        self.keyframes: List[Dict] = []
        
        logger.info(f"初始化混剪器: style={style}, theme={theme}")
    
    def add_video(self, file_path: str, start_time: float = 0.0, 
                  duration: Optional[float] = None, volume: float = 1.0) -> None:
        """
        添加视频片段
        
        Args:
            file_path: 视频文件路径
            start_time: 开始时间 (秒)
            duration: 持续时间 (秒)
            volume: 音量 (0-1)
        """
        clip = VideoClip(file_path, start_time, duration, volume)
        self.video_clips.append(clip)
        logger.info(f"添加视频: {file_path} @ {start_time}s")
    
    def add_audio(self, file_path: str, start_time: float = 0.0,
                  duration: Optional[float] = None, volume: float = 1.0,
                  fade_in: float = 0.0, fade_out: float = 0.0) -> None:
        """
        添加音频片段
        
        Args:
            file_path: 音频文件路径
            start_time: 开始时间 (秒)
            duration: 持续时间 (秒)
            volume: 音量 (0-1)
            fade_in: 淡入时间 (秒)
            fade_out: 淡出时间 (秒)
        """
        clip = AudioClip(file_path, start_time, duration, volume, fade_in, fade_out)
        self.audio_clips.append(clip)
        logger.info(f"添加音频: {file_path} @ {start_time}s")
    
    def add_transition(self, transition_type: str, duration: float = 0.5,
                      at_time: Optional[float] = None) -> None:
        """
        添加转场
        
        Args:
            transition_type: 转场类型 (crossfade, fade_to_black 等)
            duration: 转场持续时间 (秒)
            at_time: 转场发生时间
        """
        self.transitions.append({
            'type': transition_type,
            'duration': duration,
            'at_time': at_time
        })
        logger.info(f"添加转场: {transition_type} ({duration}s)")
    
    def add_keyframe(self, time: float, brightness: float = 1.0,
                    contrast: float = 1.0, saturation: float = 1.0) -> None:
        """
        添加灯光关键帧
        
        Args:
            time: 时间点 (秒)
            brightness: 亮度 (0-2)
            contrast: 对比度 (0-2)
            saturation: 饱和度 (0-2)
        """
        self.keyframes.append({
            'time': time,
            'brightness': brightness,
            'contrast': contrast,
            'saturation': saturation
        })
        logger.info(f"添加关键帧 @ {time}s")
    
    def apply_lighting_effect(self, effect: str, intensity: float = 1.0,
                             color_temp: int = 3200) -> None:
        """
        应用灯光效果
        
        Args:
            effect: 效果名称 (dramatic_shadow, golden_glow 等)
            intensity: 强度 (0-1)
            color_temp: 色温 (K值)
        """
        logger.info(f"应用灯光效果: {effect} (强度: {intensity}, 色温: {color_temp}K)")
        # 存储到lighting_effects处理器
        self.lighting_effects.apply_effect(
            effect=effect,
            intensity=intensity,
            color_temp=color_temp
        )
    
    def create_audio_mix(self, output_path: str = 'output_audio.wav') -> str:
        """
        创建音频混音
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        logger.info(f"开始创建音频混音...")
        # 转换为dict格式用于audio_editor
        tracks = [
            {
                'file': clip.file_path,
                'start': clip.start_time,
                'volume': clip.volume,
                'fade_in': clip.fade_in,
                'fade_out': clip.fade_out
            }
            for clip in self.audio_clips
        ]
        
        result = self.audio_editor.mix_tracks(tracks, output_path)
        logger.info(f"音频混音完成: {output_path}")
        return result
    
    def auto_adjust_lighting(self, reference_image: Optional[str] = None,
                            match_intensity: bool = True,
                            preserve_details: bool = True) -> None:
        """
        自动调整灯光
        
        Args:
            reference_image: 参考图像路径
            match_intensity: 是否匹配强度
            preserve_details: 是否保持细节
        """
        logger.info(f"自动调整灯光...")
        if reference_image:
            logger.info(f"使用参考图像: {reference_image}")
        # TODO: 实现AI灯光自动调整逻辑
    
    def render(self, output_path: str, quality: str = 'high') -> str:
        """
        渲染最终混剪
        
        Args:
            output_path: 输出文件路径
            quality: 质量预设 (preview, high, 4k, 8k)
            
        Returns:
            输出文件路径
        """
        if quality not in QUALITY_PRESETS:
            logger.warning(f"未知质量预设: {quality}，使用 'high'")
            quality = 'high'
        
        quality_config = QUALITY_PRESETS[quality]
        
        logger.info(f"开始渲染混剪...")
        logger.info(f"质量: {quality}")
        logger.info(f"分辨率: {quality_config['resolution']}")
        logger.info(f"帧率: {quality_config['fps']}")
        
        # 步骤1: 处理视频
        logger.info("[1/3] 处理视频...")
        self._process_videos(quality_config)
        
        # 步骤2: 处理音频
        logger.info("[2/3] 处理音频...")
        audio_path = self.create_audio_mix('temp_audio.wav')
        
        # 步骤3: 合成输出
        logger.info("[3/3] 合成输出...")
        result = self.video_editor.composite(
            output_path=output_path,
            audio_path=audio_path,
            **quality_config
        )
        
        logger.info(f"✅ 渲染完成: {output_path}")
        return result
    
    def _process_videos(self, quality_config: Dict) -> None:
        """处理视频片段"""
        for i, clip in enumerate(self.video_clips):
            logger.info(f"  处理视频 {i+1}/{len(self.video_clips)}: {clip.file_path}")
            # 应用灯光效果
            self.lighting_effects.process_video(clip.file_path)
    
    def export_project(self, project_path: str) -> None:
        """导出项目配置"""
        project_data = {
            'style': self.style,
            'theme': self.theme,
            'preset': self.preset,
            'video_clips': [vars(c) for c in self.video_clips],
            'audio_clips': [vars(c) for c in self.audio_clips],
            'transitions': self.transitions,
            'keyframes': self.keyframes
        }
        
        with open(project_path, 'w') as f:
            json.dump(project_data, f, indent=2)
        logger.info(f"项目已导出: {project_path}")
    
    def load_project(self, project_path: str) -> None:
        """加载项目配置"""
        with open(project_path, 'r') as f:
            project_data = json.load(f)
        
        for video in project_data.get('video_clips', []):
            self.add_video(**video)
        
        for audio in project_data.get('audio_clips', []):
            self.add_audio(**audio)
        
        self.transitions = project_data.get('transitions', [])
        self.keyframes = project_data.get('keyframes', [])
        
        logger.info(f"项目已加载: {project_path}")
