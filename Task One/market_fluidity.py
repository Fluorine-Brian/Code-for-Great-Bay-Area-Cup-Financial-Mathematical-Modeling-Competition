import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


def calculate_liquidity_index(stocks_data):
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

    # 计算每年的流动性指标
    yearly_liquidity = grouped_data.groupby(grouped_data['time'].dt.year).agg({
        'volume': 'mean',
        'amount': 'mean',
        'TurnoverRate': 'mean'
    }).reset_index()

    # 计算市场流动性（三个指标的平均值）
    yearly_liquidity['MarketLiquidity'] = yearly_liquidity[['volume', 'amount', 'TurnoverRate']].mean(axis=1)

    # 返回流动性指标
    liquidity_df = pd.DataFrame({
        'Year': yearly_liquidity['time'].astype(int),  # 将年份设置为整数格式
        'AverageVolume': yearly_liquidity['volume'],
        'AverageAmount': yearly_liquidity['amount'],
        'AverageTurnoverRate': yearly_liquidity['TurnoverRate'],
        'MarketLiquidity': yearly_liquidity['MarketLiquidity']
    })

    return liquidity_df


def visualize_liquidity_index(all_liquidity_df):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    # 确保年份按顺序排序
    all_liquidity_df = all_liquidity_df.sort_values(by='Year')

    # 绘制折线图
    plt.figure(figsize=(6, 10))
    plt.plot(all_liquidity_df['Year'], all_liquidity_df['AverageVolume'], marker='o', label='平均成交量')
    plt.plot(all_liquidity_df['Year'], all_liquidity_df['AverageAmount'], marker='o', label='平均成交额')
    plt.plot(all_liquidity_df['Year'], all_liquidity_df['AverageTurnoverRate'], marker='o', label='平均换手率')
    plt.plot(all_liquidity_df['Year'], all_liquidity_df['MarketLiquidity'], marker='o', label='市场流动性')

    plt.title('2014-2024年市场流动性指标', fontsize=16, fontweight='bold')
    plt.xlabel('年份', fontsize=14, fontweight='bold')
    plt.ylabel('流动性指标（标准化后）', fontsize=14, fontweight='bold')
    plt.xticks(all_liquidity_df['Year'], rotation=45)  # 显示年份并旋转标签
    plt.xticks(fontsize=12, fontweight='bold')
    plt.yticks(fontsize=12, fontweight='bold')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


# 主程序
if __name__ == "__main__":
    all_liquidity_df = pd.DataFrame()  # 创建一个空的数据框以存储所有年份的流动性指标
    for year in range(2014, 2025):
        stocks_data = load_data(year)
        liquidity_df = calculate_liquidity_index(stocks_data)
        all_liquidity_df = pd.concat([all_liquidity_df, liquidity_df], ignore_index=True)

        # 打印每年的流动性指标
        print(f"{year} 年的平均成交量: {liquidity_df['AverageVolume'].mean():.2f}, "
              f"平均成交额: {liquidity_df['AverageAmount'].mean():.2f}, "
              f"平均换手率: {liquidity_df['AverageTurnoverRate'].mean():.4f}, "
              f"市场流动性: {liquidity_df['MarketLiquidity'].mean():.4f}")

    # # 检查最终合并的数据框是否为空
    # if not all_liquidity_df.empty:
    #     visualize_liquidity_index(all_liquidity_df)
    # else:
    #     print("没有有效的流动性指标数据可供绘图。")
