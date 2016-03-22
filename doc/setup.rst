Extra Setup
===========

ssh_args for proxying
---------------------

Setup the below command, and begin the day with
``ssh -Nf -F ~/.ssh/otherconfig bastion``. This will open up a
ControlMaster connection to the bastion so only a single connection is
opened. It speeds up a connecting to servers a little bit.

Then set the ssh_args in ``~/.config/hammercloud/config`` to
``-F ~/.ssh/otherconfig``::

    Host bastion
        ProxyCommand none
        User <sso>
        Hostname <bastionhost>
        ControlPath ~/.ssh/vts-%r@%h:%p
        IdentityFile <ssh_key>
        ControlMaster auto
        ControlPersist 10m

    Host *
        ProxyCommand ssh -aY bastion -F ~/.ssh/otherconfig 'nc -w 900 %h %p'
        ForwardAgent yes
        ForwardX11 no
        GSSAPIAuthentication no
        VerifyHostKeyDNS no
        HashKnownHosts no
        StrictHostKeyChecking false
        TCPKeepAlive yes
        ServerAliveInterval 300
