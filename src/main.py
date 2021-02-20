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


class StockTickInfo(BaseModel):
    id: str  # 股票代码
    type: int  # 1,5,15,30,60 min
    restoration: int  # 0 原始 1 前复权 2 后复权


# 获得近5个月分时数据
@app.post("/stock/tick", status_code=200)
async def stocks_tick(stock_info: StockTickInfo, response: Response):
    symbol = stock_info.id
    period = "1"
    adjust = ""
    if stock_info.type == 5:
        period = "5"
    elif stock_info.type == 15:
        period = "15"
    elif stock_info.type == 30:
        period = "30"
    elif stock_info.type == 60:
        period = "60"

    if stock_info.restoration == 1:
        adjust = "qfq"
    elif stock_info.restoration == 2:
        adjust = "hfq"

    try:
        symbol = await utils.stock_id_ps_ak(symbol)
        fund_em_open_fund_rank_df = ak.stock_zh_a_minute(symbol=symbol, period=period, adjust=adjust)
        resp = []
        idx = 0
        for i in fund_em_open_fund_rank_df['day']:
            resp.append({"day": i})
            idx += 1

        idx = 0
        for i in fund_em_open_fund_rank_df['open']:
            resp[idx]['open'] = i
            idx += 1

        idx = 0
        for i in fund_em_open_fund_rank_df['high']:
            resp[idx]['high'] = i
            idx += 1

        idx = 0
        for i in fund_em_open_fund_rank_df['low']:
            resp[idx]['low'] = i
            idx += 1

        idx = 0
        for i in fund_em_open_fund_rank_df['close']:
            resp[idx]['close'] = i
            idx += 1

        idx = 0
        for i in fund_em_open_fund_rank_df['volume']:
            resp[idx]['volume'] = i
            idx += 1

        return resp
    except Exception as e:
        response.status_code = 400
        return e


# class StockHistoryTickInfo(BaseModel):
#     id: str  # 股票代码
#     trade_data: str  # 20191011 start time
#     # type: int  # 1,5,15,30,60 min
#     # restoration: int  # 0 原始 1 前复权 2 后复权


# # 历史分笔数据(近 2 年历史分笔行情数据)  http://quotes.money.163.com/service/zhubi_ajax.html?symbol=000001  未来考虑抽码分布
# @app.post("/stock/history_tick", status_code=200)
# async def stock_history_tick(stock_info: StockHistoryTickInfo, response: Response):
#     try:
#         # symbol = await utils.stock_id_ps_ak(stock_info.id)
#         # fund_em_open_fund_rank_df = ak.stock_zh_a_tick_163(code=symbol, trade_date=stock_info.trade_data)
#         fund_em_open_fund_rank_df = ak.stock_zh_a_tick_163(code="sh600848", trade_date="20210128")
#         resp = []
#         idx = 0
#         print(len(fund_em_open_fund_rank_df))
#         # for i in fund_em_open_fund_rank_df['day']:
#         #     resp.append({"day": i})
#         #     idx += 1
#         #
#         # idx = 0
#         # for i in fund_em_open_fund_rank_df['open']:
#         #     resp[idx]['open'] = i
#         #     idx += 1
#         #
#         # idx = 0
#         # for i in fund_em_open_fund_rank_df['high']:
#         #     resp[idx]['high'] = i
#         #     idx += 1
#         #
#         # idx = 0
#         # for i in fund_em_open_fund_rank_df['low']:
#         #     resp[idx]['low'] = i
#         #     idx += 1
#         #
#         # idx = 0
#         # for i in fund_em_open_fund_rank_df['close']:
#         #     resp[idx]['close'] = i
#         #     idx += 1
#         #
#         # idx = 0
#         # for i in fund_em_open_fund_rank_df['volume']:
#         #     resp[idx]['volume'] = i
#         #     idx += 1
#
#         return resp
#     except Exception as e:
#         response.status_code = 400
#         return e

# 分析师指数排名
@app.get("/fraudster/index/ranking", status_code=200)
async def fraudster_index_ranking(response: Response):
    try:
        stock_em_analyst_rank_df = ak.stock_em_analyst_rank()
        resp = []

        for i in stock_em_analyst_rank_df.values:
            resp.append({
                "serial_number": i[0],  # 序号
                'analyst_name': i[1],  # 分析师名称
                'analyst_unit': i[2],  # 分析师单位
                'annual_index': i[3],  # 年度指数
                'yield': i[4],  # 收益率
                '3_months_yield': i[5],  # 3个月收益率
                '6_months_yield': i[6],  # 6个月收益率
                '12_months_yield': i[7],  # 12个月收益率
                'number_constituent_stocks': i[8],  # 成分股个数
                'latest_stock_ratings': i[9],  # 最新个股评级
                'analyst_id': i[10],  # 分析师ID
            })

        return resp
    except Exception as e:
        response.status_code = 400
        return e


# 分析师详情 (最新跟踪成分股, 历史跟踪成分股)
@app.get("/fraudster/info/{fraudster_id}", status_code=200)
async def fraudster_info(fraudster_id: str, response: Response):
    try:
        latest_tracking_constituent = ak.stock_em_analyst_detail(analyst_id=fraudster_id, indicator="最新跟踪成分股")
        latest_tracking_constituents = []
        for i in latest_tracking_constituent.values:
            latest_tracking_constituents.append({
                'serial_number': i[0],  # 序号
                'stock_code': i[1],  # 股票代码
                'stock_name': i[2],  # 股票名称
                'date_transfer_in': i[3],  # 调入日期
                'latest_rating_date': i[4],  # 最新评级日期
                'current_rating_name': i[5],  # 当前评级名称
                'transaction_price': i[6],  # 成交价格(前复权)
                'latest_prices': i[7],  # 最新价格
                'phase_up_or_down': i[8],  # 阶段涨跌幅
            })

        history_tracking_constituent = ak.stock_em_analyst_detail(analyst_id=fraudster_id, indicator="历史跟踪成分股")
        history_tracking_constituents = []
        for i in history_tracking_constituent.values:
            history_tracking_constituents.append({
                "serial_number": i[0],  # 序号
                'stock_code': i[1],  # 股票代码
                'stock_name': i[2],  # 股票名称
                'date_transfer_in': i[3],  # 调入日期
                'date_transfer_out': i[4],  # 调出日期
                'name_of_rating_on_transfer_ins': i[5],  # 调入时评级名称
                'reason_transfer_out': i[6],  # 调出原因
                'cumulative_increase_or_decrease': i[7],  # 累计涨跌幅
            })

        return {
            "latest_tracking_constituents": latest_tracking_constituents,
            "history_tracking_constituents": history_tracking_constituents,
        }
    except Exception as e:
        response.status_code = 400
        return e


# 千股千评 http://data.eastmoney.com/stockcomment/
@app.get("/stock_comments", status_code=200)
async def stock_comments(response: Response):
    try:
        stock_em_comment_df = ak.stock_em_comment()
        stock_em_comment_dfs = []
        for i in stock_em_comment_df.values:
            stock_em_comment_dfs.append({
                "date": i[0],  # 日期时间
                'code': i[1],  # 股票code
                'name': i[2],  # 股票名称
                'new': i[3],  # 最新价
                'change_percent': i[4],  # 涨跌幅
                'pr_ration': i[5],  # 市盈率
                'turnover_rate': i[6],  # 换手率(注意%)
                'zlcb': i[7],  # 主力成本
                'jgcyd': i[8],  # 机构参与度
                'jgcyd_type': i[9],  # 机构参与度类型
                'zlcb_20r': i[10],  # 主力成本20日
                'zlcb_60r': i[11],  # 主力成本60日
                'market': i[17],  # 市场类型
                'total_score': i[18],  # 综合得分
                'ranking_up': i[19],  # 上升
                'ranking': i[20],  # 目前排名
                'focus': i[21],  # 关注指数
            })

        return stock_em_comment_dfs
    except Exception as e:
        response.status_code = 400
        return e


# 年报季报


# 个股资金流
@app.get("/stock_financial_flows/{stock_id}", status_code=200)
async def stock_financial_flows(stock_id: str, response: Response):
    try:
        market, stock = await utils.stock_id_sp_ak(stock_id)
        stock_individual_fund_flow_df = ak.stock_individual_fund_flow(stock=stock, market=market)
        stock_individual_fund_flow_dfs = []
        for i in stock_individual_fund_flow_df.values:
            stock_individual_fund_flow_dfs.append({
                "date": i[0],  # 日期时间
                'net_main_inflow_net': i[1],  # 主力净流入-净额
                'net_small_order_inflow_net': i[2],  # 小单净流入-净额
                'net_medium_inflow_net': i[3],  # 中单净流入-净额
                'net_big_inflow_net': i[4],  # 大单净流入-净额
                'net_supper_big_inflow_net': i[5],  # 超大单净流入-净额
                'net_main_inflow_net_share': i[6],  # 主力净流入-净占比
                'net_small_inflow_net_share': i[7],  # 小单净流入-净占比
                'net_medium_inflow_net_share': i[8],  # 中单净流入-净占比
                'net_big_inflow_net_share': i[9],  # 大单净流入-净占比
                'net_supper_big_inflow_net_share': i[10],  # 超大单净流入-净占比
                'closing_price': i[11],  # 收盘价
                'up_or_down': i[12],  # 涨跌幅
            })

        return stock_individual_fund_flow_dfs
    except Exception as e:
        response.status_code = 400
        return e

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
