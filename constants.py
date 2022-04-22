from enum import Enum


class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class TeamHeaderNames(NoValue):
    red_bull_racing = "Red-Bull"
    ferrari = "Ferrari"
    mercedes = "Mercedes"
    mclaren = "McLaren"
    alpine = "Alpine"
    alfa_romeo = "Alfa-Romeo"
    haas_f1_team = "Haas"
    alphatauri = "AlphaTauri"
    williams = "Williams"
    aston_martin = "Aston-Martin"
