# !/bin/sh

cd /var/lib/zerotier-one
apk add --no-cache --allow-untrusted curl

if [ ! -f identity.secret ]; then zerotier-idtool generate identity.secret identity.public; fi
if [ ! -f planet ]; then
    apk add --no-cache --allow-untrusted g++
    mkdir tmp
    mkdir -p controller.d/network
    addr=$(curl ip.sb -s)/9993
    identity=`cat identity.public`
    NODEID=`echo $identity|cut -d ":" -f 1`
    curl https://codeload.github.com/zerotier/ZeroTierOne/tar.gz/refs/tags/1.8.6 --output tmp/z.tar.gz
    tar xzf tmp/z.tar.gz -C tmp --strip-components 1
    cd tmp/attic/world
    sed -i '/roots.push_back/d;/roots.back()/d' ./mkworld.cpp
    sed -i '85i roots.push_back(World::Root());\nroots.back().identity = Identity(\"'"$identity"'\");\nroots.back().stableEndpoints.push_back(InetAddress(\"'"$addr"'\"));' ./mkworld.cpp
    echo Building world.bin...
    sh ./build.sh && ./mkworld
    mv ./world.bin ../../../planet
    cd -
    apk del g++
    rm -rf tmp
    rm -rf /var/cache/apk/*
    rm -rf /root/.cache
    echo "{\"settings\": {\"portMappingEnabled\": true,\"softwareUpdate\": \"disable\",\"allowManagementFrom\": [\"0.0.0.0/0\"]}}" > local.conf
    echo "{\"authTokens\":[null],\"authorizationEndpoint\":\"\",\"capabilities\":[],\"clientId\":\"\",\"creationTime\":1600000000000,\"dns\":[],\"enableBroadcast\":true,\"id\":\"${NODEID}000000\",\"ipAssignmentPools\":[{\"ipRangeEnd\":\"172.30.0.254\",\"ipRangeStart\":\"172.30.0.1\"}],\"mtu\":2800,\"multicastLimit\":32,\"name\":\"net\",\"nwid\":\"${NODEID}000000\",\"objtype\":\"network\",\"private\":true,\"remoteTraceLevel\":0,\"remoteTraceTarget\":null,\"revision\":1,\"routes\":[{\"target\":\"172.30.0.0/24\",\"via\":null}],\"rules\":[{\"etherType\":2048,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"},{\"etherType\":2054,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"},{\"etherType\":34525,\"not\":true,\"or\":false,\"type\":\"MATCH_ETHERTYPE\"},{\"type\":\"ACTION_DROP\"},{\"type\":\"ACTION_ACCEPT\"}],\"rulesSource\":\"\",\"ssoEnabled\":false,\"tags\":[],\"v4AssignMode\":{\"zt\":true},\"v6AssignMode\":{\"6plane\":false,\"rfc4193\":false,\"zt\":false}}" > controller.d/network/${NODEID}000000.json
    echo Nodeid: $NODEID
fi

chmod +x /z
zerotier-one -U