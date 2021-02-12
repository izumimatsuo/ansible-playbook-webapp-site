# ansible-playbook-webapp-site

Web アプリケーションをホストするための基本的なインフラ基盤を構築できる ansible playbook です

- Load Balancer (Reverse Proxy サーバ)、Application サーバ、Database サーバで構成されます
- 各サーバは、2台1セットで冗長化されます
- サンプルの Web アプリケーションとして、[ヘルスチェックアプリケーション](https://github.com/izumimatsuo/app-flask-healthcheck)がデプロイされます
- vagrant/virtualbox にて動作検証ができます

## 動作検証の方法

- vagrant/virtualbox, python3, git, ssh, curl が利用できる環境を用意してください
- SSL証明書は自己署名証明書です（Web ブラウザでアクセスする際に警告がでます）

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
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://lbservers' tests/test_default.py tests/test_lbserver.py
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://appservers' tests/test_default.py tests/test_appserver.py
(.venv) $ pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://rdbservers' tests/test_default.py tests/test_rdbserver.py
```

アプリケーションを起動して動作検証します

```
(.venv) $ ssh -F .ssh/config 192.168.33.21 sudo docker stack deploy -c /var/lib/stretcher/healthcheck-api/docker-compose.yml sample
Ignoring unsupported options: restart

Creating network sample_default
Creating service sample_app

(.venv) $ curl -k -i https://192.168.33.10/healthcheck
HTTP/1.1 200 OK
Server: nginx
Date: Thu, 11 Feb 2021 02:36:39 GMT
Content-Type: application/json
Content-Length: 23
Connection: keep-alive
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block

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

- nginx を適用
- SSL通信を終端してバックエンドの Application サーバへバランシング
- keepalived を適用して 1+1（Active/Standby）クラスタを構成

#### node

- lb1 ['192.168.33.11']
- lb2 ['192.168.33.12']

#### roles

- [nginx](https://github.com/izumimatsuo/ansible-role-nginx.git)

#### vars

| 項目名                 | 設定値                                |
| ---------------------- | ------------------------------------- |
| nginx_server_name      | web.example.com                       |
| nginx_ssl_on           | yes                                   |
| nginx_proxy_backends   | ['192.168.33.21:5000', '192.168.33.22:5000'] |
| nginx_cluster_info     | {virtual_ipaddr: '192.168.33.10', check_interface: 'eth1'} |

### Application サーバ

- docker swarm を適用して 1+1（Manager/Worker）クラスタを構成
- docker swarm Manager ノードで複数サーバでのアプリケーション起動・停止やスケールを一元的に実行
- stretcher を適用してアプリケーションの自動デプロイ（コンテナイメージのインポート）を実行

#### node

- app1 ['192.168.33.21']
- app2 ['192.168.33.22']

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
- データはサーバ間で同期レプリケーションを実行

#### node

- rdb1 ['192.168.33.31']
- rdb2 ['192.168.33.32']

#### roles

- [postgresql](https://github.com/izumimatsuo/ansible-role-postgresql.git)

#### vars

| 項目名                 | 設定値                                         |
| ---------------------- | ---------------------------------------------- |
| pgsql_cluster_hostnames | ['rdb1', 'rdb2'] |
| pgsql_cluster_info | {virtual_ipaddr: '192.168.33.30', check_interface: 'eth1'} |
