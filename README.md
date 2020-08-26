see [wiki](https://git.statoil.no/APS/GUI/wikis/)

### Getting started

```bash
make init
```

### Update truncation rule templates
Change [examples/truncation_settings.dat](examples/truncation_settings.dat) as desired.

Then, run `make generate-truncation-rules` to update.
The GUI will automatically get these rules, when it is built.
