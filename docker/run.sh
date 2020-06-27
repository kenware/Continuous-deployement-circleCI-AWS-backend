if [[ $ENV == 'local' ]]; then
    #statements
    python manage.py migrate --noinput
    python manage.py loaddata favorite_app/fixtures/*.json
    python manage.py runserver 0.0.0.0:8000
else
    cp /usr/src/app/nginx.conf /etc/nginx/conf.d/default.conf
    cp /usr/src/app/supervisor.conf /etc/supervisor/conf.d/
    supervisord -n
fi