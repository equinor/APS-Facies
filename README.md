see [gitlab wiki](https://git.equinor.com/APS/GUI/wikis/)

(there's a [github mirror](https://github.com/equinor/aps-gui))

### Getting started

```bash
make init
```

#### Starting

##### API
```bash
make run-rms.uipy-mock
```
or, from `gui`
```bash
yarn serve:api
```

##### Web
From `gui`
```bash
yarn serve:gui
```


### Update truncation rule templates
Change [examples/truncation_settings.dat](examples/truncation_settings.dat) as desired.

Then, run `make generate-truncation-rules` to update.
The GUI will automatically get these rules, when it is built.
