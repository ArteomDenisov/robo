from time import time
import FuncDivide
import DataLoader


print('start')
file = DataLoader.File("SiCandles.csv")
candles = file.getDataCandle()
file = DataLoader.File("Parameters Si.csv")
parametersWithRange, variables = file.getdataparams()
k1 = parametersWithRange.keys()
startTime = time()
i = 0
varstep = {}
for k in k1:
    if len(parametersWithRange[k][0]):
        varstep[k] = float(parametersWithRange[k][0])
# Расчет моментов входа и выхода из сделок------------------------------------------------------------------------------
signals, ws_criteria, ws_actions = FuncDivide.signalgenerator(candles, [], varstep, all_export=True)
# Расчет капитала и статистика -----------------------------------------------------------------------------------------
result, mmonthly, yearly = FuncDivide.chanelestimate(candles, varstep, signals, all_export=True)
analysis = FuncDivide.deal_analitics(result, varstep)
endtime = time()
# Экспорт расчетов -----------------------------------------------------------------------------------------------------
f = open("Results.csv", "w")
for i in range(0, len(result)):
    for j in range(0, len(result[i])):
        result[i][j] = str(result[i][j])
    towrite = ";".join(result[i]) + '\n'
    f.write(towrite)
f.close()
f = open("Analysis.csv", "w")
for i in range(0, len(analysis)):
    for j in range(0, len(analysis[i])):
        analysis[i][j] = str(analysis[i][j])
    towrite = ";".join(analysis[i]) + '\n'
    f.write(towrite)
f.close()
f = open("Monthly.csv", "w")
for i in range(0, len(mmonthly)):
    for j in range(0, len(mmonthly[i])):
        mmonthly[i][j] = str(mmonthly[i][j])
    towrite = ";".join(mmonthly[i]) + '\n'
    f.write(towrite)
f.close()
f = open("Yearly.csv", "w")
for i in range(0, len(yearly)):
    for j in range(0, len(yearly[i])):
        yearly[i][j] = str(yearly[i][j])
    towrite = ";".join(yearly[i]) + '\n'
    f.write(towrite)
f.close()

print(endtime - startTime)
print('finish')

