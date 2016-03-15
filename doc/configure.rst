Hammercloud Configuration
=========================

Hammercloud has stopped using the old ``.ini`` configuration file and has
moved to a `yaml`_ file. Running hammercloud without a configuration file
will result in a warning telling you to add one. Below is an example
configuration::

    hammercloud:
      user: <username>
      plugin: rackspace
      ssh_args: -F ~/.ssh/extraconf
      bastion: <bastion>
      bastion_key: ~/.ssh/id_rsa
      terminal: iterm
      shelltype: <pshell/expect>

Options
-------

hammercloud section
^^^^^^^^^^^^^^^^^^^

``user``: Your username. It it used to sign into the bastion you specify.

``plugin``: Optional. What plugins, if any, we should be using for hammercloud.

``ssh_args``: Optional. If you use any special ssh options to proxy through
a bastion to servers, you should specify things here.

``bastion``: Server to send your connections through when accessing remote
servers.

``bastion_key``: Optional. The SSH key for the bastion specified above.

``terminal``: Which terminal to use for opening multiple windows at once.
Takes one of ``tmux``, ``screen``, ``gnome-terminal``, ``mate-terminal``, ``xfce4-terminal``,
``konsole`` or ``iterm``

``shelltype``: One of pshell or expect for handling sending commands and
reading your terminal.

.. _yaml: http://yaml.org/
