import cx_Oracle
import os

from typing import List, Tuple

from flaskr.internal.helpers import constants as c
from flaskr.internal.helpers.models import LiniaLotnicza, Lotnisko, Producent, Model, Pas


class OracleDB:

    def __init__(self):
        pool_min = 0
        pool_max = 4
        pool_inc = 0
        pool_gmd = cx_Oracle.SPOOL_ATTRVAL_WAIT
        print("Connecting")
        cx_Oracle.init_oracle_client(lib_dir=os.environ.get('PATH_TO_INSTANTCLIENT'))
        self.pool = cx_Oracle.SessionPool(user=os.environ.get('ORACLE_USER'),
                                          password=os.environ.get('ORACLE_PASSWD'),
                                          dsn=f"{os.environ.get('ORACLE_HOSTNAME')}/{os.environ.get('ORACLE_SERVICENAME')}",
                                          min=pool_min,
                                          max=pool_max,
                                          increment=pool_inc,
                                          threaded=True,
                                          getmode=pool_gmd)

    def select_airports(self) -> Tuple[List[str], List[Lotnisko]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT LOTNISKO_ID, NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE  FROM LOTNISKO")
        headers = [header[0] for header in cr.description]
        airports_list = []
        for airport in cr:
            airports_list.append(
                Lotnisko(
                    _id=airport[0],
                    nazwa=airport[1],
                    miasto=airport[2],
                    kraj=airport[3],
                    iatacode=airport[4],
                    icaocode=airport[5],
                    longitude=airport[6],
                    latitude=airport[7]
                )
            )
        cr.close()

        return headers, airports_list

    def select_airport(self, airport_id) -> Lotnisko:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE
                        FROM LOTNISKO
                       WHERE LOTNISKO_ID = :id""",
                   id=airport_id)
        data = cr.fetchone()
        return Lotnisko(nazwa=data[0],
                        miasto=data[1],
                        kraj=data[2],
                        iatacode=data[3],
                        icaocode=data[4],
                        longitude=data[5],
                        latitude=data[6])

    def insert_airport(self, nazwa, miasto, kraj, iatacode, icaocode, longitude, latitude) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO LOTNISKO (NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE)
                          VALUES (:nazwa,
                                  :miasto,
                                  :kraj,
                                  :iatacode,
                                  :icaocode,
                                  :longitude,
                                  :latitude)""",
                       nazwa=nazwa,
                       miasto=miasto,
                       kraj=kraj,
                       iatacode=iatacode,
                       icaocode=icaocode,
                       longitude=longitude,
                       latitude=latitude)
        except cx_Oracle.IntegrityError as e:
            if c.LOTNISKO_UN_IATA in str(e):
                cr.close()
                return "Lotnisko o takim kodzie IATA już istnieje", c.ERROR, c.LOTNISKO_UN_IATA
            if c.LOTNISKO_UN_NAZWA in str(e):
                cr.close()
                return "Lotnisko o takiej nazwie już istnieje", c.ERROR, c.LOTNISKO_UN_NAZWA
            if c.LOTNISKO_UN_ICAO in str(e):
                cr.close()
                return "Lotnisko o takim kodzie ICAO już istnieje", c.ERROR, c.LOTNISKO_UN_ICAO
            if c.LOTNISKO_UN_GEO in str(e):
                cr.close()
                return "Lotnisko o takim położeniu geograficznym już istnieje", c.ERROR, c.LOTNISKO_UN_GEO
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nowe lotnisko", c.SUCCESS, None

    def update_airport(self, airport_id, nazwa, miasto, kraj, iatacode, icaocode, longitude, latitude) -> \
            Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE LOTNISKO
                          SET NAZWA = :nazwa,
                              MIASTO = :miasto,
                              KRAJ = :kraj,
                              IATACODE = :iatacode,
                              ICAOCODE = :icaocode,
                              LONGITUDE = :longitude,
                              LATITUDE = :latitude
                          WHERE LOTNISKO_ID = :id""",
                       nazwa=nazwa,
                       miasto=miasto,
                       kraj=kraj,
                       iatacode=iatacode,
                       icaocode=icaocode,
                       longitude=longitude,
                       latitude=latitude,
                       id=airport_id)
        except cx_Oracle.IntegrityError as e:
            if c.LOTNISKO_UN_IATA in str(e):
                cr.close()
                return "Lotnisko o takim kodzie IATA już istnieje", c.ERROR, c.LOTNISKO_UN_IATA
            if c.LOTNISKO_UN_NAZWA in str(e):
                cr.close()
                return "Lotnisko o takiej nazwie już istnieje", c.ERROR, c.LOTNISKO_UN_NAZWA
            if c.LOTNISKO_UN_ICAO in str(e):
                cr.close()
                return "Lotnisko o takim kodzie ICAO już istnieje", c.ERROR, c.LOTNISKO_UN_ICAO
            if c.LOTNISKO_UN_GEO in str(e):
                cr.close()
                return "Lotnisko o takim położeniu geograficznym już istnieje", c.ERROR, c.LOTNISKO_UN_GEO
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślna aktualizacja lotniska", c.SUCCESS, None

    def delete_airport(self, airport_id: int) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM LOTNISKO WHERE LOTNISKO_ID = :id", id=airport_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć lotniska, ponieważ jest powiązane z lotami", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto lotnisko", c.SUCCESS

    def select_airlines(self) -> Tuple[List[str], List[LiniaLotnicza]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT LINIALOTNICZA_ID, NAZWA, KRAJ FROM LINIALOTNICZA")
        headers = [header[0] for header in cr.description]
        airlines_list = []
        for airline in cr:
            airlines_list.append(
                LiniaLotnicza(
                    _id=airline[0],
                    nazwa=airline[1],
                    kraj=airline[2]
                )
            )
        cr.close()

        return headers, airlines_list

    def select_airline(self, airline_id) -> LiniaLotnicza:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT NAZWA, KRAJ
                        FROM LINIALOTNICZA
                       WHERE LINIALOTNICZA_ID = :id""",
                   id=airline_id)
        data = cr.fetchone()
        return LiniaLotnicza(nazwa=data[0], kraj=data[1])

    def insert_airline(self, nazwa, kraj) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO LINIALOTNICZA (NAZWA, KRAJ)
                               VALUES (:nazwa,
                                       :kraj)""",
                       nazwa=nazwa,
                       kraj=kraj)
        except cx_Oracle.IntegrityError as e:
            if c.LINIALOTNICZA_UN_NAZWA in str(e):
                cr.close()
                return "Linia lotnicza o takiej nazwie już istnieje", c.ERROR, c.LINIALOTNICZA_UN_NAZWA
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nową linię lotniczą", c.SUCCESS, None

    def update_airline(self, airline_id: int, nazwa: str, kraj: str) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE LINIALOTNICZA
                                  SET NAZWA = :nazwa,
                                      KRAJ = :kraj
                                  WHERE LINIALOTNICZA_ID = :id""",
                       nazwa=nazwa,
                       kraj=kraj,
                       id=airline_id)
        except cx_Oracle.IntegrityError as e:
            if c.LINIALOTNICZA_UN_NAZWA in str(e):
                cr.close()
                return "Linia lotnicza o takiej nazwie już istnieje", c.ERROR, c.LINIALOTNICZA_UN_NAZWA
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
            return "Pomyślna aktualizacja linii lotniczej", c.SUCCESS, None

    def delete_airline(self, airline_id: int) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM LINIALOTNICZA WHERE LINIALOTNICZA_ID = :id", id=airline_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć linii lotniczej, ponieważ jest przypisana do lotu", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto linię lotniczą", c.SUCCESS

    def select_manufacturers(self) -> Tuple[List[str], List[Producent]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT PRODUCENT_ID, NAZWA, KRAJ FROM PRODUCENT")
        headers = [header[0] for header in cr.description]
        manufacturers_list = []
        for manufacturer in cr:
            manufacturers_list.append(
                Producent(
                    _id=manufacturer[0],
                    nazwa=manufacturer[1],
                    kraj=manufacturer[2]
                )
            )
        cr.close()
        return headers, manufacturers_list

    def select_manufacturers_sort_nazwa(self) -> List[Producent]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT PRODUCENT_ID, NAZWA, KRAJ FROM PRODUCENT ORDER BY NAZWA")
        manufacturers_list = []
        for manufacturer in cr:
            manufacturers_list.append(
                Producent(
                    _id=manufacturer[0],
                    nazwa=manufacturer[1],
                    kraj=manufacturer[2]
                )
            )
        cr.close()
        return manufacturers_list

    def select_manufacturer(self, manufacturer_id: int) -> Producent:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT NAZWA, KRAJ
                            FROM PRODUCENT
                           WHERE PRODUCENT_ID = :id""",
                   id=manufacturer_id)
        data = cr.fetchone()
        return Producent(nazwa=data[0], kraj=data[1])

    def insert_manufacturer(self, nazwa, kraj) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO PRODUCENT (NAZWA, KRAJ)
                               VALUES (:nazwa,
                                       :kraj)""",
                       nazwa=nazwa,
                       kraj=kraj)
        except cx_Oracle.IntegrityError:
            # TODO: catching unique keys error
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nowego producenta", c.SUCCESS, None

    def update_manufacturer(self, manufacturer_id, nazwa, kraj) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE PRODUCENT
                             SET NAZWA = :nazwa,
                                 KRAJ = :kraj
                           WHERE PRODUCENT_ID = :id""",
                       nazwa=nazwa,
                       kraj=kraj,
                       id=manufacturer_id)
        except cx_Oracle.IntegrityError:
            # TODO: catching unique keys error
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślna aktualizacja producenta", c.SUCCESS, None

    def delete_manufacturer(self, manufacturer_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM PRODUCENT WHERE PRODUCENT_ID = :id", id=manufacturer_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć producenta, ponieważ posiada modele", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto producenta", c.SUCCESS

    def select_models_manufacturers(self) -> Tuple[List[str], List[Model]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT m.MODEL_ID AS MODEL_ID,
                                 m.NAZWA AS NAZWA_MODELU,
                                 m.LICZBAMIEJSC AS LICZBA_MIEJSC,
                                 m.PREDKOSC AS PREDKOSC,
                                 p.NAZWA AS NAZWA_PRODUCENTA
                          FROM MODEL m INNER JOIN PRODUCENT p ON m.PRODUCENT_ID = p.PRODUCENT_ID""")
        headers = [header[0] for header in cr.description]
        models_list = []
        for model in cr:
            models_list.append(
                Model(
                    _id=model[0],
                    nazwa=model[1],
                    liczba_miejsc=model[2],
                    predkosc=model[3],
                    producent=Producent(nazwa=model[4])
                )
            )
        cr.close()

        return headers, models_list

    def select_model_manufacturer(self, model_id) -> Model:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT m.NAZWA, m.LICZBAMIEJSC, m.PREDKOSC, p.PRODUCENT_ID, p.NAZWA, p.KRAJ
                        FROM MODEL m INNER JOIN PRODUCENT p ON m.PRODUCENT_ID = p.PRODUCENT_ID
                       WHERE MODEL_ID = :id""",
                   id=model_id)
        data = cr.fetchone()
        return Model(nazwa=data[0],
                     liczba_miejsc=data[1],
                     predkosc=data[2],
                     producent=Producent(_id=data[3], nazwa=data[4], kraj=data[5])
                     )

    def insert_model(self, nazwa, liczba_miejsc, predkosc, producent_id) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO MODEL (NAZWA, LICZBAMIEJSC, PREDKOSC, PRODUCENT_ID)
                               VALUES (:nazwa,
                                       :liczbamiejsc,
                                       :predkosc,
                                       :producent_id)""",
                       nazwa=nazwa,
                       liczbamiejsc=liczba_miejsc,
                       predkosc=predkosc,
                       producent_id=producent_id)
        except cx_Oracle.IntegrityError:
            # TODO: catching unique keys error
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nowy model samolotu", c.SUCCESS, None

    def update_model(self, model_id, nazwa, liczba_miejsc, predkosc, producent_id) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE MODEL
                          SET NAZWA = :nazwa,
                              LICZBAMIEJSC = :liczbamiejsc,
                              PREDKOSC = :predkosc,
                              PRODUCENT_ID = :producent_id
                          WHERE MODEL_ID = :id""",
                       nazwa=nazwa,
                       liczbamiejsc=liczba_miejsc,
                       predkosc=predkosc,
                       producent_id=producent_id,
                       id=model_id)
        except cx_Oracle.IntegrityError:
            # TODO catching unique keys error
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
            return "Pomyślna aktualizacja modelu", c.SUCCESS, None

    def delete_model(self, model_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM MODEL WHERE MODEL_ID = :id", id=model_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć modelu, ponieważ jest przypisany do lotów", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto model", c.SUCCESS

    def select_runways(self) -> Tuple[List[str], List[Pas]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT PAS_ID, NAZWA, DLUGOSC, OPIS FROM PAS")
        headers = [header[0] for header in cr.description]
        runways_list = []
        for runway in cr:
            runways_list.append(
                Pas(_id=runway[0],
                    nazwa=runway[1],
                    dlugosc=runway[2],
                    opis=runway[3])
            )
        cr.close()

        return headers, runways_list

    def select_runway(self, runway_id) -> Pas:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT NAZWA, DLUGOSC, OPIS
                        FROM PAS
                       WHERE PAS_ID = :id""",
                   id=runway_id)
        data = cr.fetchone()
        return Pas(nazwa=data[0], dlugosc=data[1], opis=data[2])

    def insert_runway(self, nazwa, dlugosc, opis) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO PAS (NAZWA, DLUGOSC, OPIS)
                               VALUES (:nazwa,
                                       :dlugosc,
                                       :opis)""",
                       nazwa=nazwa,
                       dlugosc=dlugosc,
                       opis=opis)
        except cx_Oracle.IntegrityError:
            # TODO: catching unique keys exceptions
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nowy pas startowy", c.SUCCESS, None

    def update_runway(self, runway_id, nazwa, dlugosc, opis) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE PAS
                             SET NAZWA = :nazwa,
                                 DLUGOSC = :dlugosc,
                                 OPIS = :opis
                           WHERE PAS_ID =  :id""",
                       nazwa=nazwa,
                       dlugosc=dlugosc,
                       opis=opis,
                       id=runway_id)
        except cx_Oracle.IntegrityError:
            # TODO: catching unique keys error
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
            return "Pomyślna aktualizacja pasa startowego", c.SUCCESS, None

    def delete_runway(self, runway_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM PAS WHERE PAS_ID = :id",
                       id=runway_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć pasa startowego, ponieważ jest przypisany do lotu", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto pas startowy", c.SUCCESS
