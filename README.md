see [wiki](https://git.statoil.no/APS/GUI/wikis/)

### Getting started

```bash
make init
```

#### Starting

##### API
```bash
make run-rms.uipy-mock
```
or, from `src/gui`
```bash
yarn serve:api
```

##### Web
From `src/gui`
```bash
yarn serve:gui
```


### Update truncation rule templates
Change [examples/truncation_settings.dat](examples/truncation_settings.dat) as desired.

Then, run `make generate-truncation-rules` to update.
The GUI will automatically get these rules, when it is built.
