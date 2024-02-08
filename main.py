import configparser
import re
import time

from telethon import TelegramClient, events

from config import app_logger

logger = app_logger.get_logger(__name__)

logger.info("Загружаем настройки...")
config = configparser.ConfigParser()
config.read("settings.ini", encoding="utf-8")

TIME_DELTA = int(config.get("DEFAULT", "time_delta"))
QUANTITY_SOL = float(config.get("DEFAULT", "quantity_sol"))
QUANTITY_DEALS = int(config.get("DEFAULT", "quantity_deals"))
LP_FLAG = config.get("DEFAULT", "lp").lower()
MINT_FLAG = config.get("DEFAULT", "mint").lower()
FREEZE_FLAG = config.get("DEFAULT", "freeze").lower()

USER_NAME = config.get("USER", "user_name")
API_ID = config.get("USER", "api_id")
API_HASH = config.get("USER", "api_hash")

TARGET_USER = config.get("DIRECTION", "target_user")
TARGET_CHAT = config.get("FROM", "target_chat")

logger.info("Проверяем настройки для приложения...")
if not all(
    (
        TIME_DELTA,
        QUANTITY_SOL,
        QUANTITY_DEALS,
        LP_FLAG,
        MINT_FLAG,
        FREEZE_FLAG,
        USER_NAME,
        API_ID,
        API_HASH,
        TARGET_USER,
        TARGET_CHAT,
    )
):
    logger.critical("Отсутствует хотя бы одна настройка для приложения")
    raise ValueError("Отсутствует хотя бы одна настройка для приложения!")

REGEX_DICT = {
    "quantity_sol": r"(?<=swapped )(?P<sol>.*?)(?= SOL)",
    "token_address": r"(?<=Token Address: )(?P<tok_adr>.*)(?=\n)",
    "lp_flag": r"(?<=LP: .)(?P<lp_flag>\w*)(?=.\n)",
    "mint_flag": r"(?<=Mint: .)(?P<mint_flag>\w*)(?=.\n)",
    "freeze_flag": r"(?<=Freeze: .)(?P<frz_flag>\w*)(?=.\n)",
}

data = {}
logger.info(f"Открываем сессию в телеграме для: {USER_NAME}")
client = TelegramClient(USER_NAME, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")


async def parse_message(message):
    message_data = []
    logger.info(f"Разбираем сообщение на элементы: {message[:10]}...")
    for values in REGEX_DICT.values():
        element = re.search(values, message)
        if element:
            message_data.append(element[0])
        else:
            message_data.append(element)
    logger.info(f"Возвращаем элементы: {message_data}")
    return message_data


async def check_data(data):
    logger.info(f"Проверяем данные токена на соответствие заданным параметрам: {data}")
    check_series = {
        "time": int(time.time()) - data["timestamp"] <= TIME_DELTA,
        "sol": QUANTITY_SOL <= data["count_sol"],
        "lp": LP_FLAG == data["lp_flag"],
        "mint": MINT_FLAG == data["mint_flag"],
        "freeze": FREEZE_FLAG == data["freeze_flag"],
        "deals": QUANTITY_DEALS <= data["count_deals"],
    }
    logger.info(f"Результаты проверки: {check_series}")
    return all(check_series.values())


async def update_data(new_data):
    token = new_data[1]
    count_deals = data[token]["count_deals"]
    logger.info(f"Обнаружен обновляем информацию для токена: {token}")
    logger.info(
        f"Добавляем SOL: + {new_data[0]}; "
        f"Меняем счетчик сделок с {count_deals} на: {count_deals + 1}"
    )
    data[token]["count_sol"] = data[token]["count_sol"] + float(new_data[0])
    count_deals += 1


async def clean_data():
    logger.info("Проверяем словарь с данными на наличие вышедших из временной дельты")
    if data:
        for key in list(data):
            if int(time.time()) - data[key]["timestamp"] >= TIME_DELTA:
                logger.info(f"Удаляем из отслеживаемых токен: {data[key]}")
                del data[key]


@client.on(events.NewMessage(chats=TARGET_CHAT))
async def normal_handler(event):
    logger.info("Новое сообщение!!")
    if data:
        await clean_data()
    message = await parse_message(event.message.to_dict()["message"])
    if all(message):
        logger.info("Все искомые элементы в сообщении обнаружены")
        token = message[1]
        logger.info("Проверяем токен на наличие в отслеживаемых")
        if token not in data:
            logger.info(f"Токен {token} не обнаружен создаем для него запись")
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
            logger.info(
                f"Нужное событие! Отправляем сообщение пользователю: {TARGET_USER}"
            )
            await client.send_message(TARGET_USER, ", ".join(message))
    else:
        logger.error(f"Не удалось обработать сообщение {message}")


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
