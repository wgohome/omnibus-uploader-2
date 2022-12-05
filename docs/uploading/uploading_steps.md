# Uploading data

## Check configurations

Before uploading, check if your database and data source configurations ([described here](/uploading/setup/#configurations)) are as desired.

- DATABASE_URL
- DATABASE_NAME
- DATA_DIR

Also ensure that the python environment has been activated, [as described here](/uploading/setup/#uploader-scripts).


## Default upload script

The standard uploader script is found at `uploader/scripts/main.py`. Run this script to run the upload.

``` py
cd ==<root directory of this repository>==
export PYTHONPATH=.
python uploader/scripts/main.py
```

If you would like to run it as a background process:

```
nohup python uploader/scripts/main.py > upload.out &
```

If you would like to have a customised solution, create another python file in the `/uploader/scripts/` dir and you can run it on its own. Alternatively, modify the `/uploader/scripts/main.py` file to suit your needs.
