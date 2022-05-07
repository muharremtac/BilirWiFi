import os
import sys
import setup_lib


if os.getuid():
    sys.exit('You need root access to install!')

def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

mac_address = getMAC('wlan0').replace(":", "")
entered_ssid = "bilir" + mac_address

os.system('clear')
print()
print()
print("###################################")
print("##### BilirWiFi Intial Setup  #####")
print("###################################")
print()
print()
wpa_enabled_choice = input("Would you like WPA encryption enabled on the hotspot \nwhile in Configuration Mode? [y/N]:")
print()
wpa_entered_key = input("What password would you like to for WPA hotspot \naccess (if enabled above, \nMust be at least 8 characters) [default: NO PASSWORD]:")
print()
auto_config_choice = input("Would you like to enable \nauto-reconfiguration mode [y/N]?: ")
print()
auto_config_delay = input("How long of a delay would you like without an active connection \nbefore auto-reconfiguration triggers (seconds)? [default: 300]: ")
print()
server_port_choice = input("Which port would you like to use for the Configuration Page? [default: 80]: ")
print()
ssl_enabled_choice = input("Would you like to enable SSL during configuration mode \n(NOTICE: you will get a certificate ID error \nwhen connecting, but traffic will be encrypted) [y/N]?: ")
os.system('clear')
print()
print()
install_ans = input("Are you ready to commit changes to the system? [y/N]: ")

if(install_ans.lower() == 'y'):
	setup_lib.install_prereqs()
	setup_lib.copy_configs(wpa_enabled_choice)
	setup_lib.update_main_config_file(entered_ssid, auto_config_choice, auto_config_delay, ssl_enabled_choice, server_port_choice, wpa_enabled_choice, wpa_entered_key)
else:
	print()
	print()
	print("===================================================")
	print("---------------------------------------------------")
	print()
	print("BilirWiFi installation cancelled. Nothing changed...")
	print()
	print("---------------------------------------------------")
	print("===================================================")
	print()
	print()
	sys.exit()

os.system('clear')
print()
print()
print("#####################################")
print("##### BilirWiFi Setup Complete  #####")
print("#####################################")
print()
print()
print("Initial setup is complete. A reboot is required to start in WiFi configuration mode...")
reboot_ans = input("Would you like to do that now? [y/N]: ")

if reboot_ans.lower() == 'y':
	os.system('reboot')
