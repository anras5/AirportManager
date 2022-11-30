# Airport Manager

## HOW TO RUN

`flask --app flaskr --debug run`

or

`.\run.bat`

## MODUŁY DLA ADMINA

1. **Loty** - dane dotyczące tabel Przylot, Odlot, Lotnisko, Producent, Model, Pula Biletów, Klasa
2. **Mapa** - mapa lotów na kuli ziemskiej / mapie
3. **Pasażer** - dane dotyczące tabel Pasażer i Bilet
4. **Pasy Startowe** - dane dotyczące tabel Pas, Rezerwacja

### Jakie operacje i gdzie można wykonywać na danych tabelach

1. Pas - wszystko w module Pasy Startowe
2. Rezerwacja - dodawanie przy definicji lotu, wyświetlanie w Pasy Startowe, aktualizacja w aktualizacji Lotu, usuwanie wraz z Lotem
3. Przylot - wszystko w module Loty
4. Odlot - wszystko w module Loty
5. Linia Lotnicza - wszystko w module Loty
6. Lotnisko - wszystko w module Loty
7. Producent - wszystko w module Loty
8. Model - wszystko w module Loty
9. PulaBiletow - dodawanie przy definicji lotu, wyświetlanie po kliknięciu w dany lot, aktualizacja poprzez aktualizację Lotu, usuwanie wraz z Lotem
10. Klasa - wszystko w module Loty
11. Pasażer - wszystko w module Pasażer
12. Bilet - wszystko w module Pasażer


### Categories for flash notifications
1. 'success' - kolor zielony
2. 'warning' - kolor żółty
3. 'error' - kolor czerwony
4. 'info' - kolor niebieski
5. 'neutral' - kolor szary