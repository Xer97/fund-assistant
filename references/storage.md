# 数据存储结构

## 目录结构

```
.fund-assistant/                # 项目本地目录
├── config.json                 # 全局配置（当前用户等）
└── users/
    ├── default/                # 默认用户
    │   ├── portfolio.json      # 持仓数据
    │   └── transactions.json   # 交易记录
    └── {用户名}/               # 其他用户
        ├── portfolio.json
        └── transactions.json
```

## 数据结构定义

### config.json
```json
{
  "currentUser": "default",
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

### portfolio.json
```json
{
  "funds": [
    {
      "code": "001618",
      "name": "天弘中证食品饮料指数A",
      "shares": 1000.00,
      "cost": 1.5000,
      "addedAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-15T10:30:00Z",
      "note": "定投"
    }
  ],
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

### transactions.json
```json
{
  "records": [
    {
      "id": "uuid-v4",
      "code": "001618",
      "name": "天弘中证食品饮料指数A",
      "type": "buy",
      "shares": 500.00,
      "price": 1.5200,
      "amount": 760.00,
      "fee": 0,
      "date": "2024-01-10",
      "createdAt": "2024-01-10T14:30:00Z",
      "note": "加仓"
    }
  ],
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

## 字段说明

### 持仓字段
| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 基金代码（6位） |
| name | string | 基金名称 |
| shares | number | 持有份额 |
| cost | number | 成本价（单位净值） |
| addedAt | string | 添加时间（ISO 8601） |
| updatedAt | string | 更新时间 |
| note | string | 备注（可选） |

### 交易记录字段
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识（UUID v4） |
| code | string | 基金代码 |
| name | string | 基金名称 |
| type | string | 交易类型：buy/sell |
| shares | number | 交易份额 |
| price | number | 成交净值 |
| amount | number | 成交金额 |
| fee | number | 手续费 |
| date | string | 交易日期（YYYY-MM-DD） |
| createdAt | string | 记录创建时间 |
| note | string | 备注（可选） |

## 操作示例

使用 `scripts/portfolio.py` 脚本管理数据：

```bash
# 初始化
python scripts/portfolio.py init

# 添加持仓
python scripts/portfolio.py add 001618 1000 1.5 "定投"

# 更新持仓
python scripts/portfolio.py update 001618 shares=1500

# 切换用户
python scripts/portfolio.py user 老婆
```

### 计算成本价（加仓后）
```
新成本 = (原份额 × 原成本 + 新份额 × 新价格) / (原份额 + 新份额)
```
