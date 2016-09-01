# cwr-status

Cloud Weather Report status page.

## How to run localy

Clone the repostory

Install the dependencies in a virtual env with:

    make install_deps

Edit the `cwrstatus/testing.cfg` configuration file.
You will need to specify the path with your s3cfg file the bucket name
and the directory your files are placed.

Start the server by:

    make serve

You should see something like:

    Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    Restarting with stat

If you want to run with the production config file,
edit `cwrstatus/production.cfg` and run with:

    INI=production make serve
