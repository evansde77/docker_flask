# Restful App Template 

This template provides a simple docker container template for running the (https://github.com/evansde77/docker_flask/blob/master/src/docker_flask/restful_app.py)[restful_app] example under uwsgi and nginx. 

## Rendering the template 

The template can be rendered using the dockerstache CLI installed in the packages virtual environment. 

```bash 
cd <YOUR PATH>/docker_flask
virtualenv venv 
. venv/bin/activate
pip install -r requirements.txt
cd vm
dockerstache -i restful_app_template -o restful_app_image -c restful_app_template/context.json
```

This creates a directory called restful_app_image that contains the rendered templates. 
To update settings in the templates such as python version, group and user names, edit (https://github.com/evansde77/docker_flask/blob/master/vm/restful_app_template/context.json)[restful_app_template/context.json] prior to running dockerstache


## building the image

You can build the docker image with docker build as follows:

```bash
cd restful_app_image
docker build -t docker_flask/local:v1 .
```

This builds the docker image and labels and tags it according to the -t argument. After building the image will appear in the docker images list:

```bash
docker images
REPOSITORY               TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
docker_flask/local   v1                  d506a2b65119        11 minutes ago      742.7 MB
```

## Starting a container

To start up a container using the image we just built, use docker run:

```bash
docker run -P -t -i docker_flask/local:v1 /sbin/my_init
```


To run the service interactively so that you can start the apps and poke around in the running container:

```bash
docker run -P -t -i docker_flask/local:v1 /bin/bash
root@5eb519eaf9ca:~# 
root@5eb519eaf9ca:~# 
root@5eb519eaf9ca:~# /sbin/my_init & 
[1] 10
root@5eb519eaf9ca:~# *** Running /etc/my_init.d/00_regen_ssh_host_keys.sh...
*** Running /etc/rc.local...
*** Booting runit daemon...
*** Runit started as PID 13
Dec 11 17:27:57 5eb519eaf9ca syslog-ng[23]: syslog-ng starting up; version='3.5.3'
root@5eb519eaf9ca:~# 
```


## Connecting to the app

```bash
# get the port mapping from docker ps 
docker ps 
CONTAINER ID        IMAGE                       COMMAND                  CREATED              STATUS              PORTS                                             NAMES
5eb519eaf9ca        docker_flask/evansde77:v2   "/bin/bash"              About a minute ago   Up About a minute   0.0.0.0:32794->80/tcp, 0.0.0.0:32793->8080/tcp    furious_ritchie

# get the machine ip from docker-machine
docker-machine ls 
NAME      ACTIVE   DRIVER       STATE     URL                         SWARM
default   *        virtualbox   Running   tcp://192.168.99.100:2376   

# hit the app endpoints via the host/port combination
curl 192.168.99.100:32793/docker_flask/restful_app/womp
curl -X POST 192.168.99.100:32793/docker_flask/restful_app/womp
```
