# lv-media
This repository is a submodule of the [Lecture-Viewer](https://github.com/ripples/lecture-viewer) system developed by the [ripples team at UMass Amherst](https://github.com/ripples). 

The purpose of lv-media is to act as the intermediary between the host filesystem and the other services in the [Lecture-Viewer](https://github.com/ripples/lecture-viewer) microservice stack.
It also acts as a schedule based task runner.


### How to run
We only support running lv-media through docker and docker-compose. Follow the instructions in the [parent](https://github.com/ripples/lecture-viewer) repository readme


### Core Technologies used
* [Docker](http://docker.io/)
* [Flask](http://flask.pocoo.org/)
* [APScheduler](https://pypi.python.org/pypi/APScheduler)
