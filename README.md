# tornado-upload
Upload server using Tornado web framework

## Install Tornado
```
$ sudo apt install python3-pip python3-setuptools python3-magic
$ python3 -m pip install -U pip
$ python3 -m pip install -U wheel
$ python3 -m pip install tornado filetype
```

## Start web server
```
$ git clone https://github.com/bbinet/tornado-upload
$ cd tornado-upload/tornado
$ python3 upload.py
```

## Upload file using curl
```
$ curl -i -H "Content-Type: image/jpeg" -X POST --data-binary @/tmp/image.jpg "http://localhost:8080/?nodeid=0edd220f399b4e8ebb0e67e59ab1a552&prefix=img_"

$ tree tornado/uploaded/
tornado/uploaded/
└── 0edd220f399b4e8ebb0e67e59ab1a552
    └── 2022
        └── 07
            └── 29
                └── img_20220729_101934.jpg
```
#### With an optional subfolder:
```
$ curl -i -H "Content-Type: image/jpeg" -X POST --data-binary @/tmp/image.jpg "http://localhost:8080/?nodeid=0edd220f399b4e8ebb0e67e59ab1a552&prefix=img_&subfolder=subfolder1"

$ tree tornado/uploaded/
tornado/uploaded/
└── 0edd220f399b4e8ebb0e67e59ab1a552
    └── subfolder1
        └── 2022
            └── 07
                └── 29
                    └── img_20220729_101934.jpg
```

## Docker build

To create the image `bbinet/tornado-upload`, execute the following command in the
`docker-tornado-upload` folder:

    $ docker build -t bbinet/tornado-upload .

You can now push the new image to the public registry:
    
    $ docker push bbinet/tornado-upload


## Docker run

Then, when starting your tornado-upload container, you will want to bind ports `80`
from the tornado-upload container to a host external port.
The tornado-upload container will read its configuration from the `/config/tornado-upload.cfg`
file, so make sure this file is available to docker as a volume.

For example:

    $ docker pull bbinet/tornado-upload

    $ docker run --name tornado-upload \
        -v $(pwd)/data:/app/uploaded \
        -p 80:8080 \
        bbinet/tornado-upload
