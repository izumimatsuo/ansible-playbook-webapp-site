# pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://lbservers' tests/test_lbservers.py

# パッケージがインストールされている
def test_installed_default_package(host):
    assert host.package('haproxy').is_installed
    assert host.package('keepalived').is_installed

# 起動すべきサービスが起動している
def test_running_default_service(host):
    assert host.service('haproxy').is_running
    assert host.service('keepalived').is_running


# VIPが設定されている
def test_keepalived_state_and_vip(host):
    state = host.run("journalctl -u keepalived |grep STATE |tail -n 1")
    addresses = host.interface("eth1").addresses

    if 'MASTER' in state.stdout:
        assert '192.168.56.10' in addresses
    else:
        assert '192.168.56.10' not in addresses


# 公開サービスが意図したポートでリッスンしている
def test_listen_default_port(host):
    assert host.socket('tcp://0.0.0.0:80').is_listening
