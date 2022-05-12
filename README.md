This package can now be installed with pip:

    pip install git+https://github.com/lkilcher/cmist.git@master#egg=cmist-lib

You also need to install either the webdriver for Chrome, or for Firefox (i.e., [here](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)). To install these, place the executables somewhere on your path. This can be:

- On Windows: the root folder of the virtualenvironment (i.e., `<venv folder>/`)
- On Mac/Linux: the `<venv folder>/bin/`
- Or elsewhere on the system path.

Now you should be able to load this library by doing:

    import cmist
    
From there, you can load data from cmist by doing, for example:

    data = cmist.get_station('COI1203')

The cache
------
This package uses a local cache of files to store data locally after it has been downloaded. The cache will default to be `~/.cmist-lib/cache`, or you can specify it in a `~/.cmist-lib/config` file. That file should be formatted like [this](https://docs.python.org/3/library/configparser.html). Each time you `import cmist` it will tell you what folder is being used as the cache folder. Delete files in that folder to 'clear the cache' if necessary.

Updating the index
----
Every once-in-a-while you will want to update the `station_index` variable by running the `cmist/data/scrape_cmist.py` file. This will scour the cmist website for new datasets, and add them to the `station_index` variable, so that you can quickly see what's on there. I don't think you will be able to use the `get_station` function to retrieve data that is not in the `station_index` variable. So, if you see something on cmist website that you can't get with that function, try running the `scrape_cmist.py` script to update the `cmist/data/coops_stations.json` file (which is loaded in `cmist/base.py` as the `station_index` variable).

Once you run that and generate the new `coops_stations.json` file, you can copy that file to the appropriate place in your venv to have an updated `station_index` file. Or, you can just update that file in the git source that your installing from (and reinstall if necessary).

Common Error Messages
------
`Permission denied: 'geckodriver.log'` --- Change to a folder where you have write permissions (selenium is trying to create a log file and it can't).
