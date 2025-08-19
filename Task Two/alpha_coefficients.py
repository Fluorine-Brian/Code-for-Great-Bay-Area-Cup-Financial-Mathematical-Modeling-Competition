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

# 定义一个函数来计算每个证券的 Alpha 系数
def calculate_alpha(stock_code, df):
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
    
    # Alpha 系数即为回归模型的截距项
    alpha = model.intercept_
    return alpha

# 计算所有证券的 Alpha 系数
alpha_results = {}
for stock_code in df['code'].unique():
    alpha = calculate_alpha(stock_code, df)
    alpha_results[stock_code] = alpha

# 转换为DataFrame并输出结果
alpha_df = pd.DataFrame(list(alpha_results.items()), columns=['StockCode', 'Alpha'])

# 将 Alpha 系数结果保存到 CSV 文件
alpha_df.to_csv('alpha_coefficients_2024.csv', index=False)
print("Alpha coefficients have been saved to 'alpha_coefficients.csv'")
