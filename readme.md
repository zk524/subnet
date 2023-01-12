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
  - List Networks: `docker exec zerotier sh z lsnet`
  - List Network Members: `docker exec zerotier sh z lsusr [NWID]`
  - Authorize a member: `docker exec zerotier sh z auth [MEMID]`
  - Set member ip: `docker exec zerotier sh z setip [MEMID] [IP]`
  - Create Network: `docker exec zerotier sh z addnet '{}'`
  - Delete Network: `docker exec zerotier sh z delnet [NWID]`

## Client

- Start
  - `docker compose -f docker-compose.client.yml up -d`
- Use
  - MemberID: `docker exec zerotier-client zerotier-cli info`
  - Join network: `docker exec zerotier-client zerotier-cli join [NWID]`, then Controller authorize this member by **MemberID**.
  - List Peers: `docker exec zerotier-client zerotier-cli listpeers`

[contributors-shield]: https://img.shields.io/github/contributors/zk524/zerotier-custom.svg?style=for-the-badge
[contributors-url]: https://github.com/zk524/zerotier-custom/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/zk524/zerotier-custom.svg?style=for-the-badge
[forks-url]: https://github.com/zk524/zerotier-custom/network/members
[stars-shield]: https://img.shields.io/github/stars/zk524/zerotier-custom.svg?style=for-the-badge
[stars-url]: https://github.com/zk524/zerotier-custom/stargazers
[issues-shield]: https://img.shields.io/github/issues/zk524/zerotier-custom.svg?style=for-the-badge
[issues-url]: https://github.com/zk524/zerotier-custom/issues
