#!/bin/bash

## Global variables
repository_owner="Tknika"
name="serial2tcp-gateway"


## Making sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo -e "This script must be run as root" 1>&2
   exit 1
fi


## Configuration parameters
echo -e "\n-- Configuration parameters -- "
echo -e "Friendly name (default=test): "
read friendly_name;
echo -e "Network interface (default=eth0): "
read interface;
echo -e "Allowed IP (default=all IPs): "
read allowed_ip;

echo -e "\n-- Parameters summary --"
echo -e "Friendly name: $friendly_name, Network interface: $network_interface, Allowed IP: $allowed_ip "
read -p "Do you want to continue? (y/N)? " choice
	case "$choice" in
	  y|Y|s|S ) echo -e "\nStarting the installation process...";;
	  * ) echo -e "\nInstallation aborted"; exit;;
	esac


## Installing the required programs
echo -e '\nInstalling the required programs...'
apt-get update >/dev/null
apt-get --assume-yes install git python python-pip jq socat >/dev/null
pip install pyudev zeroconf netifaces >/dev/null


## Cloning the github repository
cd /tmp
if [ -d "$name" ]; then
	echo -e "\nThe github repository already exists, let's make a 'git pull'..."
	cd $name
	git pull
else
	echo -e "\nCloning the github repository..."
	git clone https://github.com/$repository_owner/$name.git
	cd $name
fi


## Creating the <serial2tcp-gateway> username
echo -e '\nCreating the serial2tcp-gateway username...'
useradd -r $name
usermod -a -G dialout $name


## Moving the program files to the installation directory
echo -e '\nCopying the program to the installation (/opt/serial2tcp-gateway) folder...'
cp -rf $name /opt
chown -R serial2tcp-gateway /opt/$name
mkdir /var/log/$name
chown -R serial2tcp-gateway /var/log/$name


## Adding the start script file
echo -e '\nAdding the start script file...'
cp -rf /tmp/$name/systemd/$name.service /etc/systemd/system/$name.service
systemctl daemon-reload
systemctl enable $name.service


## Editing the configuration.json file
echo -e '\nEditing the configuration.json file'
cd /opt/$name
cp configuration_default.json configuration.json
if [[ ! -z "${friendly_name// }" ]]; then
   jq --arg _friendly_name $friendly_name  '. | .FRIENDLY_NAME=$_friendly_name' configuration.json > tmp.$$.json && mv tmp.$$.json configuration.json
fi
if [[ ! -z "${interface// }" ]]; then
   jq --arg _interface $interface '. | .INTERFACE=$_interface' configuration.json > tmp.$$.json && mv tmp.$$.json configuration.json
fi
if [[ ! -z "${allowed_ip// }" ]]; then
   jq --arg _allowed_ip $allowed_ip '. | .ALLOWED_IP=$_allowed_ip' configuration.json > tmp.$$.json && mv tmp.$$.json configuration.json
fi
rm -rf tmp.*.json
chown $name configuration.json


## Removing the git repository
echo
read -p "Do you want to remove the git repository from your computer (y/N)? " choice
case "$choice" in
  y|Y|s|S ) echo -e "Deleting the git repository..."; rm -rf /tmp/$name;;
  * ) echo -e "Keeping the git repository...";;
esac


## Start the program
echo
read -p "Do you want to start the program now (Y/n)? " choice
case "$choice" in
  n|N ) echo -e "You can start the program typing 'systemctl start $name.service'";;
  * ) echo -e "Starting the program..."; systemctl start $name.service;;
esac


## Done
echo -e "\nDone."
