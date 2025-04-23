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
('Ola', 'Nordmann', 12345678, 'Storgata 1, Oslo', 20),
('Kari', 'Hansen', 98765432, 'Hovedveien 10, Bergen', 21),
('Per', 'Johansen', 45678912, 'Kystveien 5, Tromsø', 22),
('Lise', 'Andersen', 11223344, 'Parkveien 3, Oslo', 20),
('Jens', 'Pettersen', 55667788, 'Strandgaten 22, Stavanger', 23),
('Eva', 'Olsen', 33445566, 'Markveien 15, Oslo', 20),
('Bjørn', 'Bakken', 77889900, 'Skolegaten 8, Bergen', 21),
('Nina', 'Larsen', 88990011, 'Fjellveien 3, Tromsø', 22),
('Geir', 'Svendsen', 22446688, 'Kirkegata 7, Stavanger', 23),
('Liv', 'Eriksen', 66880022, 'Karl Johans gate 25, Oslo', 20),
('Knut', 'Hauge', 11335577, 'Torggata 12, Bergen', 21),
('Ida', 'Moe', 44779933, 'Sjøgata 9, Tromsø', 22),
('Arne', 'Lunde', 77004488, 'Kongsgata 4, Stavanger', 23),
('Solveig', 'Holm', 33669922, 'Rådhusplassen 1, Oslo', 20),
('Tom', 'Christiansen', 99115544, 'Bryggen 6, Bergen', 21),
('Heidi', 'Mathisen', 55882299, 'Storgata 33, Tromsø', 22);

-- Sett inn data i "KontaktPerson"-tabellen
INSERT INTO KontaktPerson (Fornavn, Etternavn, Telefonnummer, EvakuertID)
VALUES
('Anne', 'Larsen', 22334455, 74),
('Erik', 'Berg', 66778899, 75),
('Mona', 'Pettersen', 44556677, 76),
('Tor', 'Nilsen', 99887766, 77),
('Line', 'Andreassen', 12344321, 78),
('Pål', 'Simonsen', 23455432, 79),
('Silje', 'Fredriksen', 34566543, 80),
('Odd', 'Gregersen', 45677654, 81),
('Bente', 'Henriksen', 56788765, 82),
('Kjell', 'Iversen', 67899876, 83),
('Randi', 'Jensen', 78900987, 84),
('Svein', 'Karlsen', 89011098, 85),
('Tove', 'Mortensen', 90122109, 86),
('Jan', 'Olsen', 12300321, 87),
('Grete', 'Paulsen', 23011132, 88),
('Frode', 'Qvist', 30122213, 89);

-- Sett inn data i "Status"-tabellen
INSERT INTO Status (Status, Lokasjon, EvakuertID)
VALUES
('Trygg', 'Oslo', 74),
('Mindre skadet', 'Bergen', 75),
('Kritisk', 'Tromsø', 76),
('Trygg', 'Oslo', 77),
('Evakuert', 'Stavanger', 78),
('Trygg', 'Oslo', 79),
('Mindre skadet', 'Bergen', 80),
('Kritisk', 'Tromsø', 81),
('Evakuert', 'Stavanger', 82),
('Trygg', 'Oslo', 83),
('Mindre skadet', 'Bergen', 84),
('Kritisk', 'Tromsø', 85),
('Evakuert', 'Stavanger', 86),
('Trygg', 'Oslo', 87),
('Mindre skadet', 'Bergen', 88),
('Kritisk', 'Tromsø', 89);