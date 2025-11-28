"""
图形化用户界面 (GUI Main) - PyQtGraph版本
基于PyQt5和PyQtGraph的用户友好交互界面
使用PyQtGraph替代matplotlib，避免NumPy版本冲突
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QTabWidget, QGroupBox, QGridLayout, QMessageBox,
    QProgressBar, QFileDialog, QSplitter, QAction, QMenu, QCompleter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QStringListModel
from PyQt5.QtGui import QFont, QPixmap, QIcon
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
import numpy as np

# 导入回测系统模块
from core.config import (
    DATA_CONFIG, STRATEGY_CONFIG, BACKTEST_CONFIG, ANALYSIS_CONFIG,
    config_manager
)
from core.data_handler import DataHandler
from strategies.strategy import StrategyFactory
from core.backtester import Backtester
from core.analyzer import Analyzer
from utils.stock_list import StockDatabase


# 配置PyQtGraph
pg.setConfigOption('background', 'w')  # 白色背景
pg.setConfigOption('foreground', 'k')  # 黑色前景


class CompareThread(QThread):
    """策略对比线程"""
    
    # 定义信号
    progress_update = pyqtSignal(str)
    result_ready = pyqtSignal(object)  # DataFrame
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self):
        """执行策略对比"""
        try:
            from core.strategy_comparator import StrategyComparator
            
            self.progress_update.emit("🔄 初始化策略对比器...")
            
            # 创建对比器
            data_handler = DataHandler(self.config['data'])
            comparator = StrategyComparator(
                data_handler,
                self.config['backtest'],
                self.config['analysis']
            )
            
            # 执行对比
            tickers = self.config['data']['tickers']
            results_df = comparator.compare_all_strategies(
                tickers,
                progress_callback=self.progress_update.emit
            )
            
            self.progress_update.emit("✅ 策略对比完成！")
            self.result_ready.emit(results_df)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class BacktestThread(QThread):
    """后台回测线程"""
    
    # 定义信号
    progress_update = pyqtSignal(str)
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
    
    def run(self):
        """执行回测"""
        try:
            # 步骤 1: 初始化模块
            self.progress_update.emit("📦 [1/6] 初始化模块...")
            
            data_handler = DataHandler(self.config['data'])
            strategy = StrategyFactory.create_strategy(self.config['strategy'])
            backtester = Backtester(self.config['backtest'])
            analyzer = Analyzer(self.config['analysis'])
            
            # 步骤 2: 获取数据
            self.progress_update.emit("📊 [2/6] 获取股票数据...")
            tickers = self.config['data']['tickers']
            data = data_handler.get_data(tickers)
            
            # 步骤 3: 生成信号
            self.progress_update.emit("💡 [3/6] 生成交易信号...")
            data_with_signals = strategy.generate_signals(data)
            
            # 步骤 4: 执行回测
            self.progress_update.emit("⚙️  [4/6] 执行回测...")
            backtest_results = backtester.run_backtest(data_with_signals)
            
            # 步骤 5: 分析结果
            self.progress_update.emit("📈 [5/6] 分析回测结果...")
            portfolio_df = backtest_results['portfolio_df']
            trades_df = backtest_results['trades']
            
            metrics = analyzer.calculate_metrics(
                portfolio_df,
                self.config['backtest']['initial_capital']
            )
            
            trade_stats = backtester.calculate_trade_stats(trades_df)
            
            # 步骤 6: 完成
            self.progress_update.emit("📊 [6/6] 准备显示结果...")
            
            # 发送结果
            result = {
                'portfolio_df': portfolio_df,
                'trades_df': trades_df,
                'metrics': metrics,
                'trade_stats': trade_stats,
                'ticker': tickers[0]
            }
            
            self.progress_update.emit("✅ 回测完成！")
            self.result_ready.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.result_data = None
        self.settings = QSettings('SpeedBroker', 'BacktestSystem')
        
        # 从配置文件加载默认值
        self.load_default_config()
        
        self.init_ui()
    
    def get_popular_stocks(self):
        """获取股票代码列表，用于自动补全"""
        # 默认使用静态列表（200+只，快速稳定）
        # 如需所有A股，可改为get_dynamic_stocks_akshare()
        print("[股票库] 加载股票列表...")
        stocks = StockDatabase.get_all_stocks()
        print(f"[股票库] 已加载 {len(stocks)} 只股票")
        return stocks
        
        # 可选：使用动态获取（需要网络，首次较慢）
        # stocks = StockDatabase.get_dynamic_stocks_akshare()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("🚀 量化交易回测系统 - GUI版本 (PyQtGraph)")
        self.setGeometry(100, 100, 1280, 720)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 主分割器：左右布局
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：参数配置面板（整列）
        left_panel = self.create_config_panel()
        main_splitter.addWidget(left_panel)
        
        # 右侧：垂直分割器（上图表、下结果）
        right_splitter = QSplitter(Qt.Vertical)
        
        # 右上：图表显示区域
        chart_panel = self.create_chart_panel()
        chart_panel.setMinimumHeight(300)  # 设置图表区域最小高度
        right_splitter.addWidget(chart_panel)
        
        # 右下：分析结果区域（标签页）
        result_panel = self.create_result_tabs()
        result_panel.setMinimumHeight(200)  # 设置结果区域最小高度
        right_splitter.addWidget(result_panel)
        
        # 设置右侧上下比例 (3:2) - 图表占比稍大
        right_splitter.setSizes([600, 400])
        
        # 将右侧分割器添加到主分割器
        main_splitter.addWidget(right_splitter)
        
        # 设置左右比例 (1:3) - 配置面板较窄，内容区域较宽
        main_splitter.setSizes([400, 1200])
        
        main_layout.addWidget(main_splitter)
        
        # 设置全局字体（确保中文显示）
        app_font = QFont("Microsoft YaHei", 9)
        self.setFont(app_font)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-family: "Microsoft YaHei";
                font-size: 11pt;
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 8px 0 8px;
                font-family: "Microsoft YaHei";
                font-size: 11pt;
            }
            QLabel {
                font-family: "Microsoft YaHei";
                font-size: 10pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
    def create_config_panel(self):
        """创建配置面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 标题
        title = QLabel("⚙️ 参数配置")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 数据配置
        data_group = self.create_data_config()
        layout.addWidget(data_group)
        
        # 策略配置
        strategy_group = self.create_strategy_config()
        layout.addWidget(strategy_group)
        
        # 回测配置
        backtest_group = self.create_backtest_config()
        layout.addWidget(backtest_group)
        
        # 运行按钮
        self.run_button = QPushButton("🚀 开始回测")
        self.run_button.setMinimumHeight(50)
        self.run_button.clicked.connect(self.run_backtest)
        layout.addWidget(self.run_button)
        
        # 对比所有策略按钮
        self.compare_button = QPushButton("📊 对比所有策略")
        self.compare_button.setMinimumHeight(50)
        self.compare_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.compare_button.clicked.connect(self.compare_all_strategies)
        layout.addWidget(self.compare_button)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        return panel
    
    def create_data_config(self):
        """创建数据配置组"""
        group = QGroupBox("📊 数据配置")
        layout = QGridLayout()
        
        # 股票代码
        layout.addWidget(QLabel("股票代码:"), 0, 0)
        self.ticker_input = QLineEdit(self.default_ticker)
        
        # 添加自动补全功能
        stock_list = self.get_popular_stocks()
        completer = QCompleter(stock_list)
        completer.setCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        completer.setFilterMode(Qt.MatchContains)  # 包含匹配
        completer.activated[str].connect(self.on_stock_selected)  # 连接选择信号（带参数）
        self.ticker_input.setCompleter(completer)
        
        # 添加提示文本
        self.ticker_input.setPlaceholderText("输入代码或名称搜索")
        
        layout.addWidget(self.ticker_input, 0, 1)
        
        # 股票信息显示框（新增）
        layout.addWidget(QLabel("选中股票:"), 1, 0)
        self.stock_info_label = QLabel(f"{self.default_ticker} - {self.default_ticker_name}")
        self.stock_info_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                padding: 8px;
                border-radius: 3px;
                color: #2e7d32;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.stock_info_label, 1, 1)
        
        # 开始日期
        layout.addWidget(QLabel("开始日期:"), 2, 0)
        self.start_date_input = QLineEdit(self.default_start_date)
        layout.addWidget(self.start_date_input, 2, 1)
        
        # 结束日期
        layout.addWidget(QLabel("结束日期:"), 3, 0)
        self.end_date_input = QLineEdit(self.default_end_date)
        layout.addWidget(self.end_date_input, 3, 1)
        
        # 数据源
        layout.addWidget(QLabel("数据源:"), 4, 0)
        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems(['akshare', 'tushare', 'futu', 'yfinance'])
        self.data_source_combo.setCurrentText(self.default_data_source)
        self.data_source_combo.currentIndexChanged.connect(self.on_data_source_changed)
        layout.addWidget(self.data_source_combo, 4, 1)
        
        # Tushare Token输入框（动态显示）
        layout.addWidget(QLabel("Tushare Token:"), 5, 0)
        self.tushare_token_input = QLineEdit()
        self.tushare_token_input.setPlaceholderText("仅使用tushare时需要")
        self.tushare_token_input.setEchoMode(QLineEdit.Password)
        self.tushare_token_input.setVisible(False)
        layout.addWidget(self.tushare_token_input, 5, 1)
        
        # Futu提示标签（动态显示）
        self.futu_hint_label = QLabel("⚠️ 需要启动Futu OpenD (端口11111)")
        self.futu_hint_label.setStyleSheet("color: #ff6600; font-size: 9pt;")
        self.futu_hint_label.setVisible(False)
        layout.addWidget(self.futu_hint_label, 6, 0, 1, 2)
        
        group.setLayout(layout)
        return group
    
    def create_strategy_config(self):
        """创建策略配置组"""
        group = QGroupBox("💡 策略配置")
        layout = QGridLayout()
        
        # 策略选择
        layout.addWidget(QLabel("策略类型:"), 0, 0)
        self.strategy_combo = QComboBox()
        strategies = [
            'DualMovingAverage',  # 双均线
            'MACD',               # MACD
            'BollingerBands',     # 布林带
            'RSI',                # RSI
            'KDJ',                # KDJ
            'TripleMovingAverage',# 三均线
            'Momentum',           # 动量
            'TurtleTrading',      # 海龟交易
            'MeanReversion',      # 均值回归
            'Combo'               # 组合策略
        ]
        self.strategy_combo.addItems(strategies)
        self.strategy_combo.setCurrentText(self.default_strategy)
        self.strategy_combo.currentIndexChanged.connect(self.on_strategy_changed)
        layout.addWidget(self.strategy_combo, 0, 1)
        
        # 策略说明标签
        self.strategy_desc_label = QLabel("")
        self.strategy_desc_label.setWordWrap(True)
        self.strategy_desc_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 8px;
                border-radius: 3px;
                color: #1565c0;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.strategy_desc_label, 1, 0, 1, 2)
        
        # === 双均线参数 ===
        self.ma_label1 = QLabel("短期均线:")
        layout.addWidget(self.ma_label1, 2, 0)
        self.short_window_spin = QSpinBox()
        self.short_window_spin.setRange(5, 60)
        self.short_window_spin.setValue(self.default_short_window)
        layout.addWidget(self.short_window_spin, 2, 1)
        
        self.ma_label2 = QLabel("长期均线:")
        layout.addWidget(self.ma_label2, 3, 0)
        self.long_window_spin = QSpinBox()
        self.long_window_spin.setRange(20, 200)
        self.long_window_spin.setValue(self.default_long_window)
        layout.addWidget(self.long_window_spin, 3, 1)
        
        # === MACD参数 ===
        self.macd_label1 = QLabel("MACD快线:")
        layout.addWidget(self.macd_label1, 4, 0)
        self.macd_fast_spin = QSpinBox()
        self.macd_fast_spin.setRange(5, 50)
        self.macd_fast_spin.setValue(12)
        layout.addWidget(self.macd_fast_spin, 4, 1)
        
        self.macd_label2 = QLabel("MACD慢线:")
        layout.addWidget(self.macd_label2, 5, 0)
        self.macd_slow_spin = QSpinBox()
        self.macd_slow_spin.setRange(10, 100)
        self.macd_slow_spin.setValue(26)
        layout.addWidget(self.macd_slow_spin, 5, 1)
        
        self.macd_label3 = QLabel("MACD信号线:")
        layout.addWidget(self.macd_label3, 6, 0)
        self.macd_signal_spin = QSpinBox()
        self.macd_signal_spin.setRange(3, 30)
        self.macd_signal_spin.setValue(9)
        layout.addWidget(self.macd_signal_spin, 6, 1)
        
        # === RSI参数 ===
        self.rsi_label1 = QLabel("RSI周期:")
        layout.addWidget(self.rsi_label1, 7, 0)
        self.rsi_period_spin = QSpinBox()
        self.rsi_period_spin.setRange(5, 30)
        self.rsi_period_spin.setValue(14)
        layout.addWidget(self.rsi_period_spin, 7, 1)
        
        self.rsi_label2 = QLabel("RSI超卖线:")
        layout.addWidget(self.rsi_label2, 8, 0)
        self.rsi_oversold_spin = QSpinBox()
        self.rsi_oversold_spin.setRange(10, 40)
        self.rsi_oversold_spin.setValue(30)
        layout.addWidget(self.rsi_oversold_spin, 8, 1)
        
        self.rsi_label3 = QLabel("RSI超买线:")
        layout.addWidget(self.rsi_label3, 9, 0)
        self.rsi_overbought_spin = QSpinBox()
        self.rsi_overbought_spin.setRange(60, 90)
        self.rsi_overbought_spin.setValue(70)
        layout.addWidget(self.rsi_overbought_spin, 9, 1)
        
        # === 布林带参数 ===
        self.bb_label1 = QLabel("布林带周期:")
        layout.addWidget(self.bb_label1, 10, 0)
        self.bb_period_spin = QSpinBox()
        self.bb_period_spin.setRange(10, 50)
        self.bb_period_spin.setValue(20)
        layout.addWidget(self.bb_period_spin, 10, 1)
        
        self.bb_label2 = QLabel("标准差倍数:")
        layout.addWidget(self.bb_label2, 11, 0)
        self.bb_std_spin = QDoubleSpinBox()
        self.bb_std_spin.setRange(1.0, 3.0)
        self.bb_std_spin.setSingleStep(0.1)
        self.bb_std_spin.setValue(2.0)
        layout.addWidget(self.bb_std_spin, 11, 1)
        
        # === KDJ参数 ===
        self.kdj_label1 = QLabel("KDJ N值:")
        layout.addWidget(self.kdj_label1, 12, 0)
        self.kdj_n_spin = QSpinBox()
        self.kdj_n_spin.setRange(5, 20)
        self.kdj_n_spin.setValue(9)
        layout.addWidget(self.kdj_n_spin, 12, 1)
        
        # === 动量策略参数 ===
        self.momentum_label1 = QLabel("动量周期:")
        layout.addWidget(self.momentum_label1, 13, 0)
        self.momentum_period_spin = QSpinBox()
        self.momentum_period_spin.setRange(10, 60)
        self.momentum_period_spin.setValue(20)
        layout.addWidget(self.momentum_period_spin, 13, 1)
        
        self.momentum_label2 = QLabel("动量阈值(%):")
        layout.addWidget(self.momentum_label2, 14, 0)
        self.momentum_threshold_spin = QDoubleSpinBox()
        self.momentum_threshold_spin.setRange(1.0, 20.0)
        self.momentum_threshold_spin.setSingleStep(1.0)
        self.momentum_threshold_spin.setValue(5.0)
        layout.addWidget(self.momentum_threshold_spin, 14, 1)
        
        # === 海龟交易参数 ===
        self.turtle_label1 = QLabel("入场周期:")
        layout.addWidget(self.turtle_label1, 15, 0)
        self.turtle_entry_spin = QSpinBox()
        self.turtle_entry_spin.setRange(10, 55)
        self.turtle_entry_spin.setValue(20)
        layout.addWidget(self.turtle_entry_spin, 15, 1)
        
        self.turtle_label2 = QLabel("出场周期:")
        layout.addWidget(self.turtle_label2, 16, 0)
        self.turtle_exit_spin = QSpinBox()
        self.turtle_exit_spin.setRange(5, 30)
        self.turtle_exit_spin.setValue(10)
        layout.addWidget(self.turtle_exit_spin, 16, 1)
        
        group.setLayout(layout)
        
        # 初始化显示
        self.on_strategy_changed()
        
        return group
    
    def on_strategy_changed(self):
        """策略切换时更新参数显示"""
        strategy = self.strategy_combo.currentText()
        
        # 策略说明
        strategy_descriptions = {
            'DualMovingAverage': '📊 双均线策略 - 适合趋势市场 (5-30天)',
            'MACD': '📈 MACD策略 - 趋势+动量 (3-15天)',
            'BollingerBands': '📉 布林带策略 - 震荡市场 (5-20天)',
            'RSI': '🎯 RSI策略 - 超买超卖 (3-14天)',
            'KDJ': '⚡ KDJ策略 - 短线高手 (3-10天)',
            'TripleMovingAverage': '📊 三均线策略 - 稳健长期 (20-60天)',
            'Momentum': '🚀 动量策略 - 追涨牛市 (20-60天)',
            'TurtleTrading': '🐢 海龟交易 - 趋势跟随 (20-55天)',
            'MeanReversion': '↩️ 均值回归 - 震荡市场 (10-30天)',
            'Combo': '🎭 组合策略 - MACD+RSI双重确认 (10-30天)'
        }
        self.strategy_desc_label.setText(strategy_descriptions.get(strategy, ''))
        
        # 隐藏所有参数
        for widget in [
            self.ma_label1, self.ma_label2, self.short_window_spin, self.long_window_spin,
            self.macd_label1, self.macd_label2, self.macd_label3,
            self.macd_fast_spin, self.macd_slow_spin, self.macd_signal_spin,
            self.rsi_label1, self.rsi_label2, self.rsi_label3,
            self.rsi_period_spin, self.rsi_oversold_spin, self.rsi_overbought_spin,
            self.bb_label1, self.bb_label2, self.bb_period_spin, self.bb_std_spin,
            self.kdj_label1, self.kdj_n_spin,
            self.momentum_label1, self.momentum_label2, 
            self.momentum_period_spin, self.momentum_threshold_spin,
            self.turtle_label1, self.turtle_label2,
            self.turtle_entry_spin, self.turtle_exit_spin
        ]:
            widget.setVisible(False)
        
        # 根据策略显示相应参数
        if strategy == 'DualMovingAverage':
            self.ma_label1.setVisible(True)
            self.ma_label2.setVisible(True)
            self.short_window_spin.setVisible(True)
            self.long_window_spin.setVisible(True)
        
        elif strategy == 'MACD':
            self.macd_label1.setVisible(True)
            self.macd_label2.setVisible(True)
            self.macd_label3.setVisible(True)
            self.macd_fast_spin.setVisible(True)
            self.macd_slow_spin.setVisible(True)
            self.macd_signal_spin.setVisible(True)
        
        elif strategy == 'BollingerBands':
            self.bb_label1.setVisible(True)
            self.bb_label2.setVisible(True)
            self.bb_period_spin.setVisible(True)
            self.bb_std_spin.setVisible(True)
        
        elif strategy == 'RSI':
            self.rsi_label1.setVisible(True)
            self.rsi_label2.setVisible(True)
            self.rsi_label3.setVisible(True)
            self.rsi_period_spin.setVisible(True)
            self.rsi_oversold_spin.setVisible(True)
            self.rsi_overbought_spin.setVisible(True)
        
        elif strategy == 'KDJ':
            self.kdj_label1.setVisible(True)
            self.kdj_n_spin.setVisible(True)
        
        elif strategy == 'TripleMovingAverage':
            self.ma_label1.setText("短期均线:")
            self.ma_label2.setText("中期均线:")
            self.ma_label1.setVisible(True)
            self.ma_label2.setVisible(True)
            self.short_window_spin.setVisible(True)
            self.long_window_spin.setVisible(True)
            # 调整范围
            self.short_window_spin.setRange(3, 20)
            self.short_window_spin.setValue(5)
            self.long_window_spin.setRange(10, 120)
            self.long_window_spin.setValue(60)
        
        elif strategy == 'Momentum':
            self.momentum_label1.setVisible(True)
            self.momentum_label2.setVisible(True)
            self.momentum_period_spin.setVisible(True)
            self.momentum_threshold_spin.setVisible(True)
        
        elif strategy == 'TurtleTrading':
            self.turtle_label1.setVisible(True)
            self.turtle_label2.setVisible(True)
            self.turtle_entry_spin.setVisible(True)
            self.turtle_exit_spin.setVisible(True)
        
        elif strategy == 'MeanReversion':
            self.ma_label1.setText("回看周期:")
            self.ma_label1.setVisible(True)
            self.short_window_spin.setVisible(True)
            self.short_window_spin.setRange(10, 50)
            self.short_window_spin.setValue(20)
        
        elif strategy == 'Combo':
            # 组合策略显示MACD和RSI参数
            self.macd_label1.setVisible(True)
            self.macd_label2.setVisible(True)
            self.macd_label3.setVisible(True)
            self.macd_fast_spin.setVisible(True)
            self.macd_slow_spin.setVisible(True)
            self.macd_signal_spin.setVisible(True)
            self.rsi_label1.setVisible(True)
            self.rsi_label2.setVisible(True)
            self.rsi_label3.setVisible(True)
            self.rsi_period_spin.setVisible(True)
            self.rsi_oversold_spin.setVisible(True)
            self.rsi_overbought_spin.setVisible(True)
    
    def create_backtest_config(self):
        """创建回测配置组"""
        group = QGroupBox("⚙️ 回测配置")
        layout = QGridLayout()
        
        # 初始资金
        layout.addWidget(QLabel("初始资金:"), 0, 0)
        self.capital_spin = QSpinBox()
        self.capital_spin.setRange(10000, 10000000)
        self.capital_spin.setSingleStep(10000)
        self.capital_spin.setValue(self.default_initial_capital)
        layout.addWidget(self.capital_spin, 0, 1)
        
        # 手续费率
        layout.addWidget(QLabel("手续费率‰:"), 1, 0)
        self.commission_spin = QDoubleSpinBox()
        self.commission_spin.setRange(0.01, 10.0)
        self.commission_spin.setSingleStep(0.01)
        self.commission_spin.setDecimals(2)
        self.commission_spin.setValue(self.default_commission_rate)
        layout.addWidget(self.commission_spin, 1, 1)
        
        # 仓位比例
        layout.addWidget(QLabel("仓位比例:"), 2, 0)
        self.position_spin = QDoubleSpinBox()
        self.position_spin.setRange(0.1, 1.0)
        self.position_spin.setSingleStep(0.1)
        self.position_spin.setValue(self.default_position_size)
        layout.addWidget(self.position_spin, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def create_chart_panel(self):
        """创建图表显示面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        title = QLabel("📈 回测图表")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # 保存图表按钮
        save_btn = QPushButton("💾 保存当前图表")
        save_btn.clicked.connect(self.save_chart)
        save_btn.setMaximumWidth(150)
        title_layout.addWidget(save_btn)
        
        layout.addLayout(title_layout)
        
        # 创建图表标签页
        self.chart_tabs = QTabWidget()
        
        # 标签页1: 价格走势与交易信号
        self.price_chart_widget = pg.GraphicsLayoutWidget()
        self.chart_tabs.addTab(self.price_chart_widget, "📊 价格走势与交易信号")
        
        # 标签页2: 资产曲线对比
        self.portfolio_chart_widget = pg.GraphicsLayoutWidget()
        self.chart_tabs.addTab(self.portfolio_chart_widget, "💰 资产曲线对比")
        
        # 标签页3: 回撤分析
        self.drawdown_chart_widget = pg.GraphicsLayoutWidget()
        self.chart_tabs.addTab(self.drawdown_chart_widget, "📉 回撤分析")
        
        layout.addWidget(self.chart_tabs)
        
        return panel
    
    def create_result_tabs(self):
        """创建结果标签页（性能指标、交易记录、大盘指数）"""
        # 标签页
        self.result_tabs = QTabWidget()
        
        # Tab 1: 性能指标
        metrics_widget = QWidget()
        metrics_layout = QVBoxLayout()
        metrics_widget.setLayout(metrics_layout)
        
        metrics_title = QLabel("📊 性能指标")
        metrics_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        metrics_layout.addWidget(metrics_title)
        
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        self.metrics_text.setFont(QFont("Courier New", 9))
        metrics_layout.addWidget(self.metrics_text)
        
        self.result_tabs.addTab(metrics_widget, "📊 性能指标")
        
        # Tab 2: 交易记录
        trades_widget = QWidget()
        trades_layout = QVBoxLayout()
        trades_widget.setLayout(trades_layout)
        
        trades_title = QLabel("📝 交易记录")
        trades_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        trades_layout.addWidget(trades_title)
        
        self.trades_text = QTextEdit()
        self.trades_text.setReadOnly(True)
        self.trades_text.setFont(QFont("Courier New", 8))
        trades_layout.addWidget(self.trades_text)
        
        self.result_tabs.addTab(trades_widget, "📝 交易记录")
        
        # Tab 3: 策略对比
        compare_widget = QWidget()
        compare_layout = QVBoxLayout()
        compare_widget.setLayout(compare_layout)
        
        compare_title = QLabel("📊 策略对比结果")
        compare_title.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        compare_layout.addWidget(compare_title)
        
        self.compare_text = QTextEdit()
        self.compare_text.setReadOnly(True)
        self.compare_text.setFont(QFont("Courier New", 9))
        self.compare_text.setText("点击'对比所有策略'按钮开始批量回测...")
        compare_layout.addWidget(self.compare_text)
        
        self.result_tabs.addTab(compare_widget, "📊 策略对比")
        
        # Tab 4: 大盘指数
        self.market_widget = self.create_market_panel()
        self.result_tabs.addTab(self.market_widget, "🌍 大盘指数")
        
        return self.result_tabs
    
    def on_data_source_changed(self, index):
        """数据源切换时更新UI"""
        data_source = self.data_source_combo.currentText()
        
        # 根据数据源显示/隐藏相关配置
        if data_source == 'tushare':
            self.tushare_token_input.setVisible(True)
            self.futu_hint_label.setVisible(False)
        elif data_source == 'futu':
            self.tushare_token_input.setVisible(False)
            self.futu_hint_label.setVisible(True)
        else:
            self.tushare_token_input.setVisible(False)
            self.futu_hint_label.setVisible(False)
    
    def run_backtest(self):
        """运行回测"""
        # 禁用按钮
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 提取纯股票代码（处理可能包含名称的情况）
        ticker_text = self.ticker_input.text().strip()
        if ' - ' in ticker_text:
            ticker_code = ticker_text.split(' - ')[0].strip()
        else:
            ticker_code = ticker_text
        
        # 收集配置
        data_source = self.data_source_combo.currentText()
        strategy_name = self.strategy_combo.currentText()
        
        # 构建策略参数
        strategy_config = {
            'strategy_name': strategy_name,
            # 双均线/三均线参数
            'short_window': self.short_window_spin.value(),
            'long_window': self.long_window_spin.value(),
            # MACD参数
            'macd_fast': self.macd_fast_spin.value(),
            'macd_slow': self.macd_slow_spin.value(),
            'macd_signal': self.macd_signal_spin.value(),
            # RSI参数
            'rsi_period': self.rsi_period_spin.value(),
            'rsi_oversold': self.rsi_oversold_spin.value(),
            'rsi_overbought': self.rsi_overbought_spin.value(),
            # 布林带参数
            'bb_period': self.bb_period_spin.value(),
            'bb_std': self.bb_std_spin.value(),
            # KDJ参数
            'kdj_n': self.kdj_n_spin.value(),
            'kdj_m1': 3,
            'kdj_m2': 3,
            'kdj_oversold': 20,
            'kdj_overbought': 80,
            # 三均线参数
            'triple_ma_short': self.short_window_spin.value() if strategy_name == 'TripleMovingAverage' else 5,
            'triple_ma_medium': 20,
            'triple_ma_long': self.long_window_spin.value() if strategy_name == 'TripleMovingAverage' else 60,
            # 动量策略参数
            'momentum_period': self.momentum_period_spin.value(),
            'momentum_threshold': self.momentum_threshold_spin.value() / 100,  # 转换为小数
            # 海龟交易参数
            'turtle_entry': self.turtle_entry_spin.value(),
            'turtle_exit': self.turtle_exit_spin.value(),
            # 均值回归参数
            'mean_reversion_period': self.short_window_spin.value() if strategy_name == 'MeanReversion' else 20,
            'mean_reversion_std': 2,
        }
        
        config = {
            'data': {
                'tickers': [ticker_code],
                'start_date': self.start_date_input.text(),
                'end_date': self.end_date_input.text(),
                'data_source': data_source,
                'use_cache': True,
                'cache_dir': './data/cache',
                # Tushare配置
                'tushare_token': self.tushare_token_input.text() if data_source == 'tushare' else '',
                # Futu配置
                'futu_host': '127.0.0.1',
                'futu_port': 11111,
            },
            'strategy': strategy_config,
            'backtest': {
                'initial_capital': self.capital_spin.value(),
                'commission_rate': self.commission_spin.value() / 1000,  # 转换为小数
                'stamp_duty_rate': 0.001,
                'slippage': 0.0001,
                'position_size': self.position_spin.value(),
            },
            'analysis': {
                'risk_free_rate': 0.03,
                'benchmark': '000300.SH',
                'output_dir': './output',
                'save_plots': True,
            }
        }
        
        # 创建并启动线程
        self.backtest_thread = BacktestThread(config)
        self.backtest_thread.progress_update.connect(self.update_status)
        self.backtest_thread.result_ready.connect(self.show_results)
        self.backtest_thread.error_occurred.connect(self.show_error)
        self.backtest_thread.start()
    
    def update_status(self, message):
        """更新状态"""
        self.status_label.setText(message)
    
    def show_results(self, result):
        """显示结果"""
        self.result_data = result
        
        # 显示性能指标
        metrics = result['metrics']
        metrics_text = "="*60 + "\n"
        metrics_text += "📊 回测性能报告\n"
        metrics_text += "="*60 + "\n\n"
        
        metrics_text += "💰 资金情况:\n"
        metrics_text += f"  初始资金: ¥{metrics['初始资金']:,.2f}\n"
        metrics_text += f"  最终资金: ¥{metrics['最终资金']:,.2f}\n"
        metrics_text += f"  总收益: ¥{metrics['总收益']:,.2f}\n\n"
        
        metrics_text += "📈 收益指标:\n"
        metrics_text += f"  总收益率: {metrics['总收益率']*100:.2f}%\n"
        metrics_text += f"  年化收益率: {metrics['年化收益率']*100:.2f}%\n\n"
        
        metrics_text += "📉 风险指标:\n"
        metrics_text += f"  日波动率: {metrics['日波动率']*100:.2f}%\n"
        metrics_text += f"  年化波动率: {metrics['年化波动率']*100:.2f}%\n"
        metrics_text += f"  最大回撤: {metrics['最大回撤']*100:.2f}%\n"
        metrics_text += f"  最大回撤持续: {metrics['最大回撤持续天数']} 天\n\n"
        
        metrics_text += "⚖️ 风险调整收益:\n"
        metrics_text += f"  夏普比率: {metrics['夏普比率']:.3f}\n"
        metrics_text += f"  卡玛比率: {metrics['卡玛比率']:.3f}\n\n"
        
        metrics_text += "🎯 交易统计:\n"
        metrics_text += f"  胜率: {metrics['胜率']*100:.2f}%\n"
        metrics_text += f"  盈亏比: {metrics['盈亏比']:.3f}\n"
        
        self.metrics_text.setText(metrics_text)
        
        # 显示交易记录
        trades_df = result['trades_df']
        if not trades_df.empty:
            self.trades_text.setText(trades_df.to_string())
        else:
            self.trades_text.setText("无交易记录")
        
        # 绘制图表
        self.plot_results(result)
        
        # 恢复按钮
        self.run_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ 回测完成！")
        
        # 弹出完成对话框
        QMessageBox.information(self, "完成", "回测已完成！请查看结果标签页。")
    
    def show_error(self, error_msg):
        """显示错误"""
        self.run_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ 错误: {error_msg}")
        QMessageBox.critical(self, "错误", f"回测失败:\n{error_msg}")
    
    def plot_results(self, result):
        """使用PyQtGraph绘制结果图表"""
        # 清空之前的图表
        self.price_chart_widget.clear()
        self.portfolio_chart_widget.clear()
        self.drawdown_chart_widget.clear()
        
        portfolio_df = result['portfolio_df']
        trades_df = result['trades_df']
        
        # 转换日期为时间戳（用于绘图）
        dates = portfolio_df.index
        # 将日期转为时间戳（秒）
        date_nums = dates.astype('int64') // 10**9  # 转换为Unix时间戳
        
        # 导入日期轴
        from pyqtgraph import DateAxisItem
        
        # ==================== 图表1: 价格走势与交易信号 ====================
        p1 = self.price_chart_widget.addPlot(title='价格走势与交易信号')
        p1.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        
        # 绘制收盘价
        p1.plot(date_nums, portfolio_df['Close'].values, pen=pg.mkPen('k', width=2), name='收盘价')
        
        # 绘制均线
        if 'MA_Short' in portfolio_df.columns:
            p1.plot(date_nums, portfolio_df['MA_Short'].values, pen=pg.mkPen('b', width=1.5), name='短期均线')
        
        if 'MA_Long' in portfolio_df.columns:
            p1.plot(date_nums, portfolio_df['MA_Long'].values, pen=pg.mkPen('r', width=1.5), name='长期均线')
        
        # 标记买卖点
        if not trades_df.empty:
            buys = trades_df[trades_df['action'] == 'BUY']
            sells = trades_df[trades_df['action'].str.startswith('SELL')]
            
            if not buys.empty:
                buy_timestamps = []
                buy_prices_list = []
                for _, trade in buys.iterrows():
                    if trade['date'] in dates:
                        idx = np.where(dates == trade['date'])[0][0]
                        buy_timestamps.append(date_nums[idx])
                        buy_prices_list.append(trade['price'])
                
                if buy_timestamps:
                    p1.plot(buy_timestamps, buy_prices_list, pen=None, symbol='t', symbolPen=None, 
                           symbolBrush='r', symbolSize=12, name='买入')
            
            if not sells.empty:
                sell_timestamps = []
                sell_prices_list = []
                for _, trade in sells.iterrows():
                    if trade['date'] in dates:
                        idx = np.where(dates == trade['date'])[0][0]
                        sell_timestamps.append(date_nums[idx])
                        sell_prices_list.append(trade['price'])
                
                if sell_timestamps:
                    p1.plot(sell_timestamps, sell_prices_list, pen=None, symbol='t1', symbolPen=None,
                           symbolBrush='g', symbolSize=12, name='卖出')
        
        p1.setLabel('bottom', '时间')
        p1.setLabel('left', '价格 (元)')
        p1.addLegend()
        p1.showGrid(x=True, y=True, alpha=0.3)
        
        # ==================== 图表2: 资产曲线对比 ====================
        p2 = self.portfolio_chart_widget.addPlot(title='资产曲线对比')
        p2.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        
        initial_value = portfolio_df['portfolio_value'].iloc[0]
        initial_price = portfolio_df['Close'].iloc[0]
        buy_hold_value = (portfolio_df['Close'] / initial_price) * initial_value
        
        p2.plot(date_nums, portfolio_df['portfolio_value'].values, 
               pen=pg.mkPen('b', width=2), name='策略收益')
        p2.plot(date_nums, buy_hold_value.values, 
               pen=pg.mkPen('gray', width=1, style=Qt.DashLine), name='买入持有')
        
        # 使用半透明背景色
        p2.getViewBox().setBackgroundColor((200, 220, 255, 30))
        
        p2.setLabel('bottom', '时间')
        p2.setLabel('left', '资产价值 (元)')
        p2.addLegend()
        p2.showGrid(x=True, y=True, alpha=0.3)
        
        # ==================== 图表3: 回撤分析 ====================
        p3 = self.drawdown_chart_widget.addPlot(title='回撤分析')
        p3.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
        
        portfolio_values = portfolio_df['portfolio_value']
        cumulative_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cumulative_max) / cumulative_max * 100
        
        p3.plot(date_nums, drawdown.values, pen=pg.mkPen('r', width=2), name='回撤')
        
        # 填充回撤区域
        p3.getViewBox().setBackgroundColor((255, 200, 200, 30))
        
        # 标记最大回撤点
        max_dd_idx = drawdown.idxmin()
        max_dd_value = drawdown.min()
        max_dd_pos_index = np.where(dates == max_dd_idx)[0][0]
        max_dd_timestamp = date_nums[max_dd_pos_index]
        p3.plot([max_dd_timestamp], [max_dd_value], pen=None, symbol='o', 
               symbolPen=None, symbolBrush='darkred', symbolSize=10)
        
        p3.setLabel('bottom', '时间')
        p3.setLabel('left', '回撤 (%)')
        p3.addLegend()
        p3.showGrid(x=True, y=True, alpha=0.3)
    
    def save_chart(self):
        """保存当前显示的图表"""
        if self.result_data is None:
            QMessageBox.warning(self, "警告", "还没有回测结果可保存！")
            return
        
        # 获取当前标签页索引
        current_index = self.chart_tabs.currentIndex()
        
        # 根据索引选择对应的图表组件
        if current_index == 0:
            chart_widget = self.price_chart_widget
            default_name = "价格走势图"
        elif current_index == 1:
            chart_widget = self.portfolio_chart_widget
            default_name = "资产曲线图"
        else:
            chart_widget = self.drawdown_chart_widget
            default_name = "回撤分析图"
        
        # 文件对话框
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存图表", f"{default_name}.png", "PNG Files (*.png);;All Files (*)"
        )
        
        if filename:
            # 使用PyQtGraph的导出功能
            exporter = ImageExporter(chart_widget.scene())
            exporter.parameters()['width'] = 1920  # 设置宽度
            exporter.export(filename)
            QMessageBox.information(self, "成功", f"图表已保存到:\n{filename}")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 设置菜单栏字体（确保中文显示）
        menubar.setFont(QFont("Microsoft YaHei", 10))
        
        # 文件菜单
        file_menu = menubar.addMenu('📁 文件')
        
        # 保存配置
        save_config_action = QAction('💾 保存配置', self)
        save_config_action.setShortcut('Ctrl+S')
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)
        
        # 加载配置
        load_config_action = QAction('📂 加载配置', self)
        load_config_action.setShortcut('Ctrl+O')
        load_config_action.triggered.connect(self.load_config)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        # 导出报告
        export_action = QAction('📄 导出报告', self)
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('🚪 退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('⚙️ 设置')
        
        # 清理缓存
        clear_cache_action = QAction('🗑️ 清理缓存', self)
        clear_cache_action.triggered.connect(self.clear_cache)
        settings_menu.addAction(clear_cache_action)
        
        settings_menu.addSeparator()
        
        # 字体设置
        font_action = QAction('🔤 字体设置', self)
        font_action.triggered.connect(self.font_settings)
        settings_menu.addAction(font_action)
        
        # 主题设置
        theme_action = QAction('🎨 主题设置', self)
        theme_action.triggered.connect(self.theme_settings)
        settings_menu.addAction(theme_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('👁️ 视图')
        
        # 显示配置面板
        self.show_config_action = QAction('显示配置面板', self, checkable=True)
        self.show_config_action.setChecked(True)
        self.show_config_action.triggered.connect(self.toggle_config_panel)
        view_menu.addAction(self.show_config_action)
        
        view_menu.addSeparator()
        
        # 全屏
        fullscreen_action = QAction('🖥️ 全屏', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('❓ 帮助')
        
        # 使用手册
        manual_action = QAction('📖 使用手册', self)
        manual_action.setShortcut('F1')
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        # 关于
        about_action = QAction('ℹ️ 关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 版本信息
        version_action = QAction('📌 版本信息', self)
        version_action.triggered.connect(self.show_version)
        help_menu.addAction(version_action)
    
    def save_config(self):
        """保存配置"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "保存配置", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            import json
            config = {
                'ticker': self.ticker_input.text(),
                'start_date': self.start_date_input.text(),
                'end_date': self.end_date_input.text(),
                'data_source': self.data_source_combo.currentText(),
                'strategy': self.strategy_combo.currentText(),
                'short_window': self.short_window_spin.value(),
                'long_window': self.long_window_spin.value(),
                'initial_capital': self.capital_spin.value(),
                'commission_rate': self.commission_spin.value(),
                'position_size': self.position_spin.value(),
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", "配置已保存！")
    
    def load_config(self):
        """加载配置"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "加载配置", "", "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            import json
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.ticker_input.setText(config.get('ticker', ''))
                self.start_date_input.setText(config.get('start_date', ''))
                self.end_date_input.setText(config.get('end_date', ''))
                self.data_source_combo.setCurrentText(config.get('data_source', 'yfinance'))
                self.strategy_combo.setCurrentText(config.get('strategy', 'DualMovingAverage'))
                self.short_window_spin.setValue(config.get('short_window', 10))
                self.long_window_spin.setValue(config.get('long_window', 30))
                self.capital_spin.setValue(config.get('initial_capital', 100000))
                self.commission_spin.setValue(config.get('commission_rate', 0.3))
                self.position_spin.setValue(config.get('position_size', 1.0))
                
                QMessageBox.information(self, "成功", "配置已加载！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置失败:\n{str(e)}")
    
    def export_report(self):
        """导出报告"""
        if self.result_data is None:
            QMessageBox.warning(self, "警告", "还没有回测结果可导出！")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出报告", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.metrics_text.toPlainText())
                f.write("\n\n" + "="*60 + "\n")
                f.write("交易记录:\n")
                f.write("="*60 + "\n\n")
                f.write(self.trades_text.toPlainText())
            QMessageBox.information(self, "成功", "报告已导出！")
    
    def clear_cache(self):
        """清理缓存"""
        reply = QMessageBox.question(
            self, '确认', 
            '确定要清理所有缓存数据吗？\n下次运行将重新下载数据。',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import shutil
            cache_dir = './data/cache'
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir)
                QMessageBox.information(self, "成功", "缓存已清理！")
            else:
                QMessageBox.information(self, "提示", "缓存目录不存在。")
    
    def font_settings(self):
        """字体设置"""
        from PyQt5.QtWidgets import QFontDialog
        
        font, ok = QFontDialog.getFont(self.font(), self)
        if ok:
            self.setFont(font)
            QMessageBox.information(self, "成功", "字体已更新！")
    
    def theme_settings(self):
        """主题设置"""
        from PyQt5.QtWidgets import QInputDialog
        
        themes = ['Fusion', 'Windows', 'WindowsVista']
        theme, ok = QInputDialog.getItem(
            self, '主题设置', '选择主题:', themes, 0, False
        )
        
        if ok and theme:
            QApplication.setStyle(theme)
            QMessageBox.information(self, "成功", f"主题已切换到: {theme}")
    
    def toggle_config_panel(self, checked):
        """切换配置面板显示"""
        # 这个功能需要保存对splitter的引用，暂时简化处理
        QMessageBox.information(self, "提示", "配置面板切换功能开发中...")
    
    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_manual(self):
        """显示使用手册"""
        manual_text = """
📖 快速使用手册

1. 配置参数
   - 在左侧面板输入股票代码、日期范围
   - 选择策略类型和参数
   - 设置资金和费率

2. 开始回测
   - 点击"开始回测"按钮
   - 等待进度完成

3. 查看结果
   - 性能指标：查看收益和风险指标
   - 交易记录：查看所有交易详情
   - 可视化图表：查看价格走势和资产曲线

4. 保存结果
   - 在图表标签页点击"保存图表"
   - 或通过"文件 → 导出报告"保存文字报告

快捷键:
  Ctrl+S - 保存配置
  Ctrl+O - 加载配置
  Ctrl+Q - 退出程序
  F1 - 显示帮助
  F11 - 全屏

更多详情请查看项目文档：docs/GUI_GUIDE.md
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("使用手册")
        msg.setText(manual_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
🚀 量化交易回测系统

版本: 1.0.0
界面: PyQtGraph

一个专业的、模块化的股票量化交易回测系统

特性:
• 模块化架构 - 五层设计
• 配置驱动 - 灵活易用
• 多数据源支持
• 专业性能分析
• 图形化界面

开发: SpeedBroker Team
许可: 仅供学习研究使用

⚠️ 免责声明:
本系统仅用于教育和研究目的。
历史回测结果不代表未来收益。
实际交易前请充分了解市场风险。
        """
        
        QMessageBox.about(self, "关于", about_text)
    
    def load_default_config(self):
        """从配置文件加载默认值"""
        if config_manager:
            # 获取默认股票信息
            self.default_ticker, self.default_ticker_name = config_manager.get_default_ticker_info()
            
            # 获取数据配置
            data_config = config_manager.get_data_config()
            self.default_start_date = data_config['start_date']
            self.default_end_date = data_config['end_date']
            self.default_data_source = data_config['data_source']
            
            # 获取策略配置
            strategy_config = config_manager.get_strategy_config()
            self.default_strategy = strategy_config['strategy_name']
            self.default_short_window = strategy_config['short_window']
            self.default_long_window = strategy_config['long_window']
            
            # 获取回测配置
            backtest_config = config_manager.get_backtest_config()
            self.default_initial_capital = backtest_config['initial_capital']
            self.default_commission_rate = backtest_config['commission_rate'] * 1000  # 转换回千分比显示
            self.default_position_size = backtest_config['position_size']
        else:
            # 使用后备默认值
            self.default_ticker = "000001.SZ"
            self.default_ticker_name = "平安银行"
            self.default_start_date = "2023-01-01"
            self.default_end_date = "2024-10-01"
            self.default_data_source = "akshare"
            self.default_strategy = "DualMovingAverage"
            self.default_short_window = 10
            self.default_long_window = 30
            self.default_initial_capital = 100000
            self.default_commission_rate = 0.3
            self.default_position_size = 1.0
    
    def show_version(self):
        """显示版本信息"""
        version_info = """
📌 系统版本信息

系统版本: v1.0.0
发布日期: 2025-10-30

组件版本:
• Python: """ + sys.version.split()[0] + """
• PyQt5: 5.15.0+
• PyQtGraph: 0.13.0+
• pandas: 2.0.0+
• numpy: """ + np.__version__ + """

图表引擎: PyQtGraph
数据源: yfinance / akshare

更新日志:
v1.0.0 (2025-10-30)
  - 首次发布
  - 实现双均线和RSI策略
  - 支持PyQtGraph图表
  - 添加菜单栏功能
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("版本信息")
        msg.setText(version_info)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
    
    def on_stock_selected(self, text):
        """处理股票选择事件"""
        # 从 "000001.SZ - 平安银行" 中提取 "000001.SZ"
        if ' - ' in text:
            code = text.split(' - ')[0].strip()
            name = text.split(' - ')[1].strip()
            
            # 只填入代码部分
            self.ticker_input.setText(code)
            
            # 在信息框显示完整信息
            self.stock_info_label.setText(f"{code} - {name}")
        else:
            # 如果没有名称，直接填入
            self.ticker_input.setText(text.strip())
            self.stock_info_label.setText(text.strip())
    
    def create_market_panel(self):
        """创建大盘指数面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 标题和按钮行
        title_layout = QHBoxLayout()
        
        title = QLabel("🌍 全球主要指数走势")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新指数数据")
        refresh_btn.clicked.connect(self.load_market_indices)
        title_layout.addWidget(refresh_btn)
        
        layout.addLayout(title_layout)
        
        # 指数选择按钮组
        button_layout = QHBoxLayout()
        
        self.index_buttons = []
        indices = [
            ("A股", ["000001.SH|上证指数", "399001.SZ|深证成指", "000300.SH|沪深300"]),
            ("美股", ["^GSPC|标普500", "^DJI|道琼斯", "^IXIC|纳斯达克"]),
            ("港股", ["^HSI|恒生指数", "^HSCE|国企指数"]),
        ]
        
        for market_name, _ in indices:
            btn = QPushButton(f"📊 {market_name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=market_name: self.show_market_indices(m))
            button_layout.addWidget(btn)
            self.index_buttons.append(btn)
        
        # 默认选中A股
        self.index_buttons[0].setChecked(True)
        
        layout.addLayout(button_layout)
        
        # 图表区域
        self.market_graphics = pg.GraphicsLayoutWidget()
        layout.addWidget(self.market_graphics)
        
        # 加载默认数据
        self.current_market = "A股"
        self.market_indices_data = {}
        
        return panel
    
    def load_market_indices(self):
        """加载指数数据"""
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            # 获取最近1年的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            indices = {
                "A股": {
                    "000001.SS": "上证指数",  # yfinance中A股指数用.SS
                    "399001.SZ": "深证成指",
                    "000300.SS": "沪深300",
                },
                "美股": {
                    "^GSPC": "标普500",
                    "^DJI": "道琼斯",
                    "^IXIC": "纳斯达克",
                },
                "港股": {
                    "^HSI": "恒生指数",
                    "0700.HK": "腾讯控股",
                    "9988.HK": "阿里巴巴",
                },
            }
            
            self.market_indices_data = {}
            
            for market, codes in indices.items():
                self.market_indices_data[market] = {}
                for code, name in codes.items():
                    try:
                        data = yf.download(code, start=start_date, end=end_date, progress=False)
                        if not data.empty:
                            # 确保Close是Series而不是DataFrame
                            close_data = data['Close']
                            if hasattr(close_data, 'iloc'):  # 是Series或DataFrame
                                if len(close_data.shape) > 1:  # DataFrame
                                    close_data = close_data.iloc[:, 0]  # 取第一列
                            self.market_indices_data[market][name] = close_data
                    except Exception as e:
                        print(f"  获取{name}失败: {e}")
                        pass
            
            # 显示当前选中的市场
            self.show_market_indices(self.current_market)
            
            QMessageBox.information(self, "成功", "指数数据已更新！")
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载指数数据失败:\n{str(e)}")
    
    def show_market_indices(self, market_name):
        """显示指定市场的指数"""
        self.current_market = market_name
        
        # 更新按钮状态
        for i, (name, _) in enumerate([("A股", []), ("美股", []), ("港股", [])]):
            self.index_buttons[i].setChecked(name == market_name)
        
        # 如果还没有数据，先加载
        if not self.market_indices_data:
            self.load_market_indices()
            return
        
        # 清空图表
        self.market_graphics.clear()
        
        # 获取该市场的数据
        if market_name not in self.market_indices_data:
            return
        
        market_data = self.market_indices_data[market_name]
        
        if not market_data:
            return
        
        # 绘制指数
        plot = self.market_graphics.addPlot(title=f'{market_name}主要指数走势')
        plot.setAxisItems({'bottom': pg.DateAxisItem(orientation='bottom')})
        
        colors = ['b', 'r', 'g', 'm', 'c']
        
        for i, (name, data) in enumerate(market_data.items()):
            if not data.empty:
                # 转换为时间戳
                timestamps = data.index.astype('int64') // 10**9
                # 归一化（以首日为100）
                normalized = (data / data.iloc[0]) * 100
                
                plot.plot(timestamps, normalized.values, 
                         pen=pg.mkPen(colors[i % len(colors)], width=2),
                         name=f'{name}')
        
        plot.setLabel('bottom', '日期')
        plot.setLabel('left', '相对涨跌 (首日=100)')
        plot.addLegend()
        plot.showGrid(x=True, y=True, alpha=0.3)
    
    def compare_all_strategies(self):
        """对比所有策略"""
        # 禁用按钮
        self.run_button.setEnabled(False)
        self.compare_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # 提取股票代码
        ticker_text = self.ticker_input.text().strip()
        if ' - ' in ticker_text:
            ticker_code = ticker_text.split(' - ')[0].strip()
        else:
            ticker_code = ticker_text
        
        # 收集配置
        data_source = self.data_source_combo.currentText()
        config = {
            'data': {
                'tickers': [ticker_code],
                'start_date': self.start_date_input.text(),
                'end_date': self.end_date_input.text(),
                'data_source': data_source,
                'use_cache': True,
                'cache_dir': './data/cache',
                'tushare_token': self.tushare_token_input.text() if data_source == 'tushare' else '',
                'futu_host': '127.0.0.1',
                'futu_port': 11111,
            },
            'backtest': {
                'initial_capital': self.capital_spin.value(),
                'commission_rate': self.commission_spin.value() / 1000,
                'stamp_duty_rate': 0.001,
                'slippage': 0.0001,
                'position_size': self.position_spin.value(),
            },
            'analysis': {
                'risk_free_rate': 0.03,
                'benchmark': '000300.SH',
                'output_dir': './output',
                'save_plots': True,
            }
        }
        
        # 创建并启动对比线程
        self.compare_thread = CompareThread(config)
        self.compare_thread.progress_update.connect(self.update_status)
        self.compare_thread.result_ready.connect(self.show_comparison_results)
        self.compare_thread.error_occurred.connect(self.show_comparison_error)
        self.compare_thread.start()
    
    def show_comparison_results(self, results_df):
        """显示策略对比结果"""
        if results_df.empty:
            self.compare_text.setText("未获取到对比结果")
            return
        
        # 使用HTML表格格式化显示（更好的对齐）
        html = """
        <style>
            table {
                font-family: 'Courier New', monospace;
                border-collapse: collapse;
                width: 100%;
                font-size: 11pt;
            }
            th {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                text-align: center;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            td {
                padding: 10px;
                text-align: center;
                border: 1px solid #ddd;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #e8f5e9;
            }
            .best {
                background-color: #fff3cd;
                font-weight: bold;
            }
            .summary {
                background-color: #e3f2fd;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #2196F3;
                font-family: 'Microsoft YaHei';
            }
            .title {
                font-size: 14pt;
                font-weight: bold;
                color: #1976D2;
                margin-bottom: 10px;
            }
        </style>
        """
        
        html += "<div class='summary'>"
        html += "<div class='title'>📊 策略对比报告</div>"
        html += f"<p>测试股票: {self.ticker_input.text()}</p>"
        html += f"<p>测试期间: {self.start_date_input.text()} 至 {self.end_date_input.text()}</p>"
        html += "</div>"
        
        # 生成表格
        html += "<table>"
        html += "<tr>"
        for col in results_df.columns:
            if not col.startswith('_'):  # 跳过内部列
                html += f"<th>{col}</th>"
        html += "</tr>"
        
        # 数据行
        for idx, row in results_df.iterrows():
            row_class = 'best' if idx == 0 else ''
            html += f"<tr class='{row_class}'>"
            for col in results_df.columns:
                if not col.startswith('_'):
                    value = row[col]
                    # 为排名第一的策略添加奖杯图标
                    if idx == 0 and col == '策略名称':
                        value = f"🏆 {value}"
                    html += f"<td>{value}</td>"
            html += "</tr>"
        
        html += "</table>"
        
        # 添加最佳策略摘要
        best = results_df.iloc[0]
        html += "<div class='summary'>"
        html += "<div class='title'>🏆 最佳策略推荐</div>"
        html += f"<p><strong>策略名称:</strong> {best['策略名称']}</p>"
        html += f"<p><strong>总收益率:</strong> {best['总收益率']}</p>"
        html += f"<p><strong>年化收益率:</strong> {best['年化收益率']}</p>"
        html += f"<p><strong>最大回撤:</strong> {best['最大回撤']}</p>"
        html += f"<p><strong>夏普比率:</strong> {best['夏普比率']}</p>"
        html += f"<p><strong>胜率:</strong> {best['胜率']}</p>"
        html += f"<p><strong>盈亏比:</strong> {best['盈亏比']}</p>"
        html += "</div>"
        
        # 设置HTML内容
        self.compare_text.setHtml(html)
        
        # 切换到对比标签页
        self.result_tabs.setCurrentIndex(2)
        
        # 恢复按钮
        self.run_button.setEnabled(True)
        self.compare_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ 策略对比完成！")
        
        QMessageBox.information(self, "完成", 
            f"策略对比已完成！\n\n🏆 最佳策略: {best['策略名称']}\n总收益率: {best['总收益率']}")
    
    def show_comparison_error(self, error_msg):
        """显示对比错误"""
        self.run_button.setEnabled(True)
        self.compare_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ 错误: {error_msg}")
        QMessageBox.critical(self, "错误", f"策略对比失败:\n{error_msg}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
