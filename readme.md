## Controller(planet)

- Start

  - `docker compose up -d`

- Use ([Doc](https://docs.zerotier.com/self-hosting/network-controllers))
  - List Networks: `docker exec zerotier sh zt lsnet`
  - List Network Members: `docker exec zerotier sh zt lsusr [NWID]`
  - Authorize a member: `docker exec zerotier sh zt auth [MEMID]`
  - Set member ip: `docker exec zerotier sh zt setip [MEMID] [IP]`
  - Create Network: `docker exec zerotier sh zt addnet '{}'`
  - Delete Network: `docker exec zerotier sh zt delnet [NWID]`

## Client

- Start
  - Copy the _planet_ from Controller to the local dir
  - `docker compose -f docker-compose.client.yml up -d`

## Note

- Dont't startup the Controller and Client in a same folder or a same port(9993).
