# Python network automation script
## About
This is a side project that I made to expand my knowledge for the amount of about 20 hours.
I started with limited knowledge of **python** and the programs/modules for **network automation** and ended up with this interactive script.
It uses **Napalm** and **Pyntc** which uses **Netmiko** as an underlying bases to make automatic changes to routers and swithces.

## Prerequisites
In order to properly run the script, there are a few things you should install in advance.

* Python
* build-essential libssl-dev libffi-dev
* python-pip
* cryptography
* netmiko
* napalm
* pyntc
* gnupg

After you have installed the necessary components, you should be able to run the script.
Off course in order to make a connection to Cisco Ios devices you first need to enable ssh on them and activate the scp server.
You can use the commands below as an example:

```
enable
configure terminal
enable secret PASSWORD
username USER secret PASSWORD
username USER privilege 15
ip domain-name example.com
crypto key generate rsa
ip ssh time-out 60
ip ssh authentication-retries 2
ip name-server 8.8.8.8
ip scp server enable
line vty 0 4
logging synchronous
login local
transport input all
exit
interface vlan NUMBER
ip address IP SUBNETMASK
no shutdown
exit
```

After this you should be able to securily ssh into your device, but we can use the script, **network.py**, to do this for us.
You can run it by entering:

```
python network.py
```

Before running this however, try to make sure you have your napalm Cisco Ios configuration files or your pyntc configation files with one command per line as seen from the configure terminal mode, ready somewhere.
You should also have a hosts file ready somewhere with the following JSON structure:

```
[{"host": "IP, "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP, "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP, "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP, "username": "USERNAME", "password": "PASSWORD"},
...]
```

This file must be encrypted with gnupg. You can encrypt this with the following command, afterwards delete the original!
You will be prompted for a passphrase. The network.py script will do the same for decrypting the file. The contents of the passwords are never shown or stored anywhere else!

```
 gpg -c file.name
```

Decrypting this manually trough the CLI can be done as follows.

```
gpg -o file.txt -d file.txt.gpg
```

Now you should have enough information to make use of this script.
Other stuff is also explained in the script itself or when using trough the interface.
