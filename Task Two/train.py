import pandas as pd
import glob
from sklearn.linear_model import LinearRegression

# 用于存储年度合并数据和训练数据
all_data = []
training_data = []

# 遍历2014-2024年
for year in range(2014, 2025):
    # 定义文件路径
    alpha_file = f"alpha_coefficients/alpha_coefficients_{year}.csv"
    beta_file = f"beta_coefficients/beta_coefficients_{year}.csv"
    sharpe_file = f"sharpe_ratio/sharpe_ratio_results_{year}.csv"
    volatility_file = f"volatility/volatility_results_{year}.csv"
    return_file = f"return/total_return_results_{year}.csv"
    
    # 读取每年的特征文件和收益率文件
    alpha_df = pd.read_csv(alpha_file)
    beta_df = pd.read_csv(beta_file)
    sharpe_df = pd.read_csv(sharpe_file)
    volatility_df = pd.read_csv(volatility_file)
    return_df = pd.read_csv(return_file)
    
    # 合并特征数据
    merged_df = alpha_df.merge(beta_df, on="StockCode", suffixes=('_alpha', '_beta'))
    merged_df = merged_df.merge(sharpe_df, on="StockCode")
    merged_df = merged_df.merge(volatility_df, on="StockCode", suffixes=('_sharpe', '_volatility'))
    merged_df = merged_df.merge(return_df, on="StockCode")
    
    # 重命名列，确保统一的列名
    merged_df.columns = ["StockCode", "Alpha", "Beta", "SharpeRatio", "Volatility", "Return"]
    
    # 添加年份列
    merged_df["Year"] = year
    
    # 将数据添加到训练集列表
    training_data.append(merged_df[["Alpha", "Beta", "SharpeRatio", "Volatility", "Return"]])
    
    # 将合并的数据存储
    all_data.append(merged_df)

# 合并所有年份的训练数据
training_df = pd.concat(training_data, ignore_index=True)

# 分割特征和目标值
X = training_df[["Alpha", "Beta", "SharpeRatio", "Volatility"]]
y = training_df["Return"]

# 使用线性回归训练权重
model = LinearRegression()
model.fit(X, y)

# 获取训练得到的权重
weights = {
    "Alpha": model.coef_[0],
    "Beta": model.coef_[1],
    "SharpeRatio": model.coef_[2],
    "Volatility": model.coef_[3]
}

print("训练得到的权重:", weights)

# 用训练好的权重计算每只股票的风险评分
final_results = []

for year_data in all_data:
    # 计算风险评分
    year_data["RiskScore"] = (
        year_data["Alpha"] * weights["Alpha"] +
        year_data["Beta"] * weights["Beta"] +
        year_data["SharpeRatio"] * weights["SharpeRatio"] +
        year_data["Volatility"] * weights["Volatility"]
    )
    final_results.append(year_data)

# 合并所有年份的风险评分数据
final_data = pd.concat(final_results, ignore_index=True)

# 保存最终结果到新文件
final_data.to_csv("trained_risk_assessment_results_2014_2024.csv", index=False)
print("风险评估结果已保存到 'trained_risk_assessment_results_2014_2024.csv'")
