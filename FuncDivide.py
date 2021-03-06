from time import time
from multiprocessing import Pool
from master import DataLoader
import copy
import numpy as np
import math
# ----------------------------------------------------------------------------------------------------------------------
# comeback -------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def pusharray(array, a):
    array.append(a)
    array.pop(0)
    return array


def deal_close_price(candles, candles_1m):
    arr_long = []
    arr_short = []
    i15 = 0
    i1 = 0
    for candle in candles:
        if candle.date == candles_1m[i1].date and candle.time == candles_1m[i1].time:
            pass
        i15 += 1
    #
    #
    #
    #
    #
    return arr_long, arr_short


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


def chanelloader(params, dimen0, dimen1, i):
    # -----------------------------------------------------------------------------------------------------------------
    # ???????????????????? ????????????????????--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    vary0 = ""
    vary1 = ""
    vary2 = ''
    a = 0
    b = 0
    c = 0
    counter = 0
    parameter = {}
    k1 = params.keys()
    for k in k1:
        parameter[k] = params[k][0]
        if parameter[k] == "Est":
            if counter == 2:
                c = i // (dimen0 * dimen1)
                parameter[k] = params[k][1] + c * params[k][2]
                vary2 = parameter[k]
                counter += 1
            if counter == 1:
                b = (i % (dimen0 * dimen1)) // dimen0
                parameter[k] = params[k][1] + b * params[k][2]
                vary1 = parameter[k]
                counter += 1
            if counter == 0:
                a = i % dimen0
                parameter[k] = params[k][1] + a * params[k][2]
                vary0 = parameter[k]
                counter += 1
    coordinates = [a, b, c, vary0, vary1, vary2]
    return parameter, coordinates


def signalgenerator(candles, candles_1m, params, arr_chanel_long=None, arr_chanel_short=None, arr_pogl_long=None,
                    arr_pogl_short=None, all_export=False):
    # -----------------------------------------------------------------------------------------------------------------
    # ???????????????????? ????????????????????--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    fantomDeals = int(params['fantomDeals'])
    pogloshenieLong = int(params['pogloshenieLong'])
    pogloshenieShort = int(params['pogloshenieShort'])
    oknoLong = int(params['oknoLong'])
    oknoShort = int(params['oknoShort'])
    if 'stop_loss_close_long' in params:
        stop_loss_close_long = int(params['stop_loss_close_long'])
    else:
        stop_loss_close_long = 0
    if 'stop_loss_close_short' in params:
        stop_loss_close_short = int(params['stop_loss_close_short'])
    else:
        stop_loss_close_short = 0
    if 'stop_loss_proboi_long' in params:
        stop_loss_proboi_long = int(params['stop_loss_proboi_long'])
    else:
        stop_loss_proboi_long = 0
    if 'stop_loss_proboi_short' in params:
        stop_loss_proboi_short = int(params['stop_loss_proboi_short'])
    else:
        stop_loss_proboi_short = 0
    if 'no15' in params:
        no15 = int(params['no15'])
    else:
        no15 = 0
    if 'no16' in params:
        no16 = int(params['no16'])
    else:
        no16 = 0
    if 'no17' in params:
        no17 = int(params['no17'])
    else:
        no17 = 0
    if 'no18' in params:
        no18 = int(params['no18'])
    else:
        no18 = 0
    if 'm1_enter_long' in params:
        m1_enter_long = int(params['m1_enter_long'])
    else:
        m1_enter_long = 0
    if 'm1_enter_short' in params:
        m1_enter_short = int(params['m1_enter_short'])
    else:
        m1_enter_short = 0
    if 'm1_exit_long' in params:
        m1_exit_long = int(params['m1_exit_long'])
    else:
        m1_exit_long = 0
    if 'm1_exit_short' in params:
        m1_exit_short = int(params['m1_exit_short'])
    else:
        m1_exit_short = 0
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # ????????????????????--------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    exitLong = int(params['exitLong'])
    exitShort = int(params['exitShort'])
    banLong = int(params['banLong'])
    hammerLong = int(params['hammerLong'])
    hammerLongFV = int(params['hammerLongFV'])
    banShort = int(params['banShort'])
    hammerShort = int(params['hammerShort'])
    hammerShortFV = int(params['hammerShortFV'])
    contrL = float(params['contrL'])
    contrS = float(params['contrS'])
    hammerContLong = int(params['hammerContLong'])
    hammerContrShort = int(params['hammerContrShort'])
    otnosProdlenLong = float(params['otnosProdlenLong'])
    otnosProdlenShort = float(params['otnosProdlenShort'])
    hammerProdlenLong = int(params['hammerProdlenLong'])
    hammerProdlenShort = int(params['hammerProdlenShort'])
    quatroLong = int(params['quatroLong'])
    quatroShort = int(params['quatroShort'])
    signalPoglLong = int(params['signalPoglLong'])
    signalPoglShort = int(params['signalPoglShort'])
    okno_x_long = float(params['okno_x_long'])
    okno_y_long = float(params['okno_y_long'])
    okno_x_short = float(params['okno_x_short'])
    okno_y_short = float(params['okno_y_short'])
    if 'm1_delay' in params:
        m1_delay = int(params['m1_delay'])
    else:
        m1_delay = 0
    if 'm1_duration' in params:
        m1_duration = int(params['m1_duration'])
    else:
        m1_duration = 1
    if 'stop_loss_percent_long' in params:
        stop_loss_percent_long = float(params['stop_loss_percent_long'])
    else:
        stop_loss_percent_long = 2000
    if 'stop_loss_percent_short' in params:
        stop_loss_percent_short = float(params['stop_loss_percent_short'])
    else:
        stop_loss_percent_short = 2000
    prosk = float(params['prosk'])
    gap = int(params['gap'])
    # ------------------------------------------------------------------------------------------------------------------
    # ???????? ?????????????? ??????????????????????--------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    if arr_chanel_long is None:
        arr_chanel_long = kanaliMax(candles, params['chanelLong'])
    if arr_chanel_short is None:
        arr_chanel_short = kanaliMin(candles, params["chanelShort"])
    if arr_pogl_long is None:
        arr_pogl_long = pogloshenie_long(candles, arr_chanel_long, params['bCanalLong'], params['sCanalLong'],
                                         params['candlePoglLong'])
    if arr_pogl_short is None:
        arr_pogl_short = pogloshenie_short(candles, arr_chanel_short, params['bCanalShort'],
                                           params['sCanalShort'],
                                           params['candlePoglShort'])
    # -----------------------------------------------------------------------------------------------------------------
    # ???????? ?????????????????????????? ????????????????????
    # -----------------------------------------------------------------------------------------------------------------
    quant = 0
    fQuant = 0
    counterLong = 0
    counterShort = 0
    signalLong = 0
    signalShort = 0
    signalLongP = 0
    signalShortP = 0
    fCounterLong = 0
    fCounterShort = 0
    fSignalLong = 0
    fSignalShort = 0
    ws_actions = 0
    dopS_counter = 0
    dopL_counter = 0
    hammer = 0
    time_from_exit_long = 0
    time_from_exit_short = 0
    # ?????????????????????? ??????????????????---------------------------------------------------------------------------------------------
    c_long_deals = 0
    c_short_deals = 0
    c_bhl = 0
    c_bhs = 0
    c_kbhl = 0
    c_kbhs = 0
    c_pogl_long = 0
    c_pogl_short = 0
    c_sl_long = 0
    c_sl_short = 0
    c_prodl_long = 0
    c_prodl_short = 0
    c_okno_long = 0
    c_okno_short = 0
    i = 0
    arr = []
    longCondition = False          # ??????????????????, ?????? ?????????????????????????? ???????????????? ?????? ????????
    shortCondition = False         # ??????????????????, ?????? ?????????????????????????? ???????????????? ?????? ????????
    pogloshenije = False           # ??????????????????, ?????? ???????????????????? ?????? ?????????? ??????????????????, ???? ???????? ???????????????????? ????????????????
    # Long -------------------------------------------------------------------------------------------------------------
    simple_long_enter = False
    time_long_exit = False
    bh_long_exit = False
    # Short ------------------------------------------------------------------------------------------------------------
    simple_short_enter = False
    time_short_exit = False
    bh_short_exit = False
    # ???????????????? ???????????????????? ----------------------------------------------------------------------------------------------
    razvorot_from_long = False
    razvorot_from_short = False
    comeback = False
    # ------------------------------------------------------------------------------------------------------------------
    # ???????????????? ??????????????
    # ------------------------------------------------------------------------------------------------------------------
    pogl_long = 0
    pogl_short = 0
    stop_loss_long_value = 0
    stop_loss_short_value = 0
    # deal_counter = 0
    for candle in candles:
        # ?????????????????????????? ????????????????????--------------------------------------------------------------------------------------
        deal_type1 = ''
        deal_type2 = ''
        deal_type3 = ''
        buyPrice = 0
        sellPrice = 0
        closeLongPrice = 0
        closeShortPrice = 0
        # ???????????? ??????????????-----------------------------------------------------------------------------------------------
        maxC = arr_chanel_long[i]
        minC = arr_chanel_short[i]
        if hammer > 0:
            hammer = hammer - 1
        time_from_exit_long += 1
        time_from_exit_short += 1
        # -------------------------------------------------------------------------------------------------------------
        # ???????????????????? ??????
        # --------------------------------------------------------------------------------------------------------------------------
        if no15 and 20150000 < int(candle.date) < 20160000 and hammer < 1000:
            hammer = 10000
        if no15 and int(candle.date) > 20160000 and hammer > 900:
            hammer = 0
        if no16 and 20160000 < int(candle.date) < 20170000 and hammer < 1000:
            hammer = 10000
        if no16 and int(candle.date) > 20170000 and hammer > 900:
            hammer = 0
        if no17 and 20170000 < int(candle.date) < 20180000 and hammer < 1000:
            hammer = 10000
        if no17 and int(candle.date) > 20180000 and hammer > 900:
            hammer = 0
        if no18 and 20180000 < int(candle.date) < 20190000 and hammer < 1000:
            hammer = 10000
        if no18 and int(candle.date) > 20190000 and hammer > 900:
            hammer = 0
        # -------------------------------------------------------------------------------------------------------------
        # ???????????????? ????????????????
        # --------------------------------------------------------------------------------------------------------------------------
        if fCounterLong >= exitLong and fQuant == 1:
            fQuant = 0
            fCounterLong = 0
            deal_type1 = 'Phanton long close'
            if fSignalShort > 0:
                if hammer < hammerProdlenLong and fSignalLong / fSignalShort <= otnosProdlenLong \
                        and hammerProdlenLong > 0:
                    hammer = hammerProdlenLong
                    c_prodl_long += 1
            fSignalLong = 0
            fSignalShort = 0
        # ???????????????? ????????
        if fCounterShort >= exitShort and fQuant == -1:
            fQuant = 0
            fCounterShort = 0
            deal_type1 = 'Phantom short close'
            if fSignalLong > 0:
                if hammer < hammerProdlenShort and fSignalShort / fSignalLong <= otnosProdlenShort \
                        and hammerProdlenShort > 0:
                    hammer = hammerProdlenShort
                    c_prodl_short += 1
            fSignalShort = 0
            fSignalLong = 0
        # -------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????
        # -------------------------------------------------------------------------------------------------------------
        if longCondition:
            if counterLong >= exitLong or (candle.date == '20160623' and int(candle.time) > int('220000')):
                time_long_exit = True
                bh_long_exit = True
                deal_type1 = 'Exit long'
                if candle.date == '20160623' and int(candle.time) > int('220000'):
                    deal_type1 = 'Brexit long'
            if stop_loss_close_long and candles[i-1].close < stop_loss_long_value and counterLong:
                time_long_exit = True
                bh_long_exit = True
                deal_type1 = 'Exit long'
                c_sl_long += 1
            if stop_loss_proboi_long and candle.low < stop_loss_long_value and counterLong:
                time_long_exit = True
                bh_long_exit = True
                deal_type1 = 'Exit long'
                c_sl_long += 1
            # ???????????????????? ???????? ------------------------------------------------------------------------------------------
            if pogloshenije and pogl_long > candles[i - 1].close and quant >= 0:
                deal_type1 = 'Pogl long'
                c_pogl_long += 1
                time_long_exit = True
                bh_long_exit = True
                if comeback:
                    bh_short_exit = False
                comeback = False
                pogloshenije = False
            # ???????????????? ?????????? ?????????????? ?????????????? ---------------------------------------------------------------------------
            if time_long_exit and quant == -1:
                time_long_exit = False
                time_short_exit = True
        # ?????????? ???? ?????????????????????? ????????????, ???????? ???? ?????? ?????????????????? -------------------------------------------------------
        if quant == 1 and hammer == 1 and False:
            time_long_exit = True
            deal_type1 = 'Exit long'
        # --------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????: ??????????????
        # --------------------------------------------------------------------------------------------------------------
        if shortCondition:
            if counterShort >= exitShort or (candle.date == '20160623' and int(candle.time) > int('220000')):
                time_short_exit = True
                bh_short_exit = True
                deal_type1 = 'Exit short time'
                if candle.date == '20160623' and int(candle.time) > int('220000'):
                    deal_type1 = 'Brexit short'
            if pogloshenije and candles[i - 1].close >= pogl_short > 0 and quant <= 0:
                time_short_exit = True
                bh_short_exit = True
                c_pogl_short += 1
                deal_type1 = 'Pogl short'
                pogloshenije = False
            if stop_loss_close_short and candles[i-1].close > stop_loss_short_value > 0:
                time_short_exit = True
                bh_short_exit = True
                deal_type1 = 'Exit short'
                c_sl_short += 1
            if stop_loss_proboi_short and candle.high > stop_loss_short_value > 0:
                time_short_exit = True
                bh_short_exit = True
                deal_type1 = 'Exit short'
                c_sl_short += 1
            if time_short_exit and quant == 1:
                time_short_exit = False
                time_long_exit = True
        # ?????????? ???? ?????????????????????? ???????????? ???? ?????????????????? ????
        if quant == -1 and hammer == 1 and False:
            time_short_exit = True
            deal_type1 = 'Exit short'
        # --------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????????: ???????????????? -----------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if time_short_exit:
            closeShortPrice = candle.open + prosk
            if stop_loss_proboi_short and candle.high > stop_loss_short_value:
                closeShortPrice = stop_loss_short_value + prosk
            if stop_loss_proboi_short and candle.open > closeShortPrice:
                closeShortPrice = candle.open + prosk
            if candle.close - candle.open > gap:
                closeShortPrice = candle.close + prosk
            if closeShortPrice > candle.high:
                closeShortPrice = candle.high
            if m1_exit_short == 1:
                closeShortPrice = 0
                if m1_delay + m1_duration > 30:
                    m1_delitel = 30 - m1_delay
                else:
                    m1_delitel = m1_duration
                for m1 in range(m1_delay + 2, m1_delay + m1_delitel + 2):
                    closeShortPrice = closeShortPrice + candles_1m[i][m1]
                closeShortPrice = closeShortPrice / m1_delitel
            if quant == 0:
                closeShortPrice = 0
            quant = 0
            pogl_short = 0
            stop_loss_short_value = 0
            time_short_exit = False
            pogloshenije = False
            time_from_exit_short = 0
            if razvorot_from_short:
                buyPrice = closeShortPrice
                quant = 1
                razvorot_from_short = False
        if bh_short_exit:
            hammer = hammerShortFV
            shortCondition = False
            if signalShort > banShort:
                hammer = hammerShort
                if hammerShort:
                    c_bhs += 1
            if signalLong and hammerContrShort:
                if signalShort / signalLong >= contrS and signalShort + signalLong > quatroShort:
                    if hammer == 0 or hammerContrShort <= hammerShort:
                        hammer = hammerContrShort
                        c_kbhs += 1
            # Brexit
            if candle.date == '20160623' and int(candle.time) > int('220000') and hammer < 20:
                hammer = 20
            bh_short_exit = False
            counterShort = 0
            signalShort = 0
            signalLong = 0
            signalLongP = 0
            signalShortP = 0
        if time_long_exit:
            closeLongPrice = candle.open - prosk
            if stop_loss_proboi_long and candle.low < stop_loss_long_value:
                closeLongPrice = stop_loss_long_value - prosk
            if stop_loss_proboi_long and candle.open < closeLongPrice:
                closeLongPrice = candle.open - prosk
            if candle.open - candle.close > gap:
                closeLongPrice = candle.close - prosk
            if closeLongPrice < candle.low:
                closeLongPrice = candle.low
            if m1_exit_long == 1:
                closeLongPrice = 0
                if m1_delay + m1_duration > 30:
                    m1_delitel = 30 - m1_delay
                else:
                    m1_delitel = m1_duration
                for m1 in range(m1_delay + 2, m1_delay + m1_delitel + 2):
                    closeLongPrice = closeLongPrice + candles_1m[i][m1]
                closeLongPrice = closeLongPrice / m1_delitel
            if quant == 0:
                closeLongPrice = 0
            quant = 0
            pogl_long = 0
            stop_loss_long_value = 0
            time_long_exit = False
            pogloshenije = False
            time_from_exit_long = 0
            if razvorot_from_long:
                sellPrice = closeLongPrice
                quant = -1
                razvorot_from_long = False
        if bh_long_exit:
            # ???????????? ?????????? ???? ??????????????
            hammer = hammerLongFV
            longCondition = False
            if signalLong > banLong:
                hammer = hammerLong
                if hammerLong:
                    c_bhl += 1
            if signalShort and hammerContLong:
                if signalLong + signalShort > quatroLong and signalLong / signalShort >= contrL:
                    if hammer == 0 or hammerContLong >= hammerLong:
                        hammer = hammerContLong
                        c_kbhl += 1
            if candle.date == '20160623' and int(candle.time) > int('220000') and hammer < 20:
                hammer = 20
            bh_long_exit = False
            counterLong = 0
            signalLong = 0
            signalShort = 0
            signalLongP = 0
            signalShortP = 0
        # ------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????
        # ------------------------------------------------------------------------------------------------------
        if candle.high >= maxC > 0 and candle.low > minC and hammer == 0 and candle.signal == 0 and \
                longCondition is False and shortCondition is False and closeShortPrice == 0 and closeShortPrice == 0 \
                and deal_type1 != 'Exit long' and deal_type1 != 'Exit short' and deal_type1 != 'Pogl long' and \
                deal_type1 != 'Pogl short':
            simple_long_enter = True
            longCondition = True
            comeback = True
            c_long_deals += 1
            deal_type1 = 'Long'
            if oknoLong and okno_x_long < maxC - candles[i - 1].close < okno_y_long:
                simple_long_enter = False
                c_okno_long += 1
                if deal_type1 == 'Zashita long':
                    deal_type2 = 'Okno long'
                else:
                    deal_type1 = 'Okno long'
            # ???????????????? ?????????????????? ????????????
            if fQuant == 1:
                fQuant = 0
                fCounterLong = 0
                fSignalLong = 0
                fSignalShort = 0
                if deal_type2 == '':
                    deal_type2 = 'Phantom long close'
                else:
                    deal_type3 = 'Phantom long close'
            if fQuant == -1:
                fQuant = 0
                fCounterShort = 0
                fSignalLong = 0
                fSignalShort = 0
                if deal_type2 == '':
                    deal_type2 = 'Phantom short close'
                else:
                    deal_type3 = 'Phantom short close'
        # ---------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????
        # ---------------------------------------------------------------------------------------------------------
        if candle.low <= minC < 1000000 and candle.high < maxC and hammer == 0 and candle.signal == 0 \
                and longCondition is False and shortCondition is False and closeShortPrice == 0 and closeLongPrice == 0 \
                and deal_type1 != 'Exit long' and deal_type1 != 'Exit short' and deal_type1 != 'Pogl long' and \
                deal_type1 != 'Pogl short':
            simple_short_enter = True
            shortCondition = True
            deal_type1 = 'Short'
            c_short_deals += 1
            # ???????? -----------------------------------------------------------------------------------------------------
            if oknoShort and okno_x_short < candles[i - 1].close - minC < okno_y_short:
                simple_short_enter = False
                c_okno_short += 1
                if deal_type1 == 'Zashita short':
                    deal_type2 = 'Okno short'
                else:
                    deal_type1 = 'Okno short'
            # ???????????????? ?????????????????? ???????????? ?????? ???????????? ???????????????? ???????????? -----------------------------------------------------
            if fQuant == 1:
                fQuant = 0
                fCounterLong = 0
                fSignalLong = 0
                fSignalShort = 0
                if deal_type2 == '':
                    deal_type2 = 'Phantom long close'
                else:
                    deal_type3 = 'Phantom long close'
            if fQuant == -1:
                fQuant = 0
                fCounterShort = 0
                fSignalLong = 0
                fSignalShort = 0
                if deal_type2 == '':
                    deal_type2 = 'Phantom short close'
                else:
                    deal_type3 = 'Phantom short close'
        # ???????????? ???????? ?????????? -------------------------------------------------------------------------------------------
        if simple_short_enter or razvorot_from_long:
            quant = -1
            sellPrice = minC - prosk
            stop_loss_short_value = int(candle.low * (1 + stop_loss_percent_short))
            if candle.open - candle.close > gap:
                sellPrice = candle.close - prosk
            if sellPrice < candle.low:
                sellPrice = candle.low
            if sellPrice > candle.high:
                sellPrice = candle.high
            if m1_enter_short == 1:
                sellPrice = 0
                if m1_delay + m1_duration > 30:
                    m1_delitel = 30 - m1_delay
                else:
                    m1_delitel = m1_duration
                for m1 in range(m1_delay + 2, m1_delay + m1_delitel + 2):
                    sellPrice = sellPrice + candles_1m[i][m1]
                sellPrice = sellPrice / m1_delitel
            simple_short_enter = False
            razvorot_from_long = False
        if simple_long_enter or razvorot_from_short:
            quant = 1
            buyPrice = maxC + prosk
            stop_loss_long_value = int(candle.high * (1 - stop_loss_percent_long))
            if candle.close - candle.open > gap:
                buyPrice = candle.close + prosk
            if buyPrice > candle.high:
                buyPrice = candle.high
            if buyPrice < candle.low:
                buyPrice = candle.low
            if m1_enter_long == 1:
                buyPrice = 0
                if m1_delay + m1_duration > 30:
                    m1_delitel = 30 - m1_delay
                else:
                    m1_delitel = m1_duration
                for m1 in range(m1_delay + 2, m1_delay + m1_delitel + 2):
                    buyPrice = buyPrice + candles_1m[i][m1]
                buyPrice = buyPrice / m1_delitel
            simple_long_enter = False
            razvorot_from_short = False
        # ---------------------------------------------------------------------------------------------------------------------------------------------------
        # ?????????????????? ????????????--------------------------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------------------------------------------------------------------------
        if fantomDeals and hammer > 0 and quant == 0:
            # ???????????????? ????????
            if candle.high >= maxC and candle.low > minC and fQuant == 0 and candle.signal == 0:
                fQuant = 1
                # ???????????????? ????????
                if deal_type1 == '':
                    deal_type1 = 'Phantom long enter'
                else:
                    deal_type2 = 'Phantom long enter'
            if candle.low <= minC and candle.high < maxC and fQuant == 0 and candle.signal == 0:
                fQuant = -1
                if deal_type1 == '':
                    deal_type1 = 'Phantom short enter'
                else:
                    deal_type2 = 'Phantom short enter'
        if fantomDeals and quant == 0 and fQuant != 0:
            # ????????????????
            if candle.high >= maxC and candle.low > minC and candle.signal == 0:
                fSignalLong = fSignalLong + 1
                if fQuant == 1:
                    fCounterLong = 1
            if candle.low <= minC and candle.high < maxC and candle.signal == 0:
                fSignalShort = fSignalShort + 1
                if fQuant == -1:
                    fCounterShort = 1
            if candle.close >= candle.open and fQuant == -1:
                fCounterShort = fCounterShort + 1
            if candle.close <= candle.open and fQuant == 1:
                fCounterLong = fCounterLong + 1
        # ---------------------------------------------------------------------------------------------------------------------
        # ???????????? ??????????????????-------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if longCondition:
            # ???????????????????????? ??????????????????
            if candle.high >= maxC and candle.low > minC and candle.signal == 0:
                signalLongP = signalLongP + 1
                counterLong = 0
                signalLong = signalLong + 1
                if arr_pogl_long[i]:
                    pogl_long = arr_pogl_long[i]
                if pogloshenieLong and signalLongP < signalPoglLong:
                    pogloshenije = False
            if candle.low <= minC and candle.high < maxC and candle.signal == 0:
                signalShort = signalShort + 1
            if candle.close <= candle.open:
                counterLong = counterLong + 1
            if pogloshenieLong and signalLongP >= signalPoglLong:
                 pogloshenije = True
            # ???????? ?????? ???????????? ???????????????? - ???????????????? ----------------------------------------------------------------------
        if shortCondition:
            # ???????????????????????? ??????????????????
            if candle.low <= minC and candle.high < maxC and candle.signal == 0:
                signalShortP = signalShortP + 1
                counterShort = 0
                signalShort = signalShort + 1
                if arr_pogl_short[i]:
                    pogl_short = arr_pogl_short[i]
                if pogloshenieShort and signalShortP < signalPoglShort:   # ?? ?????????? ???????????? ?????????????????? ????????????????????
                    pogloshenije = False
            if candle.high >= maxC and candle.signal == 0:
                signalLong = signalLong + 1
            if candle.close >= candle.open:
                counterShort = counterShort + 1
            if pogloshenieShort and signalShortP >= signalPoglShort:
                pogloshenije = True
        if candle.high >= maxC and candle.low > minC and candle.signal == 0:
            dopL_counter += 1
            dopS_counter = 0
        if candle.high < maxC and candle.low <= minC:
            dopL_counter = 0
            dopS_counter += 1
        # ???????????? ?? ???????? ------------------------------------------------------------------------------------------------
        massif = [buyPrice, closeLongPrice, sellPrice, closeShortPrice]
        ws_criteria = [c_long_deals, c_short_deals, c_bhl, c_bhs, c_kbhl, c_kbhs, c_pogl_long, c_pogl_short, c_sl_long,
                       c_sl_short, c_prodl_long, c_prodl_short, c_okno_long, c_okno_short]

        if all_export:
            massif = [buyPrice, closeLongPrice, sellPrice, closeShortPrice, quant, counterLong, counterShort,
                      signalLong, signalShort, fQuant, fCounterLong, fCounterShort, fSignalLong, fSignalShort, hammer,
                      maxC, minC, pogl_long, pogl_short, deal_type1, deal_type2, deal_type3, stop_loss_long_value,
                      stop_loss_short_value]
        arr.append(massif)
        i = i + 1
    return arr, ws_criteria, ws_actions


def chanelestimate(candles, params, arr_signal, arr_mm_long=None, arr_mm_short=None, arr_chanel_long=None,
                   arr_chanel_short=None, all_export=False, daily_export=False):
    # -----------------------------------------------------------------------------------------------------------------
    # ???????????????????? ????????????????????--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    # moneyManagement = int(params['moneyManagement'])
    decreasePosition = int(params['decreasePosition'])
    if 'decrease_position_long' in params:
        decrease_position_long = int(params['decrease_position_long'])
        decreasePosition = 0
    else:
        decrease_position_long = 0
    if 'decrease_position_short' in params:
        decrease_position_short = int(params['decrease_position_short'])
        decreasePosition = 0
    else:
        decrease_position_short = 0

    # ------------------------------------------------------------------------------------------------------------------
    # ???????????????? ????????????---------------------------------------------------------------------------------------------------
    #  -----------------------------------------------------------------------------------------------------------------
    curve21 = float(params['curve21'])
    curve22 = float(params['curve22'])
    curve23 = float(params['curve23'])
    curve11 = float(params['curve11'])
    curve12 = float(params['curve12'])
    curve13 = float(params['curve13'])
    # ------------------------------------------------------------------------------------------------------------------
    # ????????????????????--------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    comission = float(params['comission'])
    prosk = float(params['prosk'])
    # ------------------------------------------------------------------------------------------------------------------
    # ???????? ?????????????? ??????????????????????--------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    if arr_mm_long is None:
        arr_mm_long = mmCLose(candles, params['leverage'], params['mmSpeedLong'], params['mmAverageLong'],
                          params['mmConstLong'])
    if arr_mm_short is None:
        arr_mm_short = mmCLose(candles, params['leverage'], params['mmSpeedShort'], params['mmAverageShort'],
                              params['mmConstShort'])
    if arr_chanel_long is None:
        arr_chanel_long = kanaliMax(candles, params['chanelLong'])
    if arr_chanel_short is None:
        arr_chanel_short = kanaliMin(candles, params["chanelShort"])
    # -----------------------------------------------------------------------------------------------------------------
    # ???????? ?????????????????????????? ????????????????????
    # -----------------------------------------------------------------------------------------------------------------
    initialCapital = 1000000
    quant = 0
    i = 0
    capital = []
    array_days = []
    ddCapital = []
    currentCapital = initialCapital
    maxCapital = initialCapital
    capit = initialCapital
    maxDrawDown = 0
    monthlyStatistic = [initialCapital, 1, 0]   # ToDo - ???????????? ???????????? ??????????????
    monthlyStatistics = [monthlyStatistic]
    maxCapitalMonth = initialCapital
    start_capital = initialCapital
    monthlydd = 0
    month = 1
    monthlyddold = 0
    yearly_statistic = [initialCapital, 1, 0, 0]
    yearly_statistics = [yearly_statistic]
    year_dd = 0
    ddmetric1 = 0
    ddmetric2 = 0
    profit_deals_metric = 0
    loss_deals_metric = 0
    sum_dd_old = 0
    dohod = 0
    profit_deals = []
    loss_deals = []
    if all_export:
        to_export = []
        export_result = ['date', 'time', 'open', 'high', 'low', 'close', 'buyPrice', 'closeLongPrice', 'sellPrice',
                         'closeShortPrice', 'quant', 'counterLong', 'counterShort', 'signalLong', 'signalShort',
                         'fQuant', 'fCounterLong', 'fCounterShort', 'fSignalLong', 'fSignalShort', 'hammer', 'max',
                         'min', 'pogl_long', 'pogl_short', 'deal_type1', 'deal_type2', 'deal_type3', 'long condition',
                         'short condition',  'Cash', 'currentMonthlyDD', 'currentCapital', 'currentDrawDown', 'quant',
                         'mm_long', 'mm_short']
        to_export.append(export_result)
    # -----------------------------------------------------------------------------------------------------------------
    # ???????????????? ??????????????
    # -----------------------------------------------------------------------------------------------------------------
    for candle in candles:
        # -------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????
        # -------------------------------------------------------------------------------------------------------------
        if arr_signal[i][1]:
            closeLongPrice = arr_signal[i][1]
            currentCapital = currentCapital + quant * closeLongPrice - quant * comission
            if (currentCapital - start_capital) / start_capital >= 0:
                profit_deals.append((currentCapital - start_capital) / start_capital)
            else:
                loss_deals.append((currentCapital - start_capital) / start_capital)
            quant = 0
        # --------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ???????? -----------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if arr_signal[i][3]:
            closeShortPrice = arr_signal[i][3]
            currentCapital = currentCapital + quant * closeShortPrice + quant * comission
            if (currentCapital - start_capital) / start_capital >= 0:
                profit_deals.append((currentCapital - start_capital) / start_capital)
            else:
                loss_deals.append((currentCapital - start_capital) / start_capital)
            quant = 0
        # -------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ????????
        # -------------------------------------------------------------------------------------------------------------
        if arr_signal[i][0] > 0:
            buyPrice = arr_signal[i][0]
            start_capital = currentCapital
            quant = int(currentCapital * arr_mm_long[i] / buyPrice)
            currentCapital = currentCapital - quant * buyPrice - quant * comission
        # ???????????? ???????????????? ????????  # -------------------------------------------------------------------------------------
        if arr_signal[i][2] > 0:
            sellPrice = arr_signal[i][2]
            quant = -int(currentCapital * arr_mm_short[i] / sellPrice)
            currentCapital = currentCapital - quant * sellPrice + quant * comission
        # -------------------------------------------------------------------------------------------------------------
        # ?????????????????? ???????????????????? ??????????????---------------------------------------------------------------------------------
        # -------------------------------------------------------------------------------------------------------------
        if (decreasePosition or decrease_position_long) and quant > 0 and arr_signal[i][0] == 0:
            if arr_chanel_long[i] > 0:
                actQuant = int(capit * arr_mm_long[i] / arr_chanel_long[i])
            else:
                actQuant = quant
            if actQuant < quant and quant - actQuant > 1:
                closeLongPrice = candle.open - prosk
                if closeLongPrice > candle.high:
                    closeLongPrice = candle.high
                if closeLongPrice < candle.low:
                    closeLongPrice = candle.low
                currentCapital = currentCapital + (quant - actQuant) * (closeLongPrice - comission)
                quant = actQuant
        if (decreasePosition or decrease_position_short) and quant < 0 and arr_signal[i][2] == 0:
            if arr_chanel_short[i] > 0:
                actQuant = -int(capit * arr_mm_short[i] / arr_chanel_short[i])
            else:
                actQuant = quant
            if actQuant > quant and actQuant - quant > 1:
                closeShortPrice = candle.open + prosk
                if closeShortPrice > candle.high:
                    closeShortPrice = candle.high
                if closeShortPrice < candle.low:
                    closeShortPrice = candle.low
                currentCapital = currentCapital - (actQuant - quant) * (closeShortPrice + comission)
                quant = actQuant
        # --------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????????? ?? ?????????????????? ----------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # ???????? ??????????????????
        capit = currentCapital + quant * candle.close
        capital.append(capit)  # ?????????????? ??????????????
        # ???????????? ???????????????????????? ????????????????
        currentDDCapital = currentCapital
        if quant > 0:
            currentDDCapital = currentCapital + quant * candle.low
        if quant < 0:
            currentDDCapital = currentCapital + quant * candle.high
        ddCapital.append(currentDDCapital)
        if capit > maxCapital:
            maxCapital = currentCapital + quant * candle.close
        currentDrawDown = round(1 - currentDDCapital / maxCapital, 4)
        if currentDrawDown > maxDrawDown:
            maxDrawDown = currentDrawDown
        if int(candle.date) - int(candles[i - 1].date) > 1:
            array_days.append(capit)
        # ???????? ???????????????? ???????????????????? -------------------------------------------------------------------------------------
        if int(candle.date) - int(candles[i - 1].date) > 50:
            previouscapital = float(monthlyStatistic[0])
            estcapital = capital[i - 1] / previouscapital - 1
            monthlyStatistic = [capital[i - 1], estcapital, monthlydd, monthlyddold]
            monthlyStatistics.append(monthlyStatistic)
            dohod = dohod + abs(estcapital)
            ddmetric1 = ddmetric1 + abs(estcapital) * monthlydd
            ddmetric2 = ddmetric2 + abs(estcapital) * monthlyddold
            if quant != 0:
                if (capit - start_capital) / start_capital >= 0:
                    profit_deals.append((capit - start_capital) / start_capital)
                else:
                    loss_deals.append((capit - start_capital) / start_capital)
                start_capital = capit
            if len(profit_deals):
                profit_deals_metric = profit_deals_metric + sum(profit_deals) / len(profit_deals) * monthlyddold
            if len(loss_deals):
                loss_deals_metric = loss_deals_metric + sum(loss_deals) / len(loss_deals) * monthlyddold
            sum_dd_old = sum_dd_old + monthlyddold
            maxCapitalMonth = capital[i - 1]
            year_dd = year_dd + monthlyddold
            monthlydd = 0
            monthlyddold = 0
            month = month + 1
        # ???????? ?????????????? ???????????????????? -------------------------------------------------------------------------------------
        if int(candle.date) - int(candles[i - 1].date) > 8000:
            previouscapital = float(yearly_statistic[0])
            estcapital = capital[i - 1] / previouscapital - 1
            if month > 11:
                year_dd = year_dd / 12
            else:
                year_dd = year_dd / month
            curve_y = estcapital - curve21 * pow(year_dd, 2) - curve22 * year_dd - curve23
            yearly_statistic = [capital[i - 1], estcapital, year_dd, curve_y]
            yearly_statistics.append(yearly_statistic)
            year_dd = 0
        if capit > maxCapitalMonth:
            maxCapitalMonth = capit
        currentMonthlyDD = round(1 - currentDDCapital / maxCapitalMonth, 4)
        if currentMonthlyDD > monthlydd:
            monthlydd = currentMonthlyDD
        if currentDrawDown > monthlyddold:
            monthlyddold = currentDrawDown
        # ???????????????????? ?? ???????????? ?? ???????? ------------------------------------------------------------------------------------------------
        if all_export:
            export_result = [candle.date, candle.time, candle.open, candle.high, candle.low, candle.close]
            for j in range(0, len(arr_signal[i])):
                export_result.append(arr_signal[i][j])
            export_result.append(currentCapital)
            export_result.append(currentMonthlyDD)
            export_result.append(currentCapital + quant * candle.close)
            export_result.append(currentDrawDown)
            export_result.append(quant)
            export_result.append(arr_mm_long[i])
            export_result.append(arr_mm_short[i])
            to_export.append(export_result)
        i = i + 1
    # a = monthlyStatistics
    if capital[-1] > capital[0]:
        rate = pow(capital[-1] / capital[0], 12 / month) - 1
    else:
        rate = -1
    if dohod:
        ddForCurve = ddmetric2 / dohod
        ddForCurve_new = ddmetric1 / dohod
    else:
        ddForCurve = -1000
        ddForCurve_new = -1000
    curve = rate - curve21 * pow(ddForCurve, 2) - curve22 * ddForCurve - curve23
    curve_new = rate - curve11 * pow(ddForCurve_new, 2) - curve12 * ddForCurve_new - curve13
    a = [currentCapital, rate, maxDrawDown, ddmetric1 / dohod, ddmetric2 / dohod, curve,
         profit_deals_metric / sum_dd_old, loss_deals_metric / sum_dd_old, curve_new]
    # print(a)
    if rate > 0:
        stat_regeression = regression(array_days)
    else:
        stat_regeression = [100, 100, 100, 100]
    a.extend(stat_regeression)
    if daily_export:
        a.extend(array_days)
    # ------------------------------------------------------------------------------------------------------------------
    if all_export:
        a = to_export, monthlyStatistics, yearly_statistics
    return a


def deal_analitics(all_export, params):
    deals = []
    deal = ['DateOpen', 'TimeOpen', 'OpenPrice', 'Quantity', 'CapitalOpen', 'Long/Short', 'DealType', 'CapitalClose',
            'Singals', 'CounterSignals', 'DateClose', 'TimeClose', 'PriceClose', 'MaxPotentialPrice',
            'MinPotentalPrice', 'RealProfit', 'deal profit', 'Potential Profit', 'Potential Loss', 'Realized gain',
            'Realized loss', 'Ban Hammer', 'if Pogloshenije']
    deals.append(deal)
    dlina = len(all_export)
    prosk = float(params['prosk'])
    gap = int(params['gap'])
    potential = 0
    for i in range(1, dlina):
        if potential:
            potential = potential - 1
        # --------------------------------------------------------------------------------------------------------------
        # ?????????? ???? ?????????? -----------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long' \
                or all_export[i][25] == 'Phantom long close' or all_export[i][26] == 'Phantom long close':
            deal.append(all_export[i][32])  # ?????????????? ???? ??????????             7
            if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long':
                deal.append(all_export[i - 1][13])  # ??????????????              8
            else:
                deal.append(all_export[i - 1][18])
            if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long':
                deal.append(all_export[i - 1][14])  # ?????????? ??????????????        9
            else:
                deal.append(all_export[i - 1][19])
            deal.append(all_export[i][0])  # ???????? ????????????                   10
            deal.append(all_export[i][1])  # ?????????? ????????????                  11
            if deal[6] == 'Long':
                deal.append(all_export[i][7])  # ???????? ????????????               12
            else:
                closeLongPrice = all_export[i][2] - prosk
                if all_export[i][2] - all_export[i][5] > gap:
                    closeLongPrice = all_export[i][5] - prosk
                if closeLongPrice < all_export[i][4]:
                    closeLongPrice = all_export[i][4]
                deal.append(closeLongPrice)
            deal.append(max_potential)   # ???????????????????????? ?????????????????? ?? ???????????? 13
            deal.append(min_potential)   # ?????????????????????? ?????????????????? ?? ????????????  14
            if deal[6] == 'Long' or deal[6] == 'Long comeback':
                deal.append(deal[7] / deal[4] - 1)  # ?????????????? ?????? ???????????? ???? ???????????? ???? ???????????????? 15
            else:
                deal.append(0)
            deal.append((deal[12] - deal[2]) / deal[2])  # ?????????????? ?????? ???????????? ???? ????????????????         16
            if deal[2]:
                deal.append((deal[13] - deal[2]) / deal[2])  # ?????????????????? ?? ????????????  17
            else:
                deal.append(0)
            if deal[2]:
                deal.append((deal[14] - deal[2]) / deal[2])  # ???????????? ?? ????????????  18
            if deal[16] >= 0 and deal[2] != deal[13]:
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[13]))  # ?????????????????????????? ??????????????????     19
            else:
                deal.append(0)
            if deal[-1] > 1:
                deal[-1] = 1
            if deal[16] < 0 and deal[2] != deal[14]:  # ?????????????????????????? ????????????                                 20
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[14]))
            else:
                deal.append(0)
            if deal[-1] > 1:
                deal[-1] = 1
            deal.append(all_export[i][20])        # ????                                                 21
            if all_export[i][25] == 'Pogl long':  # ?????? ???????????????? ?????? ?????????????????? ????????????  22
                deal.append('Pogl long')
            else:
                deal.append('')
            deals.append(deal)
        # --------------------------------------------------------------------------------------------------------------
        # ?????????? ???? ?????????? -----------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short' \
                or all_export[i][25] == 'Phantom short close' or all_export[i][26] == 'Phantom short close':
            deal.append(all_export[i][32])          # ?????????????? ???? ??????????    7
            if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short':
                deal.append(all_export[i - 1][14])  # ??????????????             8
            else:
                deal.append(all_export[i - 1][19])  # ??????????????
            if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short':
                deal.append(all_export[i - 1][13])  # ?????????? ??????????????       9
            else:
                deal.append(all_export[i - 1][18])
            deal.append(all_export[i][0])           # ???????? ????????????         10
            deal.append(all_export[i][1])           # ?????????? ????????????        11
            if deal[5] == 'Short':
                deal.append(all_export[i][9])    # ???????? ????????????            12
            else:
                closeShortPrice = all_export[i][5] + prosk
                if all_export[i][5] - all_export[i][2] > gap:
                    closeShortPrice = all_export[i][5] + prosk
                if closeShortPrice > all_export[i][3]:
                    closeShortPrice = all_export[i][3]
                deal.append(closeShortPrice)
            deal.append(min_potential)               # ???????????????????????? ?????????????????? ?? ???????????? ????????       13
            deal.append(max_potential)               # ?????????????????????? ?????????????????? ?? ???????????? ????????        14
            if deal[6] == 'Short' or deal[6] == 'Short comeback':
                deal.append((deal[7] / deal[4]) - 1)   # ?????????????? ?????? ???????????? ???? ???????????? ???? ???????????????? 15
            else:
                deal.append(0)
            deal.append((deal[2] - deal[12]) / deal[2])  # ?????????????? ?????? ???????????? ???? ????????????????         16
            if deal[2]:
                deal.append((deal[2] - deal[13]) / deal[2])    # ?????????????????? ?? ????????????  17
            else:
                deal.append(0)
            if deal[2] - deal[14] != 0:
                deal.append((deal[2] - deal[14]) / deal[2])       # ???????????? ?? ????????????  18
            if deal[16] >= 0 and deal[2] != deal[13]:
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[13]))      # ?????????????????????????? ??????????????????     19
            else:
                deal.append(0)
            if deal[16] < 0 and deal[2] != deal[14]:  # ?????????????????????????? ????????????                                 20
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[14]))
            else:
                deal.append(0)
            deal.append(all_export[i][20])
            if all_export[i][25] == 'Pogl short':  # ?????? ???????????????? ?????? ?????????????????? ????????????            21
                deal.append('Pogl short')
            else:
                deal.append('')
            deals.append(deal)
        # --------------------------------------------------------------------------------------------------------------
        # ???????? ?? ???????? --------------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Long' or all_export[i][25] == 'Okno long' or all_export[i][25] == 'Phantom long enter'\
                or all_export[i][25] == 'Zashita long' or all_export[i][26] == 'Okno long' \
                or all_export[i][26] == 'Long' or all_export[i][26] == 'Phantom long enter' \
                or all_export[i][25] == 'Razvorot from short':
            deal = []
            deal.append(all_export[i][0])     # ???????? ????????????     0
            deal.append(all_export[i][1])     # ?????????? ????????????    1
            if all_export[i][25] == 'Long' or all_export[i][25] == 'Razvorot from short' or all_export[i][26] == 'Long':
                deal.append(all_export[i][6])     # ???????? ???????????? 2
            else:
                buyPrice = all_export[i][21] + prosk
                if all_export[i][5] - all_export[i][2] > gap:
                    buyPrice = all_export[i][5] + prosk
                if buyPrice > all_export[i][3]:
                    buyPrice = all_export[i][3]
                if buyPrice < all_export[i][4]:
                    buyPrice = all_export[i][4]
                deal.append(buyPrice)
            deal.append(all_export[i][34])    # ???????????????????? ?? ????????????   3
            deal.append(all_export[i][32])    # ?????????????? ???? ????????????     4
            deal.append(1)                    # ?????????????? ????????          5
            if all_export[i][25] == 'Long' or all_export[i][26] == 'Long':
                deal.append('Long')           # ?????? ????????????            6
            if all_export[i][25] == 'Razvorot from short':
                deal.append('Razvorot from short')
            if all_export[i][25] == 'Okno long' or all_export[i][26] == 'Okno long':
                deal.append('Okno long')
            if all_export[i][25] == 'Phantom long enter' or all_export[i][26] == 'Phantom long enter':
                deal.append('Phantom long enter')
            if all_export[i][25] == 'Zashita long':
                if deal[-1] == 'Okno long':
                    deal[-1] = deal[-1] + ' Zashita long'
                else:
                    deal.append('Zashita long')
            potential = 1
            max_potential = 0
            min_potential = 100000
        # --------------------------------------------------------------------------------------------------------------
        # ???????? ?? ???????? --------------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Short' or all_export[i][25] == 'Okno short' or all_export[i][26] == 'Short'\
                or all_export[i][25] == 'Razvorot from long' or all_export[i][26] == 'Okno short' \
                or all_export[i][25] == 'Phantom short enter' or all_export[i][25] == 'Zashita short' \
                or all_export[i][26] == 'Phantom short enter':
            deal = []
            deal.append(all_export[i][0])  # ???????? ????????????               0
            deal.append(all_export[i][1])  # ?????????? ????????????              1
            if all_export[i][25] == 'Short' or all_export[i][25] == 'Razvorot from long' \
                    or all_export[i][26] == 'Short':
                deal.append(all_export[i][8])  # ???????? ????????????           2
            else:
                sellPrice = all_export[i][22] - prosk
                if all_export[i][2] - all_export[i][5] > gap:
                    sellPrice = all_export[i][5] - prosk
                if sellPrice < all_export[i][4]:
                    sellPrice = all_export[i][4]
                if sellPrice > all_export[i][3]:
                    sellPrice = all_export[i][3]
                deal.append(sellPrice)      # ???????? ????????????
            deal.append(all_export[i][34])  # ???????????????????? ?? ????????????      3
            deal.append(all_export[i][32])  # ?????????????? ???? ????????????        4
            deal.append(-1)                 # ?????????????? ????????             5
            if all_export[i][25] == 'Short' or all_export[i][25] == 'Razvorot from long' \
                    or all_export[i][26] == 'Short':
                if all_export[i][20]:
                    deal.append('Short comeback')  # ?????? ????????????               6
                else:
                    deal.append('Short')        # ?????? ????????????               6
            if all_export[i][25] == 'Okno short' or all_export[i][26] == 'Okno short':
                deal.append('Okno short')
            if all_export[i][25] == 'Phantom short enter' or all_export[i][26] == 'Phantom short enter':
                deal.append('Phantom short enter')
            if all_export[i][25] == 'Zashita short':
                if deal[-1] == 'Okno short':
                    deal[-1] = 'Okno short & Zashita short'
                else:
                    deal.append('Zashita short')
            potential = 1
            max_potential = 0
            min_potential = 1000000
        if potential == 0 and len(deal) == 7:
                if all_export[i][3] > max_potential:
                    max_potential = all_export[i][3]
                if all_export[i][4] < min_potential:
                    min_potential = all_export[i][4]
    return deals


def signal_analytics(arg):
    candles, chanel_long, chanel_short, signalgenerator = arg
    signals = []
    signal = ['date', 'time', 'direction', 'counter', 'in deal', 'extremum counter']
    signals.append(signal)
    i = 0
    for candle in candles:
        if i:
            if candle.high >= chanel_long[i] > 0 and candle.low > chanel_short and candle.signal == 0:
                signal = [candle.date, candle.time, 'long', signalgenerator[i][7] + 1, signalgenerator[i][4]]
                signals.append(signal)
            if candle.high < chanel_long[i] and candle.low <= chanel_short and candle.signal == 0:
                signal = [candle.date, candle.time, 'short', signalgenerator[i][7] + 1, -signalgenerator[i][4]]
                signals.append(signal)
            if candle.high >= chanel_long[i] and candle.low <= chanel_short and candle.signal == 0:
                signal = [candle.date, candle.time, 'twice signal', 0, signalgenerator[i][4]]
                signals.append(signal)
        i += 1
    return signals


def pipeline_chanel_long(arg):
    candles, candles_1m, params, dimen0, dimen1, i, chanel_short, pogl_short, mm_long, mm_short, daily_export = arg
    # ???????????? ????????????????????
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    chanel_long = kanaliMax(candles, parameters['chanelLong'])
    pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                                     parameters['candlePoglLong'])
    # ???????????? ?????? ????????????
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters,
                                                          arr_chanel_short=chanel_short, arr_pogl_short=pogl_short,
                                                          arr_chanel_long=chanel_long, arr_pogl_long=pogl_long)
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                            arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_chanel_short(arg):
    candles, candles_1m, params, dimen0, dimen1, i, chanel_long, pogl_long, mm_long, mm_short, daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    chanel_short = kanaliMin(candles, parameters["chanelShort"])
    pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                       parameters['candlePoglShort'])
    # ???????????? ?????? ????????????
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters,
                                                          arr_chanel_short=chanel_short, arr_pogl_short=pogl_short,
                                                          arr_chanel_long=chanel_long, arr_pogl_long=pogl_long)
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                   arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_mm_long(arg):
    candles, params, dimen0, dimen1, i, signal, mm_short, chanel_long, chanel_short, ws_criteria, ws_actions, \
    daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                          parameters['mmConstLong'])
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
       result.append(temp[j])
    return result


def pipeline_mm_short(arg):
    candles, params, dimen0, dimen1, i, signal, mm_long, chanel_long, chanel_short, ws_criteria, ws_actions, \
    daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'], parameters['mmAverageShort'],
                           parameters['mmConstShort'])
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                            arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_pogl_long(arg):
    candles, candles_1m, params, dimen0, dimen1, i, chanel_long, chanel_short, pogl_short, mm_long, mm_short, \
    daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                                     parameters['candlePoglLong'])
    # ???????????? ?????? ????????????
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters, arr_chanel_long=chanel_long,
                                                          arr_chanel_short=chanel_short, arr_pogl_long=pogl_long,
                                                          arr_pogl_short=pogl_short)
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_pogl_short(arg):
    candles, candles_1m, params, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long, mm_long, mm_short, \
    daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                       parameters['candlePoglShort'])
    # ???????????? ?????? ????????????
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters, arr_chanel_long=chanel_long,
                                                          arr_chanel_short=chanel_short, arr_pogl_long=pogl_long,
                                                          arr_pogl_short=pogl_short)
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_other(arg):
    candles, candles_1m, params, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long, pogl_short, mm_long, \
    mm_short, daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters, arr_chanel_long=chanel_long,
                                                          arr_chanel_short=chanel_short, arr_pogl_long=pogl_long,
                                                          arr_pogl_short=pogl_short)
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def pipeline_leverage(arg):
    candles, params, dimen0, dimen1, i, signal, chanel_long, chanel_short, ws_criteria, ws_actions, daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    # ???????????? ??????????????????????
    mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                      parameters['mmConstLong'])
    mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'], parameters['mmAverageShort'],
                       parameters['mmConstShort'])
    # ???????????? ???????????????? ?? ??????????????????
    temp = chanelestimate(candles, parameters, signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
       result.append(temp[j])
    return result


def quarter_test(instrument, test_name, daily_export=False):
    print("start")
    data_file_name = instrument + 'Candles.csv'
    file = DataLoader.File(data_file_name)
    candles = file.getDataCandle()
    parameters_file_name = 'Parameters ' + instrument + ' ' + test_name + '.csv'
    file = DataLoader.File(parameters_file_name)
    parametersWithRange, est_variables = file.getdataparams() # ?????????????? ?????????????????? ?? ?????????????? ?? ????????????
    startTime = time()
    if 'm1_enter_condition' in parametersWithRange:
        m1_file_name = instrument + '_1m.csv'
        if int(parametersWithRange['m1_enter_condition'][0]) == 1:
            file = DataLoader.File(m1_file_name)
            candles_1m = file.getDataCandle_1m()
        else:
            candles_1m = []
    else:
        candles_1m = []

    # ???????????????????? ?????????????????? ???????????? --------------------------------------------------------------------------------------
    chislo = (len(est_variables["chanelLong"]))
    # ?????????????????? ???????????? ???????? ????????????--------------------------------------------------------------------------------------
    unit_test = False
    if int(parametersWithRange['unit_test'][0]):
        unit_test = True
    # ???????????? ???????????? ???????????????????? -----------------------------------------------------------------------------------------
    k1 = parametersWithRange.keys()
    fin_variables = copy.deepcopy(est_variables)  # ???????????????????? ????????????????
    i = 0
    base_variable = {}
    start_variable = {}
    result = []
    result_start = [instrument, candles[0].date, candles[0].time, candles[-1].date, candles[-1].time]
    result.append(result_start)
    result_start = ['id1', 'id2', 'id3', 'var1', 'var2', 'var3', 'Cash', 'Return', 'maxDrawDown', 'monthlyDD1',
                    'monthlyDD2', 'curve1', 'profit_deals', 'loss_deals', 'curve_new', 'a_regression', 'e_regression',
                    'r2_regresiion', 'residials2_regression', 'c_long_deals', 'c_short_deals', 'c_bhl', 'c_bhs',
                    'c_kbhl', 'c_kbhs', 'c_pogl_long', 'c_pogl_short', 'c_sl_long', 'c_sl_short', 'c_prodl_long',
                    'c_prodl_short', 'ws_actions']
    result.append(result_start)
    test_counter = 0
    for k in k1:
        if len(parametersWithRange[k][0]):
            base_variable[k] = float(parametersWithRange[k][0])
            start_variable[k] = float(parametersWithRange[k][0])
    for j in range(0, chislo):
        # --------------------------------------------------------------------------------------------------------------
        # ?????????????????????? ???????????????????? ?????? ??????????????----------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        dimen0 = 1
        dimen1 = 1
        dimen2 = 1
        imja0 = ""
        imja1 = ""
        imja2 = ""
        counter = 0
        for k in k1:
            if j == 0:
                if len(parametersWithRange[k][1]):
                    parametersWithRange[k][1] = float(parametersWithRange[k][1])
                    parametersWithRange[k][2] = float(parametersWithRange[k][2])
                    parametersWithRange[k][3] = float(parametersWithRange[k][3])
            if est_variables[k][j] == "Est" or est_variables[k][j] == "est":
                if counter == 2:
                    parametersWithRange[k][0] = "Est"
                    dimen2 = int(
                        (parametersWithRange[k][3] - parametersWithRange[k][1]) / parametersWithRange[k][2]) + 1
                    counter += 1
                    imja2 = k
                if counter == 1:
                    parametersWithRange[k][0] = "Est"
                    dimen1 = int(
                        (parametersWithRange[k][3] - parametersWithRange[k][1]) / parametersWithRange[k][2]) + 1
                    counter += 1
                    imja1 = k
                if counter == 0:
                    parametersWithRange[k][0] = "Est"
                    dimen0 = int(
                        (parametersWithRange[k][3] - parametersWithRange[k][1]) / parametersWithRange[k][2]) + 1
                    counter += 1
                    imja0 = k
            else:
                parametersWithRange[k][0] = base_variable[k]
            i += 1
        name_list = [imja0, imja1, imja2]
        result.append(name_list)
        # --------------------------------------------------------------------------------------------------------------
        # ???????????? ???????????? ?????? ???????????????????????? ??????????- ------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        other = True
        if parametersWithRange['chanelLong'][0] == "Est" or parametersWithRange['exitLong'][0] == "Est":
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'],
                                           parameters['sCanalShort'], parameters['candlePoglShort'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, candles_1m, parametersWithRange, dimen0, dimen1, i, chanel_short, pogl_short, mm_long,
                      mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_chanel_long, itera)
        if parametersWithRange['chanelShort'][0] == "Est" or parametersWithRange['exitShort'][0] == "Est":
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, candles_1m, parametersWithRange, dimen0, dimen1, i, chanel_long, pogl_long, mm_long,
                      mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_chanel_short, itera)
        if parametersWithRange['mmSpeedLong'][0] == "Est" or parametersWithRange['mmAverageLong'][0] == "Est" \
                or parametersWithRange['mmConstLong'][0] == "Est":
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                           parameters['candlePoglShort'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters,
                                                                  arr_chanel_long=chanel_long,
                                                                  arr_chanel_short=chanel_short,
                                                                  arr_pogl_long=pogl_long, arr_pogl_short=pogl_short)
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, parametersWithRange, dimen0, dimen1, i, arr_signal, mm_short, chanel_long, chanel_short,
                      ws_criteria, ws_actions, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_mm_long, itera)
        if parametersWithRange['mmSpeedShort'][0] == "Est" or parametersWithRange['mmAverageShort'][0] == "Est" \
                or parametersWithRange['mmConstShort'][0] == "Est":
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                           parameters['candlePoglShort'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters,
                                                                  arr_chanel_long=chanel_long,
                                                                  arr_chanel_short=chanel_short,
                                                                  arr_pogl_long=pogl_long, arr_pogl_short=pogl_short)
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, parametersWithRange, dimen0, dimen1, i, arr_signal, mm_long, chanel_long, chanel_short,
                      ws_criteria, ws_actions, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_mm_short, itera)
        if parametersWithRange['leverage'][0] == "Est":
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'],
                                           parameters['sCanalShort'], parameters['candlePoglShort'])
            arr_signal, ws_criteria, ws_actions = signalgenerator(candles, candles_1m, parameters,
                                                                  arr_chanel_long=chanel_long,
                                                                  arr_chanel_short=chanel_short,
                                                                  arr_pogl_long=pogl_long, arr_pogl_short=pogl_short)
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, parametersWithRange, dimen0, dimen1, i, arr_signal, chanel_long, chanel_short,
                      ws_criteria, ws_actions, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_leverage, itera)
        if parametersWithRange['bCanalLong'][0] == "Est" or parametersWithRange['sCanalLong'][0] == "Est" or \
                parametersWithRange['candlePoglLong'][0] == "Est":
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                           parameters['candlePoglShort'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            # pogl_long = None
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, candles_1m, parametersWithRange, dimen0, dimen1, i, chanel_long, chanel_short,
                      pogl_short, mm_long, mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_pogl_long, itera)
        if parametersWithRange['bCanalShort'][0] == "Est" or parametersWithRange['sCanalShort'][0] == "Est" or \
                parametersWithRange['candlePoglShort'][0] == "Est":
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, candles_1m, parametersWithRange, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long,
                      mm_long, mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            other = False
            with Pool() as p:
                result_list = p.map(pipeline_pogl_short, itera)
        if other:
            parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
            # ???????????? ?????????????????????? ---------------------------------------------------------------------------------------
            chanel_long = kanaliMax(candles, parameters['chanelLong'])
            chanel_short = kanaliMin(candles, parameters['chanelShort'])
            pogl_short = pogloshenie_short(candles, chanel_short, parameters['bCanalShort'], parameters['sCanalShort'],
                                           parameters['candlePoglShort'])
            pogl_long = pogloshenie_long(candles, chanel_long, parameters['bCanalLong'], parameters['sCanalLong'],
                                         parameters['candlePoglLong'])
            mm_long = mmCLose(candles, parameters['leverage'], parameters['mmSpeedLong'], parameters['mmAverageLong'],
                              parameters['mmConstLong'])
            mm_short = mmCLose(candles, parameters['leverage'], parameters['mmSpeedShort'],
                               parameters['mmAverageShort'], parameters['mmConstShort'])
            # ???????????????? ???????????????????? ?????? ??????????????????????????????????----------------------------------------------------------------
            itera = ([candles, candles_1m, parametersWithRange, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long,
                      pogl_short, mm_long, mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
            with Pool() as p:
                result_list = p.map(pipeline_other, itera)
        # --------------------------------------------------------------------------------------------------------------
        # ?????????? ???????????????????????? ???????????????? ?? ?????????????? ------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # for wr in range(0, len(result_list)):
        #    print(result_list[wr])
        esttime = time() - startTime
        # print(esttime - loadtime)
        poisktochki = result_list[0][11]
        optim = 0
        for i in range(0, len(result_list)):
            if result_list[i][11] > poisktochki:
                poisktochki = result_list[i][11]
                optim = i
        if imja0 != "":
            parametersWithRange[imja0][0] = result_list[optim][3]
            if unit_test is False:
                base_variable[imja0] = result_list[optim][3]
        if imja1 != "":
            parametersWithRange[imja1][0] = result_list[optim][4]
            if unit_test is False:
                base_variable[imja1] = result_list[optim][4]
        if imja2 != "":
            parametersWithRange[imja2][0] = result_list[optim][5]
            if unit_test is False:
                base_variable[imja2] = result_list[optim][5]
                est_variables['Return'][j] = result_list[optim][7]
                est_variables['maxDrawDown'][j] = result_list[optim][8]
                est_variables['monthlyDD1'][j] = result_list[optim][9]
                est_variables['monthlyDD2'][j] = result_list[optim][10]
                est_variables['curve1'][j] = result_list[optim][11]
                est_variables['profit_deals'][j] = result_list[optim][12]
                est_variables['loss_deals'][j] = result_list[optim][13]
                est_variables['curve_new'][j] = result_list[optim][14]
                est_variables['a_regression'][j] = result_list[optim][15]
                est_variables['e_regression'][j] = result_list[optim][16]
                est_variables['r2_regresiion'][j] = result_list[optim][17]
                est_variables['residials2_regression'][j] = result_list[optim][18]
                est_variables['c_long_deals'][j] = result_list[optim][19]
                est_variables['c_short_deals'][j] = result_list[optim][20]
                est_variables['c_bhl'][j] = result_list[optim][21]
                est_variables['c_bhs'][j] = result_list[optim][22]
                est_variables['c_kbhl'][j] = result_list[optim][23]
                est_variables['c_kbhs'][j] = result_list[optim][24]
                est_variables['c_pogl_long'][j] = result_list[optim][25]
                est_variables['c_pogl_short'][j] = result_list[optim][26]
                est_variables['c_sl_long'][j] = result_list[optim][27]
                est_variables['c_sl_short'][j] = result_list[optim][28]
                est_variables['c_prodl_long'][j] = result_list[optim][29]
                est_variables['c_prodl_short'][j] = result_list[optim][30]
                est_variables['c_okno_long'][j] = result_list[optim][31]
                est_variables['c_okno_short'][j] = result_list[optim][32]
                est_variables['ws_actions'][j] = result_list[optim][33]
        for k in k1:
            fin_variables[k][j] = parametersWithRange[k][0]
        fin_variables['Return'][j] = result_list[optim][7]
        fin_variables['maxDrawDown'][j] = result_list[optim][8]
        fin_variables['monthlyDD1'][j] = result_list[optim][9]
        fin_variables['monthlyDD2'][j] = result_list[optim][10]
        fin_variables['curve1'][j] = result_list[optim][11]
        fin_variables['profit_deals'][j] = result_list[optim][12]
        fin_variables['loss_deals'][j] = result_list[optim][13]
        fin_variables['curve_new'][j] = result_list[optim][14]
        fin_variables['a_regression'][j] = result_list[optim][15]
        fin_variables['e_regression'][j] = result_list[optim][16]
        fin_variables['r2_regresiion'][j] = result_list[optim][17]
        fin_variables['residials2_regression'][j] = result_list[optim][18]
        fin_variables['c_long_deals'][j] = result_list[optim][19]
        fin_variables['c_short_deals'][j] = result_list[optim][20]
        fin_variables['c_bhl'][j] = result_list[optim][21]
        fin_variables['c_bhs'][j] = result_list[optim][22]
        fin_variables['c_kbhl'][j] = result_list[optim][23]
        fin_variables['c_kbhs'][j] = result_list[optim][24]
        fin_variables['c_pogl_long'][j] = result_list[optim][25]
        fin_variables['c_pogl_short'][j] = result_list[optim][26]
        fin_variables['c_sl_long'][j] = result_list[optim][27]
        fin_variables['c_sl_short'][j] = result_list[optim][28]
        fin_variables['c_prodl_long'][j] = result_list[optim][29]
        fin_variables['c_prodl_short'][j] = result_list[optim][30]
        fin_variables['c_okno_long'][j] = result_list[optim][31]
        fin_variables['c_okno_short'][j] = result_list[optim][32]
        fin_variables['ws_actions'][j] = result_list[optim][33]
        # ???????????????????? ?????????????????????? ?? ???????????????? ????????????
        for z in range(0, len(result_list)):
            result.append(result_list[z])
        print(result_list[optim])
        test_counter = test_counter + dimen0 * dimen1 * dimen2
        if unit_test:
            for k in k1:
              parametersWithRange[k][0] = start_variable[k]
    # ------------------------------------------------------------------------------------------------------------------
    # ?????????????? ??????????????????????-----------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    endtime = time()
    result_file_name = 'Results ' + instrument + ' ' + test_name + '.csv'
    if test_counter:
        print((endtime - startTime) / test_counter)
    f = open(result_file_name, "w+")
    for i in range(0, len(result)):
        for j in range(0, len(result[i])):
            result[i][j] = str(result[i][j])
        towrite = ";".join(result[i]) + '\n'
        f.write(towrite)
    f.close()
    # ------------------------------------------------------------------------------------------------------------------
    # ?????????????? ?????????? ???????? ??????????????----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    meta_control_name = 'MetaControl ' + instrument + ' ' + test_name + '.csv'
    f = open(meta_control_name, "w+")
    for k in k1:
        for j in range(0, len(est_variables[k])):
            est_variables[k][j] = str(est_variables[k][j])
        for j in range(0, len(fin_variables[k])):
            fin_variables[k][j] = str(fin_variables[k][j])
        temp = ";".join(est_variables[k])
        towrite = k + ';' + str(start_variable[k]) + ';' + str(parametersWithRange[k][1]) + ';' + \
                  str(parametersWithRange[k][2]) + ';' + str(parametersWithRange[k][3]) + ';' + \
                  ";".join(est_variables[k]) + ";" + ";".join(fin_variables[k]) + '\n'
        f.write(towrite)
    f.close()
    print('----------------------------------------------------------------------------------------------------------')
    for k in ['Return', 'maxDrawDown', 'monthlyDD1', 'curve1', 'profit_deals', 'loss_deals']:
        print(k, fin_variables[k][-1])
    print('finish')
    return result_list[optim][11]

# 1.0

def regression(capital):
    n = len(capital)
    x_arr = np.arange(n)
    x1_arr = [x + 1 for x in x_arr]
    x2_arr = [1] * n
    y_arr = np.array([math.log(x) for x in capital])
    x_transp = [x1_arr, x2_arr]
    x_arr = np.transpose(x_transp)
    temp1 = np.linalg.inv(x_transp @ x_arr)  # ???????????? ?????????????????? ?????? ????????????????????????
    temp2 = x_transp @ y_arr                 # ???????????? ?????????????????? ?????? ????????????????????????
    a, b = temp1 @ temp2
    for_residuals = np.transpose(y_arr) - x_arr @ [a, b]
    for_residuals_transp = np.transpose(for_residuals)
    residuals = for_residuals_transp @ for_residuals
    residuals_before = np.transpose(y_arr) @ y_arr
    r2 = 1 - residuals / residuals_before
    return a, b, r2, residuals / n


# 1.1 ?????????????? ???????????? ?????????????? ???? 1 ????????
# 1.2 ?????????????? ?????????????? ??????????
# 1.3 ?????????? ???????????????????????? ???????????????????? ?????????????? ???? ?????????? ????????????????
# 1.4 ?????????????? ????????, ?????????????? ?????? ?????????????????? ?? ???????????? ?? csv Parameters
# 1.6 ?????????????? ?????????????? ?? ???????????? ???? ??????????
# 1.7 ?????????????? ???????????? ????????????
# 1.7 ?????????????? ?????????????????? ???? ???????? ?? ????????????????????
# 1.7 ?????????????? ?????????????? ???? ???????????? ????????????????
# 1.8 ?????????????? ?????????????????????? ?? ??????????, ???????????????? ???????????? ???? ?????????????? ????????????
# 1.9 ?????????????? ????????-??????????