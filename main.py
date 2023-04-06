import random
from telethon import TelegramClient, events
import sqlite3
import time

# создаем базу данных
conn = sqlite3.connect('kust_bot.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS kust_results
             (user_id integer, result integer)''')
c.execute('''CREATE TABLE IF NOT EXISTS kust_users
             (user_id integer, last_used_time integer)''')
conn.commit()

# установка параметров
api_id = 25308460
api_hash = '8f751ec587817fd74e48606658cdba2d'
bot_token = '6279713803:AAERRvX4UCmo6CmIOYPREHRFVl-b9BLMgMk'
client = TelegramClient('kust_bot_session', api_id, api_hash).start(bot_token=bot_token)

# обработчик команды /kust
@client.on(events.NewMessage(pattern='/kust'))
async def kust_handler(event):
    # проверяем, было ли сообщение отправлено в группу
    if event.is_group:
        # получаем последнее время использования команды /kust
        last_used_time = get_last_used_time(event.sender_id)

        # проверяем, прошло ли уже 10 часов с момента последнего использования команды
        if last_used_time is not None and time.time() - last_used_time < 10 * 60 * 60:
            # если прошло менее 10 часов, отправляем сообщение об ошибке
            await event.respond("Вы уже использовали команду /kust менее 10 часов назад. Попробуйте еще раз позже.")
        else:
            # если прошло 10 часов или это первое использование команды, генерируем случайное число и добавляем к общему результату
            result = random.randint(-5, 10)
            user_id = event.sender_id
            c.execute("INSERT INTO kust_results (user_id, result) VALUES (?, ?)", (user_id, result))
            conn.commit()
            update_last_used_time(user_id, time.time())

            # отправляем сообщение с результатом
            message = f"@{event.sender.username}, вы полили куст ежевики и он изменился на - {result} см. Рост куста - {get_total_result()}."
            await event.respond(message)

# функции для работы с базой данных
def get_last_used_time(user_id):
    c.execute("SELECT last_used_time FROM kust_users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result is not None:
        return result[0]
    else:
        return None

def update_last_used_time(user_id, last_used_time):
    c.execute("INSERT OR REPLACE INTO kust_users (user_id, last_used_time) VALUES (?, ?)", (user_id, last_used_time))
    conn.commit()

# функция для получения общего результата
def get_total_result():
    c.execute("SELECT sum(result) FROM kust_results")
    result = c.fetchone()[0]
    return result if result else 0

@client.on(events.NewMessage(pattern='/stat'))
async def kust_handler(event):

    message = f"@{event.sender.username}, Рост вашего куста - {get_total_result()}."
    await event.respond(message)

@client.on(events.NewMessage(pattern='/start'))
async def kust_handler(event):

    message = f"Привет, @{event.sender.username}! С помощью этого бота вы можете вырастить свой куст ежевики. Чтобы начать напишите /kust.\nЧтобы узнать свой результат напишите /stat\nИспользовать команду можно раз в 10 часов."
    await event.respond(message)

# запускаем клиента
client.run_until_disconnected()
