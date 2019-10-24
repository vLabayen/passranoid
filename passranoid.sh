DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
config="$DIR/config/passranoid.conf"
modules_path="$DIR/modules"
databases_path="$DIR/databases"
keys_path="$DIR/keys"
script_path="$DIR/script"

export PYTHONPATH=$modules_path
python3 $script_path/passranoid.py $config $databases_path $keys_path $@
