# Plex Search Bot
Serverless Telegram Bot for querying Jackett and uploading to ruTorrent

## Deployed Application Screenshots

Starting the bot

---

![start](https://i.imgur.com/WQbjM8P.png "start")

Viewing previous downloads

---

![view](https://i.imgur.com/VBHW5QU.png "view")

Searching for a torrent

---

![search](https://i.imgur.com/cAnWKtl.png "search")

Getting a torrent

---

![download](https://i.imgur.com/stKU5u7.png "download")

Suggested commands

---

![suggest](https://i.imgur.com/3cVfsVl.png "suggest")

## Architecture

---

Telegram webhook -> AWS API Gateway -> AWS Lambda -> (AWS DynamoDB) -> Telegram API

## Environment Variables

--- 

| Key                      | Value                                            |
|--------------------------|--------------------------------------------------|
| jackett_api_key          |                                                  |
| jackett_url              | jacket url /jacket/api/v2.0/indexers/all/results |
| rutorrent_basic          |                                                  |
| rutorrent_rpc            | rutorrent rpc url /rutorrent/plugins/rpc/rpc.php |
| rutorrent_url            | rutorrent url /rutorrent/php/addtorrent.php      |
| telegram_bot_key         |                                                  |
| telegram_password        |                                                  |
| plex_machine_identifier  |                                                  |
| x_plex_client_identifier |                                                  |
| x_plex_token             |                                                  |
