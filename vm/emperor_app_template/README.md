# Uwsgi Emperor managed Restful App Template 

This template provides a simple docker container template for running the [restful_app](https://github.com/evansde77/docker_flask/blob/master/src/docker_flask/restful_app.py) example under the uwsgi emperor and nginx. 

## Rendering the template 

The template can be rendered using the dockerstache CLI installed in the packages virtual environment. 

```bash 
cd <YOUR PATH>/docker_flask
virtualenv venv 
. venv/bin/activate
pip install -r requirements.txt
cd vm
dockerstache -i emperor_app_template -o emperor_app_image -c emperor_app_template/context.json
```

This creates a directory called emperor_app_image that contains the rendered templates. 
To update settings in the templates such as python version, group and user names, edit  [emperor_app_template/context.json](https://github.com/evansde77/docker_flask/blob/master/vm/emperor_app_template/context.json) prior to running dockerstache


## building the image

You can build the docker image with docker build as follows:

```bash
docker build -t evansde77/df_emperor emperor_app_image/
```

This builds the docker image and labels and tags it according to the -t argument. After building the image will appear in the docker images list:

```bash
docker images
REPOSITORY               TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
evansde77/df_emperor   latest              d506a2b65119        11 minutes ago      742.7 MB
```

## Starting a container

To start up a container using the image we just built, use docker run:

```bash
docker run --detach -P  -t -i  evansde77/df_emperor 
```



## Connecting to the app

```bash
# get the port mapping from docker ps 
docker ps 


docker ps 
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS                                                                                                                                                      NAMES
274d99a61780        evansde77/df_emperor       "/sbin/my_init"          2 seconds ago       Up 2 seconds        0.0.0.0:32930->80/tcp, 0.0.0.0:32929->8080/tcp                                                                                                             admiring_babbage


# get the machine ip from docker-machine
docker-machine ls  
NAME      ACTIVE   DRIVER       STATE     URL                         SWARM
default   *        virtualbox   Running   tcp://192.168.99.100:2376   

# hit the app endpoints via the host/port combination
curl 192.168.99.100:32793/docker_flask/restful_app/womp
curl -X POST 192.168.99.100:32793/docker_flask/restful_app/womp
```


## Configuration Updates with the Emperor 

A second app runs on this container under port 8081 that provides a simple REST API to edit a config file. Config changes can be forced to be picked up using the uwsgi emperor by touching the configuration file for the vassal. 
The source code for the configurable app can be seen [here](https://github.com/evansde77/docker_flask/blob/master/src/docker_flask/configured_app.py) and it implements a simple configuration manipulation API:

 * GET - gets a given value from the config file 
 * POST - sets a value in the config file 
 * DELETE - removes a value from the config file 





