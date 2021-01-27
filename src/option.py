def standard_return(data, success: bool, err):
    if success:
        return {
            "data": data,
            "success": True
        }
    return {
        "data": err,
        "success": False
    }


class StockInfo:
    date: str  # 交易所行情日期
    code: str  # 证券代码
    open: str  # 开盘价
    high: str
    low: str
    close: str  # 收盘价
    pre_close: str  # 前收盘价
    volume: str  # 成交量（累计 单位：股）
    amount: str  # 成交额（单位：人民币元）
    adjust_flag: str  # 复权状态(1：后复权， 2：前复权，3：不复权）
    turn: str  # 换手率
    trade_status: str  # 交易状态(1：正常交易 0：停牌）
    pct_chg: str  # 涨跌幅（百分比）
    pe_ttm: str  # 滚动市盈率
    pe_mrq: str  # 市净率
    pe_ttm: str  # 滚动市销率
    pcf_ncf_ttm: str  # 滚动市现率
    isST: str
