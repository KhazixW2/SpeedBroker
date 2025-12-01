"""
数据模块 (Data Module)
职责: 唯一的数据来源，负责获取、清洗、存储和提供数据
对上层模块屏蔽数据源的差异
"""

from .data_handler import DataHandler

__all__ = ['DataHandler']
