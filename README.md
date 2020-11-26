# StorjWidget-Exporter

<img src="https://github.com/striker43/storjWidget-exporter/blob/main/widget.png?raw=true" alt="0x187C8C43890fe4C91aFabbC62128D383A90548Dd" hight=340 width=340 align="right"/> 

StorjWidget-Exporter starts a python Flask server which pulls information from storj node api for `node`, `satellite` and `payout` metrics and aggregates the data. The endpoint is returning the total `ingress` and `egress` over all nodes, the `estimated daily earnings` and the `current months earnings`, `total space used` and `total space available`, `total number of queried nodes` and `online count of queried nodes`.

The Exporter's endpoint will be available at http://localhost:3123/bandwidth

Tested with storj node version `1.16.1`

## Support
Feel free to raise issues if you find them and also raise a pull request if you'd like to contribute.

If you wish to support my work, please find my eth/storj wallet address below or scan the qr code:

`0x80E88Ac925B259faedeD7d05c99BfA934952084a`

<img src="wallet_qr.png" alt="0x187C8C43890fe4C91aFabbC62128D383A90548Dd" hight=100 width=100/> 

## Usage

* StorjWidget-Exporter can be installed as a docker container or run as a standalone script
* Make sure you have `-p 127.0.0.1:14002:14002` in your storagenode container docker run command to allow local connections to your node's api

### Installation
#### Docker installation
##### Create docker volume where daily payout data will be stored

    docker volume create --name storjWidgetVolume
    
##### Run latest build from DockerHub for x86-64

    docker run -d --restart always -p 3123:3123 -e NODES_LIST=192.168.188.59:14002,myNodesIp.com:14002 -v storjWidgetVolume:/var/www/storjWidgetVolume mb17/storjwidget 
    
##### OR run latest build from DockerHub for raspberry pi (arm)

    docker run -d --restart always -p 3123:3123 -e NODES_LIST=192.168.188.59:14002,myNodesIp.com:14002 -v storjWidgetVolume:/var/www/storjWidgetVolume mb17/storjwidget:raspberry 
    
###### As an environment parameter `NODES_LIST` you need to add a comma seperated list of your node's ip addresses together with their storj api ports.
    
##### OR build your own
Clone this repo and cd, then

    docker volume create --name storjWidgetVolume
    sudo docker build -t storjwidget .
    docker run -p 3123:3123 -e NODES_LIST=192.168.188.59:14002,myNodesIp.com:14002 -v storjWidgetVolume:/var/www/storjWidgetVolume storjwidget 

## Next Steps:
When your storjWidget-Exporter is up and running and returning stats of your node(s) at http://localhost:3123/bandwidth, you can continue and set up your [storjWidget](https://github.com/striker43/storjWidget).

