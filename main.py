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
QUANTITY_SOL = float(config.get("DEFAULT", "quantity_sol"))
QUANTITY_DEALS = int(config.get("DEFAULT", "quantity_deals"))
LP_FLAG = config.get("DEFAULT", "lp").lower()
MINT_FLAG = config.get("DEFAULT", "mint").lower()
FREEZE_FLAG = config.get("DEFAULT", "freeze").lower()

# API_ID = os.getenv("API_ID")
# API_HASH = os.getenv("API_HASH")
# TARGET_USER = "JLeagua_bot"
# TARGET_GROUP = "FreshWallets_Tracker_SOL"

API_ID = config.get("USER", "api_id")
API_HASH = config.get("USER", "api_hash")
TARGET_USER = config.get("DIRECTION", "target_user")
TARGET_GROUP = config.get("FROM", "target_chat")

REGEX_DICT = {
    "quantity_sol": r"(?<=swapped )(?P<sol>.*?)(?= SOL)",
    "token_address": r"(?<=Token Address: )(?P<tok_adr>.*)(?=\n)",
    "lp_flag": r"(?<=LP: .)(?P<lp_flag>\w*)(?=.\n)",
    "mint_flag": r"(?<=Mint: .)(?P<mint_flag>\w*)(?=.\n)",
    "freeze_flag": r"(?<=Freeze: .)(?P<frz_flag>\w*)(?=.\n)",
}

data = {}
client = TelegramClient("Kagadi_a", API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")


async def parse_message(message):
    message_data = []
    for values in REGEX_DICT.values():
        element = re.search(values, message)
        if element:
            message_data.append(element[0])
        else:
            message_data.append(element)
    return message_data


async def check_data(data):
    check_series = {
        "time": int(time.time()) - data["timestamp"] <= TIME_DELTA,
        "sol": QUANTITY_SOL <= data["count_sol"],
        "lp": LP_FLAG == data["lp_flag"],
        "mint": MINT_FLAG == data["mint_flag"],
        "freeze": FREEZE_FLAG == data["freeze_flag"],
        "deals": QUANTITY_DEALS <= data["count_deals"],
    }
    return all(check_series.values())


async def update_data(new_data):
    token = new_data[1]
    data[token]["count_sol"] = data[token]["count_sol"] + float(new_data[0])
    data[token]["count_deals"] += 1


async def clean_data():
    if data:
        for key in list(data):
            if int(time.time()) - data[key]["timestamp"] >= TIME_DELTA:
                del data[key]


@client.on(events.NewMessage(chats=TARGET_GROUP))
async def normal_handler(event):
    await clean_data()
    message = await parse_message(event.message.to_dict()["message"])
    if all(message):
        token = message[1]

        if token not in data:
            meta_data = {
                "timestamp": int(time.time()),
                "count_sol": float(message[0]),
                "lp_flag": message[2].lower(),
                "mint_flag": message[3].lower(),
                "freeze_flag": message[4].lower(),
                "count_deals": 1,
            }
            data[token] = meta_data
        else:
            await update_data(message)

        if await check_data(data[token]):
            await client.send_message(TARGET_USER, ", ".join(message))
    else:
        print(message)
    for key in data.keys():
        print(f"{key} - {data[key]}")
    print("\n--------------------------------\n")


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
