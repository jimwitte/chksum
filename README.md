# chksum
League of Legends Check Summoner by Name

Overview
--------
This python script will check to see if a summoner name exists. If it exists, script will display the last revision date of the summoner and the date of the last match, and will attempt to calculate when each summoner name might be scheduled to expire.

If you check a single summoner name, script will additionally output a list of the last 100 matches for that name.

Requirements
------------
You will need a developer API key from <http://developer.riotgames.com>. 
This is a special code that allows your script to get data from the LL API.

Python 2.7 and the following packages are needed:

* riotwatcher
* tabulate
* argparse
* python-dateutil

Examples
--------
`chksum.py --help` will list options available.

`# check a single name`
`chksum.py --name summonername`

`# check a file of names, one name per line`
`chksum.py --input names.txt`

`# specify a region. Default is NA1`
`chksum.py --name summonername --region JP1`

Regions include: 
RU,KR,BR1,OC1,JP1,NA1,EUN1,EUW1,TR1,LA1,LA2

Installation
------------
1. Install python 2.7 from <http://python.org>. Special Windows note: during installation, have the installer set the python path. Mac OS X comes with python 2.7.

2. Install required python packages. Easiest way is to use pip, the python package manager. Python for Windows comes with pip. You can install pip on a Mac using this command:

    `sudo easy_install pip`

    Once you have pip installed, use the included list of packages to install everything:

    `pip install -r requirements.txt`

3. On a Mac/Linux, you may want to make the script executable:

    `chmod a+x chksum.py`

To run the script, open the command prompt or terminal on your computer, change directory to your script directory, and run chksum.py. On Mac/Linux. you may have to run ./chksum.py.

API key
-------
Obtain an API key from <http://developer.riotgames.com>. Paste this key into the file "apikey.txt", on a single line.

