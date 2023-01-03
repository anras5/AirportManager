# FILE WITH MODELS FROM DATABASE
import datetime


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
                 nazwa: str = '',
                 dlugosc: float = None,
                 opis: str = ''):
        self.id = _id
        self.nazwa = nazwa
        self.dlugosc = dlugosc
        self.opis = opis


class Lot:

    def __init__(self,
                 _id: int = None,
                 linia_lotnicza: LiniaLotnicza = None,
                 lotnisko: Lotnisko = None,
                 model: Model = None,
                 typ: str = ''):
        self.id = _id
        self.linia_lotnicza = linia_lotnicza
        self.lotnisko = lotnisko
        self.model = model
        self.typ = typ


class Przylot(Lot):

    def __init__(self,
                 _id: int = None,
                 data_przylotu: datetime.datetime = None,
                 liczba_pasazerow: int = None,
                 linia_lotnicza: LiniaLotnicza = None,
                 lotnisko: Lotnisko = None,
                 model: Model = None,
                 typ: str = ''):
        super().__init__(_id, linia_lotnicza, lotnisko, model, typ)
        self.id = _id
        self.data_przylotu = data_przylotu
        self.liczba_pasazerow = liczba_pasazerow


class Rezerwacja:

    def __init__(self,
                 _id: int = None,
                 poczatek: datetime.datetime = None,
                 koniec: datetime.datetime = None,
                 lot: Lot = None,
                 pas: Pas = None):
        self.id = _id
        self.poczatek = poczatek
        self.koniec = koniec
        self.lot = lot
        self.pas = pas
