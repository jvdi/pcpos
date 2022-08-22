# PCPOS API - Sadad and Pec

<span style="float: right;">
<img alt="pos terminal" width="40%" src="https://user-images.githubusercontent.com/40993115/177423038-04da4538-c186-4445-86dd-9152adde42cb.png"/>
<img alt="api tkinter gui" width="40%" src="https://user-images.githubusercontent.com/40993115/179966279-a3c424e5-be8a-4406-8876-d49d5b0a3bd1.png"/>
</span>

Getting price from MS-SQL Server and send to Payment terminal

## Requirements: ##
- Rahkar Accounting v6.0.0.0
- Microsoft SQL Server (E.g. Express 2008) -> Enabale TCP/IP access on TCP-Port 1433 with a read access with (user: PCPos_API - pass: toor)
- (<i>If you want to set special user and password for MSSQL -> change it on .env file on install location of PCPosAPI </i>)
- Sadad PCPOS Rest Service (Get from Sadad)
- Pec Windows Service (Get From Pec)

## Install: ##
* <a href="https://github.com/jvdi/rahkar-pcpos/releases/">Get last release setup file from here</a>
* Double click on it and install simply

## Helpfull Details ##
- Config file for set device ip and mssql ip and user pass and etc ... it's on -> root of Installation location -> .env file <-

## Run Source ##
0. Install RahkarPOS v6.0.0.0
1. Install Sadad Rest and Pec Windows Service - MsSql -> Add PCPos_API User to MsSQL
2. For support Windows 7 -> recommend install Python 3.7.4
3. Clone the repository
4. Create a .venv in the project with -> python -m venv .venv
5. Install requirement.txt in your .venv -> pip install -r requirement.txt
6. Add .env file to .gitignore for hide from git
7. Run: git update-index --assume-unchanged .\.env for stop following it from git
8. Edit .env file for your config and network design
9. Run app with : python run.py

## Compile to exe with PyInstaller ##
* Run:
* pyinstaller --name=PCPosAPI  --noconsole --icon=assets\pos.ico run.py
* Then copy folders : db, asset and fil: .env to dist/PCPosAPI and run the app

## Create a Setup file ##
* I'm using InnoSetup for it is
