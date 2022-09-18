## رابط ارسال مبلغ به کارتخوان برای نرم افزار حسابداری راهکار
برای مستندات فارسی چگونگی راه اندازی رابط نرم افزاری لطفا به [آموزش راه اندازی PCPOS-API](https://github.com/jvdi/rahkar-pcpos/blob/master/README_FA.md) مراجعه    کنید - پل ارتباطی : [ارسال ایمیل به محمد جاویدی](mailto:m.javidii@yahoo.com)

# Payterminal PCPOS API For Rahkar Accounting

<span style="float: right;">
<img alt="pos terminal" width="40%" src="https://user-images.githubusercontent.com/40993115/177423038-04da4538-c186-4445-86dd-9152adde42cb.png"/>
<img alt="api tkinter gui" width="40%" src="https://user-images.githubusercontent.com/40993115/179966279-a3c424e5-be8a-4406-8876-d49d5b0a3bd1.png"/>
</span>

Getting price from MS-SQL Server and send to Payment terminal

## Requirements

- Rahkar Accounting v6.0.0.0 (or v1.0.0.0 free) -> <a href="http://new.rahkarsoft.com/index.php/post161">Get Rahkar Accounting (Free)</a>
- (Enable checkout by Payment terminal in the Rahkar App) -> in default [first terminal is sadad and second is Pec]
- Microsoft SQL Server (E.g. Express 2008) -> Enabale TCP/IP access on TCP-Port 1433 with a read access with (user: PCPos_API - pass: toor)
- (<i>If you want to set special user and password for MSSQL -> change it on .env file on install location of PCPosAPI </i>)
- Enable PCPOS -> in the Sadad Payment Terminal and Pec Payment terminal
- Enable or Install Microsoft .net framework 3.5 for Sadad Rest Correctly working
- Sadad PCPOS Rest Service (Get from Sadad  or [Sadad Rest](https://drive.google.com/file/d/1jxvKtlQ1WPAsSeMGyPDHTnTAW6Kfu9RH/view?usp=sharing))
- Pec Windows Service (Get From Pec or <a href="https://drive.google.com/file/d/1MdbCYuq2LXHdqVzlAE6NOkQhGMLcd9fB/view?usp=sharing">Get Service Installer</a>)

## Install

- <a href="https://github.com/jvdi/rahkar-pcpos/releases/">Get last release setup file from here</a>

- Double click on it and install simply

## Helpfull Details

- Config file for set device ip and mssql ip and user pass and etc ... it's on -> root of Installation location -> .env file

## Run Source

1. Install RahkarPOS v6.0.0.0 or v1.0.0.0 + [Requirements](https://github.com/jvdi/rahkar-pcpos#requirements)
2. For support Windows 7 -> recommend install Python 3.7.4
3. Clone the repository
4. Create a .venv in the project with -> python -m venv .venv
5. Install requirement.txt in your .venv -> pip install -r requirement.txt
6. Add .env file to .gitignore for hide from git
7. Run: git update-index --assume-unchanged .\.env for stop following it from git
8. Edit .env file for your config and network design
9. Run app with : python run.py

## Compile to exe with PyInstaller

- Run:

- pyinstaller --name=PCPosAPI  --noconsole --icon=assets\pos.ico run.py
- Then copy folders : db, asset and file: .env to dist/PCPosAPI and run the app

## Create a Setup file

- I'm using InnoSetup for it is

## For Contribute

* At first we appreciate about your contribution

- Use issues or Email : m.javidii@yahoo.com for your suggestion or etc
- Or Create a pull request
