# Contributing

Contributions are wellcome and much appreciated.

## Contributions

### Reporting bugs and feature requests

If you find any issues, please report them by creating a [new issue](https://github.com/equinor/APS-Facies/issues/new).
If there is something missing, or some feature you would like to see, please describe it in a [new issue](https://github.com/equinor/APS-Facies/issues/new), or better yet, submit a pull request.

If you report a bug, please provide a detailed description of the bug, how to reproduce it, which version of the plugin you are using.
If possible, please also include a **minimal** RMS project where the bug happens.
This is only relevant if the plugin is unable to handle some specific data in the RMS project.

### Improving documentation
Do you find the documentation lacking?
Please reach out, create an issue, pull request, or suggest changes.


## Setting up a local developer environment

(these steps are not _strictly_ necessary to run the containers, but will make the development experience better)

**NOTE**: Running APS locally, requires [Aspen RMS&trade;](https://www.aspentech.com/en/products/sse/aspen-rms) to be installed, or available in a container with a valid license.

Install [asdf](https://asdf-vm.com/guide/getting-started.html#_3-install-asdf), if not already installed.

On macOS, you may have to set
```bash
export PYTHON_CONFIGURE_OPTS="--enable-framework"
export SYSTEM_VERSION_COMPAT=1
```
first, in order to make user Python is compiled / installed as a Framework, which is highly recommended to make matplotlib behave.

```bash
asdf install
poetry install  # Installed via asdf
```

```bash
make init
```
### Running locally
Assuming you have containerized RMS
E.g. added all relevant files to a [RedHat Enterprise Linux](https://catalog.redhat.com/software/containers/rhel7/57ea8cee9c624c035f96f3af?architecture=amd64&image=65a671adb31b6e74ca7559c8) or compatible base image, and installed the necessary dependencies.
This also assumes that the tool `roxenv` is available in the container's `PATH`.

```bash
docker compose build --build-arg="RMS_IMAGE=<your containerized RMS image>"
```

Assuming you have an RMS project
```bash
export RMS_PROJECT_PATH=<path to the RMS project you want to work with>

docker-compose up -d
```

#### Running without containers
This assumes that RMS' Python environment is activated

In one terminal execute

```bash
make api-start
```

then open a new terminal / tab and execute

```bash
make web-start
```

#### CodeSpaces

When using CodeSpaces, the API, and front-end are served by NginX as a reverse proxy on port 8888.
To access the "site", go to "ports".
There should be one called "main (8888)".
If not, please create one.
Under "Local Address", hover over the URL for port 8888, and click "Open in browser" (icon of the globe / earth / internet).
This should open a new tab with the app running.

The server should be started, but if you are unable to access the URL above, try executing

```bash
sudo service nginx restart
```

**NOTE**: CodeSpaces might not work as expected because RMS must be available.
