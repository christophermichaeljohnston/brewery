python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000 &
python3 manage.py process_tasks &
wait %1 %2
