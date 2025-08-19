import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('./data/hs300stocks_kdata_2024.csv')

# 转换日期为标准日期格式
df['time'] = pd.to_datetime(df['time'])

# 计算每个证券的每日收益率
df = df.sort_values(['code', 'time'])
df['stock_return'] = df.groupby('code')['close'].pct_change()

# 定义一个函数来计算每个证券的波动率
def calculate_volatility(stock_code, df):
    # 筛选出对应证券的数据
    stock_data = df[df['code'] == stock_code].dropna(subset=['stock_return'])
    
    # 如果数据量不足，跳过该证券
    if len(stock_data) < 2:
        return np.nan
    
    # 计算每日收益率的标准差，即为波动率
    volatility = stock_data['stock_return'].std()
    return volatility

# 计算所有证券的波动率
volatility_results = {}
for stock_code in df['code'].unique():
    volatility = calculate_volatility(stock_code, df)
    volatility_results[stock_code] = volatility

# 转换为DataFrame并输出结果
volatility_df = pd.DataFrame(list(volatility_results.items()), columns=['StockCode', 'Volatility'])

# 将波动率结果保存到 CSV 文件
volatility_df.to_csv('volatility_results_2024.csv', index=False)
print("Volatility results have been saved to 'volatility_results.csv'")
