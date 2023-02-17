rm ~/.docker/config.json

sudo docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v8,linux/arm/v7,linux/arm/v6,linux/ppc64le,linux/s390x,linux/386 --push -t mb17/storjwidget -t mb17/storjwidget:0.1.2.5 .

