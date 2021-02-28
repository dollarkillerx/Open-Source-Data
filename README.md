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

### 分析师指数排名
GET: `/fraudster/index/ranking`

### 分析师详情 (最新跟踪成分股, 历史跟踪成分股)
GET： `/fraudster/info/:fraudster_id`

### 千股千评 `http://data.eastmoney.com/stockcomment/`
GET: `/stock_comments`

### 个股资金流
GET: `/stock_financial_flows/:stock_id`

### 个股资金流排名
GET: `/stock_individual_fund_flow_rank/:indicator_idx`

### 板块资金流排名
GET: `/stock_sector_fund_flow_rank/:indicator_idx`
indicator_idx 
type: str
value: 0 今日, 1 3日, 2 5日, 3 10日

### 财报
POST: `/stock_financial_reports`
JSON:
```json
{
  "id": "sh.00001",
  "type": 1, # 1 资产负债表, 2 利润表, 3 现金流量表
}
```

### 财务摘要
GET: `/stock_financial_summary/:stock_code`

### 财务指标
GET: `/stock_financial_indicators/:stock_code`

### 基金持股v1
GET: `/stock_fund_holdings_v1/:stock_code`

### 机构持股LIST
POST: `/stock_fund_holdings_list`
```JSON 
{
    "symbol": 1, # 1 "基金持仓",2 "QFII持仓",3 "社保持仓",4 "券商持仓",5 "保险持仓",6 "信托持仓"
    "date": "20200630"  # date="20200630"; 财报发布日期, xxxx-03-31, xxxx-06-30, xxxx-09-30, xxxx-12-31
}
```

### 主要股东
GET: `/stock_major_shareholders/:stock_code`

### 机构持股一览表
GET: `/stock_list_institutional_holdings/{time}`
time: time="20211"; 从 2008 年开始, {"一季报":1, "中报":2 "三季报":3 "年报":4}, e.g., "20191", 其中的 1 表示一季报; "20193", 其中的 3 表示三季报;

### 机构持股一览表
POST: `/stock_list_institutional_holdings`
```JSON
{
  "id": str ,# 股票代码
  "quarter": str # time="20211"; 从 2008 年开始, {"一季报":1, "中报":2 "三季报":3 "年报":4}, e.g., "20191", 其中的 1 表示一季报; "20193", 其中的 3 表示三季报;
}
```

### 股票评级记录
GET: `/stock_institute_recommend_detail/{stock_code}`

### 机构推荐池
GET: `/stock_institute_recommend/:indicator`
indicator: 1 行业关注度, 2 最新投资评级, 3 上调评级股票, 4 下调评级股票,5 股票综合评级,6 首次评级股票,7 首次评级股票,8 机构关注度,9 行业关注度,10 投资评级选股

### 活跃A股统计
GET: `/stock_active_a_share/{period}`
period: 1 近一月, 2 近三月, 3 近六月,4 近一年

### 依赖
- fast_api
- nvicorn