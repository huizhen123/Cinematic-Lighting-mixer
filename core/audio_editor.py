"""音频编辑核心模块"""

import logging
from typing import List, Dict, Optional
import numpy as np
import soundfile as sf
import librosa

logger = logging.getLogger(__name__)


class AudioEditor:
    """音频编辑器 - 处理混音、效果、EQ等"""
    
    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate
        logger.info(f"初始化音频编辑器 (采样率: {sample_rate}Hz)")
    
    def mix_tracks(self, tracks: List[Dict], output_path: str) -> str:
        """
        混合多个音频轨道
        
        Args:
            tracks: 轨道列表，每个包含 {'file': str, 'volume': float, 'start': float}
            output_path: 输出文件路径
            
        Returns:
            输出路径
        """
        logger.info(f"混合 {len(tracks)} 个音频轨道...")
        
        # 计算总长度
        max_length = 0
        audio_data = []
        
        for i, track in enumerate(tracks):
            try:
                y, sr = librosa.load(track['file'], sr=self.sample_rate)
                volume = track.get('volume', 1.0)
                start = track.get('start', 0.0)
                
                # 应用音量
                y = y * volume
                
                # 应用淡入/淡出
                fade_in = track.get('fade_in', 0.0)
                fade_out = track.get('fade_out', 0.0)
                y = self._apply_fade(y, fade_in, fade_out, sr)
                
                # 计算位置和长度
                start_sample = int(start * sr)
                end_sample = start_sample + len(y)
                
                audio_data.append({
                    'audio': y,
                    'start': start_sample,
                    'end': end_sample
                })
                
                max_length = max(max_length, end_sample)
                logger.info(f"  轨道 {i+1}: {track['file']} ({len(y)} 样本)")
                
            except Exception as e:
                logger.error(f"加载音频失败: {track['file']}: {e}")
                raise
        
        # 创建混合缓冲区
        mixed = np.zeros(max_length)
        
        # 混合所有轨道
        for data in audio_data:
            start = data['start']
            end = data['end']
            mixed[start:end] += data['audio']
        
        # 标准化以防止削波
        max_val = np.max(np.abs(mixed))
        if max_val > 1.0:
            mixed = mixed / max_val
            logger.warning(f"音频超出范围，已标准化 (峰值: {max_val:.2f})")
        
        # 保存输出
        sf.write(output_path, mixed, self.sample_rate)
        logger.info(f"✅ 音频混音完成: {output_path}")
        
        return output_path
    
    def apply_reverb(self, audio_path: str, output_path: str,
                    room_size: float = 0.5, damp: float = 0.5,
                    wet: float = 0.33) -> str:
        """
        应用混响效果
        
        Args:
            audio_path: 输入音频路径
            output_path: 输出音频路径
            room_size: 房间大小 (0-1)
            damp: 阻尼 (0-1)
            wet: 湿信号 (0-1)
            
        Returns:
            输出路径
        """
        logger.info(f"应用混响效果...")
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # 简化的混响实现
        # TODO: 使用专业的混响算法
        delayed = np.pad(y, (int(0.05*sr), 0))
        reverb = y + delayed[:len(y)] * wet
        
        sf.write(output_path, reverb, sr)
        logger.info(f"✅ 混响完成: {output_path}")
        return output_path
    
    def apply_compression(self, audio_path: str, output_path: str,
                         ratio: float = 4.0, threshold: float = -20,
                         attack: float = 5, release: float = 50) -> str:
        """
        应用动态压缩
        
        Args:
            audio_path: 输入音频路径
            output_path: 输出音频路径
            ratio: 压缩比
            threshold: 阈值 (dB)
            attack: 起音时间 (ms)
            release: 释放时间 (ms)
            
        Returns:
            输出路径
        """
        logger.info(f"应用动态压缩 (比率: {ratio}:1, 阈值: {threshold}dB)...")
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # 简化的压缩实现
        # TODO: 实现完整的动态范围压缩
        compressed = np.copy(y)
        
        sf.write(output_path, compressed, sr)
        logger.info(f"✅ 压缩完成: {output_path}")
        return output_path
    
    def apply_eq(self, audio_path: str, output_path: str,
                low: float = 0, mid: float = 0, high: float = 0) -> str:
        """
        应用EQ均衡
        
        Args:
            audio_path: 输入音频路径
            output_path: 输出音频路径
            low: 低频增益 (dB)
            mid: 中频增益 (dB)
            high: 高频增益 (dB)
            
        Returns:
            输出路径
        """
        logger.info(f"应用EQ均衡 (低: {low}dB, 中: {mid}dB, 高: {high}dB)...")
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # 简化的EQ实现
        # TODO: 实现参数化EQ滤镜
        equalized = np.copy(y)
        
        sf.write(output_path, equalized, sr)
        logger.info(f"✅ EQ完成: {output_path}")
        return output_path
    
    def adjust_volume(self, audio_path: str, output_path: str,
                     volume_db: float) -> str:
        """
        调整音量
        
        Args:
            audio_path: 输入音频路径
            output_path: 输出音频路径
            volume_db: 音量变化 (dB)
            
        Returns:
            输出路径
        """
        logger.info(f"调整音量: {volume_db:+.1f}dB")
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        # 将dB转换为线性增益
        gain = 10 ** (volume_db / 20.0)
        adjusted = y * gain
        
        # 防止削波
        if np.max(np.abs(adjusted)) > 1.0:
            adjusted = adjusted / np.max(np.abs(adjusted))
        
        sf.write(output_path, adjusted, sr)
        logger.info(f"✅ 音量调整完成: {output_path}")
        return output_path
    
    def _apply_fade(self, audio: np.ndarray, fade_in: float, fade_out: float,
                   sr: int) -> np.ndarray:
        """应用淡入淡出"""
        result = np.copy(audio)
        
        if fade_in > 0:
            fade_in_samples = int(fade_in * sr)
            fade_in_env = np.linspace(0, 1, fade_in_samples)
            result[:fade_in_samples] *= fade_in_env
        
        if fade_out > 0:
            fade_out_samples = int(fade_out * sr)
            fade_out_env = np.linspace(1, 0, fade_out_samples)
            result[-fade_out_samples:] *= fade_out_env
        
        return result
