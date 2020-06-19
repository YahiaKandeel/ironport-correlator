# -*- mode: ruby -*-
# vi: set ft=ruby :
################################################################################
# IronPort Correlator Vagrant File
# Yahia Kandeel <yahia.kandeel@gmail.com>
################################################################################
Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"
  config.vm.hostname = "ironport"
  config.vm.network "public_network"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.name = "ironport"
    vb.memory = "4069"
  end
  config.vm.provider "libvirt" do |lv|
    lv.cpus = 2
    lv.memory = "4069"
  end
  config.vm.provision "shell", path: "install.sh"
end
################################################################################
