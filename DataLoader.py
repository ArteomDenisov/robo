class Candle(object):
    date = None
    time = None
    open = None
    high = None
    low = None
    close = None
    garant = None
    signal = None

    def __init__(self, date, time, open, high, low, close, garant, signal):
        self.date = date
        self.time = time
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.garant = float(garant)
        self.signal = int(signal)



# Класс для загрузки файла
class File(object):
    filename = None

    def __init__(self, filename):
        self.close = None
        self.filename = filename

    def getDataCandle(self):
        candles = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            row = row.split(";")  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if i:
                candle = Candle(row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
                candles.append(candle)
            i = i + 1
        return candles

    def getDataCandle_1m(self):
        candles_1m = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            row = row.split(";")  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if i:
                candle_1m = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                             row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19],
                             row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29],
                             row[30], row[31]]
                for j in range(2, 32):
                    candle_1m[j] = int(candle_1m[j])
                candles_1m.append(candle_1m)
            i = i + 1
        return candles_1m


    def getdataparams(self):
        temp = []
        temv = []
        file = open(self.filename)
        i = 0
        size = 0
        for x in file:
            row = x.strip("\n")
            param = []
            variable = []
            variablefordict = []
            row = row.split(";")
            if i == 0:
                size = len(row)
            if i:
                param = [row[0], [row[1], row[2], row[3], row[4]]]
                if size > 5:
                    for z in range(5, size):
                        variable.append(row[z])
                    variablefordict = [row[0], variable]
            temp.append(param)
            temv.append(variablefordict)
            i += 1
        del temp[0]
        del temv[0]
        params = dict(temp)
        variables = dict(temv)
        return [params, variables]


    def getdataparams_genetic(self):
        temp = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            param = []
            row = row.split(";")
            if i:
                if row[5] == 'int':
                    param = [row[0], [row[5], int(row[1]), int(row[2]), int(row[3]), int(row[4])]]
                elif row[5] == 'double':
                    param = [row[0], [row[5], float(row[1]), float(row[2]), float(row[3]), float(row[4])]]
                else:
                    param = [row[0], [row[5], float(row[1])]]
            temp.append(param)
            i += 1
        del temp[0]
        params = dict(temp)
        return params

    def getdataparams_multi(self):
        params = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            temp = []
            row = row.split(";")
            if i:
                temp = list(row)
                for e in range(2, len(temp)):
                    if temp[1] == 'int' or temp[1] == 'bool':
                        temp[e] = int(temp[e])
                    if temp[1] == 'float':
                        temp[e] = float(temp[e])
                params.append([temp[0], temp[2:]])
            i += 1
        del temp[0]
        params = dict(params)
        return params



    def load_monthly(self):
        months = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            row = row.split(";")
            if i > 2:
                param = [float(row[1]), float(row[2])]
                months.append(param)
            i += 1
        return months




    def exportdata(self, filename, toexport):
        file = open(self.filename, "w")
        a = len(toexport)
        if a:
            b = len(toexport[0])
        for i in range(0, a):
            for j in range(0, b):
                toexport[i][j] = str(toexport[i][j])
            towrite = ";".join(toexport[i]) + '\n'
            file.write(towrite)
        file.close

