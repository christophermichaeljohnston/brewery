# brewery

Arduino and Raspberry PI powered brewery.

Manage connected brewery devices (only fermenter at this time) and provides graphs of collected temperatures.

## dependencies

### packages

```
apt-get install python3 python3-pip
pip3 install django
pip3 install mysqlclient
pip3 install pyserial
pip3 install django-crispy-forms
apt-get install apache2 libapache2-mod-wsgi-py3
```

## configuration

### /etc/apache2/sites-enabled/000-default.conf

```
Alias /media/ /var/www/brewery-media/
Alias /static/ /var/www/brewery-static/

<Directory /var/www/brewery-media>
Require all granted
</Directory>

<Directory /var/www/brewery-static>
Require all granted
</Directory>

WSGIDaemonProcess brewery python-path=/var/www/brewery user=pi group=dialout
WSGIProcessGroup brewery
WSGIScriptAlias / /var/www/brewery/brewery/wsgi.py process-group=brewery

<Directory /var/www/brewery/brewery>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
```

## cron

Automatically capture fermenter temperatures every minute.
```
* * * * * curl http://localhost/fermenter/temperatures/ 2>/dev/null 1>&1
```
