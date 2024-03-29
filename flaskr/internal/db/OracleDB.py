import datetime

import cx_Oracle
import os

from typing import List, Tuple

from flaskr.internal.helpers import constants as c
from flaskr.internal.helpers.models import LiniaLotnicza, Lotnisko, Producent, Model, Pas, Przylot, Rezerwacja, Lot, \
    Klasa, Pasazer, Odlot, PulaBiletow, Bilet


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

    def select_arrivals_for_map(self):
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT DISTINCT l2.LATITUDE , l2.LONGITUDE, l2.NAZWA
                      FROM LOT l INNER JOIN LOTNISKO l2 ON l.LOTNISKO_ID = l2.LOTNISKO_ID
                                 INNER JOIN PRZYLOT p ON l.LOT_ID = p.LOT_ID """)
        flights_list = []
        for flight in cr:
            flights_list.append(
                Lot(lotnisko=Lotnisko(latitude=flight[0], longitude=flight[1], nazwa=flight[2]))
            )
        cr.close()
        return flights_list

    def select_departures_for_map(self):
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT DISTINCT l2.LATITUDE , l2.LONGITUDE, l2.NAZWA
                      FROM LOT l INNER JOIN LOTNISKO l2 ON l.LOTNISKO_ID = l2.LOTNISKO_ID
                                 INNER JOIN ODLOT p ON l.LOT_ID = p.LOT_ID """)
        flights_list = []
        for flight in cr:
            flights_list.append(
                Lot(lotnisko=Lotnisko(latitude=flight[0], longitude=flight[1], nazwa=flight[2]))
            )
        cr.close()
        return flights_list

    def select_arrivals(self) -> Tuple[List[str], List[Przylot]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS PRZYLOT_ID,
                             p.DATAPRZYLOTU AS TERMIN,
	                         p.LICZBAPASAZEROW AS LICZBA_PASAZEROW,
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

    def update_arrival(self, lot_id, linia_lotnicza_id, lotnisko_id, model_id, liczba_pasazerow) \
            -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        lot_sql = """UPDATE LOT
                        SET LINIALOTNICZA_ID = :1,
                            LOTNISKO_ID = :2,
                            MODEL_ID = :3
                      WHERE LOT_ID = :4"""
        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        przylot_sql = """UPDATE PRZYLOT
                            SET LICZBAPASAZEROW = :1
                          WHERE LOT_ID = :2"""
        cr.execute(przylot_sql, (liczba_pasazerow, lot_id))

        connection.commit()
        cr.close()
        return "Pomyślnie zaktualizowano przylot", c.SUCCESS, None

    def update_arrival_and_reservations(self, lot_id, linia_lotnicza_id, lotnisko_id, model_id,
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
        sql = """SELECT r.rezerwacja_id, r.poczatek, r.koniec, p.NAZWA AS PAS
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

    def select_flight_date(self, flight_id) -> datetime.datetime:
        connection = self.pool.acquire()
        cr = connection.cursor()
        sql = """SELECT 
                 CASE 
                    WHEN :lot_id IN (SELECT LOT_ID FROM PRZYLOT) THEN (SELECT p.DATAPRZYLOTU FROM PRZYLOT p WHERE p.LOT_ID = :lot_id)
                    ELSE (SELECT o.DATAODLOTU FROM ODLOT o WHERE o.LOT_ID = :lot_id)
                 END AS DATA_LOTU
                 FROM DUAL"""
        cr.execute(sql, lot_id=flight_id)
        data = cr.fetchone()
        return data[0]

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

    def update_reservation(self, reservation_id, flight_id, start_date, end_date) -> Tuple[str, str]:

        is_covering = True

        connection = self.pool.acquire()
        cr = connection.cursor()

        cr.execute("""SELECT count(*) 
                        FROM (SELECT REZERWACJA_ID
                                FROM REZERWACJA r
                               WHERE r.REZERWACJA_ID != :rezerwacja_id AND (
                        SELECT 
                        CASE 
                            WHEN :lot_id IN (SELECT LOT_ID FROM PRZYLOT) THEN (SELECT p.DATAPRZYLOTU FROM PRZYLOT p WHERE p.LOT_ID = :lot_id)
                            ELSE (SELECT o.DATAODLOTU FROM ODLOT o WHERE o.LOT_ID = :lot_id)
                        END AS DATA_LOTU
                        FROM DUAL
                        ) BETWEEN r.POCZATEK AND r.KONIEC AND r.LOT_ID = :lot_id) 
                    """,
                   lot_id=flight_id,
                   rezerwacja_id=reservation_id)
        data = cr.fetchone()[0]
        if data == 0:
            # check if the new start_date / end_date will cover the departure / arrival time
            flight_datetime = self.select_flight_date(flight_id)
            if not start_date <= flight_datetime <= end_date:
                is_covering = False

        if not is_covering:
            return "Błąd - po zmianach nie będzie rezerwacji w trakcie terminu lotu", c.WARNING
        else:
            # check if the runway is free in this time
            cr.execute("""SELECT COUNT(*)
                            FROM REZERWACJA r2 
                           WHERE r2.PAS_ID = (SELECT p.PAS_ID 
                                                FROM PAS p INNER JOIN REZERWACJA r ON p.PAS_ID = r.PAS_ID 
                                               WHERE r.REZERWACJA_ID = :rezerwacja_id)
                             AND r2.POCZATEK < :ed AND r2.KONIEC > :sd AND r2.REZERWACJA_ID != :rezerwacja_id""",
                       rezerwacja_id=reservation_id, sd=start_date, ed=end_date)
            data = cr.fetchone()[0]
            if data > 0:
                return "Pas jest już zajęty w tym terminie", c.WARNING

            # it is possible to change the start_date and end_date
            cr.execute("""  UPDATE REZERWACJA 
                               SET POCZATEK = :sd,
                                     KONIEC = :ed
                               WHERE REZERWACJA_ID = :r""",
                       r=reservation_id, sd=start_date, ed=end_date)
            connection.commit()
            cr.close()
            return "Pomyślna aktualizacja rezerwacji", c.SUCCESS

    def delete_reservation(self, reservation_id, flight_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        # sql searches how many reservations are there that will cover the departure / arrival time.
        # if there is at least one another reservation (other than we want to delete)
        # then it is safe to delete current reservation
        cr.execute("""SELECT count(*) 
                        FROM (SELECT REZERWACJA_ID
                                FROM REZERWACJA r
                               WHERE r.REZERWACJA_ID != :rezerwacja_id AND (
                        SELECT 
                        CASE 
                            WHEN :lot_id IN (SELECT LOT_ID FROM PRZYLOT) THEN (SELECT p.DATAPRZYLOTU FROM PRZYLOT p WHERE p.LOT_ID = :lot_id)
                            ELSE (SELECT o.DATAODLOTU FROM ODLOT o WHERE o.LOT_ID = :lot_id)
                        END AS DATA_LOTU
                        FROM DUAL
                        ) BETWEEN r.POCZATEK AND r.KONIEC AND r.LOT_ID = :lot_id) 
                    """,
                   lot_id=flight_id,
                   rezerwacja_id=reservation_id)
        data = cr.fetchone()[0]
        if data > 0:
            cr.execute("DELETE FROM REZERWACJA WHERE REZERWACJA_ID = :id",
                       id=reservation_id)
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto wybraną rezerwację", c.SUCCESS
        else:
            cr.close()
            return "Nie można usunąć rezerwacji, ponieważ jest jedyną w trakcie momentu przylotu", c.WARNING

    def select_classes(self, order=False) -> Tuple[List[str], List[Klasa]]:
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

    def select_passengers(self) -> Tuple[List[str], List[Pasazer]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        sql = "SELECT PASAZER_ID, LOGIN, IMIE, NAZWISKO, PESEL, DATAURODZENIA AS DATA_URODZENIA FROM PASAZER"
        cr.execute(sql)
        headers = [header[0] for header in cr.description]
        passengers_list = []
        for passenger in cr:
            passengers_list.append(
                Pasazer(
                    _id=passenger[0],
                    login=passenger[1],
                    imie=passenger[2],
                    nazwisko=passenger[3],
                    pesel=passenger[4],
                    data_urodzenia=passenger[5]
                )
            )
        cr.close()

        return headers, passengers_list

    def select_passenger(self, passenger_id) -> Pasazer:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT PASAZER_ID, LOGIN, HASLO, IMIE, NAZWISKO, PESEL, DATAURODZENIA
                            FROM PASAZER
                           WHERE PASAZER_ID = :id""",
                   id=passenger_id)
        data = cr.fetchone()
        return Pasazer(passenger_id, login=data[1], haslo=data[2],
                       imie=data[3], nazwisko=data[4],
                       pesel=data[5], data_urodzenia=data[6])

    def insert_passenger(self, login, haslo, imie, nazwisko, pesel, data_urodzenia) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""INSERT INTO PASAZER (LOGIN, HASLO, IMIE, NAZWISKO, PESEL, DATAURODZENIA)
                               VALUES (:login,
                                       :haslo,
                                       :imie,
                                       :nazwisko,
                                       :pesel,
                                       :dataurodzenia)""",
                       login=login,
                       haslo=haslo,
                       imie=imie,
                       nazwisko=nazwisko,
                       pesel=pesel,
                       dataurodzenia=data_urodzenia)
        except cx_Oracle.IntegrityError as e:
            if c.PASAZER_UN_LOGIN in str(e):
                cr.close()
                return "Pasażer o takim loginie już istnieje", c.ERROR, c.PASAZER_UN_LOGIN
            if c.PASAZER_UN_PESEL in str(e):
                cr.close()
                return "Pasażer o takim peselu już istnieje", c.ERROR, c.PASAZER_UN_PESEL
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie dodano nowego pasażera", c.SUCCESS, None

    def update_passenger(self, passenger_id, login, haslo, imie, nazwisko, pesel, data_urodzenia) \
            -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE PASAZER
                             SET LOGIN = :login,
                                 HASLO = :haslo,
                                 IMIE = :imie,
                                 NAZWISKO = :nazwisko,
                                 PESEL = :pesel,
                                 DATAURODZENIA = :dataurodzenia
                           WHERE PASAZER_ID = :id""",
                       login=login,
                       haslo=haslo,
                       imie=imie,
                       nazwisko=nazwisko,
                       pesel=pesel,
                       dataurodzenia=data_urodzenia,
                       id=passenger_id)
        except cx_Oracle.IntegrityError as e:
            if c.PASAZER_UN_LOGIN in str(e):
                cr.close()
                return "Pasażer o takim loginie już istnieje", c.ERROR, c.PASAZER_UN_LOGIN
            if c.PASAZER_UN_PESEL in str(e):
                cr.close()
                return "Pasażer o takim peselu już istnieje", c.ERROR, c.PASAZER_UN_PESEL
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie zaktualizowano pasażera", c.SUCCESS, None

    def delete_passenger(self, passenger_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("DELETE FROM PASAZER WHERE PASAZER_ID = :id", id=passenger_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć pasażera, ponieważ posiada bilety", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto pasażera", c.SUCCESS

    def select_departures(self) -> Tuple[List[str], List[Odlot]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ODLOT_ID,
                             p.DATAODLOTU AS TERMIN,
                             p.LICZBAMIEJSC AS LICZBA_MIEJSC,
                             ll.NAZWA AS LINIA_LOTNICZA,
                             lt.NAZWA AS LOTNISKO,
                             p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM ODLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                   INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                   INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                   INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                   INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID""")
        headers, departures_list = self.__select_departures_query_to_list(cr)
        cr.close()

        return headers, departures_list

    def select_departure(self, lot_id) -> Odlot:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ID,
                             p.DATAODLOTU AS TERMIN,
                             p.LICZBAMIEJSC,
                             ll.LINIALOTNICZA_ID,
                             ll.NAZWA AS LINIA_LOTNICZA,
                             lt.LOTNISKO_ID,
                             lt.NAZWA AS LOTNISKO,
                             m.MODEL_ID,
                             p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM ODLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                   INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                   INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                   INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                   INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID
                      WHERE p.LOT_ID = :lot_id""",
                   lot_id=lot_id)
        data = cr.fetchone()
        departure = Odlot(_id=data[0], data_odlotu=data[1], liczba_miejsc=data[2],
                          linia_lotnicza=LiniaLotnicza(_id=data[3], nazwa=data[4]),
                          lotnisko=LiniaLotnicza(_id=data[5], nazwa=data[6]),
                          model=Model(_id=data[7], nazwa=data[8]))
        cr.close()
        return departure

    def select_departures_by_dates(self, date_start, date_end) -> Tuple[List[str], List[Odlot]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.LOT_ID AS ID,
                             p.DATAODLOTU AS TERMIN,
        	                 p.LICZBAMIEJSC AS LICZBA_MIEJSC,
        	                 ll.NAZWA AS LINIA_LOTNICZA,
        	                 lt.NAZWA AS LOTNISKO,
        	                 p2.NAZWA || ' ' || m.NAZWA AS MODEL_SAMOLOTU 
                      FROM ODLOT p INNER JOIN LOT l ON p.LOT_ID = l.LOT_ID 
                                   INNER JOIN LINIALOTNICZA ll  ON l.LINIALOTNICZA_ID = ll.LINIALOTNICZA_ID
                                   INNER JOIN LOTNISKO lt ON l.LOTNISKO_ID = lt.LOTNISKO_ID
                                   INNER JOIN MODEL m ON l.MODEL_ID = m.MODEL_ID 
                                   INNER JOIN PRODUCENT p2 ON m.PRODUCENT_ID = p2.PRODUCENT_ID
                      WHERE p.DATAODLOTU >= :date_start AND p.DATAODLOTU <= :date_end""",
                   date_start=date_start,
                   date_end=date_end)
        headers, departures_list = self.__select_departures_query_to_list(cr)
        cr.close()

        return headers, departures_list

    def __select_departures_query_to_list(self, cr: cx_Oracle.Cursor):
        headers = [header[0] for header in cr.description]
        departures_list = []
        for departure in cr:
            departures_list.append(
                Odlot(
                    _id=departure[0],
                    data_odlotu=departure[1],
                    liczba_miejsc=departure[2],
                    linia_lotnicza=LiniaLotnicza(nazwa=departure[3]),
                    lotnisko=Lotnisko(nazwa=departure[4]),
                    model=Model(nazwa=departure[5])
                )
            )
        return headers, departures_list

    def insert_departure_and_ticket_pools(self, linia_lotnicza_id, lotnisko_id, model_id,
                                          data_odlotu, liczba_miejsc, pas_id, pule_biletow) -> Tuple[str, str, str]:

        connection = self.pool.acquire()
        cr = connection.cursor()

        lot_id = cr.var(cx_Oracle.NUMBER)

        lot_sql = """INSERT INTO LOT(LINIALOTNICZA_ID, LOTNISKO_ID, MODEL_ID, TYP)
                          VALUES (:1, :2, :3, 'odlot')
                       RETURNING LOT_ID INTO :4"""

        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        przylot_sql = """INSERT INTO ODLOT(DATAODLOTU, LICZBAMIEJSC)
                              VALUES (:1, :2)"""

        cr.execute(przylot_sql, (data_odlotu, liczba_miejsc))

        rezerwacja_sql = """INSERT INTO REZERWACJA(POCZATEK, KONIEC, LOT_ID, PAS_ID)
                                 VALUES (:1, :2, :3, :4)"""

        cr.execute(rezerwacja_sql, (data_odlotu,
                                    data_odlotu + datetime.timedelta(minutes=c.MINUTES_FOR_FLIGHT),
                                    lot_id.getvalue()[0],
                                    pas_id))

        # {(2, 'Biznes'): 5, (1, 'Ekonomiczna'): 43, (5, 'Premium'): 1} -> pula_biletow
        for pula_key, liczba_biletow in pule_biletow.items():
            if liczba_biletow > 0:
                pula_sql = """INSERT INTO PULABILETOW(ILEWSZYSTKICHMIEJSC, ILEDOSTEPNYCHMIEJSC, LOT_ID, KLASA_ID)
                                   VALUES (:1, :2, :3, :4)"""

                cr.execute(pula_sql, (liczba_biletow, liczba_biletow, lot_id.getvalue()[0], pula_key[0]))

        connection.commit()
        cr.close()

        return "Pomyślnie dodano nowy odlot", c.SUCCESS, None

    def update_departure(self, lot_id, linia_lotnicza_id, lotnisko_id, model_id, liczba_miejsc, pule_biletow) \
            -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        # UPDATE DATA CONNECTED WITH DEPARTURE

        lot_sql = """UPDATE LOT
                        SET LINIALOTNICZA_ID = :1,
                            LOTNISKO_ID = :2,
                            MODEL_ID = :3
                      WHERE LOT_ID = :4"""
        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        odlot_sql = """UPDATE ODLOT
                          SET LICZBAMIEJSC = :1
                        WHERE LOT_ID = :2"""
        cr.execute(odlot_sql, (liczba_miejsc, lot_id))

        # UPDATE DATA CONNECTED WITH TICKET POOLS
        # {(klasa_id, klasa_nazwa) : liczba_biletow, ...}
        for pula_key, liczba_biletow in pule_biletow.items():
            # check if we should insert / update / delete pool
            cr.execute("""SELECT count(*) FROM PULABILETOW p WHERE p.LOT_ID = :lot_id AND p.KLASA_ID = :klasa_id""",
                       lot_id=lot_id,
                       klasa_id=pula_key[0])
            count = cr.fetchone()[0]
            number_of_tickets = self.count_tickets_for_pool(flight_id=lot_id, class_id=pula_key[0])
            if count > 0 and liczba_biletow > 0:
                # update pool
                update_sql = """UPDATE PULABILETOW
                                   SET ILEWSZYSTKICHMIEJSC = :liczba_biletow,
                                       ILEDOSTEPNYCHMIEJSC = :dostepnych_biletow
                                 WHERE LOT_ID = :lot_id AND KLASA_ID = :klasa_id"""
                cr.execute(update_sql,
                           liczba_biletow=liczba_biletow,
                           dostepnych_biletow=liczba_biletow - number_of_tickets,
                           lot_id=lot_id,
                           klasa_id=pula_key[0])

            if count == 0 and liczba_biletow > 0:
                # insert pool
                insert_sql = """INSERT INTO PULABILETOW(ILEWSZYSTKICHMIEJSC, ILEDOSTEPNYCHMIEJSC, LOT_ID, KLASA_ID)
                                     VALUES (:1, :2, :3, :4)"""
                cr.execute(insert_sql, (liczba_biletow, liczba_biletow, lot_id, pula_key[0]))

            if count > 0 and liczba_biletow == 0:
                # delete pool
                delete_sql = """DELETE FROM PULABILETOW WHERE LOT_ID = :lot_id AND KLASA_ID = :klasa_id"""
                cr.execute(delete_sql, lot_id=lot_id, klasa_id=pula_key[0])

        connection.commit()
        cr.close()
        return "Pomyślnie zaktualizowano przylot", c.SUCCESS, None

    def update_departure_and_reservations(self, lot_id, linia_lotnicza_id, lotnisko_id, model_id,
                                          data_odlotu, liczba_miejsc, pas_id, pule_biletow) -> Tuple[str, str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        # UPDATE DATA CONNECTED WITH DEPARTURE

        lot_sql = """UPDATE LOT
                        SET LINIALOTNICZA_ID = :1,
                            LOTNISKO_ID = :2,
                            MODEL_ID = :3
                      WHERE LOT_ID = :4"""
        cr.execute(lot_sql, (linia_lotnicza_id, lotnisko_id, model_id, lot_id))

        odlot_sql = """UPDATE ODLOT
                          SET DATAODLOTU = :1,
                              LICZBAMIEJSC = :2
                        WHERE LOT_ID = :3"""
        cr.execute(odlot_sql, (data_odlotu, liczba_miejsc, lot_id))

        rezerwacje_sql = """DELETE FROM REZERWACJA WHERE LOT_ID = :lot_id"""
        cr.execute(rezerwacje_sql, lot_id=lot_id)

        rezerwacja_sql = """INSERT INTO REZERWACJA(POCZATEK, KONIEC, LOT_ID, PAS_ID)
                                 VALUES (:1, :2, :3, :4)"""
        cr.execute(rezerwacja_sql, (data_odlotu,
                                    data_odlotu + datetime.timedelta(minutes=c.MINUTES_FOR_FLIGHT),
                                    lot_id,
                                    pas_id))

        # UPDATE DATA CONNECTED WITH TICKET POOLS
        # {(klasa_id, klasa_nazwa) : liczba_biletow, ...}
        for pula_key, liczba_biletow in pule_biletow.items():
            # check if we should insert / update / delete pool
            cr.execute("""SELECT count(*) FROM PULABILETOW p WHERE p.LOT_ID = :lot_id AND p.KLASA_ID = :klasa_id""",
                       lot_id=lot_id,
                       klasa_id=pula_key[0])
            count = cr.fetchone()[0]
            number_of_tickets = self.count_tickets_for_pool(flight_id=lot_id, class_id=pula_key[0])
            if count > 0 and liczba_biletow > 0:
                # update pool
                update_sql = """UPDATE PULABILETOW
                                   SET ILEWSZYSTKICHMIEJSC = :liczba_biletow,
                                       ILEDOSTEPNYCHMIEJSC = :dostepnych_biletow
                                 WHERE LOT_ID = :lot_id AND KLASA_ID = :klasa_id"""
                cr.execute(update_sql,
                           liczba_biletow=liczba_biletow,
                           dostepnych_biletow=liczba_biletow - number_of_tickets,
                           lot_id=lot_id,
                           klasa_id=pula_key[0])

            if count == 0 and liczba_biletow > 0:
                # insert pool
                insert_sql = """INSERT INTO PULABILETOW(ILEWSZYSTKICHMIEJSC, ILEDOSTEPNYCHMIEJSC, LOT_ID, KLASA_ID)
                                     VALUES (:1, :2, :3, :4)"""
                cr.execute(insert_sql, (liczba_biletow, liczba_biletow, lot_id, pula_key[0]))

            if count > 0 and liczba_biletow == 0:
                # delete pool
                delete_sql = """DELETE FROM PULABILETOW WHERE LOT_ID = :lot_id AND KLASA_ID = :klasa_id"""
                cr.execute(delete_sql, lot_id=lot_id, klasa_id=pula_key[0])

        connection.commit()
        cr.close()
        return "Pomyślnie zaktualizowano przylot", c.SUCCESS, None

    def delete_departure(self, lot_id) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        try:
            # delete from PULABILETOW
            cr.execute("DELETE FROM PULABILETOW WHERE LOT_ID = :lot_id", lot_id=lot_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd - nie można usunąć lotu, ponieważ istnieją bilety z nim powiązane", c.ERROR

        # delete from ODLOT
        cr.execute("DELETE FROM ODLOT WHERE LOT_ID = :lot_id", lot_id=lot_id)

        # delete from REZERWACJA
        cr.execute("DELETE FROM REZERWACJA WHERE LOT_ID = :lot_id", lot_id=lot_id)

        # delete from LOT
        cr.execute("DELETE FROM LOT WHERE LOT_ID = :lot_id", lot_id=lot_id)

        connection.commit()
        cr.close()

        return "Pomyślnie usunięto odlot", c.SUCCESS

    def select_pools(self) -> Tuple[List[str], List[PulaBiletow]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.PULABILETOW_ID,
                             p.ILEWSZYSTKICHMIEJSC AS LICZBA_WSZYSTKICH_MIEJSC,
                             p.ILEDOSTEPNYCHMIEJSC AS LICZBA_DOSTEPNYCH_MIEJSC,
                             o.LOT_ID,
                             k.KLASA_ID,
                             k.NAZWA AS KLASA
                       FROM PULABILETOW p INNER JOIN ODLOT o ON p.LOT_ID = o.LOT_ID 
                                          INNER JOIN KLASA k ON p.KLASA_ID = k.KLASA_ID""")
        headers = [header[0] for header in cr.description]
        pools_list = []
        for pool in cr:
            pools_list.append(
                PulaBiletow(
                    _id=pool[0],
                    ile_wszystkich_miejsc=pool[1],
                    ile_dostepnych_miejsc=pool[2],
                    odlot=Odlot(_id=pool[3]),
                    klasa=Klasa(_id=pool[4], nazwa=pool[5])
                )
            )
        return headers, pools_list

    def select_pool(self, pool_id: int) -> PulaBiletow:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.PULABILETOW_ID,
                             p.ILEWSZYSTKICHMIEJSC AS LICZBA_WSZYSTKICH_MIEJSC,
                             p.ILEDOSTEPNYCHMIEJSC AS LICZBA_DOSTEPNYCH_MIEJSC,
                             o.LOT_ID,
                             k.KLASA_ID,
                             k.NAZWA AS KLASA
                       FROM PULABILETOW p INNER JOIN ODLOT o ON p.LOT_ID = o.LOT_ID 
                                          INNER JOIN KLASA k ON p.KLASA_ID = k.KLASA_ID
                       WHERE p.PULABILETOW_ID = :id""",
                   id=pool_id)
        pool = cr.fetchone()
        return PulaBiletow(
            _id=pool[0],
            ile_wszystkich_miejsc=pool[1],
            ile_dostepnych_miejsc=pool[2],
            odlot=Odlot(_id=pool[3]),
            klasa=Klasa(_id=pool[4], nazwa=pool[5])
        )

    def select_pools_with_seats(self) -> Tuple[List[str], List[PulaBiletow]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT p.PULABILETOW_ID,
                             p.ILEDOSTEPNYCHMIEJSC AS DOSTEPNE_MIEJSCA,
                             k.NAZWA AS KLASA,
                             k.CENA AS CENA,
                             o.DATAODLOTU AS TERMIN,
                             l2.MIASTO AS DESTYNACJA,
                             l2.KRAJ AS KRAJ
                        FROM PULABILETOW p INNER JOIN KLASA k ON k.KLASA_ID = p.KLASA_ID 
                                           INNER JOIN ODLOT o ON o.LOT_ID = p.LOT_ID 
                                           INNER JOIN LOT l ON l.LOT_ID = o.LOT_ID 
                                           INNER JOIN LOTNISKO l2 ON l2.LOTNISKO_ID = l.LOTNISKO_ID
                       WHERE p.ILEDOSTEPNYCHMIEJSC > 0""")
        headers = [header[0] for header in cr.description]
        pools_list = []
        for pool in cr:
            pools_list.append(
                PulaBiletow(
                    _id=pool[0],
                    ile_dostepnych_miejsc=pool[1],
                    klasa=Klasa(nazwa=pool[2], cena=pool[3]),
                    odlot=Odlot(data_odlotu=pool[4], lotnisko=Lotnisko(miasto=pool[5], kraj=pool[6])),
                )
            )
        return headers, pools_list

    def select_pools_by_departure(self, departure_id: int) -> Tuple[List[str], List[PulaBiletow]]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        cr.execute("""SELECT p.PULABILETOW_ID,
                             p.ILEWSZYSTKICHMIEJSC AS LICZBA_WSZYSTKICH_MIEJSC,
                             p.ILEDOSTEPNYCHMIEJSC AS LICZBA_DOSTEPNYCH_MIEJSC,
                             o.LOT_ID,
                             k.KLASA_ID,
                             k.NAZWA AS KLASA
                       FROM PULABILETOW p INNER JOIN ODLOT o ON p.LOT_ID = o.LOT_ID 
                                          INNER JOIN KLASA k ON p.KLASA_ID = k.KLASA_ID 
                      WHERE o.LOT_ID = :odlot_id""",
                   odlot_id=departure_id)
        headers = [header[0] for header in cr.description]
        pools_list = []
        for pool in cr:
            pools_list.append(
                PulaBiletow(
                    _id=pool[0],
                    ile_wszystkich_miejsc=pool[1],
                    ile_dostepnych_miejsc=pool[2],
                    odlot=Odlot(_id=pool[3]),
                    klasa=Klasa(_id=pool[4], nazwa=pool[5])
                )
            )
        return headers, pools_list

    def count_tickets_for_pool(self, pool_id: int = -1, flight_id: int = -1, class_id: int = -1) -> int:
        """Give pool_id or (flight_id and class_id)"""
        connection = self.pool.acquire()
        cr = connection.cursor()

        if pool_id != -1:
            cr.execute("""SELECT COUNT(*)
                            FROM BILET b 
                           WHERE b.PULABILETOW_ID = :pula_id""",
                       pula_id=pool_id)
            return cr.fetchone()[0]
        if flight_id != -1 and class_id != -1:
            cr.execute("""SELECT count(*)
                            FROM BILET b INNER JOIN PULABILETOW p ON b.PULABILETOW_ID = p.PULABILETOW_ID 
                           WHERE p.LOT_ID = :lot_id AND p.KLASA_ID = :klasa_id""",
                       lot_id=flight_id,
                       klasa_id=class_id)
            return cr.fetchone()[0]
        return None

    def select_tickets(self) -> Tuple[List[str], List[Bilet]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT b.BILET_ID,
                             b.CZYOPLACONY AS CZY_OPLACONY,
                             b.MIEJSCE AS MIEJSCE,
                             b.CENA,
                             p.IMIE,
                             p.NAZWISKO,
                             p.LOGIN,
                             k.NAZWA AS KLASA,
                             o.DATAODLOTU AS DATA_ODLOTU,
                             l2.NAZWA AS LOTNISKO,
                             l3.NAZWA AS LINIA_LOTNICZA 
                     FROM BILET b INNER JOIN PASAZER p ON b.PASAZER_ID = p.PASAZER_ID 
                                  INNER JOIN PULABILETOW p2 ON b.PULABILETOW_ID = p2.PULABILETOW_ID 
                                  INNER JOIN KLASA k ON k.KLASA_ID = p2.KLASA_ID 
                                  INNER JOIN ODLOT o ON o.LOT_ID = p2.LOT_ID 
                                  INNER JOIN LOT l ON l.LOT_ID = o.LOT_ID 
                                  INNER JOIN LOTNISKO l2 ON l2.LOTNISKO_ID = l.LOTNISKO_ID 
                                  INNER JOIN LINIALOTNICZA l3 ON l3.LINIALOTNICZA_ID = l.LINIALOTNICZA_ID""")
        headers = [header[0] for header in cr.description]
        tickets_list = []
        for ticket in cr:
            tickets_list.append(
                Bilet(
                    _id=ticket[0],
                    czy_oplacony=ticket[1],
                    miejsce=ticket[2],
                    cena=ticket[3],
                    pasazer=Pasazer(imie=ticket[4], nazwisko=ticket[5], login=ticket[6]),
                    pula_biletow=PulaBiletow(klasa=Klasa(nazwa=ticket[7]),
                                             odlot=Odlot(data_odlotu=ticket[8],
                                                         lotnisko=Lotnisko(nazwa=ticket[9]),
                                                         linia_lotnicza=LiniaLotnicza(nazwa=ticket[10])))
                )
            )
        return headers, tickets_list

    def select_ticket(self, ticket_id: int) -> Bilet:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT b.BILET_ID,
                             b.CZYOPLACONY AS CZY_OPLACONY,
                             b.MIEJSCE AS MIEJSCE,
                             b.CENA,
                             p.IMIE,
                             p.NAZWISKO,
                             p.LOGIN,
                             k.NAZWA AS KLASA,
                             o.DATAODLOTU AS DATA_ODLOTU,
                             l2.NAZWA AS LOTNISKO,
                             l3.NAZWA AS LINIA_LOTNICZA 
                     FROM BILET b INNER JOIN PASAZER p ON b.PASAZER_ID = p.PASAZER_ID 
                                  INNER JOIN PULABILETOW p2 ON b.PULABILETOW_ID = p2.PULABILETOW_ID 
                                  INNER JOIN KLASA k ON k.KLASA_ID = p2.KLASA_ID 
                                  INNER JOIN ODLOT o ON o.LOT_ID = p2.LOT_ID 
                                  INNER JOIN LOT l ON l.LOT_ID = o.LOT_ID 
                                  INNER JOIN LOTNISKO l2 ON l2.LOTNISKO_ID = l.LOTNISKO_ID 
                                  INNER JOIN LINIALOTNICZA l3 ON l3.LINIALOTNICZA_ID = l.LINIALOTNICZA_ID
                     WHERE b.BILET_ID = :id""",
                   id=ticket_id)
        ticket = cr.fetchone()
        return Bilet(
            _id=ticket[0],
            czy_oplacony=ticket[1],
            miejsce=ticket[2],
            cena=ticket[3],
            pasazer=Pasazer(imie=ticket[4], nazwisko=ticket[5], login=ticket[6]),
            pula_biletow=PulaBiletow(klasa=Klasa(nazwa=ticket[7]),
                                     odlot=Odlot(data_odlotu=ticket[8],
                                                 lotnisko=Lotnisko(nazwa=ticket[9]),
                                                 linia_lotnicza=LiniaLotnicza(nazwa=ticket[10])))
        )

    def select_tickets_by_passenger(self, passenger_id: int) -> Tuple[List[str], List[Bilet]]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("""SELECT b.BILET_ID,
                             p2.PULABILETOW_ID,
                             b.CZYOPLACONY AS CZY_OPLACONY,
                             b.MIEJSCE AS MIEJSCE,
                             b.CENA,
                             k.NAZWA AS KLASA,
                             o.DATAODLOTU AS DATA_ODLOTU,
                             l2.NAZWA AS LOTNISKO,
                             l3.NAZWA AS LINIA_LOTNICZA 
                     FROM BILET b INNER JOIN PULABILETOW p2 ON b.PULABILETOW_ID = p2.PULABILETOW_ID 
                                  INNER JOIN KLASA k ON k.KLASA_ID = p2.KLASA_ID 
                                  INNER JOIN ODLOT o ON o.LOT_ID = p2.LOT_ID 
                                  INNER JOIN LOT l ON l.LOT_ID = o.LOT_ID 
                                  INNER JOIN LOTNISKO l2 ON l2.LOTNISKO_ID = l.LOTNISKO_ID 
                                  INNER JOIN LINIALOTNICZA l3 ON l3.LINIALOTNICZA_ID = l.LINIALOTNICZA_ID
                      WHERE b.PASAZER_ID = :passenger_id""",
                   passenger_id=passenger_id)
        headers = [header[0] for header in cr.description]
        tickets_list = []
        for ticket in cr:
            tickets_list.append(
                Bilet(
                    _id=ticket[0],
                    czy_oplacony=ticket[2],
                    miejsce=ticket[3],
                    cena=ticket[4],
                    pula_biletow=PulaBiletow(_id=ticket[1],
                                             klasa=Klasa(nazwa=ticket[5]),
                                             odlot=Odlot(data_odlotu=ticket[6],
                                                         lotnisko=Lotnisko(nazwa=ticket[7]),
                                                         linia_lotnicza=LiniaLotnicza(nazwa=ticket[8])))
                )
            )
        return headers, tickets_list

    def insert_ticket(self, passenger_id: int, pool_id: int) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        pool = self.select_pool(pool_id)
        if pool.ile_dostepnych_miejsc <= 0:
            cr.close()
            return "Błąd - brak dostępnych biletów w tej puli biletów", c.ERROR

        # INSERT INTO TICKETS

        insert_sql = """INSERT INTO BILET (CZYOPLACONY, MIEJSCE, CENA, PASAZER_ID, PULABILETOW_ID)
                        VALUES(0,
                               (SELECT k.NAZWA
                                  FROM KLASA k INNER JOIN PULABILETOW p ON k.KLASA_ID = p.KLASA_ID
                                 WHERE p.PULABILETOW_ID = :pula_biletow) || ' ' || (SELECT count(*)+1
                                                                                      FROM BILET b
                                                                                     WHERE b.PULABILETOW_ID = :pula_biletow),
                               (SELECT k2.CENA
                                  FROM KLASA k2 INNER JOIN PULABILETOW p2 ON k2.KLASA_ID = p2.KLASA_ID
                                 WHERE p2.PULABILETOW_ID = :pula_biletow),
                               :pasazer_id,
                               :pula_biletow)"""
        cr.execute(insert_sql, pasazer_id=passenger_id, pula_biletow=pool_id)

        # UPDATE TICKETS POOL
        update_sql = """UPDATE PULABILETOW 
                           SET ILEDOSTEPNYCHMIEJSC = ILEDOSTEPNYCHMIEJSC - 1
                         WHERE PULABILETOW_ID = :pula_biletow"""
        cr.execute(update_sql, pula_biletow=pool_id)

        connection.commit()
        cr.close()

        return "Pomyślnie dodano bilet do wybranego pasażera", c.SUCCESS

    def update_ticket(self, ticket_id: int, czy_oplacony, cena) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()
        try:
            cr.execute("""UPDATE BILET 
                             SET CZYOPLACONY = :czy_oplacony,
                                 CENA = :cena
                           WHERE BILET_ID = :id """,
                       czy_oplacony=czy_oplacony,
                       cena=cena,
                       id=ticket_id)
        except cx_Oracle.IntegrityError as e:
            return "Wystąpił błąd", c.ERROR, None
        else:
            connection.commit()
            cr.close()
        return "Pomyślnie zaktualizowano bilet", c.SUCCESS, None

    def delete_ticket(self, ticket_id: int) -> Tuple[str, str]:
        connection = self.pool.acquire()
        cr = connection.cursor()

        # DELETE TICKET
        try:
            cr.execute("DELETE FROM BILET WHERE BILET_ID = :id", id=ticket_id)
        except cx_Oracle.IntegrityError:
            cr.close()
            return "Błąd usuwania biletu", c.ERROR
        else:
            connection.commit()
            cr.close()
            return "Pomyślnie usunięto bilet", c.SUCCESS

        # UPDATE TICKET POOL
        update_sql = """UPDATE PULABILETOW 
                               SET ILEDOSTEPNYCHMIEJSC = ILEDOSTEPNYCHMIEJSC + 1
                             WHERE PULABILETOW_ID = (SELECT b.PULABILETOW_ID 
                                                       FROM BILET b
                                                      WHERE b.BILET_ID = :id)"""
        cr.execute(update_sql, id=ticket_id)

        connection.commit()
        cr.close()

        return "Pomyślnie usunięto wybrany bilet", c.SUCCESS

    def call_obsluzeni(self, start_date: datetime.datetime, end_date: datetime.datetime) -> int:
        connection = self.pool.acquire()
        cr = connection.cursor()

        val = cr.callfunc('Obsluzeni', int, [start_date, end_date])
        cr.close()
        return val

    def call_zmianaceny(self, value: int, plus_minus: str):
        connection = self.pool.acquire()
        cr = connection.cursor()

        cr.callproc('ZmianaCeny', [value, plus_minus])
        connection.commit()
        cr.close()

    def select_min_price(self) -> int:
        connection = self.pool.acquire()
        cr = connection.cursor()
        cr.execute("SELECT MIN(CENA) FROM KLASA")
        data = cr.fetchone()[0]
        cr.close()
        return data
