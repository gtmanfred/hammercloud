Hammercloud Examples
====================

Login using uuid::

    hc aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee

Login using the servername::

    hc --auth username servername
    hc --auth ddi servername

.. Note: logging in by servername REQUIRES the ddi or username

Log you into the host machine::

    hc --host aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    hc --host --auth username servername

Display information about the server::

    hc --info aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
    hc --info --auth username servername

Log into all servers on an account::

    hc -a <ddi>

.. Note: Some other options work here, too, such as ``--info``

See the output of ``hc --help`` for more complete information.
