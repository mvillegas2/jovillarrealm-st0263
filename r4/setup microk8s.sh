sudo snap install microk8s --classic
sudo usermod -a -G microk8s $(whoami)
newgrp microk8s