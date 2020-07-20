if [[ $ENV == 'local' ]]; then
    #statements
    python manage.py migrate --noinput
    python manage.py loaddata favorite_app/fixtures/*.json
    cp /usr/src/app/supervisor.conf /etc/supervisor/conf.d/
    rm /etc/nginx/sites-enabled
    ln -s /usr/src/app/nginx.conf /etc/nginx/sites-enabled
    supervisord -n
else
    python manage.py migrate --noinput
    python manage.py loaddata favorite_app/fixtures/*.json
    cp /usr/src/app/supervisor.conf /etc/supervisor/conf.d/
    rm /etc/nginx/sites-enabled
    ln -s /usr/src/app/nginx.conf /etc/nginx/sites-enabled
    supervisord -n
fi
