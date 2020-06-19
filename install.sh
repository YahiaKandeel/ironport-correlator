#!/usr/bin/bash
################################################################################
# Logstash, Redis, Python3 Installation Bash Script on CentOS7
################################################################################

###########
# Bootstrap
###########
# Installation
yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum install -y wget vim firewalld net-tools gcc make openssl-devel

###########
# Logstash
###########
yum install -y java-1.8.0-openjdk
rpm -ivh https://artifacts.elastic.co/downloads/logstash/logstash-7.8.0.rpm

# Config
[ -e /vagrant/logstash.conf ] && \
	cp /vagrant/logstash.conf /etc/logstash/conf.d/ironport.conf

# Start & Enable
systemctl enable logstash --now

###########
# Redis
###########
yum install -y redis
# Start the services
systemctl enable redis --now

###########
# Python3
###########
yum -y install python36 python36-devel
yum -y install python36-pip
pip3 install ipython redis

###########
# logrotate
###########
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
systemctl mask iptables
systemctl enable firewalld --now
firewall-cmd --add-port=514/udp --permanent
firewall-cmd --reload

###########
# Systemd
###########
echo '''[Unit]
Description=Ironport Correlator Service
After=network.target

[Service]
Type=simple
User=vagrant
ExecStart=/bin/python3 /vagrant/main.py
Restart=always

[Install]
WantedBy=multi-user.target''' > /etc/systemd/system/ironport.service

systemctl daemon-reload
systemctl enable --now ironport
