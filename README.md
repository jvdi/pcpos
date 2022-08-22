# PCPOS API - Special API for Special Work

<span style="float: right;">
<img alt="pos terminal" width="40%" src="https://user-images.githubusercontent.com/40993115/177423038-04da4538-c186-4445-86dd-9152adde42cb.png"/>
<img alt="api tkinter gui" width="40%" src="https://user-images.githubusercontent.com/40993115/179966279-a3c424e5-be8a-4406-8876-d49d5b0a3bd1.png"/>
</span>

Getting price from MS-SQL Server and send to Payment terminal

## Requirements: ##
- Rahkar Accounting v6.0.0
- Microsoft SQL Server (E.g. Express 2008) -> Enabale TCP/IP access on TCP-Port 1433 with a read access with (user: PCPos_API - pass: toor)
- (<i>If you want to set special user and password for MSSQL -> change it on .env file on install location of PCPosAPI </i>)
- Sadad PCPOS Rest Service (Get from Sadad)

## Install: ##
* <a href="https://github.com/jvdi/rahkar-pcpos/releases/">Get last release setup file from here</a>
* Double click on it and install simply

## Helpfull Details ##
- Config file for set device ip and mssql ip and user pass and etc ... it's on -> root of Installation location -> .env file <-
