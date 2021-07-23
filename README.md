# ansible-playbook-webapp-site

Web アプリケーションをホストするための基本的なインフラ基盤を構築できる ansible playbook です

- Load Balancer (Reverse Proxy サーバ)、Application サーバ、Database サーバで構成されます
- 各サーバは、2台1セットで冗長化されます
- サンプルの Web アプリケーションとして、[ヘルスチェックアプリケーション](https://github.com/izumimatsuo/app-flask-healthcheck)がデプロイされます
- vagrant/virtualbox にて動作検証ができます

## 動作検証の方法

- vagrant/virtualbox, python3, git, ssh, curl が利用できる環境を用意してください

以下で環境を構築します

```
$ git clone https://github.com/izumimatsuo/ansible-playbook-webapp-site.git
$ cd ansible-playbook-webapp-site
$ ssh-keygen -t rsa -f .ssh/id_rsa_ansible -C 'ansible user'

$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install --upgrade pip
(.venv) $ pip install ansible testinfra passlib
(.venv) $ ansible-galaxy install -r requirements.yml -p ./roles

(.venv) $ vagrant up
(.venv) $ ansible-playbook site.yml
```

正しく環境構築できているか検証します

```
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://lbservers' tests/test_defaults.py tests/test_lbservers.py
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://appservers' tests/test_defaults.py tests/test_appservers.py
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://rdbservers' tests/test_defaults.py tests/test_rdbservers.py
```

アプリケーションを起動して動作検証します

```
(.venv) $ ssh -F .ssh/config 192.168.33.21 sudo docker stack deploy -c /var/lib/stretcher/healthcheck-api/docker-compose.yml sample
Ignoring unsupported options: restart

Creating network sample_default
Creating service sample_app

(.venv) $ curl -i http://192.168.33.10/healthcheck
HTTP/1.1 200 OK
Date: Thu, 11 Feb 2021 02:36:39 GMT
Content-Type: application/json
Content-Length: 23

{
  "status": "pass"
}
```

## サーバの情報

### サーバ共通

- OS に、CentOS 7 を適用
- 仮想マシンのスペックは、1CPU, 256Mbyte メモリ
- ssh を使用して管理ユーザでログインできる（公開鍵認証）

#### roles

- [osinit](https://github.com/izumimatsuo/ansible-role-osinit)

### Load Balancer (Reverse Proxy サーバ）

- haproxy を適用
- keepalived を適用して 1+1（Active/Standby）クラスタを構成

#### node

- lb_vip 192.168.33.10
- lb1 192.168.33.11
- lb2 192.168.33.12

#### roles

- [haproxy](https://github.com/izumimatsuo/ansible-role-haproxy.git)
- [keepalived](https://github.com/izumimatsuo/ansible-role-keepalived.git)

#### vars

| 項目名                  | 設定値                                |
| ----------------------- | ------------------------------------- |
| haproxy_backend_groups  | [{name: 'default', listen_port: 5000, protocol: 'http'}] |
| haproxy_backend_servers | {default: "{{ groups['appservers'] }}"} |
| keepalived_cluster_info | {virtual_ipaddr: '{{ lb_vip }}', check_interface: 'eth1'} |

### Application サーバ

- docker swarm を適用して 1+1（Manager/Worker）クラスタを構成
- stretcher を適用してアプリケーションの自動デプロイ（コンテナイメージのインポート）を実行

#### node

- app1 192.168.33.21
- app2 192.168.33.22

#### roles

- [docker](https://github.com/izumimatsuo/ansible-role-docker.git)
- [stretcher](https://github.com/izumimatsuo/ansible-role-stretcher.git)

#### vars

| 項目名                     | 設定値                                         |
| -------------------------- | ---------------------------------------------- |
| docker_swarm_manager_hostnames | ['app1'] |
| stretcher_autorun_manifest | ```https://izumimatsuo.github.io/ansible-playbook-webapp-site/deploy-latest.yml``` |

### Database サーバ

- postgresql を適用
- pacemaker/corosync を適用して 1+1（Master/Standby）クラスタを構成

#### node

- rdb_vip 192.168.33.30
- rdb1 192.168.33.31
- rdb2 192.168.33.32

#### roles

- [postgresql](https://github.com/izumimatsuo/ansible-role-postgresql.git)

#### vars

| 項目名                 | 設定値                                         |
| ---------------------- | ---------------------------------------------- |
| pgsql_cluster_hostnames | "{{ groups['rdbservers'] }}" |
| pgsql_cluster_info | {virtual_ipaddr: '{{ rdb_vip }}', check_interface: 'eth1'} |
