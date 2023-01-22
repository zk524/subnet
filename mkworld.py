from hashlib import sha512
import os
import binascii
import urllib.request
import urllib.parse
import argparse

p, L = 2**255 - 0x13,  2**252 + 0x14def9dea2f79cd65812631a5cf5d3ed
d = 0xa406d9dc56dffce7198e80f2eef3d13000e0149a8283b156ebd69b9426b2f146
G1 = bytearray.fromhex("04000c07090105070e060a07030b0f07080004090d050909020a0e0907030f090c04080d01090d0d06020e0d0b03070d00080c1205010d120a0206120f070b12")
G2 = bytearray.fromhex("01000307020100090302010d0003021206050407070605090407060d050407120b0a0907080b0a0909080b0d0a0908120c0f0e070d0c0f090e0d0c0d0f0e0d12")
group = tuple([tuple((G1+G2)[i:i+4]) for i in range(0, 128, 4)])*10


class Salsa20:
    def __init__(self, key, iv):
        k, v = [a | b << 8 | c << 16 | d << 24 for a, b, c, d in key], [a | b << 8 | c << 16 | d << 24 for a, b, c, d in iv]
        self.s = [0x61707865, k[0], k[1], k[2], k[3], 0x3320646e, v[0], v[1], 0, 0, 0x79622d32, k[4], k[5], k[6], k[7], 0x6b206574]

    def __call__(self, d):
        s = self.s[:]
        for a, b, c, r in group:
            w = s[b] + s[c] & 0xffffffff
            s[a] ^= w << r & 0xffffffff | (w >> 32 - r)
        for i in range(16):
            s[i] = s[i] + self.s[i] & 0xffffffff ^ (d[i][0] | d[i][1] << 8 | d[i][2] << 16 | d[i][3] << 24)
            d[i] = s[i] & 0xff, (s[i] & 0xff00) >> 8, (s[i] & 0xff0000) >> 16, (s[i] & 0xff000000) >> 24
        self.s[8] += 1
        return d


class C25519:
    def point_to_int(s):
        G, P = (0x216936d3cd6e53fec0a4e231fdd6dc5c692cc7609525a7b2c9562d608f25d51a, 0x6666666666666666666666666666666666666666666666666666666666666658, 1,
                0x67875f0fd78b766566ea4e8e64abe37d20f09f80775152f56dde8ab3a5b7dda3), (0, 1, 1, 0)
        while s > 0:
            if s & 1:
                a, b, c, e = (P[1] - P[0]) * (G[1] - G[0]) % p, (P[1] + P[0]) * (G[1] + G[0]) % p, P[3] * G[3] * d % p, 2 * P[2] * G[2] % p
                P = (b - a) * (e - c), (e + c) * (b + a), (e - c) * (e + c), (b - a) * (b + a)
            a, b, c, e = (G[1] - G[0]) ** 2 % p, (G[1] + G[0]) ** 2 % p, G[3] ** 2 * d % p, 2 * G[2] ** 2 % p
            G = (b - a) * (e - c), (e + c) * (b + a), (e - c) * (e + c), (b - a) * (b + a)
            s >>= 1
        z = pow(P[2], p - 2, p)
        return int.to_bytes(P[1] * z % p | (P[0] * z % p & 1) << 255, 32, "little")

    def pubED(secret):
        return C25519.point_to_int(int.from_bytes(sha512(secret).digest()[:32], "little") & ((1 << 254) - 8) | (1 << 254))

    def pubDH(secret):
        n = bytearray(secret)
        n[0], n[31] = n[0] & 248, n[31] & 127 | 64
        n = "{:b}".format(int(n[::-1].hex(), 16))
        P = 9, 1, 0x1900, 0x9660720
        for i in range(1, 255):
            x, y = (P[2]*P[0]-P[3]*P[1])**2*4 % p, (P[2]*P[1]-P[3]*P[0])**2*36 % p
            if n[i] == '1':
                P = x, y, (P[2]**2-P[3]**2)**2 % p, (P[2]**2+486662*P[2]*P[3]+P[3]**2)*P[2]*P[3]*4 % p
            else:
                P = (P[0]**2-P[1]**2)**2 % p, (P[0]**2+486662*P[0]*P[1]+P[1]**2)*P[0]*P[1]*4 % p, x, y
        return int.to_bytes(P[0] * pow(P[1], p-2, p) % p, 32, "little")

    def sign(secret, msg):
        h = sha512(secret).digest()
        s = int.from_bytes(h[:32], "little") & ((1 << 254) - 8) | (1 << 254)
        r = int.from_bytes(sha512(h[32:] + msg).digest(), "little") % L
        R = C25519.point_to_int(r)
        k = int.from_bytes(sha512(R + C25519.pubED(secret) + msg).digest(), "little") % L
        return R + int.to_bytes((r + k * s) % L, 32, "little")

    def gen_keypair_digest(pub):
        digest = bytearray(sha512(pub).digest())
        digest = [tuple(digest[i:i+4]) for i in range(0, 64, 4)]
        s20 = Salsa20(digest[:8], digest[8:10])
        genmem = [(0,)*4 for _ in range(0, 1 << 19, 4)]
        genmem[:16] = s20(genmem[:16])
        for i in range(16, 1 << 19, 16):
            genmem[i:i+16] = s20(genmem[i-16:i])
        for i in range(0, 1 << 19, 4):
            m, n = genmem[i+1][-1] % 8 * 2, (genmem[i+3][3] | genmem[i+3][2] << 8 | genmem[i+3][1] << 16 | genmem[i+3][0] << 24) % (1 << 18) * 2
            genmem[n:n+2], digest[m:m+2] = digest[m:m+2], genmem[n:n+2]
            s20(digest)
        return bytes(sum(digest, ()))

    def gen_keypair(satisfying, n=0):
        secret = bytearray(os.urandom(64))
        pubED = C25519.pubED(secret[32:])
        while n := n+1:
            pub = C25519.pubDH(secret[:32]) + pubED
            digest = C25519.gen_keypair_digest(pub)
            if not satisfying or digest[0] < 17:
                return secret, pub, digest
            else:
                secret[8], secret[16] = secret[8] + 1 & 0xff, secret[16] - 1 & 0xff
                print(f"Try generate identity: {n}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", action='append', metavar="IP:PORT", help="e.g. 192.168.0.1:9993")
    args = parser.parse_args()
    if not args.ip:
        args.ip = [urllib.request.urlopen("https://checkip.amazonaws.com").read().decode('utf-8').strip()+':9993']
    ip = [len(args.ip).to_bytes(1, 'big')]
    for i in args.ip:
        i1, i2 = i.split(":")
        ip += [b'\x04', *list(map(lambda i: int(i).to_bytes(1, 'big'), i1.split("."))), int(i2).to_bytes(2, 'big')]
    try:
        os.makedirs("controller/controller.d/network")
    except:
        ...
    try:
        with open("controller/identity.secret", 'r') as f:
            pair = f.read().split(":")
            identity = bytes.fromhex(pair[0]) + b'\x00'+bytes.fromhex(pair[2])
    except:
        pair = C25519.gen_keypair(True)
        identity = pair[2][59:]+b'\x00'+pair[1]
        output = list(map(lambda i: binascii.hexlify(i).decode("utf-8"), [pair[2][59:], pair[1], pair[0]]))
        output.insert(1, "0")
        with open("controller/identity.secret", 'w') as f:
            f.write(":".join(output))
        with open("controller/identity.public", 'w') as f:
            f.write(":".join(output[:-1]))
    try:
        with open("controller/mkworld.c25519", 'rb') as f:
            secret = f.read()[64:]
    except:
        secret = os.urandom(64)
        with open("controller/mkworld.c25519", 'wb') as f:
            f.write(C25519.pubDH(secret[:32])+C25519.pubED(secret[32:])+secret)
    msg = [b'\x7f'*8,
           b'\x01\x00\x00\x00\x00\x08\xea\xc9\n\x00\x00\x01l\xe3\xe29U',
           C25519.pubDH(secret[:32])+C25519.pubED(secret[32:]),
           b'\x01'+identity,
           b'\x00'+b''.join(ip),
           b'\xf7'*8]
    digest = sha512(b''.join(msg)).digest()[:32]
    signature = C25519.sign(secret[32:], digest)+digest
    planet = b''.join(msg[1:3]+[signature]+msg[3:-1])
    with open("controller/planet", 'wb') as f:
        f.write(planet)
    with open("controller/local.conf", 'w') as f:
        f.write('{"settings":{"portMappingEnabled":true,"softwareUpdate":"disable","allowManagementFrom":["0.0.0.0/0"]}}')
    nodeid = binascii.hexlify(identity[:5]).decode("utf-8")
    with open(f"controller/controller.d/network/{nodeid}000000.json", 'w') as f:
        f.write(f"{{\"authTokens\":[null],\"authorizationEndpoint\":\"\",\"capabilities\":[],\"clientId\":\"\",\"creationTime\":1600000000000,\"dns\":[],\"enableBroadcast\":true,\"id\":\"{nodeid}000000\",\"ipAssignmentPools\":[{{\"ipRangeEnd\":\"172.30.0.254\",\"ipRangeStart\":\"172.30.0.1\"}}],\"mtu\":2800,\"multicastLimit\":32,\"name\":\"net\",\"nwid\":\"{nodeid}000000\",\"objtype\":\"network\",\"private\":true,\"remoteTraceLevel\":0,\"remoteTraceTarget\":null,\"revision\":1,\"routes\":[{{\"target\":\"172.30.0.0/24\",\"via\":null}}],\"rules\":[{{\"etherType\":2048,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"}},{{\"etherType\":2054,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"}},{{\"etherType\":34525,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"}},{{\"type\":\"ACTION_DROP\"}},{{\"type\":\"ACTION_ACCEPT\"}}],\"rulesSource\":\"\",\"ssoEnabled\":false,\"tags\":[],\"v4AssignMode\":{{\"zt\":true}},\"v6AssignMode\":{{\"6plane\":false,\"rfc4193\":false,\"zt\":false}}}}")
    print("nodeid: ", nodeid, "\nplanet: ", binascii.hexlify(planet))
