
Spynepi
=======

This is a caching PyPI implementation that can be used as a standalone PyPI
server as well as a PyPI cache. It can be used to freeze a deployment, or as
a precaution to PyPI or local network going down.

As the name suggests, it is using `spyne http://pypi.python.org/pypi/spyne`

Requirements
------------
Spynepi uses some subsystems of Spyne which require additional dependencies
and Twisted as wsgi server:

* Spyne: http://github.com/arskom/spyne
* Twisted: http://twistedmatrix.com/
* SQLAlchemy: http://sqlalchemy.org
* Werkzeug: http://werkzeug.pocoo.org/

Installation
------------

You can get spynepi via pypi: ::

    easy_install spynepi

or you can clone from github: ::

    git clone git://github.com/arskom/spynepi.git

or get the source distribution from one of the download sites and unpack it.

To install from source distribution, you should run its setup script as
usual: ::

    python setup.py install

And if you want to make any changes to the spynepi code, it's more comfortable
to use: ::

    python setup.py develop

Using Spynepi
-------------

You can start spynepi with: :: 

    $ spynepi_daemon

You can upload packages with: ::  

    $ python setup.py register -r local sdist upload -r spynepi

And you can download packages with: ::  
    
    $ easy_install --user -U -i http://localhost:7789 package


Configuration
-------------

Config file for spynepi can be found inside ``spynepi/const/__init__.py`` 

* DB_CONNECTION_STRING : Default database for spynepi is sqlite. If you wish
  to use a different database you can change this line. It must be an
  sqlalchemy compatiable database connection string
  
  For detatils please read http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html  

* FILES_PATH : Path which packages will be stored in default it creates a file
  named files

* HOST : The host to bind to. Default is `0.0.0.0`, binds to all interfaces.

* PORT : The port to listen to. Default is `7789`

* REPO_NAME: The name of the spynepi repository in the .pypirc of the user
  that runs Spynepi. Default is `'spynepi'`. The pypirc file is found at 
  ~/.pypirc and is automatically generated or edited by Spynepi when needed.

* TABLE_PREFIX: Prefix for tables which sqlalchemy will create. Its default
  value is `'spynepi'`.

Caveats
-------

Spynepi is a work in progress, so not all of CheeseShop functionality is
implemented. Actually, there are major missing features:

1. No security and data validation precautions are implemented. (Issues 12&18)
2. Once a package is cached, there's no way of updating it. (Issue 16)

These two features make Spynepi suitable only for somewhat temporary
deployments in protected networks. Patches are welcome!

See the issue tracker at github (https://github.com/arskom/spynepi/issues)
for an up-to-date list.

A temporary nuisance is the fact that Spynepi uses features from Spyne-2.10.0
which is not yet released. You should clone git://github.com/arskom/spyne and
install it first before attempting to install Spynepi

Contributing
------------

Currently, there are no cannonical of getting in touch with the maintainers.
You can shoot us an email, tweet or just file an issue.

If you're using Spyne or Spynepi, don't forget to star these projects on github!
Thanks for reading this far :)

