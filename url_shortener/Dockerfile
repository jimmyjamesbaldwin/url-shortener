# Getting multistage docker builds to work was a bit tricky as mysqlclient has
# fiddly dependencies. Instead we just copy the application code further down 
# the Dockerfile, so the dependency installs can be cached as layers to reduce
# build time.

FROM python:3.7.2-alpine 

USER root

COPY src/requirements.txt /requirements.txt

# install python3 mysqlclient dependencies and memcached 
RUN apk add --update \
    gcc \
    libc-dev \
    linux-headers \
    mariadb-dev \
    postgresql-dev \
    python3-dev \
    memcached

# install app pip dependencies
RUN pip install --upgrade pip && pip3 install -r requirements.txt

# create non-root user to run application as
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN mkdir -p /app; 
RUN chown appuser:appgroup /app 
RUN chmod 777 /app/

# copy app files
COPY src /app
WORKDIR /app

# runtime config
EXPOSE 5000

# entrypoint
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER appuser

CMD ["/app/entrypoint.sh"]
