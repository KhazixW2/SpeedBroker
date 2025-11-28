"""
策略基类模块 (Base Strategy Module)
定义所有策略的通用接口和工厂类
"""

import pandas as pd
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """策略基类 - 定义所有策略的通用接口"""
    
    def __init__(self, config):
        """
        初始化策略
        
        Args:
            config: 策略配置字典 (STRATEGY_CONFIG)
        """
        self.config = config
        self.strategy_name = config.get('strategy_name', 'BaseStrategy')
    
    @abstractmethod
    def generate_signals(self, data):
        """
        生成交易信号的抽象方法 (子类必须实现)
        
        Args:
            data: pd.DataFrame, 包含OHLCV数据
            
        Returns:
            pd.DataFrame: 添加了信号列的数据
                - signal: 1=买入, -1=卖出, 0=持有
        """
        pass
    
    def _validate_data(self, data):
        """验证输入数据的完整性"""
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_columns if col not in data.columns]
        
        if missing:
            raise ValueError(f"数据缺少必要的列: {missing}")
        
        if data.empty:
            raise ValueError("输入数据为空")
        
        return True


class StrategyFactory:
    """策略工厂 - 用于创建不同的策略实例"""
    
    @staticmethod
    def create_strategy(config):
        """
        根据配置创建策略实例
        
        Args:
            config: 策略配置字典
            
        Returns:
            BaseStrategy: 策略实例
        """
        from .short_term_strategies import (
            DualMovingAverageStrategy, MACDStrategy, BollingerBandsStrategy,
            RSIStrategy, KDJStrategy
        )
        from .long_term_strategies import (
            TripleMovingAverageStrategy, MomentumStrategy,
            TurtleTradingStrategy, MeanReversionStrategy
        )
        from .combo_strategies import ComboStrategy
        
        strategy_name = config.get('strategy_name', 'DualMovingAverage')
        
        strategies = {
            # 短期策略
            'DualMovingAverage': DualMovingAverageStrategy,
            'MACD': MACDStrategy,
            'BollingerBands': BollingerBandsStrategy,
            'RSI': RSIStrategy,
            'KDJ': KDJStrategy,
            
            # 长期策略
            'TripleMovingAverage': TripleMovingAverageStrategy,
            'Momentum': MomentumStrategy,
            'TurtleTrading': TurtleTradingStrategy,
            'MeanReversion': MeanReversionStrategy,
            
            # 组合策略
            'Combo': ComboStrategy,
        }
        
        strategy_class = strategies.get(strategy_name)
        
        if strategy_class is None:
            available = ', '.join(strategies.keys())
            raise ValueError(f"不支持的策略: {strategy_name}。可用策略: {available}")
        
        return strategy_class(config)
