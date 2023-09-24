class Candle(object):
    date = None
    time = None
    open = None
    high = None
    low = None
    close = None

    def __init__(self, date, time, open, high, low, close):
        self.date = date
        self.time = time
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)


# Класс для загрузки файла
class File(object):
    filename = None

    def __init__(self, filename):
        self.close = None
        self.filename = filename

    def get_candle_data(self):
        candles = []
        file = open(self.filename)
        i = 0
        for x in file:
            row = x.strip("\n")
            row = row.split(",")
            if i:
                candle = Candle(row[2], row[3], row[4], row[5], row[6], row[7])
                candles.append(candle)
            i = i + 1
        return candles

    def get_data_parameters(self):
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

    def exportdata(self, filename, toexport):
        with open(self.filename, "w") as file:
            a = len(toexport)
            if a:
                b = len(toexport[0])
            for i in range(0, a):
                for j in range(0, b):
                    toexport[i][j] = str(toexport[i][j])
                towrite = ";".join(toexport[i]) + '\n'
                file.write(towrite)

