# Programowanie Sieciowe - PSIRC
*Bartosz Nowak, Łukasz Suchołbiak, Wojciech Sarwiński*

## 1. Treść Zadania

Celem projektu jest implementacja uproszczonego serwera IRC obsługującego uwierzytelnianie oraz komunikację między pojedynczymi użytkownikami, a także w kanałach (wraz z możliwością usuwania użytkowników z kanału).

## 2. Założenia

1. Funkcjonalne
    - Implementacja serwera IRC
    - Serwer IRC może połączyć się z innym serwerem IRC
    - Klient może połączyć się z serwerem IRC
    - Klient może dołączyć do istniejącego kanału na serwerze IRC
    - Klient może utworzyć nowy kanał
    - Klient może połączyć się z innym użytkownikiem w celu komunikacji między pojedynczymi użytkownikami
    - Serwer ma możliwość ustawienia hasła dostępu do wszystkich kanałów na nim obecnych
    - Klient ma możliwość dodania hasła do kanału
    - Klient, który utworzył kanał, ma możliwość usuwania innych użytkowników
2. Niefunkcjonalne
    - Serwer musi być zabezpieczony przez nieutoryzowanym użyciem
    - Serwer musi obsługiwać wielu użytkowników na raz
    - System musi być intuicyjny i zrozumiały w obsłudze
    - Serwer musi płynnie kończyć działanie - obsługa `SIGTERM`, `SIGINT`

## 3. Przypadki użycia

**Komunikacja z grupą znajomych**

*Aktor: Użytkownik*
1. Użytkownik łączy się do działającego serwera IRC
2. Użytkownik łączy się z kanałem `#znajomi` podając swój pseudonim
3. Użytkownik komunikuje się ze znajomymi

**Komunikacja z uwierzytelnieniem**

*Aktor: Użytkownik*
1. Użytkownik łączy się do działającego serwera IRC
2. Użytkownik podaje hasło dostępu do serwera
3. Użytkownik łączy się z kanałem `#znajomi`, podając pseudonim i hasło dostępu
4. Użytkownik komunikuje się ze znajomimi

**Tworzenie serwera IRC**

*Aktor: Administrator*
1. Administrator konfiguruje parametry uruchomienia serwera
2. Administrator uruchamia serwer IRC w sieci lokalnej
3. Administrator ustawia metodę uwierzytelniania na brak

**Łączenie serwerów IRC**

*Aktor: Administrator1, Administrator2*
1. Administrator1 chce połączyć swój serwer IRC z serwerem znajdującym się na maszynie innego administratora
2. Administrator1 zgłasza chęć połączenia do serwera
3. Administrator2 akceptuje prośbę o połączenie
4. Administrator1 ma teraz dostęp do kanałów obecnych na serwerze Administratora2

## 5. Wybrane środowisko sprzętowo-programowe

- Serwer działać będzie na systemie operacyjnym **Linux**
- Realizacja serwera w języku `Python`
    * Menadżer pakietowania i zależności: ***[Poetry](https://python-poetry.org/)***
    * Linter: ***[Ruff](https://docs.astral.sh/ruff/)***
    * Formater: ***[Black](https://github.com/psf/black)***
    * Debugger: ***[PDB](https://docs.python.org/3/library/pdb.html)***
    * Testowanie: ***[Pytest](https://docs.pytest.org/en/stable/)***

## 6. Architektura rozwiązania

Bloki funkcjonalne serwera

- Blok Interfejsu Połączeń
    * Akceptuje i zarządza połączeniami serwera z klientem przy pomocy gniazd
    * Akceptuje i zarządza połączeniami serwera z serwerem przy pomocy gniazd
    * Zarządza komunikacją z gniazdami
    * Zapewnia wielowątkową obsługę gniazd
- Blok Uwierzytelniania
    * Zarządza logowaniem użytkowników
    * Zapewnia niepowtarzalność nazw użytkowników
    * Potwierdza i zarządza listami uwierzytelniającymi
    * Zapewnia bezpieczny dostęp do kanałów chronionych hasłem
- Blok Menadżera Sesji
    * Zarządza listą użytkowników połączonych z serwerem
    * Zarządza asocjacją pomiędzy nazwą użykownia a gniazdem
    * Zarządza asocjacją pomiędzy nazwą użykownia a innym serwerem
    * Informuje inne bloki o rozłączeniu klienta
- Blok Menadżera Serwerów
    * Zarządza listą bezpośrednio połączonych serwerów IRC
    * Zarządza listą serwerów IRC dostępnych pośrednio przez bezpośrednio połączone serwery IRC
- Blok Menadżera Kanałów
    * Zarządza listą kanałów
    * Zarządza właścicielem kanału
    * Zarządza opcjonalnym hasłem dostępu do kanału
    * Zarządza listą użytkowników połączonych do kanału
    * Umożliwia właścicielowi usunąć użytkownia z kanału
    * Potwierdza status użytkownika jako członka kanału
- Blok Menadżera Przekierowań
    * Przekierowuje wiadomości pomiędzy klientami, kanałami i serwerami
    * Wysyła wiadomości prywatne do klientów połączonych do serwera
    * Wysyła wiadomości do wszystkich klientów znajdujących się na kanale połączonych do serwera
    * Przekierowuje wiadomości prywatne do odpowiednich połączonych bezpośrednio serwerów
    * Przekierowuje wiadomości wysłane na kanał do serwerów, do których połączeni są użytkownicy połączeni z danym kanałem