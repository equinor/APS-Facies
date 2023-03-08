see [gitlab wiki](https://git.equinor.com/APS/GUI/wikis/)

(there's a [github mirror](https://github.com/equinor/aps-gui))

## Getting started


```bash
make init
```

### Starting

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
To access the "site", go to "ports". There should be one called "main (8888)". If not, please create one.
Under "Local Address", hover over the URL for port 8888, and click "Open in browser" (icon of the globe / earth / internet).
This should open a new tab with the app running.

The server should be started, but if you are unable to access the URL above, try executing

```bash
sudo service nginx restart
```

### Update truncation rule templates
Change [examples/truncation_settings.dat](examples/truncation_settings.dat) as desired.

Then, run `make generate-truncation-rules` to update.
The GUI will automatically get these rules, when it is built.
