import sys, os, datetime
if '.' not in sys.path:
    sys.path.append('.')
from importlib import reload
from  portfolio import portfolio
reload(portfolio)
import time

summary = portfolio.Summary(path='D:\Инвест\Invest\data')
summary.load()

while True:
    invested_by_classes = summary.get_invested_by_classes()
    os.system('cls')
    for inv_class in invested_by_classes:
        print(inv_class, ": ", invested_by_classes[inv_class], sep='') 

    capital = 0
    for inv_class in invested_by_classes:
        capital += invested_by_classes[inv_class]
    print("\nCapital:", capital)

    print("Last updated:", datetime.datetime.now())
    time.sleep(60)