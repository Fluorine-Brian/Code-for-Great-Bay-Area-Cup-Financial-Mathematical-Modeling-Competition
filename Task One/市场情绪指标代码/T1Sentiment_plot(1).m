% 获取当前工作目录
folderPath = pwd;  

% 设置输出文件名
outputFilename = 'Combined_Market_Sentiment_Indicators.xlsx';

% 创建文件名模式以匹配所有文件
fileList = dir(fullfile(folderPath, 'Market_Sentiment_Indicators_*.xlsx'));

% 初始化最终结果表格
allData = [];

% 遍历每个Excel文件并合并数据
for k = 1:length(fileList)
    % 读取当前Excel文件的数据
    filePath = fullfile(folderPath, fileList(k).name);
    data = readtable(filePath);
    
    % 将当前文件的数据追加到allData中
    allData = [allData; data];
end

% 输出合并结果到新的Excel文件
writetable(allData, outputFilename);

% 正确的文件输出信息
disp(['所有文件的数据已合并到文件: ', outputFilename]);

% 读取合并后的数据
allData = readtable(outputFilename); 

% 将日期列转换为MATLAB的日期格式
allData.Date = datetime(allData.Date, 'Format', 'yyyy-MM-dd');

% 绘制折线图
figure;

% 绘制VIX
subplot(4, 1, 1);
plot(allData.Date, allData.VIX, 'b-', 'LineWidth', 1.5);
title('VIX (波动性指数)');
xlabel('Date');
ylabel('VIX');
grid on;

% 绘制MFI
subplot(4, 1, 2);
plot(allData.Date, allData.MFI, 'g-', 'LineWidth', 1.5);
title('MFI (资金流向指数)');
xlabel('Date');
ylabel('MFI');
grid on;

% 绘制ISI
subplot(4, 1, 3);
plot(allData.Date, allData.ISI, 'r-', 'LineWidth', 1.5);
title('ISI (投资者情绪指数)');
xlabel('Date');
ylabel('ISI');
grid on;

% 绘制VaR
subplot(4, 1, 4);
plot(allData.Date, allData.VaR, 'k-', 'LineWidth', 1.5);
title('VaR (风险价值)');
xlabel('Date');
ylabel('VaR');
grid on;

% 调整图表布局
sgtitle('沪深300市场情绪指标随时间的变化');
