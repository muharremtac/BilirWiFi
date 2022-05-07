import os
import sys

os.system('clear')
print()
print()
print("#################################")
print("##### BilirWiFi Uninstaller #####")
print("#################################")
print()
print()
uninstall_answer = input("Would you like to uninstall BilirWiFi? [y/N]: ")
print()

if (uninstall_answer.lower() == "y"):
    print('Uninstalling BilirWiFi from your system...')

    os.system('cp ' + os.path.dirname(os.path.realpath(__file__)) + '/reset_device/static_files/wpa_supplicant.conf.default /etc/wpa_supplicant/wpa_supplicant.conf')
    os.system('chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf')
    os.system('mv /etc/wpa_supplicant/wpa_supplicant.conf.original /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null')
    os.system('rm -rf /etc/raspiwifi')
    os.system('rm -rf /usr/lib/raspiwifi')
    os.system('rm -rf /etc/cron.raspiwifi')
    os.system('rm /etc/dnsmasq.conf')
    os.system('mv /etc/dnsmasq.conf.original /etc/dnsmasq.conf 2>/dev/null')
    os.system('rm /etc/hostapd/hostapd.conf')
    os.system('rm /etc/dhcpcd.conf')
    os.system('mv /etc/dhcpcd.conf.original /etc/dhcpcd.conf 2>/dev/null')
    os.system('sed -i \'s/# BilirWiFi Startup//\' /etc/crontab')
    os.system('sed -i \'s/@reboot root run-parts \/etc\/cron.raspiwifi\///\' /etc/crontab')
    
    print()
    print()
    reboot_answer = input('Uninstallation is complete. Would you like to reboot the system now?: ')

    if(reboot_answer.lower() == "y"):
        os.system('reboot')
else:
    print()
    print('No changes made. Exiting unistaller...')