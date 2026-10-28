# Deploying the tag-BD bot next to the item-check bot

The tag-BD bot runs next to the existing item-check bot on the same cPanel account
(`beudeliverycom`). It works the same way:

- It has its own plain virtualenv in `tag_bd_bot/venv`. It must not use the item bot's
  cPanel virtualenv: that one's `python` is a wrapper (`bin/set_env_vars.py`) that loads
  Setup Python App's Environment Variables, the item bot's token and `DATABASE_URL`,
  over the values in `start_bot.sh`.
- A cron job runs `start_bot.sh` every minute. The script starts the bot only if it
  is not already running.
- Secrets live in `start_bot.sh`, not in a `.env` file.

It needs no Setup Python App and no Passenger. The item-check bot is not touched.

| | Item-check bot (existing) | Tag-BD bot (new) |
|---|---|---|
| Folder | `/home/beudeliverycom/telegram_bot` | `/home/beudeliverycom/telegram_bot/tag_bd_bot` |
| Script | `telegram_bot.py` | `tag_bd_bot.py` |
| Restart | `pkill -f "telegram_bot.py"` | `pkill -f "tag_bd_bot.py"` |
| Log | `telegram_bot/bot.log` | `telegram_bot/tag_bd_bot/bot.log` |

The tag bot lives in a subfolder of the item bot's folder, so the home folder (which
also holds the hosted websites) gets no new top-level folder. Nothing in the item bot
reads that subfolder. When you redeploy the item bot, extract its zip over the
existing files. Never delete or replace the whole `telegram_bot` folder, because
that would also remove the tag bot.

The script is renamed on purpose. The item bot's `start_bot.sh` uses
`pgrep -f "telegram_bot.py"`. If the tag bot used the same name, the item bot
would think it was already running and never restart, and a `pkill` would kill both bots.

## 0. Stop the tag bot where it runs now
Only one process may poll Telegram with a given token. If two do, Telegram
returns `Conflict: terminated by other getUpdates request`.

## 1. Upload
Build the zip from the repo root with `python deploy/cpanel/build_zip.py`.
It is written to `deploy/cpanel/tag_bd_bot-cpanel.zip`.

1. In File Manager, upload `tag_bd_bot-cpanel.zip` to `/home/beudeliverycom/telegram_bot/`.
   Do not put it in `public_html`.
2. Extract it. This creates `/home/beudeliverycom/telegram_bot/tag_bd_bot/`.

## 2. Create the tag bot's own virtualenv
Run these in cPanel Terminal, **one line at a time**:
```
/opt/alt/python311/bin/python3.11 -m venv /home/beudeliverycom/telegram_bot/tag_bd_bot/venv
```
```
/home/beudeliverycom/telegram_bot/tag_bd_bot/venv/bin/pip install python-telegram-bot==21.11.1 "SQLAlchemy[asyncio]==2.0.50" aiomysql PyMySQL cryptography python-dotenv
```
The versions match the item bot. `cryptography` is needed so PyMySQL can log in to the
RDS MySQL 8 server. Do not create this venv through Setup Python App.

## 3. Fill in `start_bot.sh`
Open `tag_bd_bot/start_bot.sh` in File Manager's **editor** and fill in:
- `TELEGRAM_BOT_TOKEN`: the tag bot's token.
- `DATABASE_URL`: the same RDS reader as the item bot (`analyst` user, `beu` DB). Two
  differences from the item bot: the driver is `mysql+aiomysql` instead of
  `mysql+mysqlconnector`, and you must remove `?use_pure=true`.
- `SQL_DATABASE_URL`: the DB that holds `user_info` / `bd_replies`.
  - If you move this DB to the local cPanel MySQL, create it plus a user in
    MySQL Databases, then run `create_tables.sql` in phpMyAdmin. On this host,
    names have no `beudeliverycom_` prefix.
  - To keep existing BD registrations, export `user_info` from the old DB and
    import it. Otherwise every BD must send `/start` to the bot again.

Do not paste the file through a Terminal heredoc. This host's browser Terminal
mangles multi-line pastes and has already emptied a `start_bot.sh` this way.
URL-encode special characters in passwords (`@` becomes `%40`, `#` becomes `%23`).

## 4. Test before going live
```
bash /home/beudeliverycom/telegram_bot/tag_bd_bot/start_bot.sh check
```
Expect three `OK` lines: the token (which shows the bot's @username), then
`DATABASE_URL`, then `SQL_DATABASE_URL`. Fix anything marked `FAILED` before step 5.

## 5. Add the cron job
In **Cron Jobs**, add a job with every field set to `*`, using the same format as the
existing item bot job:
```
sleep $((RANDOM \% 60)) && bash /home/beudeliverycom/telegram_bot/tag_bd_bot/start_bot.sh
```
To start right away, run `bash /home/beudeliverycom/telegram_bot/tag_bd_bot/start_bot.sh` once.
Then check the log:
```
tail -n 30 /home/beudeliverycom/telegram_bot/tag_bd_bot/bot.log
```
Look for `Bot is running and routing orders...`.

## Redeploying a code change
Upload the new `tag_bd_bot.py`. Then run:
```
pkill -f "tag_bd_bot.py"
```
Cron restarts it within a minute. Never use `pkill -f "telegram_bot.py"` for this bot.
That command is the item bot's.

`bot.log` is trimmed by `start_bot.sh` once it passes 10 MB, and the previous 10 MB is
kept as `bot.log.1`.
