import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import xlsxwriter

# 读取股票价格数据
try:
    price_data = pd.read_csv(
        r'E:\大学\数学建模\2024粤港澳大湾区数学建模\沪深300成分股的数据\沪深300成分股的数据\hs300stocks_kdata_2018.csv')
except FileNotFoundError:
    print("文件 hs300stocks_kdata_2018.csv 未找到，请检查路径是否正确。")
    exit()

# 将日期列 "time" 转换为日期格式并保留日期部分
price_data['time'] = pd.to_datetime(price_data['time']).dt.date
price_data = price_data.set_index(['time', 'code'])

# 按股票代码计算每日收盘价的收益率矩阵
returns = price_data['close'].unstack(level=1).pct_change(fill_method=None).dropna()

# 读取权重数据
try:
    weights_data = pd.read_csv(
        r'E:\大学\数学建模\2024粤港澳大湾区数学建模\沪深300成分股的数据\沪深300成分股的数据\hs300stocks_2018.csv')
except FileNotFoundError:
    print("文件 hs300stocks_2018.csv 未找到，请检查路径是否正确。")
    exit()

# 确保权重数据的列名为 'code' 和 'weight'
if 'code' not in weights_data.columns or 'weight' not in weights_data.columns:
    print("请检查权重数据的列名，确保其分别为 'code' 和 'weight'")
    exit()

# 设置股票代码为索引，并按 returns 中的股票代码对齐权重数据
weights_data = weights_data.set_index('code')
weights_data = weights_data.loc[returns.columns]  # 按 returns 中的股票代码对齐
stock_weights = weights_data['weight']
stock_weights /= stock_weights.sum()  # 归一化权重

# 确保对齐后的 returns 和 stock_weights 长度一致
if len(stock_weights) != returns.shape[1]:
    print("权重数据的长度与收益率数据的列数不匹配，请检查数据的一致性。")
    exit()

# 定义无风险利率
risk_free_rate = 0.03

# 定义夏普比率的负值（添加最大回撤惩罚项）
def sharpe_ratio_with_drawdown_penalty(weights, returns, risk_free_rate, max_drawdown=0.7, penalty_factor=100):
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

    # 计算组合的最大回撤
    portfolio_returns = returns.dot(weights)
    cumulative_returns = (portfolio_returns + 1).cumprod() - 1
    peak = cumulative_returns.cummax()
    drawdown = (peak - cumulative_returns) / peak
    max_drawdown_observed = drawdown.max()

    # 若最大回撤超出0.7，增加惩罚项
    penalty = penalty_factor * max(0, max_drawdown_observed - max_drawdown)
    return -sharpe_ratio + penalty

# 约束条件：权重之和为1
constraints = [{'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}]

# 将单只股票的权重上限降到5%以增加分散化
weight_limit = 0.05
bounds = tuple((0, weight_limit) for _ in range(len(stock_weights)))

# 初始权重
initial_weights = stock_weights.values

# 优化
optimized = minimize(sharpe_ratio_with_drawdown_penalty, initial_weights, args=(returns, risk_free_rate),
                     method='SLSQP', bounds=bounds, constraints=constraints)

# 输出优化结果
if optimized.success:
    optimized_weights = optimized.x
    expected_return = np.dot(optimized_weights, returns.mean())
    volatility = np.sqrt(np.dot(optimized_weights.T, np.dot(returns.cov(), optimized_weights)))

    # 计算最终组合的最大回撤
    portfolio_returns = returns.dot(optimized_weights)
    cumulative_returns = (portfolio_returns + 1).cumprod() - 1
    peak = cumulative_returns.cummax()
    drawdown = (peak - cumulative_returns) / peak
    max_drawdown_observed = drawdown.max()

    print("Optimized Portfolio Weights:", optimized_weights)
    print("Expected Portfolio Return:", expected_return)
    print("Portfolio Volatility:", volatility)
    print("Max Drawdown:", max_drawdown_observed)

    # 可视化累计收益和回撤
    plt.figure(figsize=(14, 7))

    # 绘制累计收益曲线
    plt.subplot(2, 1, 1)
    cumulative_returns.plot()
    plt.title("Cumulative Returns of Optimized Portfolio")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")

    # 绘制最大回撤曲线
    plt.subplot(2, 1, 2)
    drawdown.plot()
    plt.title("Drawdown of Optimized Portfolio")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")

    plt.tight_layout()
    plt.show()

    # 导出结果到Excel文件
    with pd.ExcelWriter('optimized_portfolio_results.xlsx', engine='xlsxwriter') as writer:
        # 优化权重输出到Excel
        optimized_weights_df = pd.DataFrame({'Stock': returns.columns, 'Weight': optimized_weights})
        optimized_weights_df.to_excel(writer, sheet_name='Optimized Weights', index=False)

        # 输出其他指标
        summary_df = pd.DataFrame({
            'Expected Return': [expected_return],
            'Volatility': [volatility],
            'Max Drawdown': [max_drawdown_observed]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # 输出累计收益和回撤数据
        cumulative_returns.to_frame(name='Cumulative Returns').to_excel(writer, sheet_name='Cumulative Returns')
        drawdown.to_frame(name='Drawdown').to_excel(writer, sheet_name='Drawdown')
else:
    print("Optimization failed:", optimized.message)