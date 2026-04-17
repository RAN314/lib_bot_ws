#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFID噪声模型实现 - 模拟真实RFID检测行为
实现距离-概率检测曲线、漏检率、误检率等真实特性
"""

import numpy as np
import math
import time
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging


@dataclass
class RFIDTag:
    """RFID标签定义"""
    id: str
    position: tuple  # (x, y, z)
    power: float      # 标签功率
    enabled: bool    # 是否激活


@dataclass
class DetectionResult:
    """检测结果"""
    tag_id: str
    detected: bool
    signal_strength: float
    distance: float
    confidence: float


class RFIDDirectionNoiseModel:
    """单个方向的RFID噪声模型"""

    def __init__(self, direction: str, config: Dict):
        """
        初始化方向噪声模型

        Args:
            direction: 检测方向 (front, back, left, right)
            config: 配置参数
        """
        self.direction = direction
        self.config = config
        self.logger = logging.getLogger(f'RFID_{direction}')

        # 方向特定的参数
        self.direction_offset = self._get_direction_offset(direction)

    def _get_direction_offset(self, direction: str) -> float:
        """获取方向偏移量"""
        offsets = {
            'front': 0.0,
            'back': 0.1,    # 后方检测略差
            'left': 0.05,   # 左侧略差
            'right': 0.05   # 右侧略差
        }
        return offsets.get(direction, 0.0)

    def calculate_detection_probability(self, distance: float, angle: float) -> float:
        """计算检测概率

        Args:
            distance: 距离 (米)
            angle: 角度 (弧度)

        Returns:
            检测概率 (0-1)
        """
        # 基础距离衰减
        max_range = self.config.get('base_detection_range', 0.5)
        if distance > max_range:
            return 0.0

        # 距离-概率曲线 (指数衰减)
        distance_factor = math.exp(-self.config.get('distance_decay_factor', 2.0) * distance)

        # 角度敏感度
        angle_factor = math.cos(angle) ** self.config.get('angle_sensitivity', 0.8)

        # 环境噪声影响
        noise_factor = 1.0 - self.config.get('environment_noise', 0.1)

        # 方向偏移
        direction_penalty = self.direction_offset

        # 综合概率
        probability = distance_factor * angle_factor * noise_factor - direction_penalty

        # 确保在合理范围内
        return max(0.0, min(1.0, probability))

    def calculate_signal_strength(self, distance: float, base_strength: float = 1.0) -> float:
        """计算信号强度

        Args:
            distance: 距离
            base_strength: 基础信号强度

        Returns:
            信号强度 (0-1)
        """
        # 距离衰减
        max_range = self.config.get('base_detection_range', 0.5)
        if distance > max_range:
            return 0.0

        # 自由空间路径损耗模型
        strength = base_strength * (max_range / (distance + 0.1)) ** 2

        # 添加随机噪声
        noise = np.random.normal(0, 0.1)
        strength += noise

        # 确保在合理范围内
        return max(0.0, min(1.0, strength))


class RFIDNoiseSimulator:
    """RFID噪声仿真器 - 模拟真实RFID检测行为"""

    def __init__(self, config: Dict = None):
        """初始化RFID噪声仿真器

        Args:
            config: 配置参数
        """
        self.config = config or self._get_default_config()
        self.noise_models = {}
        self.detection_history = []

        # 初始化四个方向的噪声模型
        self._init_noise_models()

        # 统计信息
        self.stats = {
            'total_scans': 0,
            'successful_detections': 0,
            'false_positives': 0,
            'false_negatives': 0
        }

        self.logger = logging.getLogger(__name__)

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'directions': ['front', 'back', 'left', 'right'],
            'base_detection_range': 0.5,
            'false_negative_rate': 0.15,    # 15%漏检率
            'false_positive_rate': 0.05,    # 5%误检率
            'distance_decay_factor': 2.0,
            'angle_sensitivity': 0.8,
            'environment_noise': 0.1,
            'scan_frequency': 10.0,         # 10Hz扫描频率
            'min_signal_strength': 0.1      # 最小可检测信号强度
        }

    def _init_noise_models(self):
        """初始化各个方向的噪声模型"""
        for direction in self.config['directions']:
            self.noise_models[direction] = RFIDDirectionNoiseModel(
                direction=direction,
                config=self.config
            )

    def simulate_detection(self, direction: str, tags_in_range: List[Dict],
                          robot_pose: Tuple[float, float, float],
                          robot_orientation: float,
                          timestamp: float) -> List[DetectionResult]:
        """模拟RFID检测过程

        Args:
            direction: 检测方向
            tags_in_range: 范围内的标签列表
            robot_pose: 机器人位姿 (x, y, theta)
            robot_orientation: 机器人朝向 (弧度)
            timestamp: 时间戳

        Returns:
            检测结果列表
        """
        if direction not in self.noise_models:
            raise ValueError(f"未知方向: {direction}")

        noise_model = self.noise_models[direction]
        results = []

        self.stats['total_scans'] += 1

        # 计算方向角度
        direction_angle = self._get_direction_angle(direction, robot_orientation)

        # 对每个标签进行检测
        for tag in tags_in_range:
            # 计算相对距离和角度
            distance, angle = self._calculate_relative_position(
                robot_pose, tag['position'], direction_angle
            )

            # 计算检测概率
            detection_prob = noise_model.calculate_detection_probability(distance, angle)

            # 基础检测决策
            base_detection = np.random.random() < detection_prob

            # 添加漏检率影响
            false_negative = np.random.random() < self.config['false_negative_rate']
            actual_detection = base_detection and not false_negative

            if actual_detection:
                # 计算信号强度
                signal_strength = noise_model.calculate_signal_strength(distance)

                # 只报告足够强的信号
                if signal_strength >= self.config['min_signal_strength']:
                    confidence = min(1.0, signal_strength * detection_prob)

                    result = DetectionResult(
                        tag_id=tag['id'],
                        detected=True,
                        signal_strength=signal_strength,
                        distance=distance,
                        confidence=confidence
                    )
                    results.append(result)
                    self.stats['successful_detections'] += 1
                else:
                    self.stats['false_negatives'] += 1
            else:
                self.stats['false_negatives'] += 1

        # 添加误检（虚假检测）
        false_positives = self._generate_false_positives(direction)
        for fp_tag_id in false_positives:
            result = DetectionResult(
                tag_id=fp_tag_id,
                detected=True,
                signal_strength=0.3,  # 虚假信号强度较低
                distance=0.0,
                confidence=0.3
            )
            results.append(result)
            self.stats['false_positives'] += 1

        return results

    def _get_direction_angle(self, direction: str, robot_orientation: float) -> float:
        """获取方向对应的角度"""
        direction_angles = {
            'front': 0.0,
            'back': math.pi,
            'left': math.pi / 2,
            'right': -math.pi / 2
        }

        base_angle = direction_angles.get(direction, 0.0)
        return robot_orientation + base_angle

    def _calculate_relative_position(self, robot_pose: Tuple[float, float, float],
                                   tag_position: Tuple[float, float, float],
                                   direction_angle: float) -> Tuple[float, float]:
        """计算相对位置（距离和角度）"""
        robot_x, robot_y, _ = robot_pose
        tag_x, tag_y, _ = tag_position

        # 计算距离
        dx = tag_x - robot_x
        dy = tag_y - robot_y
        distance = math.sqrt(dx**2 + dy**2)

        # 计算相对于检测方向的角度
        tag_angle = math.atan2(dy, dx)
        relative_angle = tag_angle - direction_angle

        # 规范化角度到 [-π, π]
        relative_angle = (relative_angle + math.pi) % (2 * math.pi) - math.pi

        return distance, relative_angle

    def _generate_false_positives(self, direction: str) -> List[str]:
        """生成误检标签"""
        false_positives = []

        if np.random.random() < self.config['false_positive_rate']:
            # 生成虚假标签ID
            fake_id = f"fake_tag_{np.random.randint(1000, 9999)}"
            false_positives.append(fake_id)

        return false_positives

    def get_statistics(self) -> Dict:
        """获取检测统计信息"""
        if self.stats['total_scans'] == 0:
            return self.stats.copy()

        stats = self.stats.copy()
        stats['detection_rate'] = (stats['successful_detections'] /
                                  stats['total_scans'])
        stats['false_positive_rate'] = (stats['false_positives'] /
                                       stats['total_scans'])
        stats['false_negative_rate'] = (stats['false_negatives'] /
                                       stats['total_scans'])

        return stats

    def reset_statistics(self):
        """重置统计信息"""
        self.stats = {
            'total_scans': 0,
            'successful_detections': 0,
            'false_positives': 0,
            'false_negatives': 0
        }