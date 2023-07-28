# !/bin/sh

URL="http://localhost:9993/controller/network/"
NODEID=$(cat /var/lib/zerotier-one/identity.public | cut -d ":" -f 1)
TOKEN=$(cat /var/lib/zerotier-one/authtoken.secret)
NWID="${NODEID}000000"

if [[ $1 = "lsnet" ]]; then
    # dc exec zerotier sh zt lsnet
    curl $URL -H X-ZT1-AUTH:$TOKEN -s
    
    elif [[ $1 = "lsusr" ]]; then
    # dc exec zerotier sh zt lsusr [NWID]
    curl ${URL}${NWID}/member -H X-ZT1-AUTH:${TOKEN} -s
    
    elif [[ $1 = "auth" ]]; then
    # dc exec zerotier sh zt auth [MEMID]
    curl -X POST ${URL}${NWID}/member/$2 -H X-ZT1-AUTH:${TOKEN} -d '{"authorized": true}' -s
    
    elif [[ $1 = "delauth" ]]; then
    # dc exec zerotier sh zt delauth [MEMID]
    curl -X POST ${URL}${NWID}/member/$2 -H X-ZT1-AUTH:${TOKEN} -d '{"authorized": false}' -s
    
    elif [[ $1 = "setip" ]]; then
    # dc exec zerotier sh zt setip [MEMID] [IP]
    curl -X POST ${URL}${NWID}/member/$2 -H X-ZT1-AUTH:${TOKEN} -d '{"ipAssignments":['\""$3"\"']}' -s
    
    elif [[ $1 = "addnet" ]]; then
    # dc exec zerotier sh zt addnet '{"name":"net"}'
    curl -X POST ${URL}${NODEID}______ -H X-ZT1-AUTH:${TOKEN} -d $2 -s
    
    elif [[ $1 = "delnet" ]]; then
    # dc exec zerotier sh zt delnet [NWID]
    curl -X DELETE ${URL}$2 -H X-ZT1-AUTH:${TOKEN} -s
    
    elif [[ $1 = "delnetall" ]]; then
    # dc exec zerotier sh zt delnetall
    for nwid in $(curl ${URL} -H X-ZT1-AUTH:${TOKEN} -s |xargs|sed 's/\[//g;s/\]//g;s/,/\n/g')
    do
        if [ ! $nwid = $NWID ] ; then
            curl -X DELETE ${URL}${nwid} -H X-ZT1-AUTH:${TOKEN} -s|sed -n '/nwid/p'
        fi
    done
else
    zerotier-cli $1
fi