# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.box = "centos/7"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "256"
    vb.cpus = 1
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "vmsetup.yml"
  end

  num_of_servers = 2
  (0...num_of_servers).each do |i|
    config.vm.define "lb#{i+1}" do |c|
      c.vm.network "private_network", ip: "192.168.56.1#{i+1}"
    end
  end

  num_of_servers = 2
  (0...num_of_servers).each do |i|
    config.vm.define "app#{i+1}" do |c|
      c.vm.network "private_network", ip: "192.168.56.2#{i+1}"
    end
  end

  num_of_servers = 2
  (0...num_of_servers).each do |i|
    config.vm.define "rdb#{i+1}" do |c|
      c.vm.network "private_network", ip: "192.168.56.3#{i+1}"
    end
  end

end
