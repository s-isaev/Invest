import sys, os, datetime
if '.' not in sys.path:
    sys.path.append('.')
from importlib import reload
from portfolio import portfolio
from securities import security

import time

summary = portfolio.Summary(path='D:\Инвест\Invest\data')
summary.load()

MAX_CLASS_NAME_LEN = 10
MAX_SUMM_ROUBLES_LEN = 10
MAX_SUMM_DOLLARS_LEN = 8
TOTAL_LEN = MAX_CLASS_NAME_LEN + MAX_SUMM_ROUBLES_LEN + MAX_SUMM_DOLLARS_LEN + 2

def write_header():
    print(
        ' ' * 25 + 'Price'+ ' ' * 5 + 'Share' + ' ' * 4 + 
        'Target' + ' ' * 4 + 'Ratio' + ' ' * 18 + 'Buy', end='')
    print(' ' * 26 + 'Change' + ' ' * 4 + 'Year Profitability')
    print(
        ' ' * 13 + '(RUB)' + ' ' * 7 + '(USD)' + ' ' * 5 + ' ' * 4 +
        ' ' * 4 + ' ' * 23 + '(RUB)' + ' ' * 4 + '(USD)', end=''
    )
    print(' '*8 + '***|' + ' ' * 5+ '(RUB)' + ' ' * 5 + '(USD)'+ ' ' * 7 + '(RUB)' + ' ' * 5 + '(USD)')

classes = {
    "Gold": "GLD",
    "USA": "USA",
    "Russia": "RUS",
    "Bonds": "BND",
    "OFZ": "OFZ",
    "Emerging": "EMG",
    "Developed": "DEV",
    "Cash": "$$$",
    "Eurobonds": "RES",
    "Capital": "CAP"
}

def write_line(class_name, summ_roubles, summ_dollars, percent=None, target=None, ratio=None, buyrub=None, buyusd=None, extra_line=False):
    print('_' * (TOTAL_LEN + 3 + 10 + 10 + 8 + 19))
    str_class = (classes[class_name])
    if extra_line:
        print()
        print('_' * (TOTAL_LEN + 3 + 10 + 10 + 8 + 19))
    print(str_class, end='|    ')
    print("{:10,.2f}".format(summ_roubles), end='    ')
    print("{:8,.2f}".format(summ_dollars), end='    ' )

    if percent is not None:
        print("{:6.2%}".format(percent), end='    ')
    else:
        print(" " * 5, end='    ' )

    if target is not None:
        print("{:6.2%}".format(target), end='    ')
    else:
        print(" " * 4, end='    ' )
    
    if ratio is not None:
        print("{:5,.2f}".format(ratio), end='    ')

    if buyrub is not None:
        print("{:8,.2f}".format(buyrub), end='  ')
    if buyusd is not None:
        print("{:7,.2f}".format(buyusd), end='')

    print()

rub = security.Currency("RUB")
usd = security.Currency("USD")

def cmp_key(x):
    return 1 / x[1]

targets = {
    "Gold": .05,
    "USA": .40,
    "Russia": .10,
    "Bonds": .10,
    "OFZ": .05,
    "Emerging": .20,
    "Developed": .10,
}

while True:
    invested_by_classes = summary.get_invested_by_classes()
    rubusd = rub.convert(usd, 1)

    capital = 0
    for inv_class in invested_by_classes:
        capital += invested_by_classes[inv_class]
    capital_no_eurobonds = capital - invested_by_classes['Eurobonds']

    inv_classes = []
    for inv_class in invested_by_classes:
        if inv_class != 'Eurobonds' and inv_class != 'Cash':
            inv_classes.append((
                inv_class, 
                targets[inv_class] / (invested_by_classes[inv_class]/capital_no_eurobonds)
            ))
        
    inv_classes.sort(key=cmp_key)

    os.system('cls')
    write_header()
    for inv_class in inv_classes:
        rub_n = invested_by_classes[inv_class[0]]
        ratio = 1/(targets[inv_class[0]] / (invested_by_classes[inv_class[0]]/capital_no_eurobonds))
        buy_rub = None
        if ratio < 1:
            buy_rub = (targets[inv_class[0]] - invested_by_classes[inv_class[0]]/capital_no_eurobonds)*capital_no_eurobonds
        buy_usd = None
        if ratio < 1:
            buy_usd = buy_rub * rubusd
        

        write_line(
            inv_class[0], 
            rub_n, 
            rub_n * rubusd, 
            invested_by_classes[inv_class[0]]/capital_no_eurobonds,
            targets[inv_class[0]],
            ratio,
            buy_rub,
            buy_usd
        )

    write_line(
        "Cash", 
        invested_by_classes["Cash"], 
        invested_by_classes["Cash"] * rubusd,
        invested_by_classes["Cash"]/capital_no_eurobonds
    )
    # write_line(
    #     "Eurobonds", 
    #     invested_by_classes["Eurobonds"], 
    #     invested_by_classes["Eurobonds"] * rubusd,
    #     extra_line=True
    # )
    write_line("Capital", capital, capital * rubusd, extra_line=True)

    print("\nLast updated at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(60)