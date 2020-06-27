#!/bin/bash
sudo apt-get update #ensure you have correct value of SECRETE_KEY AND DATABASE_URL in the settings.py
sudo apt-get upgrade
sudo apt install software-properties-common
echo | sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7 #install python3.7

sudo apt-get install python3.7-venv # setup virtual env
python3.7 -m venv env
source env/bin/activate

cd favorite-things
pip3 install -r requirements.txt
python manage.py migrate

pip3 install gunicorn  # install gunicorn and nginx
sudo apt-get install nginx
sudo apt-get install supervisor
sudo nginx

cd /etc/supervisor/conf.d/ #gunicorn configuration with supervisor
if [ -e gunicorn.conf ]
then 
    echo "gunicorn configuration aleady created"
else
    sudo cat <<EOF >gunicorn.conf
    program:gunicorn]
    command=/usr/local/bin/gunicorn --chdir /home/ubuntu/favorite-things --workers 3 --bind unix:/home/ubuntu/favorite-things/app.sock config.wsgi:application
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/gunicorn/gunicorn.err.log
    stdout_logfile=/var/log/gunicorn/gunicorn.out.log

    [group:guni]
    programs:gunicorn
EOF
fi

sudo mkdir /var/log/gunicorn
sudo supervisorctl reread
sudo supervisorctl update

sudo apt install curl
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt install nodejs
cd ~
cd favorite-things/client
npm install
npm run build

cd ~
cd /etc/nginx/sites-available/
if [ -e django.conf ]
then 
    echo "nginx configuration already created"
else
    sudo cat <<EOF >gunicorn.conf
    server {
        listen 80;
        server_name ec2-34-221-201-174.us-west-2.compute.amazonaws.com;
        location /api {
            include proxy_params;
            proxy_pass http://unix:/home/ubuntu/favorite-things/app.sock;
        }

        location / {
            autoindex on;
            alias /home/ubuntu/favorite-things/client/dist/;
        }
    }
   
EOF
fi

sudo nginx -t
sudo ln django.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo service nginx restart
