CREATE TABLE bilet (
    bilet_id       NUMBER(9) NOT NULL,
    czyoplacony    NUMBER(9) NOT NULL,
    miejsce        NVARCHAR2(25) NOT NULL,
    cena           NUMBER(12, 6) NOT NULL,
    pasazer_id     NUMBER(9) NOT NULL,
    pulabiletow_id NUMBER(9) NOT NULL
);

ALTER TABLE bilet ADD CONSTRAINT bilet_pk PRIMARY KEY ( bilet_id );

CREATE TABLE klasa (
    klasa_id NUMBER(9) NOT NULL,
    nazwa    NVARCHAR2(25) NOT NULL,
    obsluga  NVARCHAR2(25) NOT NULL,
    komfort  NVARCHAR2(25) NOT NULL,
    cena     NUMBER(12, 6) NOT NULL
);

ALTER TABLE klasa ADD CONSTRAINT klasa_pk PRIMARY KEY ( klasa_id );

ALTER TABLE klasa ADD CONSTRAINT klasa_un_nazwa UNIQUE ( nazwa );

CREATE TABLE linialotnicza (
    linialotnicza_id NUMBER(9) NOT NULL,
    nazwa            NVARCHAR2(100) NOT NULL,
    kraj             NVARCHAR2(25) NOT NULL
);

ALTER TABLE linialotnicza ADD CONSTRAINT linialotnicza_pk PRIMARY KEY ( linialotnicza_id );

ALTER TABLE linialotnicza ADD CONSTRAINT linialotnicza_un_nazwa UNIQUE ( nazwa );

CREATE TABLE lot (
    lot_id               NUMBER(9) NOT NULL,
    linialotnicza_id     NUMBER(9) NOT NULL,
    lotnisko_id NUMBER(9) NOT NULL,
    model_id       NUMBER(9) NOT NULL,
    typ                  VARCHAR2(10) NOT NULL
);

ALTER TABLE lot ADD CONSTRAINT lot_pk PRIMARY KEY ( lot_id );

CREATE TABLE lotnisko (
    lotnisko_id NUMBER(9) NOT NULL,
    iatacode    NVARCHAR2(25) NOT NULL,
    nazwa       NVARCHAR2(100) NOT NULL,
    miasto      NVARCHAR2(25) NOT NULL,
    kraj        NVARCHAR2(25) NOT NULL,
    icaocode    NVARCHAR2(25) NOT NULL,
    longitude   NUMBER(12, 6) NOT NULL,
    latitude    NUMBER(12, 6) NOT NULL
);

ALTER TABLE lotnisko ADD CONSTRAINT lotnisko_pk PRIMARY KEY ( lotnisko_id );

ALTER TABLE lotnisko ADD CONSTRAINT lotnisko_un_geo UNIQUE ( longitude,
                                                             latitude );

ALTER TABLE lotnisko ADD CONSTRAINT lotnisko_un_iata UNIQUE ( iatacode );

ALTER TABLE lotnisko ADD CONSTRAINT lotnisko_un_icao UNIQUE ( icaocode );

ALTER TABLE lotnisko ADD CONSTRAINT lotnisko_un_nazwa UNIQUE ( nazwa );

CREATE TABLE model (
    model_id     NUMBER(9) NOT NULL,
    nazwa        NVARCHAR2(25) NOT NULL,
    liczbamiejsc NUMBER(9) NOT NULL,
    predkosc     NUMBER(12, 6) NOT NULL,
    producent_id NUMBER(9) NOT NULL
);

ALTER TABLE model ADD CONSTRAINT model_pk PRIMARY KEY ( model_id );

ALTER TABLE model ADD CONSTRAINT model_un_nazwa UNIQUE ( nazwa );

CREATE TABLE odlot (
    lot_id       NUMBER(9) NOT NULL,
    dataodlotu   DATE NOT NULL,
    liczbamiejsc NUMBER(9) NOT NULL
);

ALTER TABLE odlot ADD CONSTRAINT odlot_pk PRIMARY KEY ( lot_id );

CREATE TABLE pas (
    pas_id  NUMBER(9) NOT NULL,
    numer   NVARCHAR2(25) NOT NULL,
    dlugosc NUMBER(12, 6) NOT NULL,
    opis    NVARCHAR2(100)
);

ALTER TABLE pas ADD CONSTRAINT pas_pk PRIMARY KEY ( pas_id );

ALTER TABLE pas ADD CONSTRAINT pas_un_numer UNIQUE ( numer );

CREATE TABLE pasazer (
    pasazer_id    NUMBER(9) NOT NULL,
    login         NVARCHAR2(25) NOT NULL,
    haslo         NVARCHAR2(25) NOT NULL,
    imie          NVARCHAR2(25) NOT NULL,
    nazwisko      NVARCHAR2(25) NOT NULL,
    pesel         NVARCHAR2(25) NOT NULL,
    dataurodzenia DATE NOT NULL
);

ALTER TABLE pasazer ADD CONSTRAINT pasazer_pk PRIMARY KEY ( pasazer_id );

ALTER TABLE pasazer ADD CONSTRAINT pasazer_un_login UNIQUE ( login );

ALTER TABLE pasazer ADD CONSTRAINT pasazer_un_pesel UNIQUE ( pesel );

CREATE TABLE producent (
    producent_id NUMBER(9) NOT NULL,
    nazwa        NVARCHAR2(100) NOT NULL,
    kraj         NVARCHAR2(25) NOT NULL
);

ALTER TABLE producent ADD CONSTRAINT producent_pk PRIMARY KEY ( producent_id );

ALTER TABLE producent ADD CONSTRAINT producent_un_nazwa UNIQUE ( nazwa );
CREATE TABLE przylot (
    lot_id          NUMBER(9) NOT NULL,
    dataprzylotu    DATE NOT NULL,
    liczbapasazerow NUMBER(9) NOT NULL
);

ALTER TABLE przylot ADD CONSTRAINT przylot_pk PRIMARY KEY ( lot_id );

CREATE TABLE pulabiletow (
    pulabiletow_id      NUMBER(9) NOT NULL,
    ilewszystkichmiejsc NUMBER(9) NOT NULL,
    iledostepnychmiejsc NUMBER(9) NOT NULL,
    lot_id              NUMBER(9) NOT NULL,
    klasa_id            NUMBER(9) NOT NULL
);

ALTER TABLE pulabiletow ADD CONSTRAINT miejsce_pk PRIMARY KEY ( pulabiletow_id );

CREATE TABLE rezerwacja (
    rezerwacja_id NUMBER(9) NOT NULL,
    "Start"       DATE NOT NULL,
    koniec        DATE NOT NULL,
    lot_id        NUMBER(9) NOT NULL,
    pas_id        NUMBER(9) NOT NULL
);

ALTER TABLE rezerwacja ADD CONSTRAINT rezerwacja_pk PRIMARY KEY ( rezerwacja_id );

ALTER TABLE pulabiletow
    ADD CONSTRAINT klasa_fk FOREIGN KEY ( klasa_id )
        REFERENCES klasa ( klasa_id );

ALTER TABLE lot
    ADD CONSTRAINT linialotnicza_fk FOREIGN KEY ( linialotnicza_id )
        REFERENCES linialotnicza ( linialotnicza_id );

ALTER TABLE rezerwacja
    ADD CONSTRAINT lot_fk FOREIGN KEY ( lot_id )
        REFERENCES lot ( lot_id );

ALTER TABLE odlot
    ADD CONSTRAINT lot_hierarchy_odlot FOREIGN KEY ( lot_id )
        REFERENCES lot ( lot_id );

ALTER TABLE przylot
    ADD CONSTRAINT lot_hierarchy_przylot FOREIGN KEY ( lot_id )
        REFERENCES lot ( lot_id );

ALTER TABLE lot
    ADD CONSTRAINT lotnisko_fk FOREIGN KEY ( lotnisko_id )
        REFERENCES lotnisko ( lotnisko_id );

ALTER TABLE lot
    ADD CONSTRAINT model_fk FOREIGN KEY ( model_id )
        REFERENCES model ( model_id );

ALTER TABLE pulabiletow
    ADD CONSTRAINT odlot_fk FOREIGN KEY ( lot_id )
        REFERENCES odlot ( lot_id );

ALTER TABLE rezerwacja
    ADD CONSTRAINT pas_fk FOREIGN KEY ( pas_id )
        REFERENCES pas ( pas_id );

ALTER TABLE bilet
    ADD CONSTRAINT pasazer_fk FOREIGN KEY ( pasazer_id )
        REFERENCES pasazer ( pasazer_id );

ALTER TABLE model
    ADD CONSTRAINT producent_fk FOREIGN KEY ( producent_id )
        REFERENCES producent ( producent_id );

ALTER TABLE bilet
    ADD CONSTRAINT pulabiletow_fk FOREIGN KEY ( pulabiletow_id )
        REFERENCES pulabiletow ( pulabiletow_id );

CREATE OR REPLACE TRIGGER arc_fkarc_2_przylot BEFORE
    INSERT OR UPDATE OF lot_id ON przylot
    FOR EACH ROW
DECLARE
    d VARCHAR2(10);
BEGIN
    SELECT
        a.typ
    INTO d
    FROM
        lot a
    WHERE
        a.lot_id = :new.lot_id;

    IF ( d IS NULL OR d <> 'przylot' ) THEN
        raise_application_error(-20223, 'FK Lot_Hierarchy_Przylot in Table Przylot violates Arc constraint on Table Lot - discriminator column Typ doesn''t have value ''przylot'''
        );
    END IF;

EXCEPTION
    WHEN no_data_found THEN
        NULL;
    WHEN OTHERS THEN
        RAISE;
END;
/

CREATE OR REPLACE TRIGGER arc_fkarc_2_odlot BEFORE
    INSERT OR UPDATE OF lot_id ON odlot
    FOR EACH ROW
DECLARE
    d VARCHAR2(10);
BEGIN
    SELECT
        a.typ
    INTO d
    FROM
        lot a
    WHERE
        a.lot_id = :new.lot_id;

    IF ( d IS NULL OR d <> 'odlot' ) THEN
        raise_application_error(-20223, 'FK Lot_Hierarchy_Odlot in Table Odlot violates Arc constraint on Table Lot - discriminator column Typ doesn''t have value ''odlot'''
        );
    END IF;

EXCEPTION
    WHEN no_data_found THEN
        NULL;
    WHEN OTHERS THEN
        RAISE;
END;
/

CREATE SEQUENCE bilet_bilet_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER bilet_bilet_id_trg BEFORE
    INSERT ON bilet
    FOR EACH ROW
    WHEN ( new.bilet_id IS NULL )
BEGIN
    :new.bilet_id := bilet_bilet_id_seq.nextval;
END;
/

CREATE SEQUENCE klasa_klasa_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER klasa_klasa_id_trg BEFORE
    INSERT ON klasa
    FOR EACH ROW
    WHEN ( new.klasa_id IS NULL )
BEGIN
    :new.klasa_id := klasa_klasa_id_seq.nextval;
END;
/

CREATE SEQUENCE linialotnicza_linialotnicza_id START WITH 1 NOCACHE ORDER;
CREATE OR REPLACE TRIGGER linialotnicza_linialotnicza_id BEFORE
    INSERT ON linialotnicza
    FOR EACH ROW
    WHEN ( new.linialotnicza_id IS NULL )
BEGIN
    :new.linialotnicza_id := linialotnicza_linialotnicza_id.nextval;
END;
/

CREATE SEQUENCE lot_lot_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER lot_lot_id_trg BEFORE
    INSERT ON lot
    FOR EACH ROW
    WHEN ( new.lot_id IS NULL )
BEGIN
    :new.lot_id := lot_lot_id_seq.nextval;
END;
/

CREATE SEQUENCE lotnisko_lotnisko_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER lotnisko_lotnisko_id_trg BEFORE
    INSERT ON lotnisko
    FOR EACH ROW
    WHEN ( new.lotnisko_id IS NULL )
BEGIN
    :new.lotnisko_id := lotnisko_lotnisko_id_seq.nextval;
END;
/

CREATE SEQUENCE model_model_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER model_model_id_trg BEFORE
    INSERT ON model
    FOR EACH ROW
    WHEN ( new.model_id IS NULL )
BEGIN
    :new.model_id := model_model_id_seq.nextval;
END;
/

CREATE OR REPLACE TRIGGER odlot_lot_id_trg BEFORE
    INSERT ON odlot
    FOR EACH ROW
    WHEN ( new.lot_id IS NULL )
BEGIN
    :new.lot_id := lot_lot_id_seq.currval;
END;
/

CREATE SEQUENCE pas_pas_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER pas_pas_id_trg BEFORE
    INSERT ON pas
    FOR EACH ROW
    WHEN ( new.pas_id IS NULL )
BEGIN
    :new.pas_id := pas_pas_id_seq.nextval;
END;
/

CREATE SEQUENCE pasazer_pasazer_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER pasazer_pasazer_id_trg BEFORE
    INSERT ON pasazer
    FOR EACH ROW
    WHEN ( new.pasazer_id IS NULL )
BEGIN
    :new.pasazer_id := pasazer_pasazer_id_seq.nextval;
END;
/

CREATE SEQUENCE producent_producent_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER producent_producent_id_trg BEFORE
    INSERT ON producent
    FOR EACH ROW
    WHEN ( new.producent_id IS NULL )
BEGIN
    :new.producent_id := producent_producent_id_seq.nextval;
END;
/

CREATE OR REPLACE TRIGGER przylot_lot_id_trg BEFORE
    INSERT ON przylot
    FOR EACH ROW
    WHEN ( new.lot_id IS NULL )
BEGIN
    :new.lot_id := lot_lot_id_seq.currval;
END;
/

CREATE SEQUENCE pulabiletow_pulabiletow_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER pulabiletow_pulabiletow_id_trg BEFORE
    INSERT ON pulabiletow
    FOR EACH ROW
    WHEN ( new.pulabiletow_id IS NULL )
BEGIN
    :new.pulabiletow_id := pulabiletow_pulabiletow_id_seq.nextval;
END;
/

CREATE SEQUENCE rezerwacja_rezerwacja_id_seq START WITH 1 NOCACHE ORDER;

CREATE OR REPLACE TRIGGER rezerwacja_rezerwacja_id_trg BEFORE
    INSERT ON rezerwacja
    FOR EACH ROW
    WHEN ( new.rezerwacja_id IS NULL )
BEGIN
    :new.rezerwacja_id := rezerwacja_rezerwacja_id_seq.nextval;
END;
/

--Funkcja:
create or replace FUNCTION Obsluzeni (p1 DATE, p2 DATE)
        RETURN NUMBER IS
            v1 NUMBER := 0;
            v2 NUMBER := 0;
            wynik NUMBER;
        BEGIN
            SELECT SUM(LICZBAPASAZEROW) INTO v1
            FROM PRZYLOT
            WHERE DATAPRZYLOTU >= p1 AND DATAPRZYLOTU <= p2;

            SELECT SUM((p.ilewszystkichmiejsc-p.iledostepnychmiejsc)) INTO v2
            FROM PULABILETOW p JOIN ODLOT o ON p.LOT_ID = o.LOT_ID
            WHERE DATAODLOTU >= p1 AND DATAODLOTU <= p2;

            wynik := v1 + v2;
            RETURN wynik;
        END Obsluzeni;

--Procedura
create or replace PROCEDURE ZmianaCeny(p NUMBER, p2 VARCHAR2 ) AS
        BEGIN
            BEGIN
                UPDATE Klasa
                SET Cena =  CASE
                                WHEN p2 = '+' THEN Cena+p
                                ELSE Cena-p
                            END;
            END;
        END ZmianaCeny;