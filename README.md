## Sith AE


To start working on the project, just run the following commands:

    git clone https://ae-dev.utbm.fr/ae/Sith.git
    cd Sith
    python3 manage.py migrate

To load some initial data in the core:

    python3 manage.py loaddata core/fixtures/*.json

You will be prompted for your Gitlab account, so you need some.

To start the debug server, just run `python3 manage.py runserver`

#### Dependencies:
  * Django

The development is done with sqlite, but it is advised to set a more robust
DBMS for production (Postgresql for example)
