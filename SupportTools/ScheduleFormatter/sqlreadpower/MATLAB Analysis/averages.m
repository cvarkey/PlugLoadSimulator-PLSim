%summary.IdlePeriodAvg = nanmean(double(IdleSummaryreformatted(:,5:2163)),2);
summary.IdlePeriodStdev = nanstd(double(subjectIdlePeriod.all),0,2);
summary.IdlePeriodAvg = nanmean(subjectIdlePeriod.all,2)

nanstd(double(subjectIdlePeriod.all),0,2)
figure (1)
summary.IdlePeriodAvgSorted=sort(summary.IdlePeriodAvg,1)
plot (summary.IdlePeriodAvgSorted)
title 'Idle Period Averages';
xlabel 'Sample Number';
ylabel 'Period Length (min)';
figure (2)
hist(summary.IdlePeriodAvg,20)
title 'Period Averages Histogram';
xlabel 'Period Length (min)';
ylabel 'Sample Frequency';
figure (3)
bar (subjectIdleAverageSorted)
figure (4)
hist(subjectIdleAverage,30)