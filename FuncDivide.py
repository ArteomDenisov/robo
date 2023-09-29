from time import time
from multiprocessing import Pool
import copy

from numba import jit

from .strategy import kanaliMax, kanaliMin, pogloshenie_short, pogloshenie_long, mmCLose
from .DataLoader import File


def chanelloader(params, dimen0, dimen1, i):
    # -----------------------------------------------------------------------------------------------------------------
    # Логические Переменные--------------------------------------------------------------------------------------------
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


def signalgenerator(candles, params, arr_chanel_long=None, arr_chanel_short=None, arr_pogl_long=None,
                    arr_pogl_short=None, all_export=False):
    # -----------------------------------------------------------------------------------------------------------------
    # Логические Переменные--------------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------------
    fantomDeals = int(params['fantomDeals'])
    pogloshenieLong = int(params['pogloshenieLong'])
    pogloshenieShort = int(params['pogloshenieShort'])
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
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    # Переменные--------------------------------------------------------------------------------------------------------------
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
    quatroLong = int(params['quatroLong'])
    quatroShort = int(params['quatroShort'])
    signalPoglLong = int(params['signalPoglLong'])
    signalPoglShort = int(params['signalPoglShort'])
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
    # Блок расчета индикаторов--------------------------------------------------------------------------------------------------------
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
    # Блок инициализации переменных
    # -----------------------------------------------------------------------------------------------------------------
    quant = 0
    counterLong = 0
    counterShort = 0
    signalLong = 0
    signalShort = 0
    signalLongP = 0
    signalShortP = 0
    ws_actions = 0
    dopS_counter = 0
    dopL_counter = 0
    hammer = 0
    time_from_exit_long = 0
    time_from_exit_short = 0
    # Определение счетчиков---------------------------------------------------------------------------------------------
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
    i = 0
    arr = []
    longCondition = False          # состояние, что расчитываются счетчики для лонг
    shortCondition = False         # состояние, что расчитываются счетчики для шорт
    pogloshenije = False           # состояние, что поглощение уже может сработать, то есть достаточно сигналов
    # Long -------------------------------------------------------------------------------------------------------------
    simple_long_enter = False
    time_long_exit = False
    bh_long_exit = False
    # Short ------------------------------------------------------------------------------------------------------------
    simple_short_enter = False
    time_short_exit = False
    bh_short_exit = False
    # ------------------------------------------------------------------------------------------------------------------
    # Основные расчеты
    # ------------------------------------------------------------------------------------------------------------------
    pogl_long = 0
    pogl_short = 0
    stop_loss_long_value = 0
    stop_loss_short_value = 0
    # deal_counter = 0
    for candle in candles:
        # Инициализация переменных--------------------------------------------------------------------------------------
        deal_type1 = ''
        deal_type2 = ''
        deal_type3 = ''
        buyPrice = 0
        sellPrice = 0
        closeLongPrice = 0
        closeShortPrice = 0
        # Расчет каналов-----------------------------------------------------------------------------------------------
        maxC = arr_chanel_long[i]
        minC = arr_chanel_short[i]
        if hammer > 0:
            hammer = hammer - 1
        time_from_exit_long += 1
        time_from_exit_short += 1
        # -------------------------------------------------------------------------------------------------------------
        # Расчет закрытия лонг
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
                deal_type1 = 'Stop loss Exit long'
                c_sl_long += 1
            if stop_loss_proboi_long and candle.low < stop_loss_long_value and counterLong:
                time_long_exit = True
                bh_long_exit = True
                deal_type1 = 'Stop loss Exit long'
                c_sl_long += 1
            # Поглощение лонг ------------------------------------------------------------------------------------------
            if pogloshenije and pogl_long > candles[i - 1].close and quant >= 0:
                deal_type1 = 'Pogl long'
                c_pogl_long += 1
                time_long_exit = True
                bh_long_exit = True
                pogloshenije = False
        # --------------------------------------------------------------------------------------------------------------
        # Расчет закрытия шорт: условия
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
                deal_type1 = 'stop loss Exit short'
                c_sl_short += 1
            if stop_loss_proboi_short and candle.high > stop_loss_short_value > 0:
                time_short_exit = True
                bh_short_exit = True
                deal_type1 = 'stop loss Exit short'
                c_sl_short += 1
        # --------------------------------------------------------------------------------------------------------------
        # Расчет закрытия сделок: действия -----------------------------------------------------------------------------
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
            if quant == 0:
                closeShortPrice = 0
            quant = 0
            pogl_short = 0
            stop_loss_short_value = 0
            time_short_exit = False
            pogloshenije = False
            time_from_exit_short = 0
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
            if quant == 0:
                closeLongPrice = 0
            quant = 0
            pogl_long = 0
            stop_loss_long_value = 0
            time_long_exit = False
            pogloshenije = False
            time_from_exit_long = 0
        if bh_long_exit:
            # просто выход по времени
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
        # Расчет открытия лонг
        # ------------------------------------------------------------------------------------------------------
        if candle.high >= maxC > 0 and candle.low > minC and hammer == 0 and \
                longCondition is False and shortCondition is False and closeShortPrice == 0 and closeShortPrice == 0 \
                and deal_type1 != 'Exit long' and deal_type1 != 'Exit short' and deal_type1 != 'Pogl long' and \
                deal_type1 != 'Pogl short':
            simple_long_enter = True
            longCondition = True
            c_long_deals += 1
            deal_type1 = 'Long'
        # ---------------------------------------------------------------------------------------------------------
        # Расчет открытия шорт
        # ---------------------------------------------------------------------------------------------------------
        if candle.low <= minC < 1000000 and candle.high < maxC and hammer == 0 \
                and longCondition is False and shortCondition is False and closeShortPrice == 0 and closeLongPrice == 0 \
                and deal_type1 != 'Exit long' and deal_type1 != 'Exit short' and deal_type1 != 'Pogl long' and \
                deal_type1 != 'Pogl short':
            simple_short_enter = True
            shortCondition = True
            deal_type1 = 'Short'
            c_short_deals += 1
        # Расчет цены входа -------------------------------------------------------------------------------------------
        if simple_short_enter:
            quant = -1
            sellPrice = minC - prosk
            stop_loss_short_value = int(candle.low * (1 + stop_loss_percent_short))
            if candle.open - candle.close > gap:
                sellPrice = candle.close - prosk
            if sellPrice < candle.low:
                sellPrice = candle.low
            if sellPrice > candle.high:
                sellPrice = candle.high
            simple_short_enter = False
        if simple_long_enter:
            quant = 1
            buyPrice = maxC + prosk
            stop_loss_long_value = int(candle.high * (1 - stop_loss_percent_long))
            if candle.close - candle.open > gap:
                buyPrice = candle.close + prosk
            if buyPrice > candle.high:
                buyPrice = candle.high
            if buyPrice < candle.low:
                buyPrice = candle.low
            simple_long_enter = False
        # ---------------------------------------------------------------------------------------------------------------------------------------------------
        # Фантомные сделки--------------------------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------------------------------------------------------------------------
        # ---------------------------------------------------------------------------------------------------------------------
        # Расчет счетчиков-------------------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        if longCondition:
            # срабатывание счетчиков
            if candle.high >= maxC and candle.low > minC:
                signalLongP = signalLongP + 1
                counterLong = 0
                signalLong = signalLong + 1
                if arr_pogl_long[i]:
                    pogl_long = arr_pogl_long[i]
                if pogloshenieLong and signalLongP < signalPoglLong:
                    pogloshenije = False
            if candle.low <= minC and candle.high < maxC:
                signalShort = signalShort + 1
            if candle.close <= candle.open:
                counterLong = counterLong + 1
            if pogloshenieLong and signalLongP >= signalPoglLong:
                 pogloshenije = True
            # Блок для слабых сигналов - действия ----------------------------------------------------------------------
        if shortCondition:
            # срабатывание счетчиков
            if candle.low <= minC and candle.high < maxC:
                signalShortP = signalShortP + 1
                counterShort = 0
                signalShort = signalShort + 1
                if arr_pogl_short[i]:
                    pogl_short = arr_pogl_short[i]
                if pogloshenieShort and signalShortP < signalPoglShort:   # в любом случае включение поглощений
                    pogloshenije = False
            if candle.high >= maxC:
                signalLong = signalLong + 1
            if candle.close >= candle.open:
                counterShort = counterShort + 1
            if pogloshenieShort and signalShortP >= signalPoglShort:
                pogloshenije = True
        if candle.high >= maxC and candle.low > minC:
            dopL_counter += 1
            dopS_counter = 0
        if candle.high < maxC and candle.low <= minC:
            dopL_counter = 0
            dopS_counter += 1
        # Запись в файл ------------------------------------------------------------------------------------------------
        massif = [buyPrice, closeLongPrice, sellPrice, closeShortPrice]
        ws_criteria = [c_long_deals, c_short_deals, c_bhl, c_bhs, c_kbhl, c_kbhs, c_pogl_long, c_pogl_short, c_sl_long,
                       c_sl_short, c_prodl_long, c_prodl_short]

        if all_export:
            massif = [buyPrice, closeLongPrice, sellPrice, closeShortPrice, quant, counterLong, counterShort,
                      signalLong, signalShort, hammer,
                      maxC, minC, pogl_long, pogl_short, deal_type1, deal_type2, deal_type3, stop_loss_long_value,
                      stop_loss_short_value]
        arr.append(massif)
        i = i + 1
    return arr, ws_criteria, ws_actions


def chanelestimate(candles, params, arr_signal, arr_mm_long=None, arr_mm_short=None, arr_chanel_long=None,
                   arr_chanel_short=None, all_export=False, daily_export=False):
    # -----------------------------------------------------------------------------------------------------------------
    # Логические Переменные--------------------------------------------------------------------------------------------
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
    # Значения кривых---------------------------------------------------------------------------------------------------
    #  -----------------------------------------------------------------------------------------------------------------
    curve21 = float(params['curve21'])
    curve22 = float(params['curve22'])
    curve23 = float(params['curve23'])
    curve11 = float(params['curve11'])
    curve12 = float(params['curve12'])
    curve13 = float(params['curve13'])
    # ------------------------------------------------------------------------------------------------------------------
    # Переменные--------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    comission = float(params['comission'])
    prosk = float(params['prosk'])
    # ------------------------------------------------------------------------------------------------------------------
    # Блок расчета индикаторов--------------------------------------------------------------------------------------------------------
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
    # Блок инициализации переменных
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
    monthlyStatistic = [initialCapital, 1, 0]   # ToDo - убрать первую строчку
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
                         'hammer', 'max',
                         'min', 'pogl_long', 'pogl_short', 'deal_type1', 'deal_type2', 'deal_type3', 'long condition',
                         'short condition',  'Cash', 'currentMonthlyDD', 'currentCapital', 'currentDrawDown', 'quant',
                         'mm_long', 'mm_short']
        to_export.append(export_result)
    # -----------------------------------------------------------------------------------------------------------------
    # Основные расчеты
    # -----------------------------------------------------------------------------------------------------------------
    for candle in candles:
        # -------------------------------------------------------------------------------------------------------------
        # Расчет закрытия лонг
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
        # Расчет закрытия шорт -----------------------------------------------------------------------------------------
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
        # Расчет открытия лонг
        # -------------------------------------------------------------------------------------------------------------
        if arr_signal[i][0] > 0:
            buyPrice = arr_signal[i][0]
            start_capital = currentCapital
            quant = int(currentCapital * arr_mm_long[i] / buyPrice)
            currentCapital = currentCapital - quant * buyPrice - quant * comission
        # Расчет открытия шорт  # -------------------------------------------------------------------------------------
        if arr_signal[i][2] > 0:
            sellPrice = arr_signal[i][2]
            quant = -int(currentCapital * arr_mm_short[i] / sellPrice)
            currentCapital = currentCapital - quant * sellPrice + quant * comission
        # -------------------------------------------------------------------------------------------------------------
        # Частичное сокращение позиции---------------------------------------------------------------------------------
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
        # Расчет капитала и счетчиков ----------------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        # Блок аналитики
        capit = currentCapital + quant * candle.close
        capital.append(capit)  # Текущий капитал
        # Расчет максимальной просадки
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
        # Блок месячной статистики -------------------------------------------------------------------------------------
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
        # Блок годовой статистики -------------------------------------------------------------------------------------
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
        # Подготовка к запись в файл ------------------------------------------------------------------------------------------------
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
    a = [capit, rate, maxDrawDown, ddmetric1 / dohod, ddmetric2 / dohod, curve,
         profit_deals_metric / sum_dd_old, loss_deals_metric / sum_dd_old, curve_new]
    if daily_export:
        a.extend(array_days)
    # ------------------------------------------------------------------------------------------------------------------
    if all_export:
        a = to_export, monthlyStatistics, yearly_statistics
    return a


def pipeline_other(arg):
    candles, params, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long, pogl_short, mm_long, \
    mm_short, daily_export = arg
    parameters, result = chanelloader(params, dimen0, dimen1, i)
    arr_signal, ws_criteria, ws_actions = signalgenerator(candles, parameters, arr_chanel_long=chanel_long,
                                                          arr_chanel_short=chanel_short, arr_pogl_long=pogl_long,
                                                          arr_pogl_short=pogl_short)
    # Расчет капитала и аналитика
    temp = chanelestimate(candles, parameters, arr_signal, arr_mm_long=mm_long, arr_mm_short=mm_short,
                          arr_chanel_long=chanel_long, arr_chanel_short=chanel_short, daily_export=daily_export)
    temp.extend(ws_criteria)
    temp.append(ws_actions)
    for j in range(0, len(temp)):
        result.append(temp[j])
    return result


def quarter_test(instrument, test_name, candles_filename, daily_export=False):
    print("start")
    file = File(candles_filename)
    candles = file.get_candle_data()
    parameters_file_name = 'Parameters ' + instrument + ' ' + test_name + '.csv'
    file = File(parameters_file_name)
    parametersWithRange, est_variables = file.get_data_parameters()  # базовые перменные и столбцы с естами
    startTime = time()

    # Количество табличных тестов --------------------------------------------------------------------------------------
    chislo = (len(est_variables["chanelLong"]))
    # Включение режима юнит тестов--------------------------------------------------------------------------------------
    unit_test = False
    if int(parametersWithRange['unit_test'][0]):
        unit_test = True
    # Массив ключей переменных -----------------------------------------------------------------------------------------
    k1 = parametersWithRange.keys()
    fin_variables = copy.deepcopy(est_variables)  # Результаты расчетов
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
        # Определение переменных для таблицы----------------------------------------------------------------------------
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
        # Расчет таблиц для квартального теста- ------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        parameters, zdes_ne_nuzhno = chanelloader(parametersWithRange, dimen0, dimen1, i)
        # Расчет индикаторов ---------------------------------------------------------------------------------------
        chanel_long = None
        chanel_short = None
        pogl_short = None
        pogl_long = None
        mm_long = None
        mm_short = None
        startTime = time()
        # Создание переменной для мультипроцессинга----------------------------------------------------------------
        itera = ([candles, parametersWithRange, dimen0, dimen1, i, chanel_long, chanel_short, pogl_long,
                  pogl_short, mm_long, mm_short, daily_export] for i in range(0, dimen0 * dimen1 * dimen2))
        with Pool() as p:
            result_list = p.map(pipeline_other, itera)
    # --------------------------------------------------------------------------------------------------------------
        # Поиск оптимального значения в таблице ------------------------------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        esttime = time() - startTime
        print(esttime/3600)
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
                # est_variables['c_bhl'][j] = result_list[optim][21]
                # est_variables['c_bhs'][j] = result_list[optim][22]
                # est_variables['c_kbhl'][j] = result_list[optim][23]
                # est_variables['c_kbhs'][j] = result_list[optim][24]
                # est_variables['c_pogl_long'][j] = result_list[optim][25]
                # est_variables['c_pogl_short'][j] = result_list[optim][26]
                # est_variables['c_sl_long'][j] = result_list[optim][27]
                # est_variables['c_sl_short'][j] = result_list[optim][28]
                # est_variables['c_prodl_long'][j] = result_list[optim][29]
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
        # fin_variables['c_bhl'][j] = result_list[optim][21]
        # fin_variables['c_bhs'][j] = result_list[optim][22]
        # fin_variables['c_kbhl'][j] = result_list[optim][23]
        # fin_variables['c_kbhs'][j] = result_list[optim][24]
        # fin_variables['c_pogl_long'][j] = result_list[optim][25]
        # fin_variables['c_pogl_short'][j] = result_list[optim][26]
        # fin_variables['c_sl_long'][j] = result_list[optim][27]
        # fin_variables['c_sl_short'][j] = result_list[optim][28]
        # fin_variables['c_prodl_long'][j] = result_list[optim][29]
        # Добавление результатов в итоговый массив
        for z in range(0, len(result_list)):
            result.append(result_list[z])
        print(result_list[optim])
        test_counter = test_counter + dimen0 * dimen1 * dimen2
        if unit_test:
            for k in k1:
              parametersWithRange[k][0] = start_variable[k]
    # ------------------------------------------------------------------------------------------------------------------
    # Экспорт результатов-----------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    endtime = time()
    result_file_name = 'Results ' + instrument + ' ' + test_name + '.csv'
    if test_counter:
        print((endtime - startTime) / test_counter)
    with open(result_file_name, "w+") as f:
        for i in range(0, len(result)):
            for j in range(0, len(result[i])):
                result[i][j] = str(result[i][j])
            towrite = ";".join(result[i]) + '\n'
            f.write(towrite)
    # ------------------------------------------------------------------------------------------------------------------
    # Экспорт листа мета контрол----------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    meta_control_name = 'MetaControl ' + instrument + ' ' + test_name + '.csv'
    with open(meta_control_name, "w+") as f:
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
    print('----------------------------------------------------------------------------------------------------------')
    for k in ['Return', 'maxDrawDown', 'monthlyDD1', 'curve1', 'profit_deals', 'loss_deals']:
        print(k, fin_variables[k][-1])
    print('finish')
    return result_list[optim][11]