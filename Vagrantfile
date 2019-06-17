# -*- mode: ruby -*-
# vi: set ft=ruby :
################################################################################
# IronPort Correlator Vagrant File
# Yahia Kandeel <yahia.kandeel@gmail.com>
################################################################################
Vagrant.configure("2") do |config|
  config.vm.define "ironport" do |conf|
    conf.vm.box = "centos/7"
    conf.vm.hostname = "ironport"
    conf.vm.network "private_network", ip: "192.168.40.10"
    conf.vm.synced_folder ".", "/vagrant", type: "nfs"
    config.vm.network "forwarded_port", protocol: "tcp", guest: 514, host: 5014
    config.vm.network "forwarded_port", protocol: "udp", guest: 514, host: 5014
    conf.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.name = "ironport"
      vb.memory = "4069"
    end
    conf.vm.provision "shell", path: "install.sh"
  end
end
################################################################################
