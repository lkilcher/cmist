This package can now be installed with pip:

    pip install git+https://github.com/lkilcher/cmist.git@master#egg=cmist
    
You also need to install either the webdriver for Chrome, or for Firefox (i.e., [here](https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/)). To install these, place the executables somewhere on your path. This can be:

- On Windows: the root folder of the virtualenvironment (i.e., `<venv folder>/`)
- On Mac/Linux: the `<venv folder>/bin/`
- Or elsewhere on the system path.

Once that is done, if you want the most up-to-date info on what is available on the cmist website, you'll want to run the `data/scrape_cmist.py` script. This will scour the cmist website to figure out what data is available, and that information will be available to you in the `cmist.station_index` variable.

Now you should be able to load this library by doing:

    import cmist
    
