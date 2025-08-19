import pandas as pd

# 读取数据
df = pd.read_csv('./data/hs300stocks_kdata_2024.csv')

# 转换日期为标准日期格式
df['time'] = pd.to_datetime(df['time'])

# 按证券代码和日期排序
df = df.sort_values(['code', 'time'])

# 定义一个函数来计算每只证券的累计收益率
def calculate_total_return(stock_code, df):
    # 筛选出对应证券的数据
    stock_data = df[df['code'] == stock_code]
    
    # 如果数据量不足，跳过该证券
    if len(stock_data) < 2:
        return None
    
    # 计算累计收益率：(最后一个收盘价 - 第一个收盘价) / 第一个收盘价
    start_price = stock_data['close'].iloc[0]
    end_price = stock_data['close'].iloc[-1]
    total_return = (end_price - start_price) / start_price
    return total_return

# 计算所有证券的累计收益率
return_results = {}
for stock_code in df['code'].unique():
    total_return = calculate_total_return(stock_code, df)
    return_results[stock_code] = total_return

# 转换为DataFrame并输出结果
return_df = pd.DataFrame(list(return_results.items()), columns=['StockCode', 'TotalReturn'])

# 将累计收益率结果保存到 CSV 文件
return_df.to_csv('total_return_results_2024.csv', index=False)
print("Total return results have been saved to 'total_return_results.csv'")
