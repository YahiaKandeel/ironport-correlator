# -*- mode: ruby -*-
# vi: set ft=ruby :
################################################################################
# IronPort Correlator Vagrant File
# Yahia Kandeel <yahia.kandeel@gmail.com>
################################################################################
Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"
  config.vm.hostname = "ironport"
  
  # Network
  config.vm.network "private_network", ip: "192.168.40.10"
  # config.vm.network "public_network"
  
  # provider
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.name = "ironport"
    vb.memory = "4069"
  end
  config.vm.provider "libvirt" do |lv|
    lv.cpus = 2
    lv.memory = "4069"
  end  

  # install script
  config.vm.provision "shell", path: "install.sh"
end
################################################################################
