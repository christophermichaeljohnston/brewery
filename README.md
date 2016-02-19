# brewery

Raspberry PI and Arduino powered brewery.

## dependencies

### packages

```
apt-get install python3 python3-pip
apt-get install python3-serial
pip3 install mysqlclient
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

WSGIDaemonProcess localhost python-path=/var/www/brewery
WSGIProcessGroup localhost
WSGIScriptAlias / /var/www/brewery/brewery/wsgi.py process-group=localhost

<Directory /var/www/brewery/brewery>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
```
