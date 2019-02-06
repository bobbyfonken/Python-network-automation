## Necessary imports ##
import json
import os
import gnupg
from datetime import datetime
import getpass
from pyntc import ntc_device as NTC
from napalm import get_network_driver
from multiprocessing.dummy import Pool as ThreadPool

## Variables ##
gpg = gnupg.GPG()


## Definitions ##
# Print the menu
def print_menu():
	# Print menu
	print("----------------------------------------------------------------")
	print("|                           MENU                               |")
	print("----------------------------------------------------------------")
	print("| 1: Send commands to device(s) with Pyntc                     |")
	print("| 2: Send config with Napalm                                   |")
	print("| 3: Backup running config with Pyntc                          |")
	print("----------------------------------------------------------------")
	print("\n")


# Checks the path given for the end backslash
def path_backslash(path):
	if path[-1:] != "/":
		path += "/"

	# Return the path with backslash at the end
	return path


# Send commands to multiple devices with threads and one config file from menu option 1
def pyntc_multiple(device, user, passwordp, config_file):
	# Establish the connection to the device
	print("Establishing connection to: " + str(device) + "...")
	Cisco = NTC(host=device, username=user, password=passwordp, device_type='cisco_ios_ssh')
	Cisco.open()
	print("Connection established to: " + str(device))

	# Put the commands in a dictionary we can send with pyntc after we remove white spaces
	commands = []
	with open(config_file) as f:
		for command in f:
			commands.append(command.strip())

	print("Sending commands to: " + str(device))
	Cisco.config_list(commands)
	Cisco.close()
	print("Commands sent to: " + str(device))


# Takes backup with Pyntc from multiple threads from menu option 3
def pyntc_backup(device, user, passwordp, backup_path):
	print("Establishing connection to: " + str(device) + "...")
	Cisco = NTC(host=device, username=user, password=passwordp, device_type='cisco_ios_ssh')
	Cisco.open()
	print("Connection established to:  " + str(device))

	# Backup the runnin config to file based on host and date
	dateStr = datetime.now()
	Filename = str(device).replace(".","-") + "--" + str(dateStr.strftime('%Y-%m-%d')) + ".cfg"
	ios_run = Cisco.backup_running_config(str(backup_path) + Filename)
	Cisco.close()

	print(str(device) + ": Config backed up to -> " + str(backup_path) + str(Filename))


# This will compare the config per device from menu option 2
def napalm_config_file(device, user, passwordn, config_file):
	# Setting up connection
	print("Establishing connection to: " + str(device) + "...")
	driver = get_network_driver('ios')
	Cisco = driver(device, user, passwordn)
	Cisco.open()
	print("Connection established to:  " + str(device))
	print("Checking for changes...")
	# Check for difference in runnnig and config file configuration
	Cisco.load_merge_candidate(filename=config_file)
	diffs = Cisco.compare_config()

	# Do different things based on differences
	if len(diffs) > 0:
		print(diffs)
		print("\n")
		while True:
			napalm_commit = raw_input("Commit changes? (yes/no): ")
			if napalm_commit == "yes" or napalm_commit == "no":
				break
			else:
				print("Please enter either \"yes\" or \"no\".")

		if napalm_commit == "no":
			print("Not commiting, skip: " + str(device))
			Cisco.discard_config()
		else:
			print("Commiting changes to: " + str(device))
			print("Please wait, this can take a while depending on amount of changes...")
			Cisco.commit_config()

	else:
		print("No changes detected, skipping: " + str(device))
		Cisco.discard_config()


# Processes a line in a file with format: "IP:username:password"
def process_json_pyntc(info):
	values = json.loads(info)

	if len(values) > 4:
		print("Invalid format, skipping!")
	else:
		pyntc_backup(values['host'], values['username'], values['password'], values['backup_path'])


# Process the multiple threads for menu option one with multiple devices and one config
def process_json_pyntc_multiple(info):
	values = json.loads(info)

	if len(values) > 4:
		print("Invalid format, skipping!")
	else:
		pyntc_multiple(values['host'], values['username'], values['password'], values['config_file'])


#def process_json_napalm(info):
#	values = json.loads(info)
#
#	if len(values) > 4:
#		print("Invalid format, skipping!")
#	else:
#		napalm_multiple_config_auto_commit(values['host'], values['username'], values['password'], values['config_file'])


# Uses Pyntc to send commands to a device
def menu_option_1():
	# Get necessary information
	print("Menu option 1")
	print("-------------")
	print("Please enter the following information:")

	while True:
		pyntcWithList = raw_input("Use JSON gpg encrypted file with hosts, usernames and passwords, along with mutual config file (yes/no): ")
		if pyntcWithList == "yes" or pyntcWithList == "no":
			break
		else:
			print("Please enter either \"yes\" or \"no\".")

	if pyntcWithList == "no":
		pyntcHosts = raw_input("Host(s) device IP address (seperated by \",\"): ")

		# Split user input in list
		pyntcHost = pyntcHosts.split(",")

		# Use the given info to make the connection to the device
		for device in pyntcHost:
			# Get user and password of device
			pyntcUser = raw_input(str(device) + "'s username: ")
			pyntcPass = getpass.getpass(str(pyntcUser) + "'s password: ")
			print("\n")

			print("Establishing connection to: " + str(device) + "...")
			Cisco = NTC(host=device, username=pyntcUser, password=pyntcPass, device_type='cisco_ios_ssh')
			Cisco.open()
			print("Connection established")
			print("\n")

			# Ask the user for commands as long as they don't enter: "quit()"
			print("Commands to send (type \"quit()\" to stop command input):")
			print("Either enter commands one by one or paste list that was divided one command per line and press enter followed by \"quit()\".")
			commands = []
			while True:
				command = raw_input("Command(s): ")

				# Leave the while loop if user ends it
				if command == "quit()":
					break
				else:
					commands.append(command)

			if len(commands) != 0:
				print("\n")
				print("Sending commands to device: " + str(pyntcUser) + "@" + str(device))

				# Send commands and close the connection
				Cisco.config_list(commands)
				Cisco.close()
				print("Commands sent.")
				print("Commands have been send to all hosts.")
			else:
				print("No commands to send.")
	else:
		print("Please make sure the hosts file has the following structure:")
		print("[{\"host\": \"HOST_IP\", \"username\": \"USERNAME\", \"password\": \"PASSWORD\"}]")
		print("Also make sure the config file has one command per line as seen from the configuration mode.")
		print("\n")

		while True:
			pyntcFilePath = raw_input("Path to hosts file: ")
			if os.path.exists(pyntcFilePath):
				break
			else:
				print("Please enter valid path to the hosts file!")

		while True:
			pyntcConfigPath = raw_input("Path to config file: ")
			if os.path.exists(pyntcConfigPath):
				break
			else:
				print("Please enter valid path to the config file!")

		gpgPass = getpass.getpass("passphrase: ")
		print("\n")
		# Read the file and put each line with path under a new index in a dictionary
		# Then we multithread the connections to the devices
		info = []
		with open(pyntcFilePath, 'rb') as f:
			# decrypt the file, then get value by turning into string, then loading it as JSON
			d = json.loads(str(gpg.decrypt_file(f, passphrase=gpgPass)))
			for value in d:
				# Add to every value the backup path
				value["config_file"] = pyntcConfigPath
				# Then put every value in a dict to then pass with multithreading to process the json
				info.append(json.dumps(value))

		# Open max 50 connections at a time
		threads = ThreadPool(50)
		threads.map(process_json_pyntc_multiple, info)


def menu_option_2():
	# Get necessary information
	print("Menu option 2")
	print("-------------")
	print("Make sure the config file has exact look (indentation) of a normal running config.")
	print("Please enter the following information:")

	napalmHosts = raw_input("Host(s) device IP address (seperated by \",\"): ")

	# Split user input in list
	napalmHost = napalmHosts.split(",")

	# Use the given info to make the connection to the device
	for device in napalmHost:
		# Get user and password of device
		napalmUser = raw_input(str(device) + "'s username: ")
		napalmPass = getpass.getpass(str(napalmUser) + "'s password: ")

		while True:
			napalmConfig = raw_input("Path to config file: ")
			if os.path.exists(napalmConfig):
				break
			print("Please enter valid path!")

		print("\n")

		napalm_config_file(device, napalmUser, napalmPass, napalmConfig)

	print("All devices have received their config.")


def menu_option_3():
	# Get necessary information
	print("Menu option 3")
	print("-------------")
	print("Please enter the following information:")

	while True:
		pyntcPath = raw_input("Path to backup directory (\"./\" for current, end with \"/\"): ")
		if os.path.isdir(pyntcPath):
			pyntcPath = path_backslash(pyntcPath)
			break
		print("Please enter valid path!")

	while True:
		pyntcWithList = raw_input("Use JSON gpg encrypted file with hosts, usernames and passwords (yes/no): ")
		if pyntcWithList == "yes" or pyntcWithList == "no":
			break
		else:
			print("Please enter either \"yes\" or \"no\".")

	if pyntcWithList == "no":
		pyntcHosts = raw_input("Host(s) device IP address (seperated by \",\"): ")

		# Split user input in list
		pyntcHost = pyntcHosts.split(",")

		for device in pyntcHost:
			# Get user and password of device
			pyntcUser = raw_input(str(device) + "'s username: ")
			pyntcPass = getpass.getpass(str(pyntcUser) + "'s password: ")
			pyntc_backup(device, pyntcUser, pyntcPass, pyntcPath)
	else:
		print("Please make sure the file has the following structure:")
		print("[{\"host\": \"HOST_IP\", \"username\": \"USERNAME\", \"password\": \"PASSWORD\"}]")
		while True:
			pyntcFilePath = raw_input("Path to hosts file: ")
			if os.path.exists(pyntcFilePath):
				break
			else:
				print("Please enter valid path to the hosts file!")

		gpgPass = getpass.getpass("passphrase: ")
		print("\n")
		# Read the file and put each line with path under a new index in a dictionary
		# Then we multithread the connections to the devices
		info = []
		with open(pyntcFilePath, 'rb') as f:
			# decrypt the file, then get value by turning into string, then loading it as JSON
			d = json.loads(str(gpg.decrypt_file(f, passphrase=gpgPass)))
			for value in d:
				# Add to every value the backup path
				value["backup_path"] = pyntcPath
				# Then put every value in a dict to then pass with multithreading to process_json
				info.append(json.dumps(value))

		# Open max 50 connections at a time
		threads = ThreadPool(50)
		threads.map(process_json_pyntc, info)

	print("\n")
	print("Every device backup is located in: " + str(pyntcPath))


## Information ##
print("----------------------------------------------------------------------------------------------------")
print("Welcome to the interactive Python script used for network automation with Netmiko, Napalm and Pyntc.")
print("----------------------------------------------------------------------------------------------------")
print("Copyright: Bobby Fonken - 2018")
print("------------------------------")
print("You can quit by entering \"quit()\", \"q()\" or by pressing \"ctrl + c\".")
print("To see the menu again, type: \"menu()\".")
print("NOTE:")
print("Make sure your Cisco device is reachable via SSH and make sure you have runned the following command:")
print("\"ip scp server enable\"")
print("\n")

## Main run ##
if __name__ == '__main__':
	try:
		while True:
			# Print the menu
			print_menu()

			# Ask user for their input
			userText = raw_input("What would you like to do: ")
			print("\n")

			# Leave the while loop if user ends it
			if userText == "quit()" or userText == "q()":
				break

			if userText == "q" or userText == "exit" or userText == "quit":
				print("If you wish to exit the program, enter: \"quit()\" or \"q()\".")
			elif userText == "menu()":
				print_menu()
			elif userText == "1" or userText == "2" or userText == "3" or userText == "4":
				## Execute commands from the menu here ##
				if userText == "1":
					menu_option_1()
				if userText == "2":
					menu_option_2()
				if userText == "3":
					menu_option_3()
			else:
				print("Please enter an option from the menu!")


			print("\n")

		print("\n")
		print("Program ended")

	except KeyboardInterrupt:
		print("\n")
		print ("Program ended")
