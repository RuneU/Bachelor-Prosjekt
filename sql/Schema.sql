-- Opprettelse av tabellen "Krise"
CREATE TABLE Krise (
    KriseID INT NOT NULL IDENTITY(1,1),
    KriseSituasjonType VARCHAR(256) NULL,
    KriseNavn VARCHAR(256) NULL,
    Status VARCHAR(256) NOT NULL,
    Lokasjon VARCHAR(256) NOT NULL,
    Tekstboks TEXT NULL,
    Opprettet DATETIME NOT NULL DEFAULT,
    FerdigTimestamp DATETIME NULL,
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
    ImageURL NVARCHAR(500) NULL,
    FOREIGN KEY (KriseID) REFERENCES Krise(KriseID)
);

-- Opprettelse av tabellen "KontaktPerson"
CREATE TABLE KontaktPerson (
    KontaktPersonID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    Fornavn VARCHAR(256) NULL,
    MellomNavn VARCHAR(256) NULL,
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
    ChipID NVARCHAR(50) NULL, 
    EvakuertID INT UNIQUE,
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE
);

CREATE TABLE Faces (
    FaceID INT IDENTITY(1,1) PRIMARY KEY, 
    EvakuertID INT NOT NULL, 
    ImageURL NVARCHAR(500) NOT NULL, 
    Timestamp DATETIME DEFAULT GETDATE(), 
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE);

-- Oppretelse av tabell for Lokasjons logg for evakuerte gjennom Status tabell
CREATE TABLE Lokasjon_log (
    log_id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    status_id INT NOT NULL,
    evakuert_id INT NULL,
    old_lokasjon VARCHAR(256),
    new_lokasjon VARCHAR(256),
    change_date DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_LokasjonLog_Evakuerte FOREIGN KEY (evakuert_id) REFERENCES Evakuerte(EvakuertID)
);

-- Trigger event for når lokasjons feltet i status tabellen blir endret og oppdatert i Lokasjona-log
CREATE TRIGGER trg_LogLokasjonChange
ON Status
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO Lokasjon_log (status_id, evakuert_id, old_lokasjon, new_lokasjon, change_date)
    SELECT i.StatusID,
           i.EvakuertID,
           d.Lokasjon,
           i.Lokasjon,
           GETDATE()
    FROM inserted i
    INNER JOIN deleted d ON i.StatusID = d.StatusID
    WHERE ISNULL(i.Lokasjon, '') <> ISNULL(d.Lokasjon, '');
END;

-- Enkapsulert logikk for sletting av data i lokasjon_log tabellen som er eldre enn 14 dager
CREATE PROCEDURE CleanOldLokasjonLogs2
AS
BEGIN
    DELETE FROM Lokasjon_log
    WHERE change_date < DATEADD(DAY, -14, GETDATE());
END;

-- Opprettelse av tabellen "RFID"
CREATE TABLE RFID (
    ID INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    EvakuertID INT UNIQUE,
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE
);

CREATE TABLE Faces (
    FaceID INT IDENTITY(1,1) PRIMARY KEY, 
    EvakuertID INT NOT NULL, 
    ImageURL NVARCHAR(500) NOT NULL, 
    Timestamp DATETIME DEFAULT GETDATE(), 
    FOREIGN KEY (EvakuertID) REFERENCES Evakuerte(EvakuertID) ON DELETE CASCADE);

CREATE TABLE Users (
    id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    email_confirmed_at DATETIME NULL,
    password VARCHAR(255) NOT NULL,
    active BIT NOT NULL CONSTRAINT DF_Users_active DEFAULT 1,
    first_name VARCHAR(50) NULL,
    last_name VARCHAR(50) NULL,
    created_at DATETIME NOT NULL CONSTRAINT DF_Users_created_at DEFAULT GETDATE(),
    updated_at DATETIME NOT NULL CONSTRAINT DF_Users_updated_at DEFAULT GETDATE()
);
