[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 

# Adaptive Pluri-Gaussian Simulation

The current implementation of Adaptive PluriGaussian Simulation of facies in reservoir modeling is based on code developed by Equinor.
It is implemented as a plugin module to RMS 3D reservoir modeling software from Aspentech and can only be used together with this software.
It is based on the method published by B. Sebacher et.al. ([Journal of Petroleum Science and Engineering, Vol. 158, September 2017, p. 494-508](https://www.sciencedirect.com/science/article/pii/S0920410517300505)) and is extended to handle trends in Gaussian Random Fields and multiple overlay facies.
The implementation is adapted also to the FMU workflow and use of ERT (Ensemble Reservoir Tool) system for orchestration of reservoir simulations and assisted history matching.

## Getting started


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

### Starting

```bash
docker-compose up -d --build
```

##### API
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


## Releasing a new version
1. Create a new branch (e.g. `git switch -c release/v<new version>`)
2. Update the `"version"` field in `gui/package.json` 
3. Add a new entry in `gui/public/CHANGELOG.md` for this particular version
    *  To get a list of all commits since last, execute
       ```bash
       last_version="$(git describe --abbrev=0 --tags)"
       git log "$last_version"..HEAD --pretty=format:'* %s' > commits.log
       ```
    * From these, copy relevant (user-facing) changes into `gui/public/CHANGELOG.md` under appropriate headings

       ```markdown
       ## <version>
       <Optionally some description or extra notes that the user should be aware of>
    
       ### What's new
       * <list of relevant new features, or breaking changes>
    
       ### Deprecations
       * <list of removals of user facing things>
       * <dropping support of RMS versions should go here, and (probably) in the general description>
    
       ### Fixes
       * <list of fixes that are included in this release>
    
       ### Performance
       * <list of changes that are improve the performance of the plugin>
    
       ### Technical debt
       * <list of changes that "pays down" techincal dept>
    
       ### Restructure
       * <list of things that have been moved, refactored, and otherwise changed / improved without affecting the usability or features>
    
       ### Miscellaneous
       * <list of various changes that don't fit neatly anywhere else>
       * <this can include updates to libraries that are used>    
       ```

4. Add the changes in `CHANGELOG.md` and `gui/package.json` to the commit and make new commit
  The commit message can be something like ` "feat: New release ($(make print-APS_VERSION))"`
5. Tag the new commit (preferably also [sign it](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits) by using `-s`)
   ```bash
   git tag -a -s -m '<A small summary of the changes in this release>' "v$(make print-APS_VERSION)"
   ```
6. Push the commit and tag (`git push origin "$(git branch --show-current)"` and `git push --tags`)

   This will trigger the workflow in `.github/workflows/release.yml`, which will make a new release in GitHub, and build a production version of the plugin
