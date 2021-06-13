# pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://lbservers' tests/test_lbservers.py

# パッケージがインストールされている
def test_installed_default_package(host):
    assert host.package('haproxy').is_installed
    assert host.package('keepalived').is_installed

# 起動すべきサービスが起動している
def test_running_default_service(host):
    assert host.service('haproxy').is_running
    assert host.service('keepalived').is_running

# 公開サービスが意図したポートでリッスンしている
def test_listen_default_port(host):
    assert host.socket('tcp://0.0.0.0:443').is_listening
