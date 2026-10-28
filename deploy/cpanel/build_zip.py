"""Build tag_bd_bot-cpanel.zip from the repo's telegram_bot.py + this kit.

Run: python deploy/cpanel/build_zip.py   (output goes in this folder, git-ignored)
The bot's telegram_bot.py is shipped as tag_bd_bot.py; see DEPLOY.md for why.
"""
import os
import zipfile

KIT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(KIT))
OUT = os.path.join(KIT, "tag_bd_bot-cpanel.zip")

FILES = {
    # zip path: source path
    "tag_bd_bot/tag_bd_bot.py": os.path.join(REPO, "telegram_bot.py"),
    "tag_bd_bot/start_bot.sh": os.path.join(KIT, "start_bot.sh"),
    "tag_bd_bot/check_bot.py": os.path.join(KIT, "check_bot.py"),
    "tag_bd_bot/create_tables.sql": os.path.join(KIT, "create_tables.sql"),
    "tag_bd_bot/DEPLOY.md": os.path.join(KIT, "DEPLOY.md"),
}

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for arcname, src in FILES.items():
        with open(src, "rb") as f:
            data = f.read().replace(b"\r\n", b"\n")
        if data.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf")) or b"\x00" in data:
            raise SystemExit(f"{src} is not plain UTF-8 (BOM/UTF-16); re-save it first")
        info = zipfile.ZipInfo(arcname, date_time=(2026, 10, 13, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3  # unix, so permissions below are honoured
        mode = 0o755 if arcname.endswith(".sh") else 0o644
        info.external_attr = (0o100000 | mode) << 16
        z.writestr(info, data)

print(OUT)
