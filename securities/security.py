import requests
from xml.etree import ElementTree
import yfinance

class Security():
    def __init__(self, ticker: str, stock: str) -> None:
        self.ticker = ticker
        if stock == "MOEX" or stock == "OTHR":
            self.stock = stock
        else:
            raise "Incorrect stock name."
        if stock == "MOEX":
            self.load_board_()
        if stock == "MOEX":
            self.name = self.load_field_moex_('securities', 'SECNAME')
        else:
            stock = yfinance.Ticker(self.ticker)
            self.name = stock.info['shortName']

    def load_board_(self) -> str:
        url = "https://iss.moex.com/iss/securities/"+ self.ticker +".xml" \
        "?iss.meta=off&iss.only=boards&boards.columns=is_primary,boardid"
        response = requests.get(url)
        roots = ElementTree.fromstring(response.content).findall('.//data//rows//row')
        self.board_id_ = None
        for root in roots:
            items = root.items()
            # check is primary
            if items[0][1] == '1':
                self.board_id_ = items[1][1]
        if self.board_id_ is None:
            raise "Not found."

        if self.board_id_ in ["TQOB","EQOB","TQOD","TQCB","EQQI","TQIR"]:
            self.moex_security_type_ = "bonds"
        elif self.board_id_ in ["TQTF","TQBR","SNDX","TQIF","TQTD"]:
            self.moex_security_type_ = "shares"
        else:
            raise "Unknown board."

    def load_field_moex_(self, table, field) -> str:
        url = "https://iss.moex.com/iss/engines/stock/markets/" \
            + self.moex_security_type_+"/boards/"+self.board_id_ + "/securities.xml" \
            "?iss.meta=off&iss.only="+table+"&"+table+".columns=SECID,"+field
        response = requests.get(url)
        roots = ElementTree.fromstring(response.content).findall('.//row')
        for root in roots:
            items = root.items()
            if items[0][1] == self.ticker:
                return items[1][1]
        raise "Not found."

class Share(Security):
    def __init__(self, ticker: str, stock: str) -> None:
        super().__init__(ticker, stock)

    def price(self) -> tuple[float, str]:
        if self.stock == "MOEX":
            return float(self.load_field_moex_("marketdata", "LAST")), \
                self.load_field_moex_("securities", "CURRENCYID")
        stock = yfinance.Ticker(self.ticker)
        return stock.info['regularMarketPrice'], 'USD'

class Bond(Security):
    def __init__(self, ticker: str, stock: str) -> None:
        super().__init__(ticker, stock)

    def price(self) -> tuple[float, str]:
        if self.stock == "MOEX":
            percent_price = float(self.load_field_moex_("marketdata", "LAST"))
            face_value = float(self.load_field_moex_("securities", "FACEVALUE"))
            accruedint = float(self.load_field_moex_("securities", "ACCRUEDINT"))
            return percent_price / 100 * face_value + accruedint
        raise "Only MOEX for bonds supproted."
