export PYTHONPATH="$(pwd)/modules"
database="$(pwd)/databases/pass.db"
privkey="$(pwd)/keys/pass_rsa"
pubkey="$(pwd)/keys/pass_rsa.pub"
python3 script/passranoid.py $database $privkey $pubkey $@
