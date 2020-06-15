#!/usr/bin/bash
################################################################################
# Logstash, Redis, Python3 Installation Bash Script on CentOS7
################################################################################
# Bootstrap
yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
yum install -y wget vim firewalld net-tools gcc make openssl-devel
# Start Firewalld
systemctl mask iptables
systemctl enable firewalld --now

# Logstash
yum install -y java-1.8.0-openjdk
rpm -ivh https://artifacts.elastic.co/downloads/logstash/logstash-7.1.0.rpm
# copy logstash config file
if [ -e /vagrant/logstash.conf ]; then 
	cp /vagrant/logstash.conf /etc/logstash/conf.d/ironport.conf
else
	cp ./logstash.conf /etc/logstash/conf.d/ironport.conf
fi
# Start the services
systemctl enable logstash --now

# Redis
yum install -y redis
# Start the services
systemctl enable redis --now

# Python
yum -y install python36 python36-devel
yum -y install python36-pip
pip3 install ipython redis

# Configure logrotate
mkdir /var/log/ironport/
echo '''/var/log/ironport/*log {
    daily
    rotate 10
    copytruncate
    missingok
}
''' > /etc/logrotate.d/ironport

# Firewall Configurations
firewall-cmd --add-port=514/tcp --permanent
firewall-cmd --add-port=514/udp --permanent
firewall-cmd --reload

# Make it as a service
# Run it permenently ;)
