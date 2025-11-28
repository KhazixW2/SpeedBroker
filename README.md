# 🚀 量化交易回测系统

一个专业的、模块化的股票量化交易回测系统，基于Python实现。采用配置驱动设计，支持多种策略和数据源。

## ✨ 特性

- **模块化架构**：数据层、策略层、回测层、分析层完全解耦
- **配置驱动**：所有参数集中在配置文件中，无需修改代码
- **关注点分离**：每个模块职责单一，易于维护和扩展
- **多数据源支持**：支持 AkShare、yfinance 等数据源
- **完整的性能分析**：计算夏普比率、最大回撤、卡玛比率等专业指标
- **可视化报告**：自动生成价格走势、资产曲线、回撤分析等图表
- **缓存机制**：本地缓存历史数据，加快重复测试速度

## 📁 项目结构（已重组优化）

```
SpeedBroker/
│
├── 📂 gui/                          # GUI界面模块
│   └── gui_main.py                  # PyQtGraph图形界面
│
├── 📂 core/                         # 核心业务模块  
│   ├── config.py                    # 配置文件
│   ├── data_handler.py              # 数据层
│   ├── backtester.py                # 回测层
│   └── analyzer.py                  # 分析层
│
├── 📂 strategies/                   # 策略模块
│   └── strategy.py                  # 策略实现
│
├── 📂 utils/                        # 工具模块
│   └── stock_list.py                # 股票数据库
│
├── 📂 docs/                         # 文档目录（6份完整文档）
│   ├── GUI_GUIDE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── USER_GUIDE.md
│   ├── CONFIG_GUIDE.md
│   ├── STOCK_DATABASE_GUIDE.md
│   └── DATA_SOURCE_TROUBLESHOOTING.md
│
├── 📂 tests/                        # 测试脚本目录
│   ├── test_akshare.py              # AkShare基础测试
│   ├── test_akshare_detailed.py     # AkShare详细诊断
│   ├── test_fix.py                  # 功能修复验证
│   └── README.md                    # 测试说明文档
│
├── 📂 data/cache/                   # 数据缓存
├── 📂 output/                       # 输出结果
│
├── 🚀 run_gui.py                    # GUI启动（推荐）
├── 🚀 start_gui.bat                 # Windows一键启动
├── 🚀 main.py                       # CLI启动
│
├── requirements.txt                 # 依赖包
└── PROJECT_STRUCTURE.txt            # 项目结构说明
```

### 📚 详细文档

本项目提供了完整的文档体系，帮助你快速上手和深入了解：

- **[🖥️ GUI使用指南](docs/GUI_GUIDE.md)** - 图形化界面使用教程、功能详解、常见问题（推荐新手）
- **[📐 项目结构详解](docs/PROJECT_STRUCTURE.md)** - 五层架构设计、各模块职责、数据流转、设计模式
- **[📖 使用手册](docs/USER_GUIDE.md)** - 命令参考、使用场景、结果解读、常见问题、最佳实践
- **[⚙️ 配置参数手册](docs/CONFIG_GUIDE.md)** - 每个配置项的作用、范围、影响、调优建议
- **[🔧 数据源问题排查](docs/DATA_SOURCE_TROUBLESHOOTING.md)** - 数据获取失败的诊断和解决方案
- **[🧪 测试脚本说明](tests/README.md)** - 测试脚本使用指南、诊断工具

## 🔧 安装

### 1. 克隆或下载项目

```bash
cd d:/workspace/SpeedBroker
```

### 2. 创建并激活虚拟环境（推荐）⭐

**为什么使用虚拟环境？**
- 🔒 隔离项目依赖，避免版本冲突
- 🧹 保持系统 Python 环境清洁
- 📦 便于项目部署和依赖管理

**创建虚拟环境：**
```bash
# 创建虚拟环境
python -m venv venv
```

**激活虚拟环境：**
```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

激活成功后，命令行前会显示 `(venv)` 标识。

### 3. 安装依赖包

```bash
# 确保已激活虚拟环境
pip install -r requirements.txt
```

主要依赖：
- `pandas` - 数据处理
- `numpy` - 数值计算
- `akshare` - 中国股票数据源
- `matplotlib` - 数据可视化

## 🚀 快速开始

### 方式一：图形化界面（推荐新手）⭐

**最简单的使用方式！**

```bash
# 方式1：Python运行
python run_gui.py

# 方式2：双击启动（Windows）
双击 start_gui.bat
```

启动后会打开图形化界面，通过界面即可：
- 📊 配置所有参数（股票代码、日期、策略等）
- 🚀 一键开始回测
- 📈 查看性能指标和图表
- 💾 保存结果

**详细说明**: 请查看 [GUI使用指南](docs/GUI_GUIDE.md)

---

### 方式二：命令行模式（适合高级用户）

#### 1. 配置参数

编辑 `config.py` 文件，设置你的回测参数：

```python
# 数据配置
DATA_CONFIG = {
    'tickers': ['000001.SZ'],      # 股票代码
    'start_date': '2020-01-01',    # 开始日期
    'end_date': '2024-12-31',      # 结束日期
    'data_source': 'akshare',      # 数据源
}

# 策略配置
STRATEGY_CONFIG = {
    'strategy_name': 'DualMovingAverage',
    'short_window': 10,            # 短期均线
    'long_window': 30,             # 长期均线
}

# 回测配置
BACKTEST_CONFIG = {
    'initial_capital': 100000,     # 初始资金
    'commission_rate': 0.0003,     # 手续费率
    'stamp_duty_rate': 0.001,      # 印花税率
}
```

### 2. 运行回测

```bash
python main.py
```

### 3. 查看结果

程序将：
1. 自动下载股票数据（首次运行）
2. 生成交易信号
3. 执行回测模拟
4. 计算性能指标
5. 生成可视化图表
6. 保存交易日志

结果将显示在控制台，图表保存在 `output/` 目录。

## 📊 核心模块说明

### 1. 配置与主控层 (`config.py` & `main.py`)

- **config.py**：集中管理所有配置参数
- **main.py**：程序入口，协调各模块工作

### 2. 数据层 (`data_handler.py`)

**职责**：
- 从多个数据源获取股票数据
- 数据清洗和预处理
- 本地缓存管理

**核心方法**：
```python
data_handler = DataHandler(DATA_CONFIG)
data = data_handler.get_data(['000001.SZ'])
```

### 3. 策略层 (`strategy.py`)

**职责**：
- 实现各种交易策略
- 生成买入/卖出信号

**已实现策略**：
- **双均线策略** (DualMovingAverageStrategy)
  - 金叉（短期均线上穿长期均线）→ 买入
  - 死叉（短期均线下穿长期均线）→ 卖出
- **RSI策略** (RSIStrategy) - 预留扩展

**添加新策略**：
```python
class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # 实现你的策略逻辑
        data['signal'] = ...
        return data
```

### 4. 回测层 (`backtester.py`)

**职责**：
- 矢量化回测实现
- 模拟真实交易（考虑手续费、印花税、滑点）
- 记录每日资产变化

**特点**：
- 支持A股交易规则（最小100股）
- 考虑交易成本
- 强制平仓机制

### 5. 分析层 (`analyzer.py`)

**职责**：
- 计算性能指标
- 生成可视化报告

**性能指标**：
- 总收益率、年化收益率
- 夏普比率 (Sharpe Ratio)
- 最大回撤 (Maximum Drawdown)
- 卡玛比率 (Calmar Ratio)
- 胜率、盈亏比

**可视化内容**：
1. 价格走势 + 均线 + 买卖点标记
2. 策略收益 vs 买入持有基准
3. 回撤曲线分析

## 💡 使用示例

### 示例1：测试不同均线周期

修改 `config.py`：
```python
STRATEGY_CONFIG = {
    'strategy_name': 'DualMovingAverage',
    'short_window': 5,   # 改为5日均线
    'long_window': 20,   # 改为20日均线
}
```

运行 `python main.py` 查看结果。

### 示例2：测试不同股票

```python
DATA_CONFIG = {
    'tickers': ['600519.SH'],  # 改为贵州茅台
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
}
```

### 示例3：调整初始资金和手续费

```python
BACKTEST_CONFIG = {
    'initial_capital': 500000,     # 50万初始资金
    'commission_rate': 0.0002,     # 降低手续费
}
```

## 📈 性能指标说明

| 指标 | 说明 | 理想值 |
|------|------|--------|
| **总收益率** | (最终资金 - 初始资金) / 初始资金 | 越高越好 |
| **年化收益率** | 将总收益率标准化为年化值 | > 10% |
| **夏普比率** | 单位风险的超额收益 | > 1.0 |
| **最大回撤** | 从峰值到谷底的最大跌幅 | < 20% |
| **卡玛比率** | 年化收益率 / 最大回撤 | 越高越好 |
| **胜率** | 盈利交易次数 / 总交易次数 | > 50% |
| **盈亏比** | 平均盈利 / 平均亏损 | > 1.5 |

## 🔍 数据源说明

### AkShare（推荐）

- **优点**：免费、无需注册、数据全面
- **支持**：A股、港股、美股等
- **延迟**：实时数据
- **使用**：默认配置即可

### yfinance（备用）

- **优点**：全球市场、数据稳定
- **限制**：部分A股数据可能不全
- **配置**：
```python
DATA_CONFIG = {
    'data_source': 'yfinance',
}
```

## 🛠️ 扩展开发

### 添加新策略

1. 在 `strategy.py` 中创建新类：
```python
class MACDStrategy(BaseStrategy):
    def generate_signals(self, data):
        # 计算MACD指标
        # 生成交易信号
        return data
```

2. 在 `StrategyFactory` 中注册：
```python
strategies = {
    'DualMovingAverage': DualMovingAverageStrategy,
    'MACD': MACDStrategy,  # 添加新策略
}
```

3. 在 `config.py` 中配置：
```python
STRATEGY_CONFIG = {
    'strategy_name': 'MACD',
}
```

### 添加新数据源

在 `data_handler.py` 的 `DataHandler` 类中添加新方法：
```python
def _fetch_from_newsource(self, tickers):
    # 实现新数据源的获取逻辑
    return data
```

## 📝 注意事项

1. **首次运行**：首次运行会下载数据，可能需要几分钟
2. **缓存清理**：如需更新数据，删除 `data/cache/` 目录
3. **中文显示**：如果图表中文显示异常，安装中文字体
4. **数据质量**：回测结果高度依赖数据质量，请确保数据准确
5. **过拟合风险**：避免过度优化参数导致过拟合

## 🐛 常见问题

### Q1: 导入 akshare 失败？
```bash
pip install akshare --upgrade
```

### Q2: 图表显示乱码？
修改 `analyzer.py` 中的字体设置：
```python
plt.rcParams['font.sans-serif'] = ['你的字体名称']
```

### Q3: 数据下载失败？
- 检查网络连接
- 尝试切换数据源
- 检查股票代码格式

## 📚 学习资源

- [AkShare 文档](https://akshare.akfamily.xyz/)
- [Pandas 官方文档](https://pandas.pydata.org/)
- [量化交易入门](https://www.quantstart.com/)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

本项目仅供学习和研究使用。实盘交易需谨慎，风险自负。

## ⚠️ 免责声明

本系统仅用于教育和研究目的。历史回测结果不代表未来收益。实际交易前请充分了解市场风险，谨慎决策。

---

**祝你量化交易顺利！📈💰**
