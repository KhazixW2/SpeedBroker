# config.ini 配置文件使用指南

## 📋 概述

`config.ini` 是系统的统一配置文件，GUI版本和CLI版本都从这个文件读取默认参数。这确保了两个版本的界面参数统一，避免了硬编码。

## 📁 配置文件位置

```
SpeedBroker/
├── config.ini          # 主配置文件（项目根目录）
├── core/
│   └── config.py       # 配置管理器
├── gui/
│   └── gui_main.py     # GUI界面（从config.ini读取默认值）
└── main.py             # CLI主程序（从config.ini读取配置）
```

## ⚙️ 配置文件结构

### [DATA] - 数据配置

```ini
[DATA]
# 默认股票代码（可以是代码或"代码 - 名称"格式）
default_ticker = 000001.SZ
default_ticker_name = 平安银行

# 数据时间范围
start_date = 2023-01-01
end_date = 2024-10-01

# 数据源选择 ('akshare', 'tushare', 'futu', 'yfinance')
data_source = akshare

# Tushare配置（仅使用tushare时需要）
tushare_token = 

# Futu配置（仅使用futu时需要）
futu_host = 127.0.0.1
futu_port = 11111

# 本地缓存设置
use_cache = True
cache_dir = ./data/cache
```

**说明：**
- `default_ticker`: GUI启动时显示的默认股票代码
- `default_ticker_name`: GUI启动时显示的默认股票名称
- `start_date` / `end_date`: 回测的默认时间范围
- `data_source`: 默认数据源（推荐使用 akshare，免费无需注册）
- `tushare_token`: 使用 Tushare 时需要填写
- `futu_host` / `futu_port`: 使用富途时的连接配置

### [STRATEGY] - 策略配置

```ini
[STRATEGY]
# 策略名称
strategy_name = DualMovingAverage

# 双均线策略参数
short_window = 10
long_window = 30

# RSI策略参数
rsi_period = 14
rsi_oversold = 30
rsi_overbought = 70
```

**说明：**
- `strategy_name`: 默认策略类型（DualMovingAverage 或 RSI）
- `short_window`: 短期均线周期（天数）
- `long_window`: 长期均线周期（天数）
- RSI参数：仅在使用RSI策略时生效

### [BACKTEST] - 回测配置

```ini
[BACKTEST]
# 初始资金 (元)
initial_capital = 100000

# 手续费率 (万分之三 = 0.03%)
commission_rate = 0.3

# 印花税率 (千分之一 = 0.1%)
stamp_duty_rate = 1.0

# 滑点设置 (万分之一 = 0.01%)
slippage = 0.1

# 每次交易资金占比 (1.0表示全仓)
position_size = 1.0
```

**说明：**
- `initial_capital`: 回测初始资金（元）
- `commission_rate`: 手续费率，单位为‰（千分比）
- `stamp_duty_rate`: 印花税率，单位为‰（千分比）
- `slippage`: 滑点，单位为万分比
- `position_size`: 每次交易使用的资金比例（0.1-1.0）

**注意：** 在配置文件中，费率使用千分比/万分比表示，程序会自动转换为小数。

### [ANALYSIS] - 分析配置

```ini
[ANALYSIS]
# 无风险利率 (年化)
risk_free_rate = 0.03

# 基准指数代码
benchmark = 000300.SH

# 图表保存路径
output_dir = ./output
save_plots = True
```

**说明：**
- `risk_free_rate`: 无风险利率，用于计算夏普比率（年化，小数形式）
- `benchmark`: 基准指数代码（沪深300）
- `output_dir`: 输出文件保存目录
- `save_plots`: 是否自动保存图表

### [LOGGING] - 日志配置

```ini
[LOGGING]
# 日志级别 (DEBUG, INFO, WARNING, ERROR)
level = INFO
format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
file = ./logs/backtest.log
```

**说明：**
- `level`: 日志级别（DEBUG, INFO, WARNING, ERROR）
- `format`: 日志格式
- `file`: 日志文件路径

### [GLOBAL] - 全局配置

```ini
[GLOBAL]
# 调试模式开关
debug_mode = False
```

**说明：**
- `debug_mode`: 是否启用调试模式（显示详细错误信息）

## 🔧 使用方法

### 1. 修改配置文件

直接编辑 `config.ini` 文件，修改你需要的参数。

### 2. GUI版本读取配置

GUI启动时会自动从 `config.ini` 读取默认值：

```python
# gui/gui_main.py
def load_default_config(self):
    """从配置文件加载默认值"""
    if config_manager:
        # 获取默认股票信息
        self.default_ticker, self.default_ticker_name = config_manager.get_default_ticker_info()
        
        # 获取数据配置
        data_config = config_manager.get_data_config()
        self.default_start_date = data_config['start_date']
        self.default_end_date = data_config['end_date']
        # ...
```

### 3. CLI版本读取配置

CLI版本直接使用 `core/config.py` 导出的配置字典：

```python
# main.py
from core.config import (
    DATA_CONFIG,
    STRATEGY_CONFIG,
    BACKTEST_CONFIG,
    ANALYSIS_CONFIG,
    DEBUG_MODE
)
```

## 📝 配置优先级

1. **GUI运行时参数** > **config.ini配置** > **默认值**
   - 用户在GUI界面修改的参数优先级最高
   - config.ini提供默认值
   - 如果config.ini不存在或读取失败，使用硬编码的默认值

2. **CLI运行时** 完全使用 **config.ini配置**
   - CLI版本启动时读取config.ini
   - 所有参数都从配置文件获取

## 🎯 优势

### 1. 统一配置
- GUI和CLI使用相同的配置文件
- 避免参数不一致

### 2. 无硬编码
- 所有可变参数都在配置文件中
- 代码更加灵活和可维护

### 3. 易于修改
- INI格式简单易读
- 支持注释说明
- 修改后立即生效（重启程序）

### 4. 向后兼容
- 如果配置文件缺失，使用默认值
- 不影响现有功能

## 🚨 注意事项

### 1. 配置文件编码
- 使用 UTF-8 编码保存
- 确保中文字符正确显示

### 2. 配置格式
- 遵循INI格式规范
- 不要删除section标题（如 [DATA]）
- 参数名称区分大小写

### 3. 数值范围
- `position_size`: 0.1 - 1.0
- `commission_rate`: 建议 0.1 - 5.0 （千分比）
- `initial_capital`: 建议 > 10000

### 4. 日期格式
- 统一使用 YYYY-MM-DD 格式
- 例如：2023-01-01

### 5. 布尔值
- 使用 True 或 False
- 大小写敏感

## 🔄 配置迁移

如果从旧版本升级：

1. **备份旧配置文件** （如 `core/config.py`）
2. **创建 config.ini**
3. **将旧参数迁移到 config.ini**
4. **测试确认** 两个版本界面参数一致

## 📚 相关文档

- [配置详细说明](CONFIG_GUIDE.md)
- [项目结构说明](PROJECT_STRUCTURE.md)
- [GUI使用指南](GUI_GUIDE.md)
- [用户指南](USER_GUIDE.md)

## 🆘 常见问题

### Q1: 配置文件不存在会怎样？
**A**: 程序会使用内置的默认值，并在控制台显示警告信息。

### Q2: 如何恢复默认配置？
**A**: 删除 `config.ini`，重新运行程序会使用默认值。或者参考本文档重新创建配置文件。

### Q3: 修改配置后需要重启程序吗？
**A**: 是的，配置文件在程序启动时读取。修改后需要重启GUI或CLI才能生效。

### Q4: GUI界面可以保存配置吗？
**A**: 可以。GUI提供"保存配置"功能，但保存的是JSON格式（用于会话管理）。如需修改默认值，请直接编辑 `config.ini`。

### Q5: 费率为什么要用千分比？
**A**: 为了便于理解。例如"万三"（0.03%）在配置文件中写为 `0.3`（千分比），程序会自动转换为 `0.0003`（小数）。

---

**更新时间**: 2025-11-11
**版本**: v1.0.0
