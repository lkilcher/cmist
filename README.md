Getting this package running

    conda env create -f environment.yml
    
You also need to install either the webdriver for Chrome, or for Firefox (i.e., [here](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)). To install these, place the executables somewhere on your path.

You'll want to place this folder on your python path somewhere.

Once that is done, if you want the most up-to-date info on what is available on the cmist website, you'll want to run the `data/scrape_cmist.py` script. This will scour the cmist website to figure out what data is available, and that information will be available to you in the `cmist.station_index` variable.

Now you should be able to load this library by doing:

    import cmist
    
