# Playlist App Django
 Fun game to play with friends built on django


# Installation
 1. Clone the repository.
 2. Create and activate virtual environment with the following command:
```
virtualenv venv && venv\Scripts\activate
```
 3. To install dependencies -
 ```
 pip install -r requirements.txt
 ```
 
 4. Migrate the db:
```
python manage.py makemigrations
```
```
python manage.py migrate
```
 4. Run the Server:
```
python manage.py runserver
```
To run the celery application :
```
celery -A playlist worker -l info
```