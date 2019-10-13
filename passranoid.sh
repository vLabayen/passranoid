export PYTHONPATH="/<path>/passranoid/modules"
database="/<path>/passranoid/databases/pass.db"
privkey="/<path>/passranoid/keys/pass_rsa"
pubkey="/<path>/passranoid/keys/pass_rsa.pub"
python3 script/passranoid.py $database $privkey $pubkey $@
