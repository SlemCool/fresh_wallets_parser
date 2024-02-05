import csv
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

from config import app_logger

load_dotenv()


API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

phone = "Kagadi_a"
TARGET_GROUP = "Fresh Wallets Tracker SOLANA"

if __name__ == "__main__":
    client = TelegramClient(phone, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")
    client.start()

    chats = []
    last_date = None
    size_chats = 200
    groups = []

    result = client(
        GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=size_chats,
            hash=0,
        )
    )
    chats.extend(result.chats)

    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue

    print("Выберите номер группы из перечня:")
    i = 1
    for g in groups:
        print(str(i) + " - " + g.title)
        i += 1

    g_index = input("Введите нужную цифру: ")
    target_group = groups[int(g_index) - 1]

    print("Узнаём пользователей...")
    all_participants = []
    all_participants = client.get_participants(target_group)

    print("Сохраняем данные в файл...")
    with open("members.csv", "w", encoding="UTF-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(["username", "name", "group"])
        for user in all_participants:
            if user.username:
                username = user.username
            else:
                username = ""
            if user.first_name:
                first_name = user.first_name
            else:
                first_name = ""
            if user.last_name:
                last_name = user.last_name
            else:
                last_name = ""
            if user.phone:
                user_phone = user.phone
            else:
                user_phone = ""
            name = (first_name + " " + last_name).strip()
            writer.writerow([username, name, user_phone, target_group.title])
    print("Парсинг участников группы успешно выполнен.")

    # dialogs = client.get_dialogs()
    # for dialog in dialogs:
    #     if dialog.name == TARGET_GROUP:
    #         for message in dialog.messages:
    #             print(message)
