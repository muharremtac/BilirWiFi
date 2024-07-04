from flask import Flask, render_template, request
import subprocess
import os
import time
from threading import Thread
import fileinput
import uuid

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    wifi_ap_array = scan_wifi_networks()
    config_hash = config_file_hash()

    return render_template('app.html', wifi_ap_array=wifi_ap_array, config_hash=config_hash)


@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')


@app.route('/wpa_settings')
def wpa_settings():
    config_hash = config_file_hash()
    return render_template('wpa_settings.html', wpa_enabled=config_hash['wpa_enabled'], wpa_key=config_hash['wpa_key'])


@app.route('/save_credentials', methods=['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']

    create_wpa_supplicant(ssid, wifi_key)

    # Call set_ap_client_mode() in a thread otherwise the reboot will prevent
    # the response from getting to the browser
    def sleep_and_start_ap():
        time.sleep(2)
        set_ap_client_mode()

    t = Thread(target=sleep_and_start_ap)
    t.start()

    return render_template('save_credentials.html', ssid=ssid)


@app.route('/save_wpa_credentials', methods=['GET', 'POST'])
def save_wpa_credentials():
    config_hash = config_file_hash()
    wpa_enabled = request.form.get('wpa_enabled')
    wpa_key = request.form['wpa_key']

    if str(wpa_enabled) == '1':
        update_wpa(1, wpa_key)
    else:
        update_wpa(0, wpa_key)

    def sleep_and_reboot_for_wpa():
        time.sleep(2)
        os.system('cp /usr/lib/bilirwifi/configuration_app/rc.local.backup /etc/rc.local')
        os.system('reboot')

    t = Thread(target=sleep_and_reboot_for_wpa)
    t.start()

    config_hash = config_file_hash()
    return render_template('save_wpa_credentials.html', wpa_enabled=config_hash['wpa_enabled'],
                           wpa_key=config_hash['wpa_key'])


######## FUNCTIONS ##########

def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array


def create_wpa_supplicant(ssid, wifi_key):
    os.system('cp /usr/lib/bilirwifi/configuration_app/rc.local.backup /etc/rc.local')

    uuid1 = uuid.uuid1()
    temp_nmconnection_file = open('wifi.nmconnection.tmp', 'w')
    temp_nmconnection_file.write('[connection]\n')
    temp_nmconnection_file.write('id=' + ssid + '\n')
    temp_nmconnection_file.write(f'uuid={uuid1}\n')
    temp_nmconnection_file.write('type=wifi\n')
    temp_nmconnection_file.write('autoconnect=true\n')
    temp_nmconnection_file.write('[wifi]\n')
    temp_nmconnection_file.write('ssid=' + ssid + '\n')
    temp_nmconnection_file.write('mode=infrastructure\n')
    temp_nmconnection_file.write('[wifi-security]\n')
    temp_nmconnection_file.write('key-mgmt=wpa-psk\n')
    temp_nmconnection_file.write('psk=' + wifi_key + '\n')
    temp_nmconnection_file.write('[ipv4]\n')
    temp_nmconnection_file.write('method=auto\n')
    temp_nmconnection_file.write('[ipv6]\n')
    temp_nmconnection_file.write('method=ignore\n')
    temp_nmconnection_file.close

    os.system('mv wifi.nmconnection.tmp /etc/NetworkManager/system-connections/' + ssid + '.nmconnection')
    os.system('sudo chown root:root /etc/NetworkManager/system-connections/' + ssid + '.nmconnection')
    os.system('sudo chmod 600 /etc/NetworkManager/system-connections/' + ssid + '.nmconnection')

    network_manager = subprocess.Popen('sudo systemctl restart NetworkManager', shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, universal_newlines=True)
    network_manager.communicate()

    os.system('sudo nmcli radio wifi on')
    os.system('sudo nmcli conn reload')

    os.system('sudo systemctl disable dnsmasq')
    os.system('sudo systemctl stop dnsmasq')
    os.system('sudo systemctl disable hostapd')
    os.system('sudo systemctl stop hostapd')

    os.system('sudo systemctl enable wyoming-satellite')
    os.system('sudo systemctl start wyoming-satellite')
    os.system('sudo systemctl enable mpd')
    os.system('sudo systemctl start mpd')

    nmcli = subprocess.Popen(f'sudo nmcli connection up {ssid}',
                      shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      universal_newlines=True)
    nmcli.communicate()

def set_ap_client_mode():
    os.system('cp /usr/lib/bilirwifi/configuration_app/rc.local.backup /etc/rc.local')
    os.system('rm -f /etc/bilirwifi/host_mode')
    os.system('rm /etc/cron.bilirwifi/aphost_bootstrapper')
    os.system('cp /usr/lib/bilirwifi/reset_device/static_files/apclient_bootstrapper /etc/cron.bilirwifi/')
    os.system('chmod +x /etc/cron.bilirwifi/apclient_bootstrapper')
    os.system('mv /etc/dnsmasq.conf.original /etc/dnsmasq.conf')
    os.system('mv /etc/dhcpcd.conf.original /etc/dhcpcd.conf')
    os.system('reboot')


def update_wpa(wpa_enabled, wpa_key):
    with fileinput.FileInput('/etc/bilirwifi/bilirwifi.conf', inplace=True) as raspiwifi_conf:
        for line in raspiwifi_conf:
            if 'wpa_enabled=' in line:
                line_array = line.split('=')
                line_array[1] = wpa_enabled
                print(line_array[0] + '=' + str(line_array[1]))

            if 'wpa_key=' in line:
                line_array = line.split('=')
                line_array[1] = wpa_key
                print(line_array[0] + '=' + line_array[1])

            if 'wpa_enabled=' not in line and 'wpa_key=' not in line:
                print(line, end='')


def config_file_hash():
    config_file = open('/etc/bilirwifi/bilirwifi.conf')
    config_hash = {}

    for line in config_file:
        line_key = line.split("=")[0]
        line_value = line.split("=")[1].rstrip()
        config_hash[line_key] = line_value

    return config_hash


if __name__ == '__main__':
    config_hash = config_file_hash()

    if config_hash['ssl_enabled'] == "1":
        app.run(host='0.0.0.0', port=int(config_hash['server_port']), ssl_context='adhoc')
    else:
        app.run(host='0.0.0.0', port=int(config_hash['server_port']))
