# StorjWidget-Exporter

StorjWidget-Exporter starts a python Flask server which pulls information from storj node api for `node`, `satellite` and `payout` metrics and aggregates the data. The endpoint is returning the total `ingress` and `egress` over all nodes, the `estimated daily earnings` and the `current months earnings`, `total space used` and `total space available`, `total number of queried nodes` and `online count of queried nodes`.

Tested with storj node version `1.16.1`

## Support
Feel free to raise issues if you find them and also raise a pull request if you'd like to contribute.

If you wish to support my work, please find my eth/storj wallet address below or scan the qr code:

`0x80E88Ac925B259faedeD7d05c99BfA934952084a`

## Usage

* StorjWidget-Exporter can be installed as a docker container or run as a standalone script
* Make sure you have `-p 127.0.0.1:14002:14002` in your storagenode container docker run command to allow local connections to your node's api

### Installation
#### Docker installation
##### Run latest build from DockerHub

    docker run -p 3123:3123 -e NODES_LIST=192.168.188.59:14002,myNodesIp.com:14002 mb17/storjwidget 
    
    
##### OR build your own
Clone this repo and cd, then

    sudo docker build -t storjwidget .
    docker run -p 3123:3123 -e NODES_LIST=192.168.188.59:14002,myNodesIp.com:14002 storjwidget 


