-- Opprettelse av tabellen "Krise"
CREATE TABLE Krise (
    KriseID INT NOT NULL IDENTITY(1,1),
    KriseSituasjonType VARCHAR(256) NULL,
    KriseNavn VARCHAR(256) NULL,
    Lokasjon VARCHAR(256) NOT NULL,
    Tekstboks TEXT NULL,
    PRIMARY KEY (KriseID)
);

-- Opprettelse av tabellen "Evakuerte"
CREATE TABLE Evakuerte (
    EvakuertID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    Fornavn VARCHAR(256) NULL,
    MellomNavn VARCHAR(256) NULL,
    Etternavn VARCHAR(256) NULL,
    Telefonnummer VARCHAR(20) NULL,
    Adresse VARCHAR(256) NULL,
    KriseID INT NULL,
    FOREIGN KEY (KriseID) REFERENCES Krise(KriseID)
);

-- Opprettelse av tabellen "KontaktPerson"
CREATE TABLE KontaktPerson (
    KontaktPersonID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    Fornavn VARCHAR(256) NULL,
    MellomNavn VARCHAR(256) NULL
    Etternavn VARCHAR(256) NULL,
    Telefonnummer VARCHAR(20) NULL,
    EvakuertID INT NULL,
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE
);

-- Opprettelse av tabellen "Status"
CREATE TABLE Status (
    StatusID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    Status VARCHAR(256) NOT NULL,
    Lokasjon VARCHAR(256) NOT NULL,
    EvakuertID INT NULL,
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE
);

-- Opprettelse av tabellen "RFID"
CREATE TABLE RFID (
    ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    EvakuertID INT UNIQUE,
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE
);