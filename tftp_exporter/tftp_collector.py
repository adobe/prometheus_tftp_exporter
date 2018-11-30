"""
Prometheus TFTP probe and data collector functions.
"""
import itertools
import time
import random
import os
import subprocess
import pprint
import re
import prometheus_client
from prometheus_client import Metric, CollectorRegistry, generate_latest, Gauge

pp = pprint.PrettyPrinter(indent=4)


def tftp_probe(host, port, tftp_file):
    """
    Check and verify that we can get the PXE boot-file from TFTP in a timely manner.

    This is using a TFTP -client that needs to be installed on the system.
    The 'tftp'-package on RH/CentOS has this output but may need adjustments.
    I tested a few Python Clients - but they adds a lot of complexity.
    The temp-files downloaded are stored in /tmp/ with host and timestamp to avoid conflicts.
    Files are deleted afterwards.
    :param host: Host/Target that we want to get a file from.
    :param port: TFTP Port - default 69.
    :param tftp_file: TFTP file to download. Defaults to 'pxelinux.0' but file/path depends on the system.
    :return: Dictionary with 'status' (1 = success, 0 = error), and up to 3 other metrics if successful.
    """
    res = dict()
    received = False
    local_file = '/tmp/tftp_' + str(host) + '_' + str(time.time()) + '.tmp'
    try:
        # Get either pxelinux.0 or the uefi version that is 14 times as big (easier to time).
        cmdlist_tftp_get = ('tftp', '-v', host, port, '-m', 'binary', '-c', 'get', tftp_file, local_file)
        proc = subprocess.Popen(cmdlist_tftp_get, shell=False, cwd='/tmp/', stdout=subprocess.PIPE)
        ret = proc.communicate()[0].strip()
        retcode = proc.wait()
        if ret and retcode == 0:
            speed = 0
            for line in ret.splitlines():
                match = re.search(r'^Received (\d+) bytes.*\[(\d+)\s+bit/s\]', line)
                if match:
                    received = True
                    rec_bytes = int(match.group(1))
                    speed = int(match.group(2))
                    speed_kbytes = speed / 1024 / 8
                    res['speed_KBpS'] = speed_kbytes
                    res['status'] = 1
                    res['rec_bytes'] = rec_bytes

    except OSError as err:
        print('Error (' + str(host) + '): ' + str(err))
    if os.path.isfile(local_file):
        os.remove(local_file)
    else:
        if received:
            print('Error: TFTP fetched file did not exist so it could not be deleted. (' + local_file + ')')
    if not received:
        print("Error: TFTP file not received from host: " + str(host) + ' ' + str(tftp_file))
        res['status'] = 0
    return res


def collect_tftp(host, port_str='69', tftp_file='pxelinux.0'):
    """
    Collect tftp-probing data from a host and return prometheus formatted stats
    """
    start = time.time()
    metrics = {}
    res = tftp_probe(host=host, port=port_str, tftp_file=tftp_file)
    # pp.pprint(res)

    # noinspection PyMethodMayBeStatic
    class Collector(object):
        """
        Collector-class with necessary callback-functions.
        """
        def collect(self):
            """
            This is called on every web-request.
            """
            return metrics.values()

    registry = CollectorRegistry()
    registry.register(Collector())
    probe_duration = Gauge('tftp_probe_duration_seconds', 'Returns how long the probe took to return in seconds', registry=registry)
    probe_success = Gauge('tftp_probe_success', 'Displays whether or not the probe was a success', registry=registry)
    probe_content_length = Gauge('tftp_probe_content_length_bytes', 'Content bytes received', registry=registry)
    probe_dl_speed = Gauge('tftp_probe_dl_speed', 'Returns the download speed in KB/s', registry=registry)

    probe_duration.set(time.time() - start)
    if res:
        if 'status' in res:
            probe_success.set(res['status'])
        if 'rec_bytes' in res:
            probe_content_length.set(res['rec_bytes'])
        if 'speed_KBpS' in res:
            probe_dl_speed.set(res['speed_KBpS'])

    return generate_latest(registry)
