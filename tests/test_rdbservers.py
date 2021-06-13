# pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://rdbservers' tests/test_rdbserver.py

# パッケージがインストールされている
def test_installed_default_package(host):
    assert host.package('postgresql96').is_installed

# 起動すべきサービスが起動している
def test_running_default_service(host):
    assert host.service('pacemaker').is_running
    assert host.service('corosync').is_running
    assert host.service('pcsd').is_running

# 公開サービスが意図したポートでリッスンしている
def test_listen_default_port(host):
    assert host.socket('tcp://0.0.0.0:5432').is_listening
