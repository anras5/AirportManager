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

    def __init__(self,
                 _id: int = None,
                 nazwa: str = '',
                 kraj: str = ''):
        self.id = _id
        self.nazwa = nazwa
        self.kraj = kraj


class Producent:

    def __init__(self,
                 _id: int = None,
                 nazwa: str = '',
                 kraj: str = ''):
        self.id = _id
        self.nazwa = nazwa
        self.kraj = kraj


class Model:

    def __init__(self,
                 _id: int = None,
                 nazwa: str = '',
                 liczba_miejsc: int = None,
                 predkosc: float = None,
                 producent: Producent = None
                 ):
        self.id = _id
        self.nazwa = nazwa
        self.liczba_miejsc = liczba_miejsc
        self.predkosc = predkosc
        self.producent = producent


class Pas:

    def __init__(self,
                 _id: int = None,
                 dlugosc: float = None,
                 opis: str = ''):
        self.id = _id
        self.dlugosc = dlugosc
        self.opis = opis
