#!/bin/bash

# Program to install the Prometheus TFTP-exporter

# Program is installed under /opt/


if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [ -z "$1" ]; then
    echo "You need to supply the name and full path to the PIP package: [/FULL_PATH/-0.x.x.tar.gz]"
    exit 1
fi

if echo "$1" | grep -q "prometheus_tftp_exporter-" ; then
    if  [ -f "$1" ]; then
	echo "Looks like we have a valid PIP-package at: $1"
    else
	echo "File not found: $1"
	exit 1
    fi
else
    echo "Entered arguments doesn't look like a valid file for prometheus_tftp_exporter."
    exit 1
fi

PROJECTDIR=/opt/tftp_exporter
BINDIR="$PROJECTDIR/bin/"
mkdir -p $PROJECTDIR
cd $PROJECTDIR

# Select Package manager based on distro
if [ -f '/etc/redhat-release' ]; then
    #redhat based distros
    echo "RedHat-based distro, using 'yum'."
    PACKAGE_MANAGER=yum
    DEPS=(python-virtualenv python-devel)
elif [ -f '/etc/debian_version' ]; then
    # debian based distros
    echo "Debian based distro, using 'apt-get'"
    PACKAGE_MANAGER=apt-get
    DEPS=(python-virtualenv)
else
    echo "Unknown Distribution - Aborting."
    exit 1
fi

for package in ${DEPS[@]}; do
    $PACKAGE_MANAGER -y install $package
done

echo "Set up Virtual Envirnoment."



# Install under /opt/kickstartpwhashrotate
virtualenv -p python2 $PROJECTDIR

VIRTUAL_ENV="$PROJECTDIR"
$BINDIR/pip install --upgrade pip
$BINDIR/pip install --upgrade virtualenv

$BINDIR/pip install $1



if [ -f "$BINDIR/tftp_exporter" ]; then
    chmod 755 $BINDIR/tftp_exporter

    echo "Start/stop using 'systemctl start|stop prometheus-tftp-exporter.service"

    echo "Done"
    #echo "Tool has been added to path as: rotate_root_hash_vault"
else
    echo "Error: Something failed. Please review and try again."
    exit 1
fi
