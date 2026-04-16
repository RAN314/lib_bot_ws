#!/usr/bin/env python3
"""
压缩工具模块
提供异步文件压缩、解压缩和归档功能
"""

import gzip
import shutil
import os
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class CompressionResult:
    """压缩结果"""
    original_path: Path
    compressed_path: Optional[Path]
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    success: bool
    error_message: Optional[str] = None


class CompressionUtils:
    """
    压缩工具类

    提供文件压缩、解压缩和归档功能：
    - 异步压缩避免阻塞
    - 支持gzip压缩
    - 压缩率统计
    - 错误处理和恢复
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化压缩工具

        Args:
            config: 压缩配置
        """
        self.config = config or {}
        self.compression_level = self.config.get('compression_level', 6)
        self.enable_async = self.config.get('async_compression', True)
        self.logger = logging.getLogger(__name__)

    async def compress_file(self, file_path, output_path: Optional[Path] = None) -> CompressionResult:
        """异步压缩文件

        Args:
            file_path: 要压缩的文件路径
            output_path: 输出文件路径（可选）

        Returns:
            压缩结果
        """
        start_time = datetime.now()

        try:
            file_path_obj = Path(file_path) if not isinstance(file_path, Path) else file_path
            if not file_path_obj.exists():
                return CompressionResult(
                    original_path=file_path_obj,
                    compressed_path=None,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    compression_time=0.0,
                    success=False,
                    error_message=f"文件不存在: {file_path}"
                )

            # 确定输出路径
            if output_path is None:
                file_path_obj = Path(file_path) if not isinstance(file_path, Path) else file_path
                output_path = file_path_obj.with_suffix(file_path_obj.suffix + '.gz')

            # 获取原始文件大小
            file_path_obj = Path(file_path) if not isinstance(file_path, Path) else file_path
            original_size = file_path_obj.stat().st_size

            if self.enable_async:
                # 异步压缩
                loop = asyncio.get_event_loop()
                compressed_size = await loop.run_in_executor(
                    None,
                    self._compress_file_sync,
                    file_path,
                    output_path
                )
            else:
                # 同步压缩
                compressed_size = self._compress_file_sync(file_path, output_path)

            # 计算压缩信息
            compression_time = (datetime.now() - start_time).total_seconds()
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            self.logger.info(
                f"文件压缩成功: {file_path} -> {output_path}, "
                f"压缩率: {compression_ratio:.1f}%, "
                f"耗时: {compression_time:.2f}秒"
            )

            return CompressionResult(
                original_path=file_path,
                compressed_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                success=True
            )

        except Exception as e:
            compression_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"压缩失败: {str(e)}"
            self.logger.error(f"{error_msg} - {file_path}")

            return CompressionResult(
                original_path=file_path,
                compressed_path=None,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                compression_time=compression_time,
                success=False,
                error_message=error_msg
            )

    def _compress_file_sync(self, source_path: Path, target_path: Path) -> int:
        """同步压缩文件

        Args:
            source_path: 源文件路径
            target_path: 目标文件路径

        Returns:
            压缩后文件大小
        """
        try:
            with open(source_path, 'rb') as f_in:
                with gzip.open(
                    target_path,
                    'wb',
                    compresslevel=self.compression_level
                ) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            return target_path.stat().st_size

        except Exception as e:
            # 清理可能创建的不完整文件
            if target_path.exists():
                target_path.unlink()
            raise e

    async def decompress_file(self, compressed_path: Path, output_path: Optional[Path] = None) -> CompressionResult:
        """异步解压缩文件

        Args:
            compressed_path: 压缩文件路径
            output_path: 输出文件路径（可选）

        Returns:
            解压缩结果
        """
        start_time = datetime.now()

        try:
            if not compressed_path.exists():
                return CompressionResult(
                    original_path=compressed_path,
                    compressed_path=None,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    compression_time=0.0,
                    success=False,
                    error_message=f"压缩文件不存在: {compressed_path}"
                )

            # 确定输出路径
            if output_path is None:
                # 移除.gz后缀
                output_path = compressed_path
                if output_path.suffix == '.gz':
                    output_path = output_path.with_suffix('')

            # 获取压缩文件大小
            compressed_size = compressed_path.stat().st_size

            if self.enable_async:
                # 异步解压缩
                loop = asyncio.get_event_loop()
                original_size = await loop.run_in_executor(
                    None,
                    self._decompress_file_sync,
                    compressed_path,
                    output_path
                )
            else:
                # 同步解压缩
                original_size = self._decompress_file_sync(compressed_path, output_path)

            # 计算信息
            compression_time = (datetime.now() - start_time).total_seconds()
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            self.logger.info(
                f"文件解压缩成功: {compressed_path} -> {output_path}, "
                f"压缩率: {compression_ratio:.1f}%, "
                f"耗时: {compression_time:.2f}秒"
            )

            return CompressionResult(
                original_path=compressed_path,
                compressed_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                success=True
            )

        except Exception as e:
            compression_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"解压缩失败: {str(e)}"
            self.logger.error(f"{error_msg} - {compressed_path}")

            return CompressionResult(
                original_path=compressed_path,
                compressed_path=None,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                compression_time=compression_time,
                success=False,
                error_message=error_msg
            )

    def _decompress_file_sync(self, source_path: Path, target_path: Path) -> int:
        """同步解压缩文件

        Args:
            source_path: 压缩文件路径
            target_path: 目标文件路径

        Returns:
            解压缩后文件大小
        """
        try:
            with gzip.open(source_path, 'rb') as f_in:
                with open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            return target_path.stat().st_size

        except Exception as e:
            # 清理可能创建的不完整文件
            if target_path.exists():
                target_path.unlink()
            raise e

    async def compress_directory(self, dir_path: Path, output_path: Optional[Path] = None) -> CompressionResult:
        """异步压缩目录

        Args:
            dir_path: 目录路径
            output_path: 输出文件路径（可选）

        Returns:
            压缩结果
        """
        start_time = datetime.now()

        try:
            if not dir_path.exists() or not dir_path.is_dir():
                return CompressionResult(
                    original_path=dir_path,
                    compressed_path=None,
                    original_size=0,
                    compressed_size=0,
                    compression_ratio=0.0,
                    compression_time=0.0,
                    success=False,
                    error_message=f"目录不存在或不是目录: {dir_path}"
                )

            # 确定输出路径
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = dir_path.parent / f"{dir_path.name}_{timestamp}.tar.gz"

            # 计算原始大小
            original_size = self._get_directory_size(dir_path)

            if self.enable_async:
                # 异步压缩
                loop = asyncio.get_event_loop()
                compressed_size = await loop.run_in_executor(
                    None,
                    self._compress_directory_sync,
                    dir_path,
                    output_path
                )
            else:
                # 同步压缩
                compressed_size = self._compress_directory_sync(dir_path, output_path)

            # 计算压缩信息
            compression_time = (datetime.now() - start_time).total_seconds()
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

            self.logger.info(
                f"目录压缩成功: {dir_path} -> {output_path}, "
                f"压缩率: {compression_ratio:.1f}%, "
                f"耗时: {compression_time:.2f}秒"
            )

            return CompressionResult(
                original_path=dir_path,
                compressed_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                success=True
            )

        except Exception as e:
            compression_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"目录压缩失败: {str(e)}"
            self.logger.error(f"{error_msg} - {dir_path}")

            return CompressionResult(
                original_path=dir_path,
                compressed_path=None,
                original_size=0,
                compressed_size=0,
                compression_ratio=0.0,
                compression_time=compression_time,
                success=False,
                error_message=error_msg
            )