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

    def delete_elem(self, elem: str) -> None:
        if elem in self:
            del self.data[elem]
        else:
            print("Nothing to delete.")

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.data = json.load(json_file)

    def dump(self, path) -> None:
        with open(path, 'w') as json_file:
            json.dump(self.data, json_file, indent=4, ensure_ascii=False)


class SecInfo(Json):
    def __init__(self) -> None:
        self.data: dict[str, dict[str, str]] = dict[str, dict[str, str]]()

    def set_info(self, sectype: str, ticker: str, goal: str, stock: str = None) -> None:
        self.data[ticker] = {'goal': goal, 'sectype': sectype, 'stock': stock}


class PortfoliosNames(Json):
    def __init__(self) -> None:
        self.data: list[str] = list[str]()

    def add_portfolio(self, portfolio: str) -> None:
        if portfolio not in self.data:
            self.data.append(portfolio)


class Portfolio(Json):
    def __init__(self) -> None:
        self.data: dict = dict()

    def set_paper(self, ticker: str, quantity) -> None:
        self.data[ticker] = quantity


class Summary:
    def __init__(self, path: str) -> None:
        self.path = path
        self.portfolios_names = PortfoliosNames()
        self.sec_info = SecInfo()
        self.portfolios = dict[str, Portfolio]()

    def add_portfolio(self, name: str) -> None:
        self.portfolios_names.add_portfolio(name)
        self.portfolios[name] = Portfolio()

    def dump(self):
        path = os.path.join(self.path, 'portfolios.json')
        self.portfolios_names.dump(path)

        path = os.path.join(self.path, 'securities.json')
        self.sec_info.dump(path)

        for name in self.portfolios:
            path = os.path.join(self.path, name+'.json')
            self.portfolios[name].dump(path)



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
