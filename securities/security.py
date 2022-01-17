from __future__ import annotations
import requests
from xml.etree import ElementTree
import yfinance
from forex_python.converter import CurrencyRates


class Paper():
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker


class Currency(Paper):
    def __init__(self, ticker: str) -> None:
        super().__init__(ticker)
        if ticker in ("SUR", "RUR"):
            self.ticker = "RUB"

    def price(self) -> tuple[float, Currency]:
        return 1.0, self

    def convert(self, target: Currency, value: float):
        if self.ticker == target.ticker:
            return value
        c = CurrencyRates()
        return value * c.get_rate(self.ticker, target.ticker)


class Security(Paper):
    def __init__(self, ticker: str, stock: str) -> None:
        super().__init__(ticker)
        if stock not in ("MOEX", "OTHR"):
            raise "Incorrect stock name."
        self.stock = stock
        if stock == "MOEX":
            self.load_moex_board_()
            fields = self.load_fields_moex_('securities', ('SECNAME', 'CURRENCYID'))
            self.name = fields[0]
            self.currency = Currency(fields[1]) 
        else:
            stock = yfinance.Ticker(self.ticker)
            self.name = stock.info['shortName']
            self.currency = Currency(stock.info['currency'])

    def load_moex_board_(self) -> str:
        url = "https://iss.moex.com/iss/securities/" + self.ticker + ".xml" \
            "?iss.meta=off&iss.only=boards&boards.columns=is_primary,boardid"
        response = requests.get(url)
        roots = ElementTree.fromstring(
            response.content).findall('.//data//rows//row')
        self.board_id_ = None
        for root in roots:
            items = root.items()
            # check is primary
            if items[0][1] == '1':
                self.board_id_ = items[1][1]
        if self.board_id_ is None:
            raise "Not found"

        if self.board_id_ in ["TQOB", "EQOB", "TQOD", "TQCB", "EQQI", "TQIR"]:
            self.moex_security_type_ = "bonds"
        elif self.board_id_ in ["TQTF", "TQBR", "SNDX", "TQIF", "TQTD"]:
            self.moex_security_type_ = "shares"
        else:
            raise "Unknown board"

    def load_fields_moex_(self, table, fields, return_meta=False) -> str:
        url = "https://iss.moex.com/iss/engines/stock/markets/" \
            + self.moex_security_type_+"/boards/"+self.board_id_ + "/securities.xml" \
            "?iss.meta=off&iss.only="+table+"&"+table+".columns=SECID,"
        for field in fields:
            url += field+','

        response = requests.get(url)
        roots = ElementTree.fromstring(response.content).findall('.//row')
        for root in roots:
            items = root.items()
            if items[0][1] == self.ticker:
                res = []
                for item in items[1:]:
                    res.append(item[1])

                if return_meta:
                    return res, {"url": url, "response": response.content.decode('utf-8')}
                return res
        raise "Not found"

    def field_to_float(self, price: str, meta: dict) -> float:
        try:
            return float(price)
        except:
            raise Exception(
                "Unable to load field for {}.\nQuery:\n{}\nResponce:\n{}".format(
                    self.ticker, meta['url'], meta['response']
                )
            )
        


class Share(Security):
    def __init__(self, ticker: str, stock: str) -> None:
        super().__init__(ticker, stock)

    def price(self) -> tuple[float, Currency]:
        if self.stock == "MOEX":
            # price_str, meta = self.load_field_moex_("marketdata", "LAST", return_meta=True)
            price, meta = self.load_fields_moex_(
                "marketdata", ("LCURRENTPRICE",), return_meta=True
            )
            return self.field_to_float(price[0], meta), self.currency

        stock = yfinance.Ticker(self.ticker)
        return stock.info['regularMarketPrice'], self.currency


class Bond(Security):
    def __init__(self, ticker: str, stock: str) -> None:
        super().__init__(ticker, stock)

    def price(self) -> tuple[float, Currency]:
        if self.stock == "MOEX":
            # percent_price = float(self.load_field_moex_("marketdata", "LAST"))
            price, meta = self.load_fields_moex_(
                "marketdata", ("LCURRENTPRICE",), return_meta=True
            )
            percent_price = self.field_to_float(price[0], meta)
            fields, meta = self.load_fields_moex_(
                "securities", ("FACEVALUE", "ACCRUEDINT"), return_meta=True
            )
            face_value = self.field_to_float(fields[0], meta)
            accruedint = self.field_to_float(fields[1], meta)
            return percent_price / 100 * face_value + accruedint, self.currency
        raise "Only MOEX for bonds supproted"
