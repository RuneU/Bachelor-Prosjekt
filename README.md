# Bachelor-Prosjekt

Bruksanvisning for installering av prosjekt:

Installer npm: https://nodejs.org/en
Installer Python: https://www.python.org/downloads/


## venv
Hvis venv skal ignoreres, ignoreres denne delen og hopper rett til ``` pip install flask ```.

Installering og aktivering av flask i venv enviroment. 

 For å installere i venv enviroment som brukes i VS Code må og python extention installeres i VS Code som den finner automatisk og spør om installering når du klikker inn i app.py

Gå inn i Bachelor-Prosjekt mappen i CLI. Kjør kommando Linux:``` python3 -m venv .venv ``` Windows: ``` py -3 -m venv .venv ```

Aktiver så venv med Windows: ``` .venv\Scripts\activate ``` Linux: ```. .venv/bin/activate```

Venv er nå aktivert.

Start ny CLI i samme mappe da den du er i nå er i Venv enviroment

## start
 Kjør nå ``` pip install flask ``` 

Lagt til requirements.txt, for dependencies slik som flask, odbc og videre kjør kommando:```pip install -r requirements.txt```

Installer tailwind css med ```npm install -D tailwindcss``` 

Initialiser tailwind med ```npx tailwindcss init``` 

Installer flowbite ```npm install flowbite```

kjør ```python app.py``` for å sjekke at det fungerer.

## Database tilkobling
Opprett en env fil i root directory av prosjektet som heter ```.env```

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

Husk å installere driveren
```
pip install pyodbc
```

Ferdig

## Tester
For å kjøre testene i prosjekte bruk kommandoen under
```
python -m unittest discover test
```

## Ekstra packages som kan være nødvendig for IoT funksjonalitet

```
 pip install opencv-python 
```

```
 pip install opencv-python-headless   
```

<<<<<<< HEAD
=======

>>>>>>> cf376ac67c9eece8d8169572403f4b53a947d3c1
Link flask nettside: https://flask.palletsprojects.com/en/stable/installation/

Link til Flowbite for tailwind og flowbite: https://flowbite.com/docs/getting-started/flask/