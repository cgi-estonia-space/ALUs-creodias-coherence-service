# Hello World Processor

## How to use this repository
This repository contains sample processor docker file, docker-compose which uses the processor image and sample k8s
pod manifest which uses processor in a preferred way. 
### Quick start
```commandline
$cd example
$ls
data  docker-compose.yaml  Dockerfile  k8s  processor.py  requirements.txt
$docker-compose up --remove-orphans --force-recreate --build
Building hello-world-processor

(...)
(skip...)
(...)

hello-world-processor_1  | result.data
example_hello-world-processor_1 exited with code 0
```

This example was tested with docker:
```commandline
docker version
Client: Docker Engine - Community
 Version:           20.10.14
 API version:       1.41
 Go version:        go1.16.15
 Git commit:        a224086
 Built:             Thu Mar 24 01:48:02 2022
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.14
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.16.15
  Git commit:       87a90dc
  Built:            Thu Mar 24 01:45:53 2022
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.5.11
  GitCommit:        3df54a852345ae127d1fa3092b95168e4a88e2f8
 runc:
  Version:          1.0.3
  GitCommit:        v1.0.3-0-gf46b6ba
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

```
and docker compose:
```commandline
docker-compose --version
docker-compose version 1.27.4, build 40524192
```


### Processor dockerfile
This is a very simple dockerfile which creates an images with 
a very simple python app. This python app simulates a processor.
Take a look at sample's processor help message:

```commandline
/example$ python processor.py --help
Usage: processor.py [OPTIONS]

Options:
  --input PATH                    [required]
  --output PATH                   [required]
  --config-file PATH
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

```
All of the places where the processor is writing/reading from have to be configurable. 
**Writing anywhere else than mounted volume will be forbidden.** This means that the place where 
processor can write to must be passed by the command line options. This includes temporary directories, processing results, 
partial results, etc...

As you can see:
* input path - this is the path where the product is. It has to be configurable.
* output path - this is the directory name where the processor has to put its results
* config path - optional, the system provides a method to pass a config file to a processor


### Docker compose
Docker compose serves as an example of processor usage.
Docker compose has a volume attachment. This is a folder with an input data.  Data tree looks like:

```commandline
example$ tree data/
data/
└── input_file_location
    └── example.data

1 directory, 1 file

```

There is also a command for the hello-world-processor which starts the processing.
Note that input file location and output file location is passed as a command line argument.

To run docker file and build a processor image type 
```commandline
example$ docker-compose up --force-recreate --build
```

Processor will be built and started. It will write logs to stdout or stderr.
It will create a processing result in the output path:

```commandline
example$ tree data
data
├── input_file_location
│   └── example.data
└── output
    └── my_new_product_name
        └── result.data

3 directories, 2 files

```
There is a new directory called "output" and a processing result in it.

### K8s manifest file
Manifest file is a simple Pod and VolumeClaim definition. This is using the same processor image
as docker file - called "registry.cloudferro.com/processing/processors/hello-world".
Volume is used to provide input data and collect output data. The idea is the same as in case of docker-compose.
Resources definition is required therefore processor specification must have requests and limits (https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-resource-requests-and-limits). 
Resources:
```commandline
resources:
  limits:
    cpu: 1
    memory: 1Gi
  requests:
    cpu: 1
    memory: 1Gi
```


### Running hello-world-processor

Hello world processor is a very simple python script which writes a sample output to the directory from the command line options.

```commandline
python3.10 -m venv venv310
source venv310/bin/activate
pip install -r requirements.txt
```

### Internet connectivity
Processor internet connectivity is not guaranteed and it should work offline.
Auxiliary files (if needed) should be passed separately.
