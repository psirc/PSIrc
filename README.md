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
    * Menadżer pakietowania i zależności: [Poetry](https://python-poetry.org/)
