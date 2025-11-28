"""
策略层 (Strategy Layer)
职责: 生成交易信号，这是策略思想的纯粹实现

此文件现在作为向后兼容的导入接口，实际策略实现已拆分为多个模块：
- base_strategy.py: 基类和工厂类
- short_term_strategies.py: 短期策略
- long_term_strategies.py: 长期策略
- combo_strategies.py: 组合策略
"""

# 从新的模块结构导入所有策略
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

# 保持向后兼容性
__all__ = [
    'BaseStrategy',
    'StrategyFactory',
    'DualMovingAverageStrategy',
    'MACDStrategy',
    'BollingerBandsStrategy',
    'RSIStrategy',
    'KDJStrategy',
    'TripleMovingAverageStrategy',
    'MomentumStrategy',
    'TurtleTradingStrategy',
    'MeanReversionStrategy',
    'ComboStrategy',
]
