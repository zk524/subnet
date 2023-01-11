[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<div align="center">
  <h2 align="center">Zerotier Custom</h3>
  <p align="center">Controller and Client by docker</p>
</div>

## Controller

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

[contributors-shield]: https://img.shields.io/github/contributors/zk524/zerotier-custom.svg?style=for-the-badge
[contributors-url]: https://github.com/zk524/zerotier-custom/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/zk524/zerotier-custom.svg?style=for-the-badge
[forks-url]: https://github.com/zk524/zerotier-custom/network/members
[stars-shield]: https://img.shields.io/github/stars/zk524/zerotier-custom.svg?style=for-the-badge
[stars-url]: https://github.com/zk524/zerotier-custom/stargazers
[issues-shield]: https://img.shields.io/github/issues/zk524/zerotier-custom.svg?style=for-the-badge
[issues-url]: https://github.com/zk524/zerotier-custom/issues
