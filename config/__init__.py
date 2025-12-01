"""
配置模块 (Configuration Module)
职责: 管理所有配置参数，提供统一的配置接口
"""

from .config import (
    ConfigManager,
    config_manager,
    DATA_CONFIG,
    STRATEGY_CONFIG,
    BACKTEST_CONFIG,
    ANALYSIS_CONFIG,
    LOGGING_CONFIG,
    DEBUG_MODE
)

__all__ = [
    'ConfigManager',
    'config_manager',
    'DATA_CONFIG',
    'STRATEGY_CONFIG',
    'BACKTEST_CONFIG',
    'ANALYSIS_CONFIG',
    'LOGGING_CONFIG',
    'DEBUG_MODE'
]
