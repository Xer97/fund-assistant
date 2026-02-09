#!/usr/bin/env python3
"""
基金助手 API 封装脚本
用法：
    python fund_api.py query 001618,000001      # 查询基金实时估值（推荐）
    python fund_api.py search 白酒              # 搜索基金
    python fund_api.py detail 001618            # 基金详情
    python fund_api.py history 001618 y         # 历史净值 (y/3y/6y/n/3n/5n)
    python fund_api.py position 001618          # 持仓明细
    python fund_api.py manager 001618           # 基金经理
    python fund_api.py index                    # 大盘指数
    python fund_api.py flow                     # 资金流向
    python fund_api.py north                    # 北向资金
"""

import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://fundmobapi.eastmoney.com"
PUSH_URL = "https://push2.eastmoney.com"
# 天天基金实时估值接口（JSONP格式，更可靠）
FUND_GZ_URL = "http://fundgz.1234567.com.cn/js"

def fetch(url):
    """发起 HTTP 请求并返回 JSON"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; FundAssistant/1.0)'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def fetch_jsonp(url):
    """发起 HTTP 请求并解析 JSONP 响应"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; FundAssistant/1.0)'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            # 解析 JSONP: jsonpgz({...});
            match = re.search(r'jsonpgz\((.*)\);?', content)
            if match:
                return json.loads(match.group(1))
            return {"error": "Invalid JSONP response"}
    except Exception as e:
        return {"error": str(e)}

def _fetch_single_fund(code):
    """查询单个基金（内部函数，供并发调用）"""
    code = code.strip()
    if not code:
        return None

    url = f"{FUND_GZ_URL}/{code}.js?rt={int(datetime.now().timestamp() * 1000)}"
    data = fetch_jsonp(url)

    if "error" in data:
        return {"code": code, "error": data["error"]}

    return {
        "code": data.get("fundcode"),
        "name": data.get("name"),
        "nav": float(data.get("dwjz", 0)) if data.get("dwjz") else None,
        "nav_date": data.get("jzrq"),
        "gsz": float(data.get("gsz", 0)) if data.get("gsz") else None,
        "gszzl": float(data.get("gszzl", 0)) if data.get("gszzl") else 0,
        "gztime": data.get("gztime")
    }

def query_funds(codes, max_workers=5):
    """查询基金实时估值（并发查询，使用天天基金JSONP接口）"""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]

    if not code_list:
        return {"funds": []}

    # 单个基金不需要并发
    if len(code_list) == 1:
        fund = _fetch_single_fund(code_list[0])
        return {"funds": [fund] if fund else []}

    result = []
    # 使用线程池并发查询，限制最大并发数避免被封
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_code = {executor.submit(_fetch_single_fund, code): code for code in code_list}
        for future in as_completed(future_to_code):
            fund = future.result()
            if fund:
                result.append(fund)

    # 按原始顺序排序（可选，保持输入顺序）
    code_order = {code: i for i, code in enumerate(code_list)}
    result.sort(key=lambda x: code_order.get(x.get("code", ""), 999))

    return {"funds": result}

def search_funds(keyword):
    """搜索基金"""
    url = f"https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?m=9&key={urllib.parse.quote(keyword)}"
    data = fetch(url)
    if "error" in data:
        return data

    result = []
    for item in data.get("Datas", [])[:20]:  # 限制返回20条
        result.append({
            "code": item.get("CODE"),
            "name": item.get("NAME")
        })
    return {"funds": result}

def fund_detail(code):
    """基金详情"""
    url = f"{BASE_URL}/FundMApi/FundBaseTypeInformation.ashx?FCODE={code}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0"
    data = fetch(url)
    if "error" in data:
        return data

    d = data.get("Datas", {})
    return {
        "code": d.get("FCODE"),
        "name": d.get("SHORTNAME"),
        "nav": d.get("DWJZ"),
        "nav_acc": d.get("LJJZ"),
        "nav_date": d.get("FSRQ"),
        "type": d.get("FTYPE"),
        "company": d.get("JJGS"),
        "manager": d.get("JJJL"),
        "scale": d.get("ENDNAV"),
        "buy_status": d.get("SGZT"),
        "sell_status": d.get("SHZT"),
        "return_1m": d.get("SYL_Y"),
        "return_3m": d.get("SYL_3Y"),
        "return_6m": d.get("SYL_6Y"),
        "return_1y": d.get("SYL_1N"),
        "rank_1m": d.get("RANKM"),
        "rank_3m": d.get("RANKQ"),
        "rank_6m": d.get("RANKHY"),
        "rank_1y": d.get("RANKY")
    }

def fund_history(code, range_type="y"):
    """历史净值"""
    url = f"{BASE_URL}/FundMApi/FundNetDiagram.ashx?FCODE={code}&RANGE={range_type}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0"
    data = fetch(url)
    if "error" in data:
        return data

    result = []
    for item in data.get("Datas", []):
        result.append({
            "date": item.get("FSRQ"),
            "nav": item.get("DWJZ"),
            "nav_acc": item.get("LJJZ"),
            "change": item.get("JZZZL")
        })
    return {"history": result}

def fund_position(code):
    """持仓明细"""
    url = f"{BASE_URL}/FundMNewApi/FundMNInverstPosition?FCODE={code}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0"
    data = fetch(url)
    if "error" in data:
        return data

    stocks = data.get("Datas", {}).get("fundStocks", [])
    result = []
    for item in stocks:
        result.append({
            "code": item.get("GPDM"),
            "name": item.get("GPJC"),
            "ratio": item.get("JZBL"),
            "change": item.get("PCTNVCHG"),
            "change_type": item.get("PCTNVCHGTYPE")
        })
    return {
        "date": data.get("Expansion"),
        "stocks": result
    }

def fund_manager(code):
    """基金经理"""
    url = f"{BASE_URL}/FundMApi/FundManagerList.ashx?FCODE={code}&deviceid=Wap&plat=Wap&product=EFund&version=2.0.0"
    data = fetch(url)
    if "error" in data:
        return data

    result = []
    for item in data.get("Datas", []):
        result.append({
            "name": item.get("MGRNAME"),
            "start_date": item.get("FEMPDATE"),
            "end_date": item.get("LEMPDATE") or "至今",
            "days": item.get("DAYS"),
            "return": item.get("PENAVGROWTH")
        })
    return {"managers": result}

def market_index():
    """大盘指数"""
    secids = "1.000001,0.399001,1.000300,0.399006,1.000688"
    url = f"{PUSH_URL}/api/qt/ulist.np/get?fltt=2&secids={secids}&fields=f2,f3,f4,f12,f14"
    data = fetch(url)
    if "error" in data:
        return data

    result = []
    for item in data.get("data", {}).get("diff", []):
        result.append({
            "code": item.get("f12"),
            "name": item.get("f14"),
            "price": item.get("f2"),
            "change": item.get("f3"),
            "change_amount": item.get("f4")
        })
    return {"indices": result}

def capital_flow():
    """资金流向"""
    url = f"http://push2.eastmoney.com/api/qt/stock/fflow/kline/get?lmt=0&klt=1&secid=1.000001&secid2=0.399001&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56"
    data = fetch(url)
    if "error" in data:
        return data

    klines = data.get("data", {}).get("klines", [])
    if not klines:
        return {"flow": []}

    # 只返回最新的数据
    latest = klines[-1].split(",")
    return {
        "time": latest[0] if len(latest) > 0 else None,
        "main_net": float(latest[1]) / 100000000 if len(latest) > 1 else None,
        "small_net": float(latest[2]) / 100000000 if len(latest) > 2 else None,
        "medium_net": float(latest[3]) / 100000000 if len(latest) > 3 else None,
        "large_net": float(latest[4]) / 100000000 if len(latest) > 4 else None,
        "super_net": float(latest[5]) / 100000000 if len(latest) > 5 else None
    }

def north_capital():
    """北向资金"""
    url = f"http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56"
    data = fetch(url)
    if "error" in data:
        return data

    s2n = data.get("data", {}).get("s2n", [])
    if not s2n:
        return {"north": {}}

    # 找到最新的有效数据
    latest = None
    for item in reversed(s2n):
        parts = item.split(",")
        if len(parts) > 1 and parts[1] != "-":
            latest = parts
            break

    if not latest:
        return {"north": {}}

    return {
        "time": latest[0],
        "sh_net": float(latest[1]) / 10000 if latest[1] != "-" else None,
        "sh_balance": float(latest[2]) / 10000 if latest[2] != "-" else None,
        "sz_net": float(latest[3]) / 10000 if latest[3] != "-" else None,
        "sz_balance": float(latest[4]) / 10000 if latest[4] != "-" else None,
        "total_net": float(latest[5]) / 10000 if latest[5] != "-" else None
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "query" and len(sys.argv) > 2:
        result = query_funds(sys.argv[2])
    elif cmd == "search" and len(sys.argv) > 2:
        result = search_funds(sys.argv[2])
    elif cmd == "detail" and len(sys.argv) > 2:
        result = fund_detail(sys.argv[2])
    elif cmd == "history" and len(sys.argv) > 2:
        range_type = sys.argv[3] if len(sys.argv) > 3 else "y"
        result = fund_history(sys.argv[2], range_type)
    elif cmd == "position" and len(sys.argv) > 2:
        result = fund_position(sys.argv[2])
    elif cmd == "manager" and len(sys.argv) > 2:
        result = fund_manager(sys.argv[2])
    elif cmd == "index":
        result = market_index()
    elif cmd == "flow":
        result = capital_flow()
    elif cmd == "north":
        result = north_capital()
    else:
        print(__doc__)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
