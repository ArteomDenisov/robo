def pusharray(array, a):
    array.append(a)
    array.pop(0)
    return array


def kanaliMax(candles, chanel):
    i = 0
    indicator = []
    lfm = []
    chanel = int(chanel)
    for candle in candles:
        if i == chanel:
            lfm = candles[0:chanel]
        if i > chanel:
            lfm = pusharray(lfm, candles[i-1])
            maxC = max(candle.high for candle in lfm)
        else:
            maxC = 1000000
        indicator.append(maxC)
        i += 1
    return indicator


def kanaliMin(candles, chanel):
    i = 0
    indicator = []
    minC = 1000000
    lfm = []
    chanel = int(chanel)
    for candle in candles:
        if i == chanel:
            lfm = candles[0:chanel]
        if i > chanel:
            lfm = pusharray(lfm, candles[i-1])
            minC = min(candle_min.low for candle_min in lfm)
        else:
            minC = 0
        indicator.append(minC)
        i += 1
    return indicator


def pogloshenie_long(candles, canal, b_canal, s_canal, candle_pogl, all_export=False):
    i = 0
    indicator = []
    to_export = []
    telo = []
    pogl = 0
    b_canal = int(b_canal)
    s_canal = int(s_canal)
    candle_pogl = int(candle_pogl)
    b_razmer = 0
    s_razmer = 0
    for candle in candles:
        telo.append(candle.close - candle.open)
        if candle.high >= canal[i]:
            if i > s_canal and i > b_canal:
                temp = 0
                lfr = candles[i - b_canal + 1: i]
                for candle_razmer in lfr:
                    temp = temp + abs(candle_razmer.close - candle_razmer.open)
                b_razmer = temp / b_canal
                temp = 0
                lfr = candles[i - s_canal + 1: i]
                for candle_razmer in lfr:
                    temp = temp + abs(candle_razmer.close - candle_razmer.open)
                s_razmer = temp / s_canal
                if s_razmer >= b_razmer and candle_pogl < i + 1:
                    pogl = candles[i - 1].close
                    for x in reversed(range(i - candle_pogl, i)):
                        pogl = pogl - telo[x]
                else:
                    pogl = 0
        indicator.append(pogl)
        i += 1
        if all_export:
            to_export.append([b_razmer, s_razmer, candle.close - candle.open])
    return indicator


def pogloshenie_short(candles, canal, bCanal, sCanal, candlePogl, all_export=False):
    i = 0
    indicator = []
    telo = []
    bRazmer = 0
    sRazmer = 0
    pogl = 0
    if all_export:
        to_export = []
    bCanal = int(bCanal)
    sCanal = int(sCanal)
    candlePogl = int(candlePogl)
    for candle in candles:
        telo.append(candle.close - candle.open)
        if candle.low <= canal[i]:
            if i > sCanal and i > bCanal:
                temp = 0
                lfr = candles[i - bCanal + 1: i]
                for candle in lfr:
                    temp = temp + abs(candle.close - candle.open)
                bRazmer = temp / bCanal
                temp = 0
                lfr = candles[i - sCanal + 1: i]
                for candle_temp in lfr:
                    temp = temp + abs(candle_temp.close - candle_temp.open)
                sRazmer = temp / sCanal
                if sRazmer >= bRazmer and candlePogl < i + 1:
                    pogl = candles[i - 1].close
                    for x in reversed(range(i - candlePogl, i)):
                        pogl = pogl - telo[x]
                else:
                    pogl = 0
        indicator.append(pogl)
        if all_export:
            to_export.append([bRazmer, sRazmer, telo[i]])
        i += 1
    return indicator


def mmCLose(candles, leverage, mm_speed, mm_average, mm_const):
    i = 0
    indicator = []
    prirost = []
    temp = []
    leverage = float(leverage)
    mm_const = float(mm_const)
    mm_speed = int(mm_speed)
    mm_average = int(mm_average)
    for candle in candles:
        mult = leverage
        if i > mm_speed - 1:
            prirost.append((candle.close - candles[i - mm_speed].open) / candles[i - mm_speed].open)
            if i == mm_speed + mm_average:
                temp = prirost[0:mm_average]
                sum_prirost = sum(temp)
                if sum_prirost != 0:
                    mult = leverage * mm_average * mm_const / abs(sum_prirost)
                if mult > leverage:
                    mult = leverage
                mult = round(mult, 5)
        if i > mm_speed + mm_average:
            temp = pusharray(temp, prirost[i - mm_speed - 1])
            sum_prirost = sum(temp)
            if sum_prirost != 0:
                mult = leverage * mm_average * mm_const / abs(sum_prirost)
            if mult > leverage:
                mult = leverage
            mult = round(mult, 5)
        indicator.append(mult)
        i += 1
    return indicator
