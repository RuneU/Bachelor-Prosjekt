# Bachelor-Prosjekt

## Del 1: Generell installasjon og oppsett

### Forhåndskrav

- [Node.js (npm)](https://nodejs.org/en)
- [Python](https://www.python.org/downloads/)
- [pyodbc driver for din maskin](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=windows)

### Virtuelt miljø (venv)

- Opprett og aktiver venv:
  - **Windows:**  
    ```
    py -3 -m venv .venv
    .venv\Scripts\activate
    ```
  - **Linux:**  
    ```
    python3 -m venv .venv
    . .venv/bin/activate
    ```

### Installer avhengigheter

```
pip install -r requirements.txt
npm install -D tailwindcss
npx tailwindcss init
npm install flowbite
```

### Database tilkobling

Opprett `.env`-fil i prosjektets rotmappe med følgende innhold (bytt ut plassholdere):

```
DB_DRIVER={ODBC Driver 18 for SQL Server}
DB_SERVER=<server.database.windows.net>
DB_DATABASE=<databaseNavn>
DB_UID=<brukerID>
DB_PWD=<Passord>
ENCRYPT=yes
TrustServerCertificate=yes
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=<>;AccountKey=<...>;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=faces
```

### Starte applikasjonen

```
python app.py
```

### Kjøre tester

```
python -m unittest discover test
```

---

## Del 2: Spesielt for IoT-maskinen

### Ekstra krav

- [CMake](https://cmake.org/)
- [Microsoft Visual Studio Build Tools 2022 C++](https://visualstudio.microsoft.com/downloads/?q=build+tools)
- Start PC-en på nytt etter installasjon

### Ekstra Python-pakker

Disse må installeres manuelt

```
pip install face.recognition
pip install opencv-python
pip install opencv-python-headless
```

---

## Docker

For å lettere kunne åpne prosjektet gjennom nye PC-er, bruk Docker:

- Bygg Docker-container:
  ```
  docker build --no-cache -t flask-app .
  ```
  Det kan ta litt tid på grunn av face registering-modulen. Hvis du kun trenger å åpne nettsiden, og ikke IoT-siden, kan du ignorere face recognition & opencv

- Start container:
  ```
  docker run -p 5000:5000 flask-app
  ```

- For å kunne kjøre IoT-nettsiden:
  ```
  docker run -p 5000:5000 flask-app python IOT.py
  ```

---

## Nyttige lenker

- [Flask dokumentasjon](https://flask.palletsprojects.com/en/stable/installation/)
- [Flowbite for Tailwind/Flask](https://flowbite.com/docs/getting-started/flask/)