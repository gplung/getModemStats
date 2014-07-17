getModemStats
=============

# Description 

The Script, getZyxelQ100ModemStats.py, scrapes the web interface of a ZyXEL
Q100 DSL modem and outputs some statistics in a format that Cacti can use. With
the right parameters, it will also display the output in a human readable
format.

The script was written based off of firmware QZQ002-4.2.001.1-Q100. Other 
firmware versions may or may not work.

The script also assumes you require a username and password to enter the Web
UI.

# Usage

`python getZyxelQ100ModemStats.py -h`
Displays help

`python getZyxelQ100ModemStats.py -H 192.168.0.1 -u admin -p password`
Displays stats from host 192.168.0.1 in a format suitable for Cacti.

`python getZyxelQ100ModemStats.py -H 192.168.0.1 -u admin -p password -r`
Displays stats from host 192.168.0.1 in a human readable format.
