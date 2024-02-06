import configparser
import os
import re
import time

from dotenv import load_dotenv
from telethon import TelegramClient, events, sync

load_dotenv()
config = configparser.ConfigParser()
config.read("settings.ini")

TIME_DELTA = int(config.get("DEFAULT", "time_delta"))
QUANTITY_SOL = int(config.get("DEFAULT", "quantity_sol"))
LP_FLAG = config.get("DEFAULT", "lp")
MINT_FLAG = config.get("DEFAULT", "mint")
FREEZE_FLAG = config.get("DEFAULT", "freeze")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

TARGET_USER = "JLeagua_bot"
TARGET_GROUP = "FreshWallets_Tracker_SOL"

REGEX_DICT = {
    "quantity_sol": r"(?<=swapped )(?P<sol>.*)(?= SOL)",
    "token_address": r"(?<=Token Address: )(?P<tok_adr>.*)(?=\n)",
    "lp_flag": r"(?<=LP: .)(?P<lp_flag>\w*)(?=.\n)",
    "mint_flag": r"(?<=Mint: .)(?P<mint_flag>\w*)(?=.\n)",
    "freeze_flag": r"(?<=Freeze: .)(?P<frz_flag>\w*)(?=.\n)",
}

data = {}
client = TelegramClient("Kagadi_a", API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")

print(int(time.time()))
current_time = time.time()
formatted_time = time.ctime(current_time)
print(formatted_time)

# client.start()
# for dialog in client.iter_dialogs():
#     print(dialog.title)


async def parse_message(message):
    message_data = []
    for values in REGEX_DICT.values():
        message_data.append(re.search(values, message)[0])
    return message_data


@client.on(events.NewMessage(chats=TARGET_GROUP))
async def normal_handler(event):
    message = await parse_message(event.message.to_dict()["message"])
    if all(message):
        print(message)
        timestamp = int(time.time())
        meta_data = {
            "timestamp": timestamp,
            "count_sol": message[0],
            "lp_flag": message[2],
            "mint_flag": message[3],
            "freeze_flag": message[4],
        }
        data.setdefault(message[1], meta_data)
    print(data)
    # if result:
    #     print(result[0])

    await client.send_message(TARGET_USER, " ".join(message))

    # s_user_id = event.message.to_dict()["from_id"]
    # user_id = int(s_user_id)
    # user = d.get(user_id)

    # mess_date = event.message.to_dict()["date"]

    # f.write(mess_date.strftime("%d-%m-%Y %H:%M") + "\n")
    # f.write(user + "\n")
    # f.write(user_mess + "\n\n")

    # f.flush()


client.start()

client.run_until_disconnected()
