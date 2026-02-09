# 基金助手 API 参考文档

## 目录
1. [基金核心 API](#基金核心-api)
2. [市场行情 API](#市场行情-api)
3. [响应数据结构](#响应数据结构)

---

## 基金核心 API

### 1. 基金实时估值（推荐）
```
GET http://fundgz.1234567.com.cn/js/{基金代码}.js
```

**说明：** 天天基金JSONP接口，盘中实时估值最可靠的数据源

**响应格式：** JSONP
```javascript
jsonpgz({
  "fundcode": "012734",
  "name": "易方达中证人工智能主题ETF联接C",
  "jzrq": "2026-02-06",      // 净值日期
  "dwjz": "1.7573",          // 昨日净值
  "gsz": "1.8158",           // 估算净值
  "gszzl": "3.33",           // 估算涨跌幅(%)
  "gztime": "2026-02-09 10:55"  // 估值时间
});
```

**使用场景：**
- 盘中查询基金实时估值
- 计算当日预估收益

**注意事项：**
- 仅交易时段（9:30-15:00）有实时数据
- QDII基金估值可能延迟
- 部分新发基金可能无估值数据

---

### 2. 基金实时估值（备用）
```
GET https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFInfo
```

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| Fcodes | 基金代码，多个逗号分隔 | 001618,000001 |
| pageIndex | 页码 | 1 |
| pageSize | 每页数量 | 200 |
| plat | 平台 | Android |
| appType | 应用类型 | ttjj |
| product | 产品 | EFund |
| Version | 版本 | 1 |
| deviceid | 设备ID（可选） | 随机UUID |

**响应字段：**
```json
{
  "Datas": [{
    "FCODE": "001618",      // 基金代码
    "SHORTNAME": "天弘中证食品饮料", // 基金名称
    "NAV": "1.5234",        // 单位净值
    "GSZ": "1.5300",        // 估算净值
    "GSZZL": "0.43",        // 估算涨跌幅(%)
    "NAVCHGRT": "0.42",     // 实际涨跌幅(%)
    "PDATE": "2024-01-15",  // 净值日期
    "GZTIME": "2024-01-15 15:00" // 估值时间
  }]
}
```

**判断逻辑：**
- 当 `PDATE == GZTIME.substr(0,10)` 时，表示当日净值已公布
- 此时使用 `NAV` 和 `NAVCHGRT`，而非 `GSZ` 和 `GSZZL`

---

### 2. 基金搜索
```
GET https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx
```

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| m | 固定值 | 9 |
| key | 搜索关键词 | 白酒 |

**响应字段：**
```json
{
  "Datas": [{
    "CODE": "001618",
    "NAME": "天弘中证食品饮料指数A",
    "FundBaseInfo": {...}
  }]
}
```

---

### 3. 基金详情
```
GET https://fundmobapi.eastmoney.com/FundMApi/FundBaseTypeInformation.ashx
```

**参数：**
| 参数 | 说明 |
|------|------|
| FCODE | 基金代码 |
| deviceid | Wap |
| plat | Wap |
| product | EFund |
| version | 2.0.0 |

**响应字段：**
```json
{
  "Datas": {
    "FCODE": "001618",
    "SHORTNAME": "天弘中证食品饮料",
    "DWJZ": "1.5234",       // 单位净值
    "LJJZ": "1.8234",       // 累计净值
    "FSRQ": "2024-01-15",   // 净值日期
    "FTYPE": "指数型-股票", // 基金类型
    "JJGS": "天弘基金",     // 基金公司
    "JJJL": "张三",         // 基金经理
    "ENDNAV": "12345678",   // 基金规模(元)
    "SGZT": "开放申购",     // 申购状态
    "SHZT": "开放赎回",     // 赎回状态
    "SYL_Y": "5.23",        // 近1月收益率
    "SYL_3Y": "12.34",      // 近3月收益率
    "SYL_6Y": "18.56",      // 近6月收益率
    "SYL_1N": "25.67",      // 近1年收益率
    "RANKM": "123/456",     // 近1月排名
    "RANKQ": "100/456",     // 近3月排名
    "RANKHY": "80/456",     // 近6月排名
    "RANKY": "50/456"       // 近1年排名
  }
}
```

---

### 4. 净值估算走势（当日分时）
```
GET https://fundmobapi.eastmoney.com/FundMApi/FundVarietieValuationDetail.ashx
```

**参数：** FCODE=基金代码

**响应：**
```json
{
  "Datas": ["09:30,1.5200,0.12", "09:31,1.5210,0.18", ...],
  "Expansion": {"DWJZ": "1.5180"}  // 昨日净值
}
```
数据格式：`时间,估算净值,估算涨跌幅`

---

### 5. 历史净值
```
GET https://fundmobapi.eastmoney.com/FundMApi/FundNetDiagram.ashx
```

**参数：**
| 参数 | 说明 | 可选值 |
|------|------|--------|
| FCODE | 基金代码 | |
| RANGE | 时间范围 | y(月), 3y(季), 6y(半年), n(1年), 3n(3年), 5n(5年) |

**响应：**
```json
{
  "Datas": [{
    "FSRQ": "2024-01-15",  // 日期
    "DWJZ": "1.5234",      // 单位净值
    "LJJZ": "1.8234",      // 累计净值
    "JZZZL": "0.42"        // 日增长率(%)
  }]
}
```

---

### 6. 累计收益走势
```
GET https://fundmobapi.eastmoney.com/FundMApi/FundYieldDiagramNew.ashx
```

**参数：** FCODE, RANGE（同历史净值）

**响应：**
```json
{
  "Datas": [{
    "PDATE": "2024-01-15",
    "YIELD": "25.67",       // 基金涨幅(%)
    "INDEXYIED": "18.34"    // 对比指数涨幅(%)
  }],
  "Expansion": {"INDEXNAME": "沪深300"}
}
```

---

### 7. 持仓明细
```
GET https://fundmobapi.eastmoney.com/FundMNewApi/FundMNInverstPosition
```

**参数：** FCODE=基金代码

**响应：**
```json
{
  "Datas": {
    "fundStocks": [{
      "GPDM": "600519",     // 股票代码
      "GPJC": "贵州茅台",   // 股票简称
      "JZBL": "9.87",       // 持仓占比(%)
      "PCTNVCHG": "0.5",    // 较上期变化(%)
      "PCTNVCHGTYPE": "增持", // 变化类型
      "NEWTEXCH": "1"       // 交易所(1=沪, 0=深)
    }]
  },
  "Expansion": "2024-01-15"  // 持仓截止日期
}
```

---

### 8. 基金经理
```
# 经理列表
GET https://fundmobapi.eastmoney.com/FundMApi/FundManagerList.ashx?FCODE=001618

# 经理详情
GET https://fundmobapi.eastmoney.com/FundMApi/FundMangerDetail.ashx?FCODE=001618
```

**经理列表响应：**
```json
{
  "Datas": [{
    "MGRID": "123",
    "MGRNAME": "张三",
    "FEMPDATE": "2020-01-01",  // 任职开始
    "LEMPDATE": "",            // 任职结束（空=至今）
    "DAYS": 1000,              // 任职天数
    "PENAVGROWTH": 56.78       // 任职涨幅(%)
  }]
}
```

---

## 市场行情 API

### 1. 指数实时行情
```
GET https://push2.eastmoney.com/api/qt/ulist.np/get
```

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| secids | 证券代码 | 1.000001,0.399001 |
| fields | 返回字段 | f2,f3,f4,f12,f13,f14 |
| fltt | 固定值 | 2 |

**常用指数代码：**
| 代码 | 名称 |
|------|------|
| 1.000001 | 上证指数 |
| 0.399001 | 深证成指 |
| 1.000300 | 沪深300 |
| 0.399006 | 创业板指 |
| 1.000688 | 科创50 |
| 100.HSI | 恒生指数 |
| 100.NDX | 纳斯达克 |

**响应字段：**
```json
{
  "data": {
    "diff": [{
      "f2": 3000.12,   // 最新价
      "f3": 0.56,      // 涨跌幅(%)
      "f4": 16.78,     // 涨跌额
      "f12": "000001", // 代码
      "f13": "1",      // 市场(1=沪, 0=深)
      "f14": "上证指数" // 名称
    }]
  }
}
```

---

### 2. 股票实时行情
```
GET https://push2.eastmoney.com/api/qt/ulist.np/get
```

**参数：** secids=1.600519（格式：市场.代码）

**响应字段：** 同指数行情，额外包含 f6(成交额)

---

### 3. 大盘资金流向
```
GET http://push2.eastmoney.com/api/qt/stock/fflow/kline/get
```

**参数：**
| 参数 | 说明 |
|------|------|
| secid | 1.000001 |
| secid2 | 0.399001 |
| lmt | 0 |
| klt | 1 |
| fields1 | f1,f2,f3,f7 |
| fields2 | f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63 |

**响应：**
```json
{
  "data": {
    "klines": [
      "09:31,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入",
      ...
    ]
  }
}
```

---

### 4. 行业板块资金
```
GET http://push2.eastmoney.com/api/qt/clist/get
```

**参数：**
| 参数 | 说明 |
|------|------|
| fs | m:90+t:2 |
| fid | f62 |
| pn | 1 |
| pz | 500 |
| po | 1 |
| np | 1 |
| fields | f12,f13,f14,f62 |

**响应：**
```json
{
  "data": {
    "diff": [{
      "f14": "酿酒行业",  // 板块名称
      "f62": 123456789    // 主力净流入(元)
    }]
  }
}
```

---

### 5. 北向/南向资金
```
GET http://push2.eastmoney.com/api/qt/kamt.rtmin/get
```

**参数：** fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56

**响应：**
```json
{
  "data": {
    "s2n": [  // 北向资金（南向北）
      "09:30,沪股通净流入,沪股通余额,深股通净流入,深股通余额,北向合计",
      ...
    ],
    "n2s": [  // 南向资金（北向南）
      "09:30,港股通(沪)净流入,余额,港股通(深)净流入,余额,南向合计",
      ...
    ]
  }
}
```

---

## 响应数据结构

### 通用响应格式
```json
{
  "Datas": [...],        // 主数据
  "Expansion": {...},    // 扩展数据
  "ErrCode": 0,          // 错误码
  "ErrMsg": null         // 错误信息
}
```

### 错误处理
- ErrCode = 0：成功
- ErrCode != 0：失败，查看 ErrMsg

### 数据类型说明
- 金额单位：元（需除以 100000000 转为亿）
- 涨跌幅：百分比数值（如 0.56 表示 0.56%）
- 日期格式：YYYY-MM-DD
- 时间格式：HH:mm 或 YYYY-MM-DD HH:mm
