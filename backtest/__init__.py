"""
回测模块 (Backtest Module)
职责: 模拟交易执行、性能分析和策略对比
"""

from .backtester import Backtester
from .analyzer import Analyzer
from .strategy_comparator import StrategyComparator

__all__ = ['Backtester', 'Analyzer', 'StrategyComparator']
