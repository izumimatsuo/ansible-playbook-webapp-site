# pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://appservers' tests/test_appserver.py

# パッケージがインストールされている
def test_installed_default_package(host):
    assert host.package('docker-ce').is_installed

# 起動すべきサービスが起動している
def test_running_default_service(host):
    assert host.service('docker').is_running


# Swarm クラスタが起動している
def test_swarm_active(host):
    state = host.run("docker info | grep Swarm:")
    assert 'Swarm: active' in state.stdout


# 公開サービスが意図したポートでリッスンしている
# def test_listen_default_port(host):
#     assert host.socket('tcp://0.0.0.0:80').is_listening
