from enum import Enum

TABSIZE = 4

class DataType(Enum):
    NONE = 0
    STRING = 1
    NUMBER = 2
    PERCENT = 3

class Element:
    def __init__(self, value, dataype: DataType, uses_left:int=0) -> None:
        self.value = value
        self.datatype = dataype

        # сколько помимо своего использует левых полей
        self.uses_left = uses_left

    def to_printable(self) -> str:
        match self.datatype:
            case DataType.NONE:
                return ""
            case DataType.STRING:
                return self.value
            case DataType.NUMBER:
                return "{:,.2f}".format(self.value)
            case DataType.PERCENT:
                return "{:.2%}".format(self.value)
            case _:
                raise "WTF"

class Column:
    def __init__(self, values: list[Element]) -> None:
        self.values = values

    def to_printable(
        self, rcol: list[Element]|None, tab:bool=True
    ) -> tuple[list[str], list[Element]]:
        if rcol is not None:
            for i, el in enumerate(rcol):
                if el.datatype != DataType.NONE:
                    self.values[i] = el

        maxlen = 0
        for el in self.values:
            if el.uses_left == 0:
                s = el.to_printable()
                maxlen = max(maxlen, len(s))
        if tab:
            maxlen += TABSIZE
        
        res_strings = []
        res_elems = []
        for el in self.values:
            if el.uses_left == 0:
                res_strings.append(el.to_printable().rjust(maxlen))
                res_elems.append(Element(None, DataType.NONE))
            else:
                s = el.to_printable()
                if len(s) > maxlen:
                    res_strings.append(s[-maxlen:])
                    res_elems.append(
                        Element(
                            s[:-maxlen], 
                            DataType.STRING, 
                            el.uses_left-1
                        )
                    )
                else:
                    res_strings.append(el.to_printable().rjust(maxlen))
                    res_elems.append(Element(None, DataType.NONE))

        return res_strings, res_elems


class Table:
    def __init__(
        self, shape: tuple[int, int], lines: list[int]
    ) -> None:
        self.columns: list[Column] = []
        for _ in range(shape[1]):
            self.columns.append(Column([]))
            for _ in range(shape[0]):
                self.columns[-1].values.append(Element(None, DataType.NONE))
        self.lines = lines

    def set_element(
        self, point: tuple[int, int], element: Element
    ):
        self.columns[point[1]].values[point[0]] = element

    def to_ptintable(self) -> str:
        # columns to printable
        str_columns = []
        old_elems = None
        for i in range(len(self.columns)-1, -1, -1):
            str_column, old_elems = self.columns[i].to_printable(
                old_elems, i!=0
            )
            str_columns.append(str_column)
        str_columns.reverse()

        # printable to string
        result = ""
        row_len = 0
        for i in range(len(str_columns[0])):
            for j in range(len(str_columns)):
                if i == 0:
                    row_len += len(str_columns[j][i])
                result += str_columns[j][i]
            result += "\n"
            if i in self.lines:
                result += "_"*row_len + "\n"
        return result
