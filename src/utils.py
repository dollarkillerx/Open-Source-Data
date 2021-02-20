import time


# 获取当前时间 年
def get_time():
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    dt = time.strftime("%Y", time_local)
    return dt


# 股票代码格式化 akShare   sh.000300 => sh000300
async def stock_id_ps_ak(stock_id: str):
    idx = stock_id.find(".")
    return stock_id[:idx] + stock_id[idx+1:]
