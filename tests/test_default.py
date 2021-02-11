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

# カーネルパラメータが正しく設定されている
def test_kernel_parameters(host):
    assert 1 == host.sysctl('net.ipv6.conf.all.disable_ipv6') # IPv6を無効化
    assert 1 == host.sysctl('net.ipv6.conf.default.disable_ipv6')
    assert 1 == host.sysctl('net.ipv4.conf.all.rp_filter') # 厳密な逆方向パス転送を使用（なりすまし攻撃対策）
    assert 1 == host.sysctl('net.ipv4.conf.default.rp_filter')
    assert 0 == host.sysctl('net.ipv4.conf.all.accept_redirects') # ICMP リダイレクトを無視（MITM 攻撃対策）
    assert 0 == host.sysctl('net.ipv4.conf.default.accept_redirects')
    assert 0 == host.sysctl('net.ipv4.conf.all.accept_source_route') # ソースルーティングの無効化
    assert 1 == host.sysctl('net.ipv4.conf.all.log_martians') # 不審なパケット検知
    assert 1 == host.sysctl('net.ipv4.icmp_echo_ignore_broadcasts') # Smurf攻撃対策
    assert 1 == host.sysctl('net.ipv4.icmp_ignore_bogus_error_responses') # 不正なICMPエラーを無視
    assert 1 == host.sysctl('net.ipv4.tcp_syncookies') # SYN flood攻撃対策
    assert 2 == host.sysctl('kernel.randomize_va_space') # バッファ・オーバーフロ－攻撃対策

# sudoers が正しく設定されている
def test_sudoers(host):
    assert '%ansible ALL=(ALL) NOPASSWD: ALL' == host.check_output('cat /etc/sudoers.d/ansible') # sudo許可ユーザ

# selinux がオフになっている
def test_disabled_selinux(host):
    assert 'Disabled' == host.check_output('getenforce')

# curl,net-tools,... など、全サーバ共通のパッケージがインストールされている
def test_installed_default_package(host):
    assert host.package('bash-completion').is_installed
    assert host.package('bind-utils').is_installed
    assert host.package('curl').is_installed
    assert host.package('lsof').is_installed
    assert host.package('net-tools').is_installed
    assert host.package('python3').is_installed
    assert host.package('wget').is_installed
    assert host.package('yum-utils').is_installed

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
    assert host.run('grep "^PermitRootLogin no" /etc/ssh/sshd_config').succeeded # rootでのログイン禁止
    assert host.run('grep "^PasswordAuthentication no" /etc/ssh/sshd_config').succeeded # パスワード認証を禁止
    assert host.run('grep "^PubkeyAuthentication yes" /etc/ssh/sshd_config').succeeded # 公開鍵認証を使用
    assert host.run('grep "^AllowTcpForwarding no" /etc/ssh/sshd_config').succeeded # ポートフォワードを禁止
    assert host.run('grep "^X11Forwarding no" /etc/ssh/sshd_config').succeeded # X11を禁止
