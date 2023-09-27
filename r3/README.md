# Integrantes del reto 3

Jorge Alfredo Villarreal Márquez

Daniel Gonzalez Bernal

Martin Villegas Aristizábal

Para las máquinas que no sean el servidor de NFS:
```sh
sudo apt update
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo apt install git -y

sudo systemctl enable docker
sudo systemctl start docker
```

Para AWS
```sh
sudo usermod -a -G docker ubuntu 
```
Para GCP
```sh
sudo usermod -a -G docker <username>
```

Y si necesita más permisos que Dios
```sh
sudo chmod 666 /var/run/docker.sock
```

O se puede quedar con el defecto de
```sh
sudo chmod 660 /var/run/docker.sock
```

![[Pasted image 20230922215612.png]]
### IPs
Privadas:

NFS_Server: 172.31.41.237 
MySQL: 172.31.36.135

Drupal1: 172.31.42.234
Drupal2: 172.31.35.156

LB
IP Pública: 35.153.228.44
(Solo http)
IP Privada: 172.31.83.12

### En el servidor NFS
PrivateIPs: 172.31.41.237
Tras seguir [algunos](https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04) [tutoriales](https://linuxhint.com/install-and-configure-nfs-server-ubuntu-22-04/) se puede quedar con el siguiente /etc/exports

```/etc/exports
/mnt/nfs_share 172.31.0.0/16(rw,sync,no_root_squash,no_subtree_check)
/home  172.31.0.0/16(rw,sync,no_root_squash,no_subtree_check)
```

Y asegurarse que los grupos queden así 
![[Pasted image 20230922221541.png]]
### En la base de datos
MySQL
PrivateIPs: 172.31.36.135


Se sube el siguiente docker-compose.yml
```yml
version: '3.1'
services:
  db:
    image: mysql:5.7
    restart: always
    ports:
      - 3306:3306 
    environment:
      MYSQL_DATABASE: exampledb
      MYSQL_USER: exampleuser
      MYSQL_PASSWORD: examplepass
      MYSQL_RANDOM_ROOT_PASSWORD: '1'
    volumes:
      - db:/var/lib/mysql
volumes:
  db:
```

De ser necesario, se puede activar con
```sh
docker start ubuntu_db_1
```
y para monitorear en tiempo real
```sh
docker attach ubuntu_db_1
```


## En las apps de procesamiento:

App1
PrivateIPs: 172.31.42.234

Drupal2
PrivateIPs: 172.31.35.156


Una vez esté configurado el nfs, se correrá el siguiente comando para montar cada vez (parar las instancias no permite que persista el montaje entonces hay que hacerse cada vez)

`sudo mount 172.31.41.237:/mnt/nfs_share /mnt/nfs_clientshare`


con el siguiente docker-compose.yml

```yml 
services:
  drupal:
    image: drupal:latest
    ports:
      - "80:80"
      - "3306:3306"
    volumes:
      - /mnt/nfs_clientshare:/var/www/html/sites/default/files  # Mount the NFS share here for Drupal files
      - /var/www/html/modules
      - /var/www/html/profiles
      - /var/www/html/themes
      # this takes advantage of the feature in Docker that a new anonymous
      # volume (which is what we're creating here) will be initialized with the
      # existing content of the image at the same location
      - /var/www/html/sites
    restart: always
    environment:
      DRUPAL_DATABASE_HOST: 172.31.36.135  # Replace with the IP address or hostname of your MySQL client (Machine C)
      DRUPAL_DATABASE_PORT: 3306
      DRUPAL_DATABASE_NAME: exampledb
      DRUPAL_DATABASE_USER: exampleuser
      DRUPAL_DATABASE_PASSWORD: examplepass
```
De ser necesario, se puede activar con
```sh
docker start ubuntu_drupal_1
```
y para monitorear en tiempo real
```sh
docker attach ubuntu_drupal_1
```

Drupal para esto tuvo que haber sido configurada manualmente con los datos de la base de datos igualmente.

### En el LB
LB
IP Pública: 
35.153.228.44:80
IP Privada:
172.31.83.12

Con una network en docker ya creada
```sh
docker network create nginx_network
```
Se creará el contenedor así
```sh
docker run -d --name nginx-lb --network nginx_network -p 80:80 nginx

```

Y se ingresa la siguiente configuración nginx.conf en el volumen de docker
```nginx
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    upstream my_servers {
        server 172.31.42.234;
        server 172.31.35.156;
    }


    server {
        listen 80;

        location / {
            proxy_pass http://my_servers;
    }
    }
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;
      
    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

Como en este caso se copia el archivo desde afuera, basta un 
```sh
docker cp ./nginx.conf nginx-lb:/etc/nginx/nginx.conf
```
Para copiar desde el directorio del host al directorio especificado del contenedor

Bibliografía

https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04

https://linuxhint.com/install-and-configure-nfs-server-ubuntu-22-04/

https://hub.docker.com/_/drupal

https://hevodata.com/learn/docker-mysql/#Step_2_Deploy_and_Start_the_MySQL_Container

https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket

