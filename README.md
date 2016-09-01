# cwr-status
Cloud Weather Report status page. 

## How to use localy

Clone the repostory

Install the dependencies in a virtual env with:

    make install_deps
    source ./venv/bin/activate

Add the project to your python path

    export PYTHONPATH=`pwd`

Select the configuration file you want to use, either 'tesing' or 'production'

    export INI=testing

Edit the configuration file. In this case the cwrstatus/testing.cfg. 
You will need to specify the path with your s3cfg file the bucket name and the directory your files are placed.

Start the server by:

    cd cwrstatus
    python main.py

You should see something like:

    Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    Restarting with stat


