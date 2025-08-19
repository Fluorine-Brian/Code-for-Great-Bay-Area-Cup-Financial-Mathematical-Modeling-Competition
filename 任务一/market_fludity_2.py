import pandas as pd
import numpy as np
import os

data_folder = './沪深300成分股的数据/'


def load_data(year):
    stock_info_path = os.path.join(data_folder, f'hs300stocks_{year}.csv')
    kdata_path = os.path.join(data_folder, f'hs300stocks_kdata_{year}.csv')

    # 读取CSV文件
    stock_info = pd.read_csv(stock_info_path)
    kdata = pd.read_csv(kdata_path)

    # 合并成分股信息和每日行情数据
    data = pd.merge(kdata, stock_info[['code', 'weight']], on='code', how='left')
    return data


def min_max_scaling(series):
    if series.max() == series.min():
        return pd.Series([0] * len(series))  # 如果所有值相同，返回全0的系列
    return (series - series.min()) / (series.max() - series.min())


def calculate_daily_liquidity_index(stocks_data):
    # 确保时间列存在并转换为日期格式
    if 'time' not in stocks_data.columns:
        raise KeyError("数据中缺少 'time' 列，请检查数据格式。")

    stocks_data['time'] = pd.to_datetime(stocks_data['time'], errors='coerce')

    # 检查日期转换是否成功
    if stocks_data['time'].isnull().any():
        raise ValueError("日期格式不正确，无法转换为日期。请检查数据中的 'time' 列。")

    # 计算流动性指标
    grouped_data = stocks_data.groupby('time').agg({
        'volume': 'sum',
        'amount': 'sum'
    }).reset_index()

    # 换手率的近似计算
    total_volume = grouped_data['volume'].sum()
    grouped_data['TurnoverRate'] = grouped_data['volume'] / total_volume if total_volume > 0 else 0

    # 标准化数据（Min-Max）
    grouped_data[['volume', 'amount', 'TurnoverRate']] = grouped_data[['volume', 'amount', 'TurnoverRate']].apply(
        min_max_scaling)

    # 计算每日市场流动性（三个指标的平均值）
    grouped_data['MarketLiquidity'] = grouped_data[['volume', 'amount', 'TurnoverRate']].mean(axis=1)

    # 返回每日的流动性指标
    liquidity_df = pd.DataFrame({
        'Date': grouped_data['time'],
        'MarketLiquidity': grouped_data['MarketLiquidity']
    })

    return liquidity_df


# 主程序
if __name__ == "__main__":
    all_liquidity_df = pd.DataFrame()  # 创建一个空的数据框以存储所有年份的每日流动性指标
    for year in range(2014, 2025):
        stocks_data = load_data(year)
        daily_liquidity_df = calculate_daily_liquidity_index(stocks_data)
        all_liquidity_df = pd.concat([all_liquidity_df, daily_liquidity_df], ignore_index=True)

    # 将结果保存到Excel文件
    output_file = '市场流动性每日指标.xlsx'
    all_liquidity_df.to_excel(output_file, index=False)

    print(f"所有年份的每日市场流动性指标已保存到 {output_file}。")
