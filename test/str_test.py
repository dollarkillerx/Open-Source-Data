def stock_id_ps_ak(stock_id: str):
    idx = stock_id.find(".")
    return stock_id[:idx] + stock_id[idx+1:]


if __name__ == '__main__':
    print(stock_id_ps_ak('sh.600751'))