
Primero se crean las VM de los nodos y del líder con E2-MICRO Y Ubuntu 22.04 y se corre:
	sudo snap refresh
	
En cada maquina instalamos el microk8s con : 
sudo snap install microk8s --classic

Además corremos el siguiente comando para otorgar permisos de superusuario y no tener que estar utilizando sudo para cada comando que se corre:
sudo usermod -a -G microk8s $(whoami)

En la máquina que va a ser el líder (control plane) usamos el código (se corre n cantidad de máquinas que haya para obtener un código para cada uno): 
microk8s add-node
	
De acá obtenemos los códigos únicos para más adelante utilizar en cada máquina y poderla conectar al líder.


Cuando se tienen los códigos necesarios se corre la siguiente línea en cada máquina para conectarse al líder:
	microk8s join 10.128.0.11:25000/834739147cdfa9bb857e7b1f19b0de70/d997f5f24439


Luego para revisar que los nodos ya hacen parte del cluster, usamos el código:
 microk8s kubectl get node
s




En el nodo principal creamos la base de datos definiendo una configuración por medio de un archivo yaml y luego aplicamos los cambios de esa configuración por medio del siguiente comando: 
	microk8s kubectl apply -f mysql-statefulset.yaml



Luego para ver las bases de datos que tenemos corremos el siguiente comando (debe mostrar 2 porque tenemos 2 réplicas):
microk8s kubectl get pods


Y para ver todos los servicios que se están corriendo en el cluster lo hacemos con el comando (My service es el load balancer):
	microk8s kubectl get svc




Luego en el plane se hacen unos archivos de configuración yaml para el pvc del wordpress para luego proceder a crear el wordpress como tal. Luego de tener el yaml para el pvc corremos este comando:
	kubectl apply -f wordpress-pvc.yaml

Y para correr el archivo de configuraciones del wordpress utilizamos lo siguiente:
	microk8s kubectl apply -f wordpress-deployment.yaml
