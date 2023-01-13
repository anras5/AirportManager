import datetime

import cx_Oracle
import os

from typing import List, Tuple

from flaskr.internal.helpers import constants as c
from flaskr.internal.helpers.models import LiniaLotnicza, Lotnisko, Producent, Model, Pas, Przylot, Rezerwacja, Lot, \
    Klasa


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

    def select_airports(self, order=False) -> Tuple[List[str], List[Lotnisko]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        if not order:
            sql = "SELECT LOTNISKO_ID, NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE FROM LOTNISKO"
        else:
            sql = "SELECT LOTNISKO_ID, NAZWA, MIASTO, KRAJ, IATACODE, ICAOCODE, LONGITUDE, LATITUDE " \
                  "FROM LOTNISKO ORDER BY NAZWA"
        cr.execute(sql)
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

    def select_airlines(self, order=False) -> Tuple[List[str], List[LiniaLotnicza]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        if not order:
            sql = "SELECT LINIALOTNICZA_ID, NAZWA, KRAJ FROM LINIALOTNICZA"
        else:
            sql = "SELECT LINIALOTNICZA_ID, NAZWA, KRAJ FROM LINIALOTNICZA ORDER BY NAZWA"
        cr.execute(sql)
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

    def select_manufacturers(self, order=False) -> Tuple[List[str], List[Producent]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        if not order:
            sql = "SELECT PRODUCENT_ID, NAZWA, KRAJ FROM PRODUCENT"
        else:
            sql = "SELECT PRODUCENT_ID, NAZWA, KRAJ FROM PRODUCENT ORDER BY NAZWA"
        cr.execute(sql)
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
        except cx_Oracle.IntegrityError as e:
            if c.PRODUCENT__UN in str(e):
                cr.close()
                return "Producent o takiej nazwie już istnieje", c.ERROR, c.PRODUCENT__UN
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
        except cx_Oracle.IntegrityError as e:
            if c.PRODUCENT__UN in str(e):
                cr.close()
                return "Producent o takiej nazwie już istnieje", c.ERROR, c.PRODUCENT__UN
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

    def select_models_manufacturers(self, order=False) -> Tuple[List[str], List[Model]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        if not order:
            sql = """SELECT m.MODEL_ID AS MODEL_ID,
                            m.NAZWA AS NAZWA_MODELU,
                            m.LICZBAMIEJSC AS LICZBA_MIEJSC,
                            m.PREDKOSC AS PREDKOSC,
                            p.NAZWA AS NAZWA_PRODUCENTA
                       FROM MODEL m INNER JOIN PRODUCENT p ON m.PRODUCENT_ID = p.PRODUCENT_ID"""
        else:
            sql = """SELECT m.MODEL_ID AS MODEL_ID,
                            m.NAZWA AS NAZWA_MODELU,
                            m.LICZBAMIEJSC AS LICZBA_MIEJSC,
                            m.PREDKOSC AS PREDKOSC,
                            p.NAZWA AS NAZWA_PRODUCENTA
                       FROM MODEL m INNER JOIN PRODUCENT p ON m.PRODUCENT_ID = p.PRODUCENT_ID
                       ORDER BY p.NAZWA, m.NAZWA"""
        cr.execute(sql)
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
        except cx_Oracle.IntegrityError as e:
            if c.MODEL_UN_NAZWA in str(e):
                cr.close()
                return "Ten producent już posiada model o takiej nazwie", c.ERROR, c.MODEL_UN_NAZWA
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
        except cx_Oracle.IntegrityError as e:
            if c.MODEL_UN_NAZWA in str(e):
                cr.close()
                return "Ten producent już posiada model o takiej nazwie", c.ERROR, c.MODEL_UN_NAZWA
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

    def select_runways_by_ids(self, runways_id) -> List[Pas]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        bind_names = [f":{i + 1}" for i in range(len(runways_id))]
        sql = "SELECT PAS_ID, NAZWA, DLUGOSC, OPIS FROM PAS WHERE PAS_ID IN (%s)" % (','.join(bind_names))
        cr.execute(sql, runways_id)
        runways_list = []
        for runway in cr:
            runways_list.append(
                Pas(_id=runway[0],
                    nazwa=runway[1],
                    dlugosc=runway[2],
                    opis=runway[3])
            )
        cr.close()

        return runways_list

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
        except cx_Oracle.IntegrityError as e:
            if c.PAS__UN in str(e):
                cr.close()
                return "Pas o takiej nazwie już istnieje", c.ERROR, c.PAS__UN
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
        except cx_Oracle.IntegrityError as e:
            if c.PAS__UN in str(e):
                cr.close()
                return "Pas o takiej nazwie już istnieje", c.ERROR, c.PAS__UN
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

    def select_available_runways(self, start: datetime.datetime, end: datetime.datetime) -> List[Pas]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.PAS_ID, p.NAZWA
                        FROM PAS p 
                       WHERE p.PAS_ID NOT IN (SELECT r.PAS_ID
 					                        FROM REZERWACJA r
 					                       WHERE :start_time < r.KONIEC AND :end_time > r.POCZATEK)""",
                   start_time=start,
                   end_time=end)
        runways_list = []
        for runway in cr:
            runways_list.append(
                Pas(_id=runway[0], nazwa=runway[1])
            )
        cr.close()
        return runways_list

    def select_arrivals(self) -> Tuple[List[str], List[Przylot]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ID,
                             p.DATAPRZYLOTU AS TERMIN,
	                         p.LICZBAPASAZEROW,
	                         ll.NAZWA AS LINIA_LOTNICZA,
	                         lt.NAZWA AS LOTNISKO,
	                         p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM PRZYLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                     INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                     INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                     INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                     INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID""")
        headers, arrivals_list = self.__select_arrivals_query_to_list(cr)
        cr.close()

        return headers, arrivals_list

    def select_arrivals_by_dates(self, date_start, date_end) -> Tuple[List[str], List[Przylot]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ID,
                                     p.DATAPRZYLOTU AS TERMIN,
        	                         p.LICZBAPASAZEROW,
        	                         ll.NAZWA AS LINIA_LOTNICZA,
        	                         lt.NAZWA AS LOTNISKO,
        	                         p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM PRZYLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                     INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                     INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                     INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                     INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID
                      WHERE p.DATAPRZYLOTU >= :date_start AND p.DATAPRZYLOTU <= :date_end""",
                   date_start=date_start,
                   date_end=date_end)
        headers, arrivals_list = self.__select_arrivals_query_to_list(cr)
        cr.close()

        return headers, arrivals_list

    def __select_arrivals_query_to_list(self, cr: cx_Oracle.Cursor):
        headers = [header[0] for header in cr.description]
        arrivals_list = []
        for arrival in cr:
            arrivals_list.append(
                Przylot(
                    _id=arrival[0],
                    data_przylotu=arrival[1],
                    liczba_pasazerow=arrival[2],
                    linia_lotnicza=LiniaLotnicza(nazwa=arrival[3]),
                    lotnisko=Lotnisko(nazwa=arrival[4]),
                    model=Model(nazwa=arrival[5])
                )
            )
        return headers, arrivals_list

    def select_arrival(self, lot_id) -> Przylot:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ID,
                             p.DATAPRZYLOTU AS TERMIN,
                             p.LICZBAPASAZEROW,
                             ll.LINIALOTNICZA_ID,
                             ll.NAZWA AS LINIA_LOTNICZA,
                             lt.LOTNISKO_ID,
                             lt.NAZWA AS LOTNISKO,
                             m.MODEL_ID,
                             p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM PRZYLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                     INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                     INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                     INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                     INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID
                      WHERE p.LOT_ID = :lot_id""",
                   lot_id=lot_id)
        data = cr.fetchone()
        arrival = Przylot(_id=data[0], data_przylotu=data[1], liczba_pasazerow=data[2],
                          linia_lotnicza=LiniaLotnicza(_id=data[3], nazwa=data[4]),
                          lotnisko=LiniaLotnicza(_id=data[5], nazwa=data[6]),
                          model=Model(_id=data[7], nazwa=data[8]))
        cr.close()
        return arrival

    def insert_arrival(self, linia_lotnicza_id, lotnisko_id, model_id,
                       data_przylotu, liczba_pasazerow, pas_id) -> Tuple[str, str, str]:

        connection = self.pool.acquire()
        cr = connection.cursor()

        lot_id = cr.var(cx_Oracle.NUMBER)

        lot_sql = """INSERT INTO LOT(LINIALOTNICZA_ID, LOTNISKO_ID, MODEL_ID, TYP)
                          VALUES (:1, :2, :3, 'przylot')
                       RETURNING LOT_ID INTO :4"""

        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        przylot_sql = """INSERT INTO PRZYLOT(DATAPRZYLOTU, LICZBAPASAZEROW)
                              VALUES (:1, :2)"""

        cr.execute(przylot_sql, (data_przylotu, liczba_pasazerow))

        rezerwacja_sql = """INSERT INTO REZERWACJA(POCZATEK, KONIEC, LOT_ID, PAS_ID)
                                 VALUES (:1, :2, :3, :4)"""

        cr.execute(rezerwacja_sql, (data_przylotu,
                                    data_przylotu + datetime.timedelta(minutes=c.MINUTES_FOR_FLIGHT),
                                    lot_id.getvalue()[0],
                                    pas_id))

        connection.commit()
        cr.close()

        return "Pomyślnie dodano nowy przylot", c.SUCCESS, None

    def update_arrival(self, lot_id, linia_lotnicza_id, lotnisko_id, model_id,
                       data_przylotu, liczba_pasazerow, pas_id) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        lot_sql = """UPDATE LOT
                        SET LINIALOTNICZA_ID = :1,
                            LOTNISKO_ID = :2,
                            MODEL_ID = :3
                      WHERE LOT_ID = :4"""
        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        przylot_sql = """UPDATE PRZYLOT
                            SET DATAPRZYLOTU = :1,
                                LICZBAPASAZEROW = :2
                          WHERE LOT_ID = :3"""
        cr.execute(przylot_sql, (data_przylotu, liczba_pasazerow, lot_id))

        rezerwacje_sql = """DELETE FROM REZERWACJA WHERE LOT_ID = :lot_id"""
        cr.execute(rezerwacje_sql, lot_id=lot_id)

        rezerwacja_sql = """INSERT INTO REZERWACJA(POCZATEK, KONIEC, LOT_ID, PAS_ID)
                                 VALUES (:1, :2, :3, :4)"""
        cr.execute(rezerwacja_sql, (data_przylotu,
                                    data_przylotu + datetime.timedelta(minutes=c.MINUTES_FOR_FLIGHT),
                                    lot_id,
                                    pas_id))

        connection.commit()
        cr.close()
        return "Pomyślnie zaktualizowano przylot", c.SUCCESS, None

    def delete_arrival(self, lot_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        # delete from PRZYLOT
        cr.execute("DELETE FROM PRZYLOT WHERE LOT_ID = :lot_id", lot_id=lot_id)

        # delete from REZERWACJA
        cr.execute("DELETE FROM REZERWACJA WHERE LOT_ID = :lot_id", lot_id=lot_id)

        # delete from LOT
        cr.execute("DELETE FROM LOT WHERE LOT_ID = :lot_id", lot_id=lot_id)

        connection.commit()
        cr.close()

        return "Pomyślnie usunięto przylot", c.SUCCESS

    def select_reservations(self) -> Tuple[List[str], List[Rezerwacja]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        sql = """SELECT r.rezerwacja_id, r.poczatek, r.koniec, l.lot_id, p.NAZWA 
                 FROM REZERWACJA r INNER JOIN LOT l ON r.LOT_ID = l.LOT_ID 
                                   INNER JOIN PAS p ON r.PAS_ID = p.PAS_ID"""
        cr.execute(sql)
        headers = [header[0] for header in cr.description]
        reservations_list = []
        for data in cr:
            reservations_list.append(
                Rezerwacja(
                    _id=data[0],
                    poczatek=data[1],
                    koniec=data[2],
                    lot=Lot(_id=data[3]),
                    pas=Pas(nazwa=data[4])
                )
            )
        cr.close()

        return headers, reservations_list

    def select_reservations_by_flight(self, flight_id) -> Tuple[List[str], List[Rezerwacja]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        sql = """SELECT r.rezerwacja_id, r.poczatek, r.koniec, p.NAZWA 
                 FROM REZERWACJA r INNER JOIN LOT l ON r.LOT_ID = l.LOT_ID 
                                   INNER JOIN PAS p ON r.PAS_ID = p.PAS_ID
                 WHERE l.lot_id = :flight_id"""
        cr.execute(sql, flight_id=flight_id)
        headers = [header[0] for header in cr.description]
        reservations_list = []
        for data in cr:
            reservations_list.append(
                Rezerwacja(
                    _id=data[0],
                    poczatek=data[1],
                    koniec=data[2],
                    pas=Pas(nazwa=data[3])
                )
            )
        cr.close()

        return headers, reservations_list

    def insert_reservation(self, poczatek, koniec, lot_id, pas_id) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""INSERT INTO REZERWACJA (POCZATEK, KONIEC, LOT_ID, PAS_ID)
                           VALUES (:poczatek,
                                   :koniec,
                                   :lot_id,
                                   :pas_id)""",
                   poczatek=poczatek,
                   koniec=koniec,
                   lot_id=lot_id,
                   pas_id=pas_id)
        connection.commit()
        cr.close()
        return "Pomyślnie dodano nową rezerwację", c.SUCCESS, None

    def delete_reservation(self, reservation_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("DELETE FROM REZERWACJA WHERE REZERWACJA_ID = :id",
                   id=reservation_id)
        connection.commit()
        cr.close()
        return "Pomyślnie usunięto wybraną rezerwację", c.SUCCESS

    def select_classes(self, order=False) -> Tuple[List[str], List[LiniaLotnicza]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        if not order:
            sql = "SELECT KLASA_ID, NAZWA, OBSLUGA, KOMFORT, CENA FROM KLASA"
        else:
            sql = "SELECT KLASA_ID, NAZWA, OBSLUGA, KOMFORT, CENA FROM KLASA ORDER BY NAZWA"
        cr.execute(sql)
        headers = [header[0] for header in cr.description]
        classes_list = []
        for class_ in cr:
            classes_list.append(
                Klasa(
                    _id=class_[0],
                    nazwa=class_[1],
                    obsluga=class_[2],
                    komfort=class_[3],
                    cena=class_[4]
                )
            )
        cr.close()

        return headers, classes_list

    def insert_class(self, nazwa, obsluga, komfort, cena) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO KLASA (NAZWA, OBSLUGA, KOMFORT, CENA)
                               VALUES (:nazwa,
                                       :obsluga,
                                       :komfort,
                                       :cena)""",
                       nazwa=nazwa,
                       obsluga=obsluga,
                       komfort=komfort,
                       cena=cena)
        except cx_Oracle.IntegrityError as e:
            if c.KLASA_UN_NAZWA in str(e):
                cr.close()
                return "Klasa o takiej nazwie już istnieje", c.ERROR, c.KLASA_UN_NAZWA
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nową klasę", c.SUCCESS, None

    def select_class(self, class_id: int) -> Klasa:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT NAZWA, OBSLUGA, KOMFORT, CENA
                            FROM KLASA
                           WHERE KLASA_ID = :id""",
                   id=class_id)
        data = cr.fetchone()
        return Klasa(class_id, nazwa=data[0], obsluga=data[1], komfort=data[2], cena=data[3])

    def update_class(self, class_id, nazwa, obsluga, komfort, cena) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE KLASA
                             SET NAZWA = :nazwa,
                                 OBSLUGA = :obsluga,
                                 KOMFORT = :komfort,
                                 CENA = :cena
                           WHERE KLASA_ID = :id""",
                       nazwa=nazwa,
                       obsluga=obsluga,
                       komfort=komfort,
                       cena=cena,
                       id=class_id)
        except cx_Oracle.IntegrityError as e:
            if c.KLASA_UN_NAZWA in str(e):
                cr.close()
                return "Klasa o takiej nazwie już istnieje", c.ERROR, c.KLASA_UN_NAZWA
            cr.close()
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślna aktualizacja klasy", c.SUCCESS, None

    def delete_class(self, class_id: int) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM KLASA WHERE KLASA_ID = :id", id=class_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć klasy, ponieważ jest przypisana do biletów", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto klasę biletów", c.SUCCESS
