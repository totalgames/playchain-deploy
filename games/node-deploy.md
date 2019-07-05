# Configuring for gambling node

The instruction will be given on the example of the **PlayChain game TotalPoker**. In all places where 'poker' is not mentioned, it is suitable for other games. The differences also apply to the 'tables.info' file.

# Common notes

When you setup PlayChain node you maintain **PlayChain room**. It requires several new objects in blockchain and demends fee. Fee depends on amount of tables in room. If you are not satisfied with the cost offered by the system, you can reduce the number of tables by default by changing the file 'tables.info' (see section *Configuring for advanced users*).

PlayChain node consists of two servers in docker container. These are **blockchain node (BN)** and
**game node (GN)**. GN server is master for container (if it will be stopped it would stop BN server).
Servers use folowing ports:

| *port* |  *default interface* | *description*  |
|---|---|---|
| 8094  |  0.0.0.0 | TCP port for GN. Must be opened for Internet. It is desirable to connect it outside through the balancer or any means of protection against DDoS  |
| 10300  | 0.0.0.0  | P2P port for blockchain network. It should be opened for Internet  |
| 10100  |  127.0.0.1 | API port for blockchain. Available locally only for BN administrating. It is not recommended to forward it to the Internet in unsecurity way  |
|  9100 |  127.0.0.1 | Control port for GN administrating. Available locally. It is not recommended to forward it to the Internet in unsecurity way  |

Container requires disk space for configuration and blockchain data on the host system.
By default the installation script create '~/.local/share/playchain_poker_room' folder for this purpose

# System requirements

Linux OS (tested at Ubuntu 18.04 and Ubuntu 16.04). 
Minimum 2 GB Mem, 30 GB Disk, 2 Core CPU

# Security notes

When you configure PlayChain node first time you become **room owner** with personal name and password (for SSL key).
You should separate this role from **player role** because this account can't play at the own tables in own room.
Thus if you have already registered in PlayChain to play with PLC create new account for new role. 
Make sure that only you have access to configuration folder because the key of the room owner’s account is stored there. Use the new account to withdraw profits from the game of your tables.

# Run from deploying script (recommended)

Deploying script will download self extracting docker image file from the google disk drive
and launch installation script

1. Download deploying script. Enshure that file has executable atribute

`chmode +x node-deploy.sh`

`./node-deploy.sh`

or

`./node-deploy.sh -g poker`

for TotalPoker

_To uncompress and install node you need about 3 GB disk space plus space for docker software_

2. Follow the installation script instructions.

# Configuring for advanced users

You can change or create configuration files before starting the PlayChain node.
There are: 

| *file* | *description*  |
|---|---|
|playchain.config.ini| Config file for BN |
|poker_room.config.ini| Config file for GN |
|tables.info| Room content configuration |

Note that '/var/lib/room' path matches the folder with that files in host system.

For example. To reduce tables amount you should change 'count' field in tables.info
for exact type of table. 
You can also set name and WIF-key for room owner in poker_room.config.ini
You can set pluging or etc. for blockain node in playchain.config.ini
