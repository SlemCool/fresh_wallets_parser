import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events, sync

load_dotenv()


API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

phone = "Kagadi_a"
TARGET_GROUP = "FreshWallets_Tracker_SOL"
client = TelegramClient(phone, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")

REGEX_DICT = {
    "quantity_sol": r"(?<=swapped )(?P<sol>.*)(?= SOL)",
    "token_address": r"(?<=Token Address: )(?P<tok_adr>.*)(?=\n)",
    "lp_flag": r"(?<=LP: .)(?P<lp_flag>\w*)(?=.\n)",
    "mint_flag": r"(?<=Mint: .)(?P<mint_flag>\w*)(?=.\n)",
    "freeze_flag": r"(?<=Freeze: .)(?P<frz_flag>\w*)(?=.\n)",
}

# client.start()

# for dialog in client.iter_dialogs():
#     print(dialog.title)


@client.on(events.NewMessage(chats=TARGET_GROUP))
async def normal_handler(event):
    # print(event.message.to_dict()['message'])
    user_mess = event.message.to_dict()["message"]
    result = []
    for key, values in REGEX_DICT.items():
        result.append(re.search(values, user_mess)[0])
    print(float(result[0]))
    # if result:
    #     print(result[0])
    
    # await client.send_message('don_pahom', user_mess)

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
