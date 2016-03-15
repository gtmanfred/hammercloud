Installing Hammercloud
======================

To install the release version of hammercloud to your current python
environment, use::

    pip install --upgrade -i https://hammercloud.rackspace.com/simple hammercloud

If you want to use the development version you can install it as an editable
package using::

    pip install -e git+git@github.com:gtmanfred/hammercloud.git#egg=hammercloud

Requirements
------------

By default ``pip`` will grab the python dependencies for the package.
However there are a few non-python dependencies.

If you want to use hammercloud to log into systems, you need to install the
expect package. Some systems may have this installed already, so no action
will be needed.

Installation on Linux
---------------------

Generally the above should work, though it is recommended to use a
virtualenv_ if you're running the ``pip`` commands above. If ``expect`` is
not on your system, logging into servers will not work.

If you have pyenv_, that also works.

Installation on Mac
-------------------

The default python environment on a Mac does not seem to like installing via
pip, so we get around that using pyenv_. To install this you should probably
use something like macports or homebrew.

As pyenv_ will compile the python sources for you, you will also need to
install Xcode for the compiler.

After setting up your python environment and activating it, you should be
able to install using pip very easily.

.. _virtualenv: http://virtualenv.readthedocs.org/en/latest/
.. _pyenv: https://github.com/yyuu/pyenv
