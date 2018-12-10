# Prometheus TFTP Exporter

This is an exporter that fetches files from remote servers using hte TFTP protocol.
It's designed to be able to run on the Prometheus server directly.

Doing it remote measures network performance as well as it actually transfers a file over the network.
Calling a client_exporter would just send a few bytes with the result over the network using HTTP.

## Requirements

 * Python 2.7 or 3
 * [prometheus\_client](https://github.com/prometheus/client_python)
 * Systems own tftp-client (Developed using output from RedHat/CentOS 'tftp')

## Usage

Install using a Package - and run it as a daemon. (To be done)


### Prometheus configuration

The tftp_exporter configuration looks much from the blackbox_exporter.
It needs to be passed the address as a parameter, this can be
done with relabelling.

```YAML
scrape_configs:

  - job_name: tftp
    scrape_interval: 60s
    scrape_timeout: 15s
    params:
      module: [tftp]
      tftp_filename: [pxelinux.0]
      tftp_port: [69]
    static_configs:
       - targets:
         - 'tftpserver1.domain'
         - 'tftpserver2.domain'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9519  # The tftp exporter's real hostname:port.
```

The configuration contains information about which file to retrieve using TFTP - and the targets to test.
Then the code was heavily inspired by the snmp_exporter, (https://github.com/prometheus/snmp_exporter)

This service can run on any host - as the targets to test is passed in the Prometheus call. Tests are performed when the function is called.

As this isn't a "normal" client-side test, we will also test the DNS and Network - for good and for bad.
If you want to run in on your clients - it's also possible, and then just use localhost as the hostname. With a server config to point out all the clients.


Run `tftp_exporter.py`, and then visit http://127.0.0.1:9519/metrics??module=tftp&target=tftpserver1.domain&tftp_filename=pxelinux.0
where target is is the dns-name of the TFT-service to probe and tftp_filename is the name of the file on the TFTP-server to get..
The metrics will be tagged with the hostnames for easy identifying.

## Metrics
This module will collect:
* tftp_probe_success
* tftp_probe_duration_seconds
* tftp_probe_dl_speed
* tftp_probe_content_length_bytes

In Prometheus all the metrics will start with tftp_probe and have 2 tags:
```
tftp_probe_duration_seconds{instance="tftpserver1.domain",job="tftp"}
tftp_probe_duration_seconds{instance="tftpserver2.domain",job="tftp"}
```
Where instance is the targets specified in the config, and job is the scrape_configs job_name.


## Design

There are two components. An exporter that does the actual scraping,
and a generator that creates the configuration for use by the exporter.
The scraping can be done in parallel as the probing is done in a fork.


## Exported metrics
For each of the targets specified you will get the following info.

| Name                            | Type  | Description                                          |
| ------------------------------- | ----- | ---------------------------------------------------- |
| tftp_probe_duration_seconds     | gauge | Returns how long the probe took to return in seconds |
| tftp_probe_success              | gauge | Displays whether or not the probe was a success      |
| tftp_probe_dl_speed             | gauge | Returns the download speed in KB/s                   |
| tftp_probe_content_length_bytes | gauge | Content bytes received                               |


## Packaging
###
python setup.py sdist
Will create a tar.gz archive with all the files - as well as setup script to help you get it running.
Distribute and unpack, run the bin/install.sh with the full path to the original archive-file and you will get it set up under /opt/.

### RPM
To create a CentOS RPM-package that has dependencies on the required tftp package, and SystemD init-scripts.
Install build-requirements: yum install rpm-build

Then run: python setup.py bdist --formats=rpm

