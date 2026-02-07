# Fund Assistant / 基金投资助手

A Claude Code skill for Chinese mutual fund investment management.

一个用于中国公募基金投资管理的 Claude Code 技能。

---

## English

### Overview

Fund Assistant is a comprehensive tool for querying fund data, managing investment portfolios, and tracking market trends. It integrates with Eastmoney APIs to provide real-time fund valuations, NAV data, and market information.

### Features

- **Fund Query**: Real-time NAV estimates, historical NAV, fund details
- **Fund Search**: Search funds by name or code
- **Portfolio Management**: Add/remove holdings, track cost basis, calculate returns
- **Market Data**: Major indices, capital flow, northbound capital
- **Multi-user Support**: Isolated data storage for different users
- **Import/Export**: Backup and restore portfolio data

### Quick Start

```bash
# Initialize data directory
python scripts/portfolio.py init

# Query fund real-time valuation
python scripts/fund_api.py query 001618

# Add a holding (code, shares, cost)
python scripts/portfolio.py add 001618 1000 1.5

# View portfolio
python scripts/portfolio.py list
```

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fund_api.py` | Fund data API (query, search, history, positions) |
| `scripts/portfolio.py` | Portfolio management (add, update, remove, export) |

### Data Storage

Data is stored locally in `.fund-assistant/` directory:
```
.fund-assistant/
├── config.json           # Global config (current user)
└── users/
    └── {username}/
        ├── portfolio.json    # Holdings
        └── transactions.json # Transaction history
```

---

## 中文

### 概述

基金投资助手是一个综合性工具，用于查询基金数据、管理投资组合和跟踪市场趋势。它集成了东方财富 API，提供实时基金估值、净值数据和市场信息。

### 功能特性

- **基金查询**：实时估值、历史净值、基金详情
- **基金搜索**：按名称或代码搜索基金
- **持仓管理**：添加/删除持仓、记录成本、计算收益
- **市场数据**：大盘指数、资金流向、北向资金
- **多用户支持**：不同用户数据隔离存储
- **导入导出**：备份和恢复持仓数据

### 快速开始

```bash
# 初始化数据目录
python scripts/portfolio.py init

# 查询基金实时估值
python scripts/fund_api.py query 001618

# 添加持仓（代码、份额、成本）
python scripts/portfolio.py add 001618 1000 1.5

# 查看持仓
python scripts/portfolio.py list
```

### 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/fund_api.py` | 基金数据 API（查询、搜索、历史、持仓） |
| `scripts/portfolio.py` | 持仓管理（添加、更新、删除、导出） |

### 常用命令

#### 基金 API
```bash
python scripts/fund_api.py query 001618,000001   # 查询实时估值
python scripts/fund_api.py search 白酒           # 搜索基金
python scripts/fund_api.py detail 001618         # 基金详情
python scripts/fund_api.py history 001618 y      # 历史净值
python scripts/fund_api.py position 001618       # 持仓明细
python scripts/fund_api.py manager 001618        # 基金经理
python scripts/fund_api.py index                 # 大盘指数
python scripts/fund_api.py flow                  # 资金流向
python scripts/fund_api.py north                 # 北向资金
```

#### 持仓管理
```bash
python scripts/portfolio.py init                 # 初始化
python scripts/portfolio.py list                 # 查看持仓
python scripts/portfolio.py add 001618 1000 1.5  # 添加持仓
python scripts/portfolio.py update 001618 shares=1500  # 更新
python scripts/portfolio.py remove 001618        # 删除
python scripts/portfolio.py user 老婆            # 切换用户
python scripts/portfolio.py users                # 列出用户
python scripts/portfolio.py export data.json     # 导出
python scripts/portfolio.py import data.json     # 导入
```

### 数据存储

数据存储在本地 `.fund-assistant/` 目录：
```
.fund-assistant/
├── config.json           # 全局配置（当前用户）
└── users/
    └── {用户名}/
        ├── portfolio.json    # 持仓数据
        └── transactions.json # 交易记录
```

### 收益计算

```
当日收益 = (当前净值 - 昨日净值) × 持有份额
持仓收益 = (当前净值 - 成本价) × 持有份额
收益率 = (当前净值 - 成本价) / 成本价 × 100%
```

### 注意事项

1. 首次使用需运行 `portfolio.py init` 初始化
2. 交易时段：9:30-11:30, 13:00-15:00（工作日）
3. 净值通常在交易日 18:00-22:00 公布

---

## License

MIT
