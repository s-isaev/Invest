import json
import os
from securities.security import Currency, Share, Bond
from multiprocessing.pool import ThreadPool


class Json:
    def __init__(self) -> None:
        self.data = None

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, index):
        return self.data.__getitem__(index)

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.data = json.load(json_file)

    def dump(self, path) -> None:
        with open(path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, ensure_ascii=False)


class SecuritiesInfo(Json):
    def __init__(self) -> None:
        self.data: dict[str, dict[str, str]] = dict[str, dict[str, str]]()

    def set_info(self, sectype: str, ticker: str, goal: str, stock: str = None) -> None:
        self.data[ticker] = {'goal': goal, 'sectype': sectype, 'stock': stock}


class Portfolios(Json):
    def __init__(self) -> None:
        self.data: dict[str, dict] = dict()

    def add_porfolio(self, portfolio: str) -> None:
        self.data[portfolio] = dict()

    def set_paper(self, portfolio: str, ticker: str, quantity) -> None:
        if portfolio in self.data:
            self.data[portfolio][ticker] = quantity
        else:
            print("Portfolio does not exist.")


class Summary:
    def __init__(self, path: str) -> None:
        self.path = path
        self.sec_info = SecuritiesInfo()
        self.portfolios = Portfolios()

    def add_portfolio(self, name: str) -> None:
        self.portfolios.add_porfolio(name)

    def set_paper_info(self, goal: str, ticker: str, sectype: str, stock: str = None) -> None:
        self.sec_info.set_info(sectype, ticker, goal, stock)

    def set_paper(self, portfolio: str, ticker: str, quantity) -> None:
        self.portfolios.set_paper(portfolio, ticker, quantity)

    def dump(self):
        path = os.path.join(self.path, 'portfolios.json')
        self.portfolios.dump(path)
        path = os.path.join(self.path, 'securities.json')
        self.sec_info.dump(path)

    def load(self):
        path = os.path.join(self.path, 'portfolios.json')
        self.portfolios.load(path)
        path = os.path.join(self.path, 'securities.json')
        self.sec_info.load(path)

    def get_invested_by_classes(self):
        pools = dict()
        def get_price(security_name, info, quantity):
            if info['sectype'] == 'share':
                security = Share(security_name, info['stock'])
            elif info['sectype'] == 'bond':
                security = Bond(security_name, info['stock'])
            elif info['sectype'] == 'currency':
                security = Currency(security_name)
            else:
                raise "error"
            price, currency = security.price()
            return currency.convert(Currency('RUB'), price) * quantity

        for potfolio_name in self.portfolios:
            for security_name in self.portfolios[potfolio_name]:
                quantity = self.portfolios[potfolio_name][security_name]
                info = self.sec_info[security_name]
                pools[(potfolio_name, security_name)] = ThreadPool(1).apply_async(
                    get_price, (security_name, info, quantity))

        table = dict()
        for potfolio_name in self.portfolios:
            for security_name in self.portfolios[potfolio_name]:
                info = self.sec_info[security_name]
                if info['goal'] not in table:
                    table[info['goal']] = 0.0
                table[info['goal']] += pools[(potfolio_name, security_name)].get()
        return table
