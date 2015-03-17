Styria summer
#############

Install and run
***************

::

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py loadfeeds
    python manage.py fetchfeeds
    python manage.py runserver

    # Optional
    python manage.py createsuperuser



Urls
****

- ``/`` - feed list
- ``/add-feed/`` - add feed
- ``/words/`` - word API
- ``/top-words/`` - top words


ToDo
****

- Modify Feeder class to make testing of fetching feeds easier
- Tests
- Documentation
