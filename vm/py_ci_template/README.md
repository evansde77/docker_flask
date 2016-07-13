# Python CI environment container

This template provides a docker container that sets up and installs several python CI tools such as tox, devpi etc and a suite of testing tools. It installs several pythons via pyenv and generates virtualenvs for each python with the appropriate requirements installed.

## Rendering the template

The template can be rendered using the dockerstache CLI installed in the packages virtual environment.

```bash
cd <YOUR PATH>/docker_flask
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
cd vm
dockerstache -i py_ci_template -o py_ci_image -c py_ci_template/context.json

```

This creates a directory called py_ci_image that contains the rendered templates.
To update settings in the templates such as python versions, requirements, group and user names, edit  [py_ci_template/context.json](https://github.com/evansde77/docker_flask/blob/master/vm/py_ci_template/context.json) prior to running dockerstache


## building the image

You can build the docker image with docker build as follows:

```bash
docker build -t evansde77/py_ci_image py_ci_image
```

This builds the docker image and labels and tags it according to the -t argument. After building the image will appear in the docker images list:

```bash
docker images
REPOSITORY               TAG                 IMAGE ID            CREATED             VIRTUAL SIZE
evansde77/py_ci_image   latest              d506a2b65119        11 minutes ago      742.7 MB
```

## Starting a container

To start up a container using the image we just built, use docker run:

```bash
docker run --detach -P  -t -i  evansde77/py_ci_image
```





