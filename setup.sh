#!/bin/bash
if [[ $EUID -eq 0 ]]; then
  echo "This script must NOT be run as root" 1>&2
  exit 1
fi

echo "###### Update Packages list"
sudo apt update
echo
echo
echo "###### Ensure system packages are installed:"
sudo apt-get install python3-pip python3-venv git libopenjp2-7 libportaudio2 -y
echo
if [ -d "ShazamPi" ]; then
    echo "Old installation found deleting it"
    sudo rm -rf ShazamPi
fi
echo
echo "###### Clone ShazamPi git"
git clone https://github.com/ravi72munde/ShazamPi
echo "Switching into installation directory"
cd ShazamPi
install_path=$(pwd)
echo
echo "##### Creating shazampi Python environment"
python3 -m venv --system-site-packages shazampienv
echo "Activating shazampi Python environment"
source ${install_path}/shazampienv/bin/activate
echo Install Python packages
pip3 install -r requirements.txt
echo "##### shazampi Python environment created"
echo
echo "###### Generate config"
if ! [ -d "${install_path}/config" ]; then
    echo "creating  ${install_path}/config path"
    mkdir -p "${install_path}/config"
fi

cd ${install_path}
echo
if ! [ -d "${install_path}/resources" ]; then
    echo "creating ${install_path}/resources path"
    mkdir -p "${install_path}/resources"
fi
echo
echo
echo "###### Creating default config entries and files"
echo "shazampi_log = ${install_path}/log/shazampi.log" >> ${install_path}/config/options.ini
echo "done creation default config  ${install_path}/config/options.ini"

if ! [ -d "${install_path}/log" ]; then
    echo "creating ${install_path}/log"
    mkdir "${install_path}/log"
fi
echo
echo "###### shazampi update service installation"
echo
if [ -f "/etc/systemd/system/shazampi.service" ]; then
    echo
    echo "Removing old shazampi service:"
    sudo systemctl stop shazampi
    sudo systemctl disable shazampi
    sudo rm -rf /etc/systemd/system/shazampi.*
    sudo systemctl daemon-reload
    echo "...done"
fi
UID_TO_USE=$(id -u)
GID_TO_USE=$(id -g)
echo
echo "Creating shazampi service:"
sudo cp "${install_path}/setup/service_template/shazampi.service" /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/shazampienv/bin/python3 ${install_path}/python/main.py" /etc/systemd/system/shazampi.service
sudo sed -i -e "/ExecStart/a WorkingDirectory=${install_path}" /etc/systemd/system/shazampi.service
sudo sed -i -e "/EnvironmentFile/a User=${UID_TO_USE}" /etc/systemd/system/shazampi.service
sudo sed -i -e "/User/a Group=${GID_TO_USE}" /etc/systemd/system/shazampi.service
sudo mkdir /etc/systemd/system/shazampi.service.d
shazampi_env_path=/etc/systemd/system/shazampi.service.d/shazampi_env.conf
sudo touch $shazampi_env_path
echo "[Service]" | sudo tee -a $shazampi_env_path > /dev/null
sudo systemctl daemon-reload
sudo systemctl start shazampi
sudo systemctl enable shazampi
echo "...done"
echo
echo
