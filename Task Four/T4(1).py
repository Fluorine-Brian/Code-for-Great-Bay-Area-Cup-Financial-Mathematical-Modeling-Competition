import pandas as pd
import numpy as np
import zipfile
import os

# 步骤 1：解压并加载沪深300成分股数据
hs300_zip_path = r"E:\大学\数学建模\2024粤港澳大湾区数学建模\沪深300成分股的数据.zip"

# 解压缩文件内容到指定目录
with zipfile.ZipFile(hs300_zip_path, 'r') as zip_ref:
    zip_ref.extractall("E:/大学/数学建模/2024粤港澳大湾区数学建模/沪深300成分股的数据/extracted_hs300_data")

# 加载每年的沪深300数据，并使用“weight”列的均值作为年收益的代理值
hs300_data_dir = 'E:/大学/数学建模/2024粤港澳大湾区数学建模/沪深300成分股的数据/'
hs300_annual_files = [f for f in os.listdir(hs300_data_dir) if f.startswith('hs300stocks_') and f.endswith('.csv')]

# 存储年收益率
annual_returns = {}
for file_name in hs300_annual_files:
    year = int(file_name.split('_')[-1].split('.')[0])
    file_path = os.path.join(hs300_data_dir, file_name)
    hs300_data = pd.read_csv(file_path)
    if 'weight' in hs300_data.columns:
        annual_returns[year] = hs300_data['weight'].mean()

# 步骤 2：使用几何平均公式计算市场平均收益率 R_m
N = len(annual_returns)
R_m = (np.prod([1 + r for r in annual_returns.values()]) ** (1 / N)) - 1

# 步骤 3：加载并处理10年期国债数据
treasury_data_path = '/mnt/data/十年国债每月数据.xlsx'
treasury_data = pd.read_excel(treasury_data_path, header=None)
treasury_data.columns = ['Date', 'Yield']
treasury_data['Date'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(treasury_data['Date'], 'D')
R_f = treasury_data['Yield'].mean() / 100  # 转换百分比为小数

# 步骤 4：计算风险溢价 RP
RP = R_m - R_f

# 步骤 5：计算合理收益预期 E(R)
E_R = R_f + RP

# 输出结果
print("市场平均收益率 (R_m):", R_m)
print("无风险收益率 (R_f):", R_f)
print("风险溢价 (RP):", RP)
print("合理收益预期 (E(R)):", E_R)
