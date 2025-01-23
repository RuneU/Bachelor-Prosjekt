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

Ferdig

Link flask nettside: https://flask.palletsprojects.com/en/stable/installation/
Link til Flowbite for tailwind og flowbite: https://flowbite.com/docs/getting-started/flask/