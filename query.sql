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