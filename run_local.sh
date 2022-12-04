export ENV=local
export NODES_LIST=192.168.188.87:14006,192.168.188.87:14017
python -m flask run --port 3123 --host=0.0.0.0
