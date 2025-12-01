"""
配置文件 - 项目的"控制面板"
从config.ini读取配置参数，实现配置驱动的设计理念
"""

import os
import configparser
from pathlib import Path


class ConfigManager:
    """配置管理器 - 从config.ini读取配置"""
    
    def __init__(self, config_file='config.ini'):
        """初始化配置管理器"""
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        
        # 检查配置文件是否存在
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 读取配置文件
        self.config.read(config_file, encoding='utf-8')
    
    def get_data_config(self):
        """获取数据配置"""
        section = 'DATA'
        return {
            'tickers': [self.config.get(section, 'default_ticker')],
            'start_date': self.config.get(section, 'start_date'),
            'end_date': self.config.get(section, 'end_date'),
            'data_source': self.config.get(section, 'data_source'),
            'tushare_token': self.config.get(section, 'tushare_token', fallback=''),
            'futu_host': self.config.get(section, 'futu_host', fallback='127.0.0.1'),
            'futu_port': self.config.getint(section, 'futu_port', fallback=11111),
            'use_cache': self.config.getboolean(section, 'use_cache', fallback=True),
            'cache_dir': self.config.get(section, 'cache_dir', fallback='./data/cache'),
        }
    
    def get_strategy_config(self):
        """获取策略配置"""
        section = 'STRATEGY'
        return {
            'strategy_name': self.config.get(section, 'strategy_name'),
            'short_window': self.config.getint(section, 'short_window'),
            'long_window': self.config.getint(section, 'long_window'),
            'rsi_period': self.config.getint(section, 'rsi_period', fallback=14),
            'rsi_oversold': self.config.getint(section, 'rsi_oversold', fallback=30),
            'rsi_overbought': self.config.getint(section, 'rsi_overbought', fallback=70),
        }
    
    def get_backtest_config(self):
        """获取回测配置"""
        section = 'BACKTEST'
        # 注意：config.ini中的费率是千分比/万分比，需要转换为小数
        return {
            'initial_capital': self.config.getint(section, 'initial_capital'),
            'commission_rate': self.config.getfloat(section, 'commission_rate') / 1000,  # 转换为小数
            'stamp_duty_rate': self.config.getfloat(section, 'stamp_duty_rate') / 1000,
            'slippage': self.config.getfloat(section, 'slippage') / 10000,
            'position_size': self.config.getfloat(section, 'position_size'),
        }
    
    def get_analysis_config(self):
        """获取分析配置"""
        section = 'ANALYSIS'
        return {
            'risk_free_rate': self.config.getfloat(section, 'risk_free_rate'),
            'benchmark': self.config.get(section, 'benchmark'),
            'output_dir': self.config.get(section, 'output_dir'),
            'save_plots': self.config.getboolean(section, 'save_plots'),
        }
    
    def get_logging_config(self):
        """获取日志配置"""
        section = 'LOGGING'
        return {
            'level': self.config.get(section, 'level', fallback='INFO'),
            'format': self.config.get(section, 'format', fallback='%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file': self.config.get(section, 'file', fallback='./logs/backtest.log'),
        }
    
    def get_global_config(self):
        """获取全局配置"""
        section = 'GLOBAL'
        return {
            'debug_mode': self.config.getboolean(section, 'debug_mode', fallback=False),
        }
    
    def get_default_ticker_info(self):
        """获取默认股票信息"""
        section = 'DATA'
        ticker = self.config.get(section, 'default_ticker')
        name = self.config.get(section, 'default_ticker_name', fallback='')
        return ticker, name


# 创建全局配置管理器实例
try:
    config_manager = ConfigManager()
    
    # 导出配置字典（保持向后兼容）
    DATA_CONFIG = config_manager.get_data_config()
    STRATEGY_CONFIG = config_manager.get_strategy_config()
    BACKTEST_CONFIG = config_manager.get_backtest_config()
    ANALYSIS_CONFIG = config_manager.get_analysis_config()
    LOGGING_CONFIG = config_manager.get_logging_config()
    DEBUG_MODE = config_manager.get_global_config()['debug_mode']
    
except FileNotFoundError as e:
    print(f"警告: {e}")
    print("将使用默认配置...")
    
    # 提供默认配置作为后备
    DATA_CONFIG = {
        'tickers': ['000001.SZ'],
        'start_date': '2023-01-01',
        'end_date': '2024-10-01',
        'data_source': 'akshare',
        'tushare_token': '',
        'futu_host': '127.0.0.1',
        'futu_port': 11111,
        'use_cache': True,
        'cache_dir': './data/cache',
    }
    
    STRATEGY_CONFIG = {
        'strategy_name': 'DualMovingAverage',
        'short_window': 10,
        'long_window': 30,
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
    }
    
    BACKTEST_CONFIG = {
        'initial_capital': 100000,
        'commission_rate': 0.0003,
        'stamp_duty_rate': 0.001,
        'slippage': 0.0001,
        'position_size': 1.0,
    }
    
    ANALYSIS_CONFIG = {
        'risk_free_rate': 0.03,
        'benchmark': '000300.SH',
        'output_dir': './output',
        'save_plots': True,
    }
    
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': './logs/backtest.log',
    }
    
    DEBUG_MODE = False
    config_manager = None
