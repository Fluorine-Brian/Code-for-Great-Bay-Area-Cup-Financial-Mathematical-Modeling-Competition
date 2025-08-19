import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('./data/hs300stocks_kdata_2024.csv')

# 转换日期为标准日期格式
df['time'] = pd.to_datetime(df['time'])

# 计算每个证券的每日收益率
df = df.sort_values(['code', 'time'])
df['stock_return'] = df.groupby('code')['close'].pct_change()

# 假设年化无风险收益率为2%，转化为每日收益率
risk_free_rate_daily = (1 + 0.02) ** (1 / 252) - 1  # 252个交易日

# 定义一个函数来计算每个证券的夏普比率
def calculate_sharpe_ratio(stock_code, df):
    # 筛选出对应证券的数据
    stock_data = df[df['code'] == stock_code].dropna(subset=['stock_return'])
    
    # 如果数据量不足，跳过该证券
    if len(stock_data) < 2:
        return np.nan
    
    # 计算平均每日收益率
    avg_return = stock_data['stock_return'].mean()
    
    # 计算收益率的标准差（波动率）
    volatility = stock_data['stock_return'].std()
    
    # 计算夏普比率
    sharpe_ratio = (avg_return - risk_free_rate_daily) / volatility
    return sharpe_ratio

# 计算所有证券的夏普比率
sharpe_ratio_results = {}
for stock_code in df['code'].unique():
    sharpe_ratio = calculate_sharpe_ratio(stock_code, df)
    sharpe_ratio_results[stock_code] = sharpe_ratio

# 转换为DataFrame并输出结果
sharpe_ratio_df = pd.DataFrame(list(sharpe_ratio_results.items()), columns=['StockCode', 'SharpeRatio'])

# 将夏普比率结果保存到 CSV 文件
sharpe_ratio_df.to_csv('sharpe_ratio_results_2024.csv', index=False)
print("Sharpe Ratio results have been saved to 'sharpe_ratio_results.csv'")
