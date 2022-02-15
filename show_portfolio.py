import sys, os, datetime
if '.' not in sys.path:
    sys.path.append('.')
from portfolio import portfolio
from securities import security
from financial_table import DataType, Element, Table

import time

summary = portfolio.Summary(path='D:\Инвест\Invest\data')
summary.load()

def create_header(table: Table, rubusd: float):
    table.set_element((0, 1), Element("×{:,.2f}".format(1/rubusd), DataType.STRING))
    table.set_element((0, 2), Element("Price", DataType.STRING))
    table.set_element((0, 3), Element("Share", DataType.STRING))
    table.set_element((0, 4), Element("Target", DataType.STRING))
    table.set_element((0, 5), Element("Ratio", DataType.STRING))
    table.set_element((0, 6), Element("×{:,.2f}".format(1/rubusd), DataType.STRING))
    table.set_element((0, 7), Element("Buy", DataType.STRING))

    table.set_element((1, 1), Element("(RUB)", DataType.STRING))
    table.set_element((1, 2), Element("(USD)", DataType.STRING))
    table.set_element((1, 6), Element("(RUB)", DataType.STRING))
    table.set_element((1, 7), Element("(USD)", DataType.STRING))

classes = {
    "Gold": "GLD|",
    "USA": "USA|",
    "Russia": "RUS|",
    "Bonds": "BND|",
    "OFZ": "OFZ|",
    "Emerging": "EMG|",
    "Developed": "DEV|",
    "Cash": "$$$|",
    "Eurobonds": "RES|",
    "Capital": "CAP|"
}

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

    table = Table((12, 8), [1,2,3,4,5,6,7,8,9,10])
    create_header(table, rubusd)
    for i, inv_class in enumerate(inv_classes):
        rub_n = invested_by_classes[inv_class[0]]
        ratio = 1/(targets[inv_class[0]] / (invested_by_classes[inv_class[0]]/capital_no_eurobonds))
        buy_rub = (targets[inv_class[0]] - invested_by_classes[inv_class[0]]/capital_no_eurobonds)*capital_no_eurobonds
        

        table.set_element((i+2, 0), Element(classes[inv_class[0]], DataType.STRING))
        table.set_element((i+2, 1), Element(rub_n, DataType.NUMBER))
        table.set_element((i+2, 2), Element(rub_n*rubusd, DataType.NUMBER))
        table.set_element((i+2, 3), Element(invested_by_classes[inv_class[0]]/capital_no_eurobonds, DataType.PERCENT))
        table.set_element((i+2, 4), Element(targets[inv_class[0]], DataType.PERCENT))
        table.set_element((i+2, 5), Element(ratio, DataType.NUMBER))
        table.set_element((i+2, 6), Element(buy_rub, DataType.NUMBER))
        table.set_element((i+2, 7), Element(buy_rub*rubusd, DataType.NUMBER))

    table.set_element((9, 0), Element(classes["Cash"], DataType.STRING))
    table.set_element((9, 1), Element(invested_by_classes["Cash"], DataType.NUMBER))
    table.set_element((9, 2), Element(invested_by_classes["Cash"] * rubusd, DataType.NUMBER))
    table.set_element((9, 3), Element(invested_by_classes["Cash"]/capital_no_eurobonds, DataType.PERCENT))

    table.set_element((11, 0), Element(classes["Capital"], DataType.STRING))
    table.set_element((11, 1), Element(capital, DataType.NUMBER))
    table.set_element((11, 2), Element(capital * rubusd, DataType.NUMBER))

    os.system('cls')
    print(table.to_ptintable())

    print("Last updated at", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(60)