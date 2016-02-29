sh_ Hammercloud

## What does it do

Currently still expanding that.  This is just getting stuff added as I think about it

Currently it can:

- Log you into nextgen cloud servers (using the uuid or server name)
- Just show general information about the cloud server
- Setup your `supernova temp <command>` stuff (ddi or username)

## Installing

```
pip install --upgrade hammercloud
```

## Configuring

You need a config file, if for nothing else than your sso

### ~/.config/hammercloud/config.yml

```yaml
hammercloud:
  user: <user>
  plugin: rackspace
  ssh_args: -F ~/.ssh/extraconf
  bastion_key: ~/.ssh/id_rsa
  bastion: <bastion>
  terminal: iterm
  use_supernova: True
  shelltype: <pshell/expect>
```

## Autorun!

Autorun scripts can go in two places, if you just want to have one script for
everything, you can drop it in `~/.config/hammercloud/autorun`. Alternatively
`~/.config/hammercloud/autorun.d/` is available.  It runs them in order
(running sorted() in python against the listdir of the directory.

To list out all the scripts so you can see the order they will run, pass
--list-scripts.

```
hc --list-scripts
```

```
[~]$ tail -c +0 ~/.config/hammercloud/autorun.d/*
==> /home/gtmanfred/.config/hammercloud/autorun.d/1-terminfo <==
export TERM=xterm

==> /home/gtmanfred/.config/hammercloud/autorun.d/10-check-ip <==
ip addr show
ip route show
ip -s link

==> /home/gtmanfred/.config/hammercloud/autorun.d/20-heartbleed <==
lsof +c 0 -n | awk '/lib(ssl|crypto)/ && /DEL/ && !x[$1]++ {print $1}'
```

## Setting up supernova

Add the following to your ~/.supernova file

```ini
[temp]
OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/
OS_AUTH_SYSTEM=rackspace
OS_REGION_NAME=USE_KEYRING
NOVA_SERVICE_NAME=cloudServersOpenStack
OS_USERNAME=USE_KEYRING
OS_PASSWORD=USE_KEYRING
OS_TENANT_ID=USE_KEYRING
NOVA_RAX_AUTH=1
OS_NO_CACHE=1
NOVACLIENT_INSECURE=1
```

## ssh_args for proxying

Setup the below command, and begin the day with `ssh -Nf -F ~/.ssh/extraconf bastion`

Then set the ssh_args in `~/.config/hammercloud/config.yml` to `-F ~/.ssh/extraconf`

#### ~/.ssh/extraconf

```
Host bastion
    ProxyCommand none
    User <user>
    Hostname <bastion>
    ControlPath ~/.ssh/vts-%r@%h:%p
    IdentityFile <ssh_key>
    ControlMaster auto
    ControlPersist 10m

Host *
    ProxyCommand ssh -aY bastion -F ~/.ssh/extraconf -W %h:%p
    ForwardAgent yes
    ForwardX11 no
    GSSAPIAuthentication no
    VerifyHostKeyDNS no
    HashKnownHosts no
    StrictHostKeyChecking false
    TCPKeepAlive yes
    ServerAliveInterval 300
```

`Note: if you do not use something like this, and use Host * in your .ssh/config, you should include
the following above your Host * to make sure the ProxyCommand is empty`

```
Host cbast*
  ProxyCommand none
```
