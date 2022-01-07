from enum import Enum
class DataType(Enum):
    NONE = 0
    STRING = 1
    NUMBER = 2
    PERCENT = 3

class Element:
    def __init__(self, value, dataype: DataType, uses_left:int=0) -> None:
        self.value = value
        self.datatype = dataype
        self.uses_left = uses_left

    def to_printable(self):
        if self.datatype is DataType.NONE:
            return ""
        elif self.datatype == DataType.STRING:
            return self.value
        elif self.datatype == DataType.NUMBER:
            return "{.2f}".format(self.value)
        elif self.datatype == DataType.PERCENT:
            return "{.2%}".format(self.value)
        else:
            raise "WTF"

class Column:
    def __init__(self, values) -> None:
        self.values = values
    def to_printable(self):
        maxlen: int = 0
        for el in self.values:
            if el.uses_left == 0:
                s = el.to_printabe()
                maxlen = max(maxlen, len(s))
        rescol = Column([])
        for el in self.values:
            pass


class Table:
    def __init__(self) -> None:
        pass