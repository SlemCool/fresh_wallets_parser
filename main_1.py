from dotenv import load_dotenv
import os
from telethon import TelegramClient, events, sync

load_dotenv()


API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

phone = "Kagadi_a"
TARGET_GROUP = "Fresh Wallets Tracker SOLANA"
client = TelegramClient(phone, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")

client.download_profile_photo('me')


@client.on(events.NewMessage(chats=("Проект по API. ЯП")))
async def normal_handler(event):
    #    print(event.message)
    user_mess = event.message.to_dict()["message"]

    s_user_id = event.message.to_dict()["from_id"]
    user_id = int(s_user_id)
    user = d.get(user_id)

    mess_date = event.message.to_dict()["date"]

    f.write(mess_date.strftime("%d-%m-%Y %H:%M") + "\n")
    f.write(user + "\n")
    f.write(user_mess + "\n\n")

    f.flush()


client.start()

group = "group_name"

participants = client.get_participants(group)
users = {}

for partic in client.iter_participants(group):
    lastname = ""
    if partic.last_name:
        lastname = partic.last_name
    users[partic.id] = partic.first_name + " " + lastname

f = open("messages_from_chat", "a")

client.send_message('kagadi_a', 'Hello! Talking to you from Telethon')

client.run_until_disconnected()
f.close()
