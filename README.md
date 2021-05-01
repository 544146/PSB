# Plex Search Bot
Serverless Telegram bot for querying Jackett and uploading to ruTorrent

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
