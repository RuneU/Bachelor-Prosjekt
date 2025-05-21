-- Sett inn data i "Krise"-tabellen
INSERT INTO Krise (KriseSituasjonType, KriseNavn, Lokasjon, status)
VALUES
('Brann', 'Bybrann i Oslo', 'Oslo', 'Ny'),
('Flom', 'Vannflom i Bergen', 'Bergen', 'Pågående'),
('Jordskjelv', 'Jordskjelv i Tromsø', 'Tromsø', 'Pågående'),
('Storm', 'Høststorm i Stavanger', 'Stavanger', 'Pågående');

-- Sett inn data i "Evakuerte"-tabellen
INSERT INTO Evakuerte (Fornavn, Etternavn, Telefonnummer, Adresse, KriseID)
VALUES
('Ola', 'Nordmann', 12345678, 'Storgata 1, Oslo', 1),
('Kari', 'Hansen', 98765432, 'Hovedveien 10, Bergen', 2),
('Per', 'Johansen', 45678912, 'Kystveien 5, Tromsø', 3),
('Lise', 'Andersen', 11223344, 'Parkveien 3, Oslo', 1),
('Jens', 'Pettersen', 55667788, 'Strandgaten 22, Stavanger', 4),
('Eva', 'Olsen', 33445566, 'Markveien 15, Oslo', 1),
('Bjørn', 'Bakken', 77889900, 'Skolegaten 8, Bergen', 2),
('Nina', 'Larsen', 88990011, 'Fjellveien 3, Tromsø', 3),
('Geir', 'Svendsen', 22446688, 'Kirkegata 7, Stavanger', 4),
('Liv', 'Eriksen', 66880022, 'Karl Johans gate 25, Oslo', 1),
('Knut', 'Hauge', 11335577, 'Torggata 12, Bergen', 2),
('Ida', 'Moe', 44779933, 'Sjøgata 9, Tromsø', 3),
('Arne', 'Lunde', 77004488, 'Kongsgata 4, Stavanger', 3),
('Solveig', 'Holm', 33669922, 'Rådhusplassen 1, Oslo', 1),
('Tom', 'Christiansen', 99115544, 'Bryggen 6, Bergen', 3),
('Heidi', 'Mathisen', 55882299, 'Storgata 33, Tromsø', 3);

-- Sett inn data i "KontaktPerson"-tabellen
INSERT INTO KontaktPerson (Fornavn, Etternavn, Telefonnummer, EvakuertID)
VALUES
('Anne', 'Larsen', 22334455, 1),
('Erik', 'Berg', 66778899, 2),
('Mona', 'Pettersen', 44556677, 3),
('Tor', 'Nilsen', 99887766, 4);

-- Sett inn data i "Status"-tabellen
INSERT INTO Status (Status, Lokasjon, EvakuertID)
VALUES
('Trygg', 'Oslo', 1),
('Mindre skadet', 'Bergen', 2),
('Kritisk', 'Tromsø', 3),
('Trygg', 'Oslo', 4),
('Evakuert', 'Stavanger', 5),
('Trygg', 'Oslo', 6),
('Mindre skadet', 'Bergen', 7),
('Kritisk', 'Tromsø', 8),
('Evakuert', 'Stavanger', 9),
('Trygg', 'Oslo', 10),
('Mindre skadet', 'Bergen', 11),
('Kritisk', 'Tromsø', 12),
('Evakuert', 'Stavanger', 13),
('Trygg', 'Oslo', 14),
('Mindre skadet', 'Bergen', 15),
('Kritisk', 'Tromsø', 16);