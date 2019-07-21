#!/bin/sh
until nc -z -v -w30 db 3306
do
  echo "Waiting for database container to start..."
  sleep 5
done

until nc -z -v -w30 memcached 11211
do
  echo "Waiting for memcached container to start..."
  sleep 5
done

python3 manage.py runserver