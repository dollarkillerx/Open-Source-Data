# baostock
Open-Source-Data 数据同步本地

# install
``` 
pipenv shell
make install_requirements
```

### run
``` 
make run
or
make debug
```

### Baostock Server
- [x] K 线基础数据

### 数据来源
- Baostock
- Akshare

### history stocks 获取历史数据
POST: `/history_stocks`
```json
{
  "id": "sh.601398",
  "start_time": "2021-01-01",
  "end_time": "2021-02-16",
  "type": 0,
  "restoration": 1
} 
```

### history fund 获取基金历史净值
GET: `history_fund/:fund_id`

### TOP100 funds rank
GET: `/funds_rank`

### fund 持仓信息
GET: `/fund_portfolio_hold/:fund_id`

### 获得近5个月分时数据
POST： `/stock/tick`
```JSON
{
    "id": "sh000300",  # 股票代码
    "type": 1,         # 1,5,15,30,60 min
    "restoration": 0   # 0 原始 1 前复权 2 后复权
}
```

### 依赖
- fast_api
- nvicorn