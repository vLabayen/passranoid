export PYTHONPATH="/media/windows/proyects/passranoid/v9/modules"
database="/media/windows/proyects/passranoid/v9/databases/pass.db"
privkey="/media/windows/proyects/passranoid/v9/keys/pass_rsa"
pubkey="/media/windows/proyects/passranoid/v9/keys/pass_rsa.pub"
python3 script/passranoid.py $database $privkey $pubkey $@
