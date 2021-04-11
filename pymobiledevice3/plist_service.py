#!/usr/bin/env python3

import plistlib
import ssl
import struct
import logging
import codecs
from re import sub

from pymobiledevice3.usbmux import usbmux


class ConnectionFailedException(Exception):
    pass


class PlistService(object):
    def __init__(self, port, udid=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.port = port
        self.connect(udid)

    def connect(self, udid=None):
        mux = usbmux.USBMux()
        mux.process(1.0)
        dev = None

        while not dev and mux.devices:
            mux.process(1.0)
            if udid:
                for d in mux.devices:
                    if d.serial == udid:
                        dev = d
            else:
                dev = mux.devices[0]
                self.logger.info(f'Connecting to device: {dev.serial}')
        try:
            self.s = mux.connect(dev, self.port)
        except:
            raise ConnectionFailedException("Connection to device port %d failed" % self.port)
        return dev.serial

    def close(self):
        self.s.close()

    def recv(self, length=4096):
        return self.s.recv(length)

    def send(self, data):
        try:
            self.s.sendall(data)
        except:
            self.logger.error("Sending data to device failed")
            return -1
        return 0

    def send_request(self, data):
        res = None
        if self.send_plist(data) >= 0:
            res = self.recv_plist()
        return res

    def recv_exact(self, l):
        data = b""
        while l > 0:
            d = self.recv(l)
            if not d or len(d) == 0:
                break
            data += d
            l -= len(d)
        return data

    def recv_raw(self):
        l = self.recv_exact(4)
        if not l or len(l) != 4:
            return
        l = struct.unpack(">L", l)[0]
        return self.recv_exact(l)

    def send_raw(self, data):
        if isinstance(data, str):
            data = data.encode()
        hdr = struct.pack(">L", len(data))
        msg = b"".join([hdr, data])
        return self.send(msg)

    def recv_plist(self):
        payload = self.recv_raw()
        if not payload:
            return
        bplist_header = b'bplist00'
        xml_header = b'<?xml'
        if payload.startswith(bplist_header):
            return plistlib.loads(payload)
        elif payload.startswith(xml_header):
            # HAX lockdown HardwarePlatform with null bytes
            payload = sub('[^\w<>\/ \-_0-9\"\'\\=\.\?\!\+]+', '', payload.decode('utf-8')).encode('utf-8')
            return plistlib.loads(payload)
        else:
            raise Exception(f'recv_plist invalid data: {payload[:100].hex()}')

    def send_plist(self, d):
        payload = plistlib.dumps(d)
        l = struct.pack(">L", len(payload))
        return self.send(l + payload)

    def ssl_start(self, keyfile, certfile):
        self.s = ssl.wrap_socket(self.s, keyfile, certfile, ssl_version=ssl.PROTOCOL_TLSv1)