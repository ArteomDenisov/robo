

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


def deal_analytics(all_export, params):
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
        # выход из лонга -----------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long' \
                or all_export[i][25] == 'Phantom long close' or all_export[i][26] == 'Phantom long close':
            deal.append(all_export[i][32])  # капитал на конец             7
            if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long':
                deal.append(all_export[i - 1][13])  # сигналы              8
            else:
                deal.append(all_export[i - 1][18])
            if all_export[i][25] == 'Exit long' or all_export[i][25] == 'Pogl long':
                deal.append(all_export[i - 1][14])  # контр сигналы        9
            else:
                deal.append(all_export[i - 1][19])
            deal.append(all_export[i][0])  # дата выхода                   10
            deal.append(all_export[i][1])  # время выхода                  11
            if deal[6] == 'Long':
                deal.append(all_export[i][7])  # цена выхода               12
            else:
                closeLongPrice = all_export[i][2] - prosk
                if all_export[i][2] - all_export[i][5] > gap:
                    closeLongPrice = all_export[i][5] - prosk
                if closeLongPrice < all_export[i][4]:
                    closeLongPrice = all_export[i][4]
                deal.append(closeLongPrice)
            deal.append(max_potential)   # максимальный потенциал в сделке 13
            deal.append(min_potential)   # минимальный потенциал в сделке  14
            if deal[6] == 'Long' or deal[6] == 'Long comeback':
                deal.append(deal[7] / deal[4] - 1)  # Прибыль или убыток по сделке по капиталу 15
            else:
                deal.append(0)
            deal.append((deal[12] - deal[2]) / deal[2])  # Прибыль или убыток по фантомам         16
            if deal[2]:
                deal.append((deal[13] - deal[2]) / deal[2])  # Потенциал в сделке  17
            else:
                deal.append(0)
            if deal[2]:
                deal.append((deal[14] - deal[2]) / deal[2])  # Угроза в сделке  18
            if deal[16] >= 0 and deal[2] != deal[13]:
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[13]))  # Реализованный потенциал     19
            else:
                deal.append(0)
            if deal[-1] > 1:
                deal[-1] = 1
            if deal[16] < 0 and deal[2] != deal[14]:  # Реализованная угроза                                 20
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[14]))
            else:
                deal.append(0)
            if deal[-1] > 1:
                deal[-1] = 1
            deal.append(all_export[i][20])        # бх                                                 21
            if all_export[i][25] == 'Pogl long':  # тип реальной или фантомной сделки  22
                deal.append('Pogl long')
            else:
                deal.append('')
            deals.append(deal)
        # --------------------------------------------------------------------------------------------------------------
        # выход из шорта -----------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short' \
                or all_export[i][25] == 'Phantom short close' or all_export[i][26] == 'Phantom short close':
            deal.append(all_export[i][32])          # капитал на конец    7
            if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short':
                deal.append(all_export[i - 1][14])  # сигналы             8
            else:
                deal.append(all_export[i - 1][19])  # сигналы
            if all_export[i][25] == 'Exit short' or all_export[i][25] == 'Pogl short':
                deal.append(all_export[i - 1][13])  # контр сигналы       9
            else:
                deal.append(all_export[i - 1][18])
            deal.append(all_export[i][0])           # дата выхода         10
            deal.append(all_export[i][1])           # время выхода        11
            if deal[5] == 'Short':
                deal.append(all_export[i][9])    # цена выхода            12
            else:
                closeShortPrice = all_export[i][5] + prosk
                if all_export[i][5] - all_export[i][2] > gap:
                    closeShortPrice = all_export[i][5] + prosk
                if closeShortPrice > all_export[i][3]:
                    closeShortPrice = all_export[i][3]
                deal.append(closeShortPrice)
            deal.append(min_potential)               # Максимальный потенциал в сделке шорт       13
            deal.append(max_potential)               # минимальный потенциал в сделке шорт        14
            if deal[6] == 'Short' or deal[6] == 'Short comeback':
                deal.append((deal[7] / deal[4]) - 1)   # Прибыль или убыток по сделке по капиталу 15
            else:
                deal.append(0)
            deal.append((deal[2] - deal[12]) / deal[2])  # Прибыль или убыток по фантомам         16
            if deal[2]:
                deal.append((deal[2] - deal[13]) / deal[2])    # Потенциал в сделке  17
            else:
                deal.append(0)
            if deal[2] - deal[14] != 0:
                deal.append((deal[2] - deal[14]) / deal[2])       # Угроза в сделке  18
            if deal[16] >= 0 and deal[2] != deal[13]:
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[13]))      # Реализованный потенциал     19
            else:
                deal.append(0)
            if deal[16] < 0 and deal[2] != deal[14]:  # Реализованная угроза                                 20
                deal.append((deal[2] - deal[12]) / (deal[2] - deal[14]))
            else:
                deal.append(0)
            deal.append(all_export[i][20])
            if all_export[i][25] == 'Pogl short':  # тип реальной или фантомной сделки            21
                deal.append('Pogl short')
            else:
                deal.append('')
            deals.append(deal)
        # --------------------------------------------------------------------------------------------------------------
        # вход в лонг --------------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Long' or all_export[i][25] == 'Okno long' or all_export[i][25] == 'Phantom long enter'\
                or all_export[i][25] == 'Zashita long' or all_export[i][26] == 'Okno long' \
                or all_export[i][26] == 'Long' or all_export[i][26] == 'Phantom long enter' \
                or all_export[i][25] == 'Razvorot from short':
            deal = []
            deal.append(all_export[i][0])     # дата начала     0
            deal.append(all_export[i][1])     # время начала    1
            if all_export[i][25] == 'Long' or all_export[i][25] == 'Razvorot from short' or all_export[i][26] == 'Long':
                deal.append(all_export[i][6])     # цена сделки 2
            else:
                buyPrice = all_export[i][21] + prosk
                if all_export[i][5] - all_export[i][2] > gap:
                    buyPrice = all_export[i][5] + prosk
                if buyPrice > all_export[i][3]:
                    buyPrice = all_export[i][3]
                if buyPrice < all_export[i][4]:
                    buyPrice = all_export[i][4]
                deal.append(buyPrice)
            deal.append(all_export[i][34])    # количество в сделке   3
            deal.append(all_export[i][32])    # капитал на начало     4
            deal.append(1)                    # Признак лонг          5
            if all_export[i][25] == 'Long' or all_export[i][26] == 'Long':
                deal.append('Long')           # Тип сделки            6
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
        # вход в шорт --------------------------------------------------------------------------------------------------
        if all_export[i][25] == 'Short' or all_export[i][25] == 'Okno short' or all_export[i][26] == 'Short'\
                or all_export[i][25] == 'Razvorot from long' or all_export[i][26] == 'Okno short' \
                or all_export[i][25] == 'Phantom short enter' or all_export[i][25] == 'Zashita short' \
                or all_export[i][26] == 'Phantom short enter':
            deal = []
            deal.append(all_export[i][0])  # дата начала               0
            deal.append(all_export[i][1])  # время начала              1
            if all_export[i][25] == 'Short' or all_export[i][25] == 'Razvorot from long' \
                    or all_export[i][26] == 'Short':
                deal.append(all_export[i][8])  # цена сделки           2
            else:
                sellPrice = all_export[i][22] - prosk
                if all_export[i][2] - all_export[i][5] > gap:
                    sellPrice = all_export[i][5] - prosk
                if sellPrice < all_export[i][4]:
                    sellPrice = all_export[i][4]
                if sellPrice > all_export[i][3]:
                    sellPrice = all_export[i][3]
                deal.append(sellPrice)      # цена сделки
            deal.append(all_export[i][34])  # количество в сделке      3
            deal.append(all_export[i][32])  # капитал на начало        4
            deal.append(-1)                 # признак шорт             5
            if all_export[i][25] == 'Short' or all_export[i][25] == 'Razvorot from long' \
                    or all_export[i][26] == 'Short':
                if all_export[i][20]:
                    deal.append('Short comeback')  # тип сделки               6
                else:
                    deal.append('Short')        # тип сделки               6
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
