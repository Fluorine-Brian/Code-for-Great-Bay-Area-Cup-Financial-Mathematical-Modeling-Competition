% 读取数据
data = readtable('hs300stocks_kdata_2022.csv'); 
dates = unique(data.time);  % 使用实际的日期列名
numDates = length(dates);
alpha = 0.95; % VaR和CVaR置信水平

% 初始化各个情绪指标
VIX = zeros(numDates, 1);  
MFI = zeros(numDates, 1);  
ISI = zeros(numDates, 1);  
VaR_values = zeros(numDates, 1);

% 循环日期计算每日的情绪指标
for i = 2:numDates
    dailyData = data(data.time == dates(i), :);  % 使用实际的日期列名
    returns = diff(log(dailyData.close));  % 使用实际的收盘价列名计算对数收益率
    
    % 1. 波动性指数（VIX）
    VIX(i) = sqrt(var(returns));
    
    % 2. 资金流向指数（MFI）
    typicalPrice = (dailyData.high + dailyData.low + dailyData.close) / 3;  % 使用实际列名
    moneyFlow = typicalPrice .* dailyData.volume;
    posFlow = sum(moneyFlow(returns > 0));
    negFlow = sum(moneyFlow(returns < 0));
    MFI(i) = 100 - (100 / (1 + posFlow / negFlow));
    
    % 3. 投资者情绪指数（ISI）
    ISI(i) = sum((dailyData.close - dailyData.open) .* dailyData.volume) / sum(dailyData.volume);
    
    % 4. VaR
    mu = mean(returns);
    sigma = std(returns);
    VaR_values(i) = mu + sigma * norminv(alpha);
end

% 创建表格
T = table(dates(2:end), VIX(2:end), MFI(2:end), ISI(2:end), VaR_values(2:end), ...
    'VariableNames', {'Date', 'VIX', 'MFI', 'ISI', 'VaR'});

% 输出结果到Excel文件
outputFilename = 'Market_Sentiment_Indicators_2022.xlsx';
writetable(T, outputFilename);

disp(['市场情绪指标已导出到文件: ', 'Market_Sentiment_Indicators_2022.xlsx']);