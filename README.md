# Bachelor-Prosjekt

Bruksanvisning for installering av prosjekt:

Installer npm: https://nodejs.org/en
Installer Python: https://www.python.org/downloads/

Installering og aktivering av flask i venv enviroment. 

Hvis venv skal ignoreres, ignoreres denne delen og hopper rett til ``` pip install flask ```. For å installere i venv enviroment som brukes i VS Code må og python extention installeres i VS Code som den finner automatisk og spør om installering når du klikker inn i app.py

Gå inn i Bachelor-Prosjekt mappen i CLI. Kjør kommando Linux:``` python3 -m venv .venv ``` Windows: ``` py -3 -m venv .venv ```


Aktiver så venv med Windows: ``` .venv\Scripts\activate ``` Linux: ```. .venv/bin/activate```

Venv er nå aktivert. Kjør nå ``` pip install flask ``` 

Start ny CLI i samme mappe da den du er i nå er i Venv enviroment

kjør ```python app.py``` for å sjekke at det fungerer. 

Installer tailwind css med ```npm install -D tailwindcss``` 

Initialiser tailwind med ```npx tailwindcss init``` 


Installer flowbite ```npm install flowbite```

Lagt til requirements.txt, for dependencies slik som flask, odbc og videre kjør kommando:```pip install -r requirements.txt```

## Database tilkobling
Opprett en env fil i root directory som heter ```.env```

I ```.env``` filen legg til koden under. Bytt ut plassholder informasjon med den ekte database informasjonen

```
DB_DRIVER={ODBC Driver 18 for SQL Server}
DB_SERVER=<server.database.windows.net>
DB_DATABASE=<databaseNavn>
DB_UID=<brukerID>
DB_PWD=<Passord>
```

Installer dotenv 
```
pip install python-dotenv
```


Installer `pyodbc` driveren for din maskin med å klikke [her](https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-1-configure-development-environment-for-pyodbc-python-development?view=sql-server-ver16&tabs=windows)

```
pip install pyodbc
```

Ferdig

## Tester
For å kjøre testene i prosjekte bruk kommandoen under

## Ekstra packages som kan være nødvendig for IoT funksjonalitet

 pip install opencv-python 

 pip install opencv-python-headless   

```
python -m unittest discover test
```

Link flask nettside: https://flask.palletsprojects.com/en/stable/installation/
Link til Flowbite for tailwind og flowbite: https://flowbite.com/docs/getting-started/flask/


