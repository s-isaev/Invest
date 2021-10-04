import json, os
from securities import security
from currecy import currecy

class SecInfo:
    def __init__(self) -> None:
        self.info = dict()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.info = json.load(json_file)

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

class Portfolios:
    def __init__(self) -> None:
        self.portfolios = list()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.portfolios = json.load(json_file)

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
        self.securities = dict()

    def load(self, path) -> None:
        with open(path, 'r') as json_file:
            self.securities = json.load(json_file)

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
        self.portfolios_desctiptions = Portfolios()
        self.sec_info = SecInfo()
        self.portfolios = dict()

    def add_portfolio(self, name: str) -> None:
        self.portfolios_desctiptions.add_portfolio(name)
        self.portfolios[name] = Portfolio()

    def dump(self):
        path = os.path.join(self.path, 'portfolios.json')
        self.portfolios_desctiptions.dump(path)

        path = os.path.join(self.path, 'securities.json')
        self.sec_info.dump(path)

        for name in self.portfolios:
            path = os.path.join(self.path, name+'.json')
            self.portfolios[name].dump(path)

    def create_table(self):
        table = dict()
        for potfolio in self.portfolios:
            for c_security in self.portfolios[potfolio].securities:
                quantity = self.portfolios[potfolio].securities[c_security]
                info = self.sec_info.info[c_security]
                
                if info['goal'] not in table:
                        table[info['goal']] = 0.0
                if info['sectype'] == 'share':
                    c_sec = security.Share(c_security, info['stock'])
                elif info['sectype'] == 'bond':
                    c_sec = security.Bond(c_security, info['stock'])
                prc, curr = c_sec.price()
                table[info['goal']] += currecy.convert_to_rouble(prc, curr) * quantity

        return table

