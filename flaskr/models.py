# FILE WITH MODELS FROM DATABASE


class Lotnisko:

    def __init__(self,
                 _id: int = None,
                 nazwa: str = '', miasto: str = '', kraj: str = '',
                 iatacode: str = '', icaocode: str = '',
                 longitude: float = None, latitude: float = None):
        self.id = _id
        self.nazwa = nazwa
        self.miasto = miasto
        self.kraj = kraj
        self.iatacode = iatacode
        self.icaocode = icaocode
        self.longitude = longitude
        self.latitude = latitude


class LiniaLotnicza:

    def __init__(self, _id, nazwa, kraj):
        self.id = _id,
        self.nazwa = nazwa,
        self.kraj = kraj
