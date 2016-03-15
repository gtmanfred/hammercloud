Automatically Running Commands on Login
=======================================

It is possible to run commands automatically on login using hammercloud. If
your terminfo isn't supported by servers, this can be useful to export a
``TERM`` variable. Maybe set up some much needed aliases for everyday tasks
on servers.

Autorun files are simple bash scripts that are 'minified' by hammercloud
before being passed to the server (newlines removed, replaced with ``;``'s)

To list out all the scripts so you can see the order they will run, pass
``--list-scripts``::

    $ hc --list-scripts
    <=== Script: <HOME>/.config/hammercloud/autorun ===>
    echo "Something"

    <=== Script: 01.terminfo ===>
    [[ -e /usr/share/terminfo/s/screen-256color ]] && export TERM=screen-256color || export TERM=screen
    export PS1="\u@\h:\w \$ "
    alias mysqltuner='perl <( curl -sL mysqltuner.pl )'

The scripts are loaded in this order:

1. ``$HOME/.config/hammercloud/autorun``
2. ``$HOME/.config/hammercloud/autorun.d/*``

The ``autorun.d/*`` scripts are run in the order or a python ``sorted()``
list of their names. There is no required suffix or prefix for the files.
