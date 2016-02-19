# brewery

Raspberry PI and Arduino powered brewery.

## apache 2
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
