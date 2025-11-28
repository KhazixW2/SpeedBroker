"""
策略模块 - 交易策略实现

模块结构:
- base_strategy.py: 基类和工厂类
- short_term_strategies.py: 短期策略（3-30天）
- long_term_strategies.py: 长期策略（20-60天）
- combo_strategies.py: 组合策略（10-30天）
"""

from .base_strategy import BaseStrategy, StrategyFactory

from .short_term_strategies import (
    DualMovingAverageStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
    RSIStrategy,
    KDJStrategy
)

from .long_term_strategies import (
    TripleMovingAverageStrategy,
    MomentumStrategy,
    TurtleTradingStrategy,
    MeanReversionStrategy
)

from .combo_strategies import (
    ComboStrategy
)

__all__ = [
    # 基类和工厂
    'BaseStrategy',
    'StrategyFactory',
    
    # 短期策略
    'DualMovingAverageStrategy',
    'MACDStrategy',
    'BollingerBandsStrategy',
    'RSIStrategy',
    'KDJStrategy',
    
    # 长期策略
    'TripleMovingAverageStrategy',
    'MomentumStrategy',
    'TurtleTradingStrategy',
    'MeanReversionStrategy',
    
    # 组合策略
    'ComboStrategy',
]
