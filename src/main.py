from fastapi import FastAPI, Response
from pydantic import BaseModel
import baostock as bs
import src.option as option
import akshare as ak
import src.utils as utils

app = FastAPI()


@app.get("/")
async def read_root():
    return "Open-Source-Data  Api Server"


class StockInfo(BaseModel):
    id: str  # 股票代码
    start_time: str  # 格式“YYYY-MM-DD”，为空时取2015-01-01；
    end_time: str  # 格式“YYYY-MM-DD”，为空时取最近一个交易日；
    type: int  # 0 日key 1 周k  2 1小时k  3 30分钟K
    restoration: int  # 0 原始 1 前复权 2 后复权


# {
#     "id": "sh.601398",
#     "start_time": "2021-01-01",
#     "end_time": "2021-02-16",
#     "type": 0,
#     "restoration": 1
# }


# 获取stocks历史数据
@app.post("/history_stocks", status_code=200)
async def history_stocks(stock_info: StockInfo, response: Response):
    try:
        bs.login()
        frequency = "d"
        adjust_flag = "3"
        query = "date,code,open,high,low,close,volume,amount,adjustflag"

        if stock_info.type == 0:
            frequency = "d"
            query = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM," \
                    "pbMRQ,psTTM,pcfNcfTTM,isST"
        elif stock_info.type == 1:
            frequency = "w"
            query = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"
        elif stock_info.type == 2:
            frequency = "60"
        elif stock_info.type == 3:
            frequency = "30"

        if stock_info.restoration == 0:
            adjust_flag = "3"
        elif stock_info.restoration == 1:
            adjust_flag = "1"
        elif stock_info.restoration == 2:
            adjust_flag = "2"

        rs = bs.query_history_k_data_plus(stock_info.id,
                                          query,
                                          start_date=stock_info.start_time, end_date=stock_info.end_time,
                                          frequency=frequency,
                                          adjustflag=adjust_flag)  # frequency="d"取日k线，adjustflag="3"默认不复权
        bs.logout()

        if rs.error_code != "0":
            response.status_code = 500
            return option.standard_return(None, False, rs.error_msg, query)

        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        return option.standard_return(data_list, True, None, query)
    except Exception as e:
        response.status_code = 500
        return option.standard_return(None, False, e, query)


# 获取fund历史数据
@app.get("/history_fund/{fund_id}", status_code=200)
async def history_fund(fund_id: str, response: Response):
    try:
        r = ak.fund_em_open_fund_info(fund=fund_id)
        return r
    except Exception as e:
        response.status_code = 400
        return e


# fund排名
@app.get("/funds_rank", status_code=200)
async def funds_rank(response: Response):
    try:
        fund_em_open_fund_rank_df = ak.fund_em_open_fund_rank(symbol="全部")
        resp = []
        idx = 0
        for i in fund_em_open_fund_rank_df['基金代码']:
            resp.append({"fund_id": i})
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_open_fund_rank_df['基金简称']:
            resp[idx]['fund_name'] = i
            idx += 1
            if idx >= 100:
                break

        return resp
    except Exception as e:
        response.status_code = 400
        return e


# fund 持仓信息
@app.get("/fund_portfolio_hold/{fund_id}", status_code=200)
async def fund_portfolio_hold(fund_id: str, response: Response):
    try:
        fund_em_portfolio_hold_df = ak.fund_em_portfolio_hold(code=fund_id, year=utils.get_time())
        if len(fund_em_portfolio_hold_df) == 0:
            # 如果今年没有获取去年数据
            year = str(int(utils.get_time()) - 1)
            fund_em_portfolio_hold_df = ak.fund_em_portfolio_hold(code=fund_id, year=year)

        resp = []
        idx = 0
        for i in fund_em_portfolio_hold_df['股票代码']:
            resp.append({"stock_id": i})
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_portfolio_hold_df['股票名称']:
            resp[idx]['stock_name'] = i
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_portfolio_hold_df['占净值比例']:
            resp[idx]['percentage_net_worth'] = i
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_portfolio_hold_df['持股数']:
            resp[idx]['number_shares_held'] = i
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_portfolio_hold_df['持仓市值']:
            resp[idx]['position_market'] = i
            idx += 1
            if idx >= 100:
                break

        idx = 0
        sk = ""
        for i in fund_em_portfolio_hold_df['季度']:
            if idx == 0:
                sk = i
            if sk != i:
                break
            resp[idx]['quarterly'] = i
            idx += 1
            if idx >= 100:
                break

        return resp[:idx]
    except Exception as e:
        response.status_code = 400
        return e


# 分时数据
@app.get("/fund_portfolio_hold/{fund_id}", status_code=200)
async def stocks_minute(response: Response):
    try:
        fund_em_open_fund_rank_df = ak.fund_em_open_fund_rank(symbol="全部")
        resp = []
        idx = 0
        for i in fund_em_open_fund_rank_df['基金代码']:
            resp.append({"fund_id": i})
            idx += 1
            if idx >= 100:
                break

        idx = 0
        for i in fund_em_open_fund_rank_df['基金简称']:
            resp[idx]['fund_name'] = i
            idx += 1
            if idx >= 100:
                break

        return resp
    except Exception as e:
        response.status_code = 400
        return e

# 历史分笔数据

# 年报季报

# 个股资金流

# 个股资金流排名

# 大盘资金流

# 财务报表

# 财务摘要

# 基金持股

# 机构推荐池

# 股票评级记录

# 龙虎榜

# 活跃A股统计

# 企业社会责任