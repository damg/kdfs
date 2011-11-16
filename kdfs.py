import socket as so
from hashlib import sha1
from time import time

class NodeId(object):
    def __init__(self, bytes):
        if not isinstance(bytes, list) and not isinstance(bytes, tuple):
            raise TypeError("Expected list() or tuple(), hit %s()" % bytes.__class__.__name__)
        if len(bytes) != 20:
            raise ValueError("Bytes has length %d, must be 20" % len(bytes))
        for e in bytes:
            if not isinstance(e, int):
                raise TypeError("Bytes contains a %s(), must be int()" % e.__class__.__name__)
            if e < 0 or e > 255:
                raise ValueError("Bytes contains value %d, must be [0..255]" % e)

        self.bytes = tuple(bytes)

    def __xor__(self, o):
        if not isinstance(o, NodeId):
            raise TypeError("Cannot xor NodeId and %s()" % o.__class__.__name__)

        bs = map(lambda e: e[0] ^ e[1], zip(self.bytes, o.bytes))
        return NodeId(bs)

    def __eq__(self, o):
        return isinstance(o, NodeId) and self.bytes == o.bytes

    def __lt__(self, o):
        if not isinstance(o, NodeId):
            raise TypeError("Cannot compare NodeId() with %s()" % o.__class__.__name__)
        return self.bytes < o.bytes

    def __gt__(self, o):
        if not isinstance(o, NodeId):
            raise TypeError("Cannot compare NodeId() with %s()" % o.__class__.__name__)
        return self.bytes > o.bytes

    def __le__(self, o):
        if not isinstance(o, NodeId):
            raise TypeError("Cannot compare NodeId() with %s()" % o.__class__.__name__)
        return self.bytes <= o.bytes

    def __ge__(self, o):
        if not isinstance(o, NodeId):
            raise TypeError("Cannot compare NodeId() with %s()" % o.__class__.__name__)
        return self.bytes >= o.bytes

    def __str__(self):
        return ("%x" * 20) % self.bytes

    def __hash__(self):
        return hash(self.bytes)

class Bucket(object):
    def __init__(self, k=20):
        if not isinstance(k, int):
            raise TypeError("k-Bucket size is %s(), must be int()" % k.__class__.__name__)
        if k < 1:
            raise ValueError("k-Bucket size is %d, must be >= 1" % k)
        self.k = k
        self.values = {} # { node_id => sock_addr, timestamp }

    def __len__(self):
        return len(self.values)

    def add_node(self, node_id, node_host, node_port):
        if not isinstance(node_id, NodeId):
            raise TypeError("node_id is %s(), must be NodeId()" % node_id.__class__.__name__)

        if not isinstance(node_host, str):
            raise TypeError("node_host is %s(), must be str()" % node_host.__class__.__name__)

        if not isinstance(node_port, int):
            raise TypeError("node_port is %s(), must be int()" % node_port.__class__.__name__)

        if node_port < 1 or node_port > 65535:
            raise ValueError("node port is %d, must be in [1..65535] range" % node_port)

        t = time()
        self.values[node_id] = (node_host, node_port, t)

        if len(self.values) > k:
            vs = [ (self.values[key][2], key) for key in self.values ]
            vs.sort()
            del self.values[vs[0][1]]
                

class BucketStore(object):
    def __init__(self, my_node_id):
        if not isinstance(my_node_id, NodeId):
            raise TypeError("my_node_id is %s(), must be NodeId()" % my_node_id.__class__.__name__)

        self.my_node_id = my_node_id
        self.buckets = {} # { i => Bucket ; 0 <= i < 160 }
