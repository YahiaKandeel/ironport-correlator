#!/usr/bin/bash
################################################################################
# Logstash, Redis, Python3 Installation Bash Script on CentOS7
################################################################################

###########
# Bootstrap
###########
# Installation
echo "Task 1: Install Init Packages"
yum -y -q install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum install -y -q wget vim firewalld net-tools gcc make openssl-devel

###########
# Logstash
###########
echo "Task 2: Install & Configure Logstash"
yum install -y -q java-1.8.0-openjdk
rpm -ivh https://artifacts.elastic.co/downloads/logstash/logstash-7.8.0.rpm > /dev/null

# Config
if [ -e /vagrant ]; then 
    # logstash config
	cp /vagrant/logstash.conf /etc/logstash/conf.d/ironport.conf
else
    cp ./logstash.conf /etc/logstash/conf.d/ironport.conf 
fi
# Start & Enable
systemctl enable logstash --now

###########
# Redis
###########
echo "Task 3: Install Redis"
yum install -y -q redis
# Start the services
systemctl enable redis --now

###########
# Python3
###########
echo "Task 4: Install Python3"
yum -y -q install python36 python36-devel
yum -y -q install python36-pip
pip3 install ipython redis > /dev/null

###########
# logrotate
###########
echo "Task 5: Configure Logrotate"
mkdir /var/log/ironport/
echo '''/var/log/ironport/*.log {
    daily
    rotate 10
    copytruncate
    missingok
}
''' > /etc/logrotate.d/ironport

###########
# Firewalld
###########
echo "Task 6: Configure Firewall"
systemctl mask iptables
systemctl enable firewalld --now
firewall-cmd --add-port=5144/udp --permanent
firewall-cmd --reload

###########
# Systemd
###########
echo "Task 7: Configure Systemd"
echo '''[Unit]
Description=Ironport Correlator Service
After=network.target

[Service]
EnvironmentFile=/vagrant/envs.sh
Type=simple
User=vagrant
ExecStart=/bin/python3 /vagrant/main.py
Restart=always

[Install]
WantedBy=multi-user.target''' > /etc/systemd/system/ironport.service

systemctl daemon-reload
systemctl enable --now ironport
