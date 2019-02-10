# Python network automation script
## About
This is a side project that I made for school.
I started with limited knowledge of **python** and the programs/modules for **network automation** and ended up with this interactive script.
It uses **Napalm** and **Pyntc** which uses **Netmiko** as an underlying bases to make automatic changes to routers and switches.

## Prerequisites
In order to properly run the script, there are a few things you should install in advance.

* python
* build-essential libssl-dev libffi-dev
* python-pip
* cryptography
* netmiko
* napalm
* pyntc
* gnupg

You can do this with the following commands:

```
apt-get update
apt-get install python -y
apt-get install build-essential libssl-dev libffi-dev -y
apt-get install python-pip -y
pip install cryptography
pip install netmiko
pip install napalm
pip install pyntc
pip install gnupg
```

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

After this you should be able to securely ssh into your device, but we can use the script, **network.py**, to do this for us.
You can run it by entering:

```
python network.py
```

Before running this however, try to make sure you have your napalm Cisco Ios configuration files or your Pyntc configuration files with one command per line as seen from the configure terminal mode, ready somewhere.
You should also have a hosts file ready somewhere with the following JSON structure:

```
[{"host": "IP", "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP", "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP", "username": "USERNAME", "password": "PASSWORD"},
{"host": "IP", "username": "USERNAME", "password": "PASSWORD"},
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
Other stuff is also explained in the script itself or when using it through the interface.

**Napalm config file**
A Napalm config file looks like the running config, but without the following lines:

```

```

Also if these are present delete them aswell, besides these you should copy and paste from an original file to make sure the identation is correct.

```

```

For references you can look at: "sample_napalm_config.cfg".

**Pyntc config file**
This file contains commands as seen from the configure terminal mode seperated as one command per line.
For references you can look at: "sample_pyntc_config.cfg".
