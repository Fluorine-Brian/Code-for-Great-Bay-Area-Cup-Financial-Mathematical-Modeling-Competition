import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# 读取数据
df = pd.read_csv('./data/hs300stocks_kdata_2024.csv')

# 转换日期为标准日期格式
df['time'] = pd.to_datetime(df['time'])

# 按日期分组，计算所有证券的平均收盘价，作为市场指数的近似
market_index = df.groupby('time')['close'].mean().reset_index()
market_index.columns = ['time', 'market_close']

# 计算市场的每日收益率
market_index = market_index.sort_values('time')
market_index['market_return'] = market_index['market_close'].pct_change()

# 将市场收益率合并到主数据框中
df = df.merge(market_index[['time', 'market_return']], on='time', how='left')

# 计算每个证券的每日收益率
df['stock_return'] = df.groupby('code')['close'].pct_change()

# 定义一个函数来计算每个证券的 Beta 系数
def calculate_beta(stock_code, df):
    # 筛选出对应证券的数据
    stock_data = df[df['code'] == stock_code].dropna(subset=['stock_return', 'market_return'])
    
    # 如果数据量不足，跳过该证券
    if len(stock_data) < 2:
        return np.nan
    
    # 回归模型
    X = stock_data['market_return'].values.reshape(-1, 1)  # 市场收益率
    y = stock_data['stock_return'].values  # 证券收益率
    
    # 创建并训练模型
    model = LinearRegression()
    model.fit(X, y)
    
    # Beta系数即为回归模型的系数
    beta = model.coef_[0]
    return beta

# 计算所有证券的 Beta 系数
beta_results = {}
for stock_code in df['code'].unique():
    beta = calculate_beta(stock_code, df)
    beta_results[stock_code] = beta

# 转换为DataFrame并输出结果
beta_df = pd.DataFrame(list(beta_results.items()), columns=['StockCode', 'Beta'])
print(beta_df)
beta_df.to_csv('beta_coefficients_2024.csv', index=False)
print("Beta coefficients have been saved to 'beta_coefficients.csv'")