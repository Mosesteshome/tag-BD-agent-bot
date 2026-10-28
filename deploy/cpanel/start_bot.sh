#!/bin/bash
# Keep-alive launcher for the tag-BD bot, run by cron every minute. Same pattern
# as /home/beudeliverycom/telegram_bot/start_bot.sh (item-check bot).
# Fill in the values below with File Manager's editor, not a Terminal heredoc.
#
#   bash start_bot.sh          start the bot if it is not already running
#   bash start_bot.sh check    test the token and both DB connections, then exit

BOT_DIR=/home/beudeliverycom/telegram_bot/tag_bd_bot
# Own plain venv on purpose: the item bot's cPanel venv python is a wrapper that
# loads Setup Python App's env vars (item bot token/DB) over these exports.
PYTHON_BIN=$BOT_DIR/venv/bin/python

export TELEGRAM_BOT_TOKEN="PUT_TAG_BOT_TOKEN_HERE"
# Business DB (read-only, restaurants table) - same RDS reader the item bot uses
export DATABASE_URL="mysql+aiomysql://analyst:PASSWORD@RDS_READER_HOST:3306/beu"
# Bot's own DB (user_info + bd_replies tables)
export SQL_DATABASE_URL="mysql+aiomysql://USER:PASSWORD@localhost:3306/DBNAME"

cd "$BOT_DIR" || exit 1

if [ "$1" = "check" ]; then
    exec "$PYTHON_BIN" check_bot.py
fi

# Keep bot.log under ~10 MB (the previous 10 MB is kept as bot.log.1)
if [ -f bot.log ] && [ "$(stat -c %s bot.log)" -gt 10485760 ]; then
    cp bot.log bot.log.1 && : > bot.log
fi

# The script is named tag_bd_bot.py (not telegram_bot.py) so this check and the
# item bot's `pgrep/pkill -f "telegram_bot.py"` never match each other.
if ! pgrep -f "tag_bd_bot\.py" > /dev/null; then
    nohup "$PYTHON_BIN" -u tag_bd_bot.py >> bot.log 2>&1 &
fi
