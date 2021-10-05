import json, os
from securities.security import Share, Bond
from currency import currency_functions

class SecInfo:
    def __init__(self) -> None:
        self.info = dict[str, dict[str, str]]()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.info: dict[str, dict[str, str]] = json.load(json_file)

    def dump(self, path) -> None:
        with open(path, 'w') as json_file:
            json.dump(self.info, json_file, indent=4, ensure_ascii=False)

    def set_info(self, sectype:str, ticker: str, goal: str, stock: str) -> None:
        self.info[ticker] = {'goal': goal, 'sectype': sectype, 'stock': stock}

    def del_info(self, ticker: str) -> None:
        if ticker in self.info:
            del self.info[ticker]
        else:
            print("Nothing to delete.")

class PortfoliosNames:
    def __init__(self) -> None:
        self.portfolios = list[str]()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.portfolios: list[str] = json.load(json_file)

    def dump(self, path) -> None:
        with open(path, 'w') as json_file:
            json.dump(self.portfolios, json_file, indent=4, ensure_ascii=False)

    def add_portfolio(self, portfolio:str) -> None:
        if portfolio not in self.portfolios:
            self.portfolios.append(portfolio)

    def del_portfolio(self, portfolio: str) -> None:
        if portfolio in self.portfolios:
            del self.portfolios[portfolio]
        else:
            print("Nothing to delete.")

class Portfolio:
    def __init__(self) -> None:
        self.securities = dict[str, int]()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.securities: dict[str, int] = json.load(json_file)

    def dump(self, path) -> None:
        with open(path, 'w') as json_file:
            json.dump(self.securities, json_file, indent=4, ensure_ascii=False)

    def set_position(self, ticker: str, number: int) -> None:
        self.securities[ticker] = number

    def del_position(self, ticker: str) -> None:
        if ticker in self.securities:
            del self.securities[ticker]
        else:
            print("Nothing to delete.")

class Summary:
    def __init__(self, path:str) -> None:
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

    def create_table(self):
        table = dict()
        for potfolio_name in self.portfolios:
            for security_name in self.portfolios[potfolio_name].securities:
                quantity = self.portfolios[potfolio_name].securities[security_name]
                info = self.sec_info.info[security_name]
                
                if info['goal'] not in table:
                        table[info['goal']] = 0.0
                if info['sectype'] == 'share':
                    security = Share(security_name, info['stock'])
                elif info['sectype'] == 'bond':
                    security = Bond(security_name, info['stock'])
                else:
                    raise "error"
                price, currancy = security.price()
                table[info['goal']] += \
                    currency_functions.convert_to_rouble(
                        price, currancy) * quantity

        return table
