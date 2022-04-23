# pytest -v --sudo --ssh-config=.ssh/config --ansible-inventory=inventory --hosts='ansible://all' tests/test_default.py

# インストールされているLinuxディストリビューションが正しい
def test_distribution(host):
    assert 'centos' == host.system_info.distribution
    assert '7.8' in host.check_output('cat /etc/redhat-release')

# タイムゾーンが正しく設定されている
def test_timezone(host):
    assert 'Asia/Tokyo' in host.check_output('timedatectl | grep "Time zone:"')

# ロケールが正しく設定されている
def test_locale(host):
    assert 'en_US.UTF-8' in host.check_output('localectl | grep Locale')

# sudoers が正しく設定されている
def test_sudoers(host):
    assert '%ansible ALL=(ALL) NOPASSWD: ALL' == host.check_output('cat /etc/sudoers.d/ansible') # sudo許可ユーザ

# selinux がオフになっている
def test_disabled_selinux(host):
    assert 'Enforcing' != host.check_output('getenforce')

# sshd,chronyd,... など起動すべきサービスが起動している
def test_running_default_service(host):
    assert host.service('auditd').is_running
    assert host.service("chronyd").is_running
    assert host.service("crond").is_running
    assert host.service("dbus").is_running
    assert host.service('getty@tty1').is_running
    assert host.service("NetworkManager").is_running
    assert host.service("polkit").is_running
    assert host.service("rsyslog").is_running
    assert host.service("sshd").is_running

# 公開サービスが意図したポートでリッスンしている
def test_listen_default_port(host):
    assert host.socket('tcp://0.0.0.0:22').is_listening # sshd
    assert host.socket('udp://127.0.0.1:323').is_listening # chronyd

# chronyがきちんと時刻同期できている
def test_sync_chronyd(host):
    assert host.run('chronyc sources | grep "^.\\*"').succeeded

# sshの設定内容が正しい
def test_sshd_config(host):
    assert host.run('grep "^PasswordAuthentication no" /etc/ssh/sshd_config').succeeded # パスワード認証を禁止
    assert host.run('grep "^PubkeyAuthentication yes" /etc/ssh/sshd_config').succeeded # 公開鍵認証を使用
