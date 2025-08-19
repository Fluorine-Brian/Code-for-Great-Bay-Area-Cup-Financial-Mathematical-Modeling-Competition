import numpy as np
import pandas as pd
import os

data_folder = "./沪深300成分股的数据/"


# 温莎化处理函数
def winsorize(series, lower_percentile=5, upper_percentile=95):
    lower_limit = np.percentile(series, lower_percentile)
    upper_limit = np.percentile(series, upper_percentile)
    return np.clip(series, lower_limit, upper_limit)


# 加载数据的函数，包括成分股信息和行情数据的合并
def load_data(year):
    stock_info_path = os.path.join(data_folder, f'hs300stocks_{year}.csv')
    kdata_path = os.path.join(data_folder, f'hs300stocks_kdata_{year}.csv')

    # 读取CSV文件
    stock_info = pd.read_csv(stock_info_path)
    kdata = pd.read_csv(kdata_path)

    # 合并成分股信息和每日行情数据
    data = pd.merge(kdata, stock_info[['code', 'weight']], on='code')
    return data


# 计算每日收益率的函数
def calculate_daily_returns(data):
    # 计算前一日收盘价
    data['prev_close'] = data.groupby('code')['close'].shift(1)
    # 计算每日收益率
    data['daily_return'] = (data['close'] - data['prev_close']) / data['prev_close']
    # 去掉因移动计算而产生的NaN值
    data = data.dropna(subset=['daily_return'])
    return data


# 计算每日温莎化处理后的平均收益率
def calculate_daily_average_return(data):
    # 温莎化处理每日收益率，消除极端值的影响
    data['daily_return_winsorized'] = data.groupby('time')['daily_return'].transform(
        lambda x: winsorize(x, lower_percentile=5, upper_percentile=95)
    )
    # 按日期计算温莎化后的每日平均收益率
    daily_index_returns = data.groupby('time')['daily_return_winsorized'].mean().reset_index()
    daily_index_returns.columns = ['Date', 'AverageDailyReturn']  # 重命名列
    return daily_index_returns


# 主函数，遍历所有年份并计算每日平均收益率
def main():
    all_daily_returns = pd.DataFrame()  # 创建一个空的数据框以存储所有年份的每日平均收益率

    # 遍历2014至2024年
    for year in range(2014, 2025):
        print(f"正在处理{year}年的数据...")
        # 加载数据
        data = load_data(year)
        # 计算每日收益率
        data = calculate_daily_returns(data)
        # 计算每日平均收益率
        daily_returns_df = calculate_daily_average_return(data)
        # 将每年的每日收益率数据合并
        all_daily_returns = pd.concat([all_daily_returns, daily_returns_df], ignore_index=True)

    # 将结果保存到Excel文件
    output_file = '平均每日收益率_2014_2024.xlsx'
    all_daily_returns.to_excel(output_file, index=False)

    print(f"每日平均收益率数据已保存至 {output_file}")


# 执行主函数
if __name__ == "__main__":
    main()
