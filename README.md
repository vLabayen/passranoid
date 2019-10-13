# passranoid
Password manager with console interface  
Configure the database, privkey and pubkey in the bash by the bash script  
Usage through the bash script  
&nbsp;  
&nbsp;  
`positional arguments:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`command`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`command to execute. Available options are:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- create : create a new database`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- select : select a password by a service`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- insert : insert a password for a service`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- list : list all passwords and services`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- generate : generate a new password`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`- session : open an interactive session`  

`optional arguments:`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-h, --help`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`show this help message and exit`  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`-v, --verbose`&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`show info and progress`  

`create usage   : passranoid.sh create [dbfile]`  
`select usage   : passranoid.sh select [service]`  
`insert usage   : passranoid.sh insert [service] [passwd]`  
`list usage     : passranoid.sh list`  
`generate usage : passranoid.sh generate [length] [alphabet]`  
`session usage  : passranoid.sh session`  
&nbsp;  
&nbsp;  
Termux installation:  
`pkg install git`  
`git clone https://github.com/vLabayen/passranoid`  
`cd passranoid`  
`bash install/termux.sh`  
