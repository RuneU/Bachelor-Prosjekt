-- Sett inn data i "Krise"-tabellen
INSERT INTO Krise (KriseSituasjonType, KriseNavn, Lokasjon, status)
VALUES
('Brann', 'Bybrann i Oslo', 'Oslo', 'Ny'),
('Flom', 'Vannflom i Bergen', 'Bergen', 'Pågående'),
('Jordskjelv', 'Jordskjelv i Tromsø', 'Tromsø', 'Pågående');

-- Sett inn data i "Evakuerte"-tabellen
INSERT INTO Evakuerte (Fornavn, Etternavn, Telefonnummer, Adresse, KriseID)
VALUES
('Ola', 'Nordmann', 12345678, 'Storgata 1, Oslo', 1),
('Kari', 'Hansen', 98765432, 'Hovedveien 10, Bergen', 2),
('Per', 'Johansen', 45678912, 'Kystveien 5, Tromsø', 3),
('Lise', 'Andersen', 11223344, 'Parkveien 3, Oslo', 1);

-- Sett inn data i "KontaktPerson"-tabellen
INSERT INTO KontaktPerson (Fornavn, Etternavn, Telefonnummer, EvakuertID)
VALUES
('Anne', 'Larsen', 22334455, 1),
('Erik', 'Berg', 66778899, 2),
('Mona', 'Pettersen', 44556677, 1),
('Tor', 'Nilsen', 99887766, 4);

-- Sett inn data i "Status"-tabellen
INSERT INTO Status (Status, Lokasjon, EvakuertID)
VALUES
('Trygg', 'Oslo', 1),
('Mindre skadet', 'Bergen', 2),
('Kritisk', 'Tromsø', 3),
('Trygg', 'Oslo', 4);

-- Sett inn data i "RFID"-tabellen
INSERT INTO RFID (EvakuertID)
VALUES
(1),
(2),
(3),
(4);
