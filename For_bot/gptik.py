import logging
from for_SQL import SQL
import requests
import telebot
from telebot import types
import config
import nou
from transformers import AutoTokenizer

bot = telebot.TeleBot(token=config.token)
answer = ''
user = {}
max_tokens_in_task = 2048
system_content = {}
task = ''
sql = SQL()
assistant_content = 'Ответь на вопрос:'

def count_tokens(text):
    tokenizer = AutoTokenizer.from_pretrained("rhysjones/phi-2-orange")  # название модели
    return len(tokenizer.encode(text))



@bot.message_handler(commands=['help'])
def help_function(message):
    user_id = message.chat.id
    bot.send_message(user_id, text='С помощью команд: \n'
                                   '/solve_task - можно задать роль боту \n'
                                   '/continue - бот продолжит формулировать ответ')

#обработка команды start
@bot.message_handler(commands=['start'])
def start_function(message):
    #создание таблицы и бд с помощью функций
    sql.create_db()
    sql.create_table()

    #имя пользователя сохраняется в переменных
    user_name = message.from_user.first_name

    keyboard = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton(text='Начать!', callback_data='button_1')
    keyboard.add(but1)
    bot.send_message(message.chat.id, text=f"Приветствую тебя, {user_name}!", reply_markup=keyboard)

    #переход к следующей функции
    bot.register_next_step_handler_by_chat_id(message, subject)



@bot.callback_query_handler(func=lambda call: call.data == 'button_1')
def subject(message):
    user_id = message.from_user.id
    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton('Химия')
    button_2 = types.KeyboardButton('Физика')
    keyboard.row(button_1, button_2)
    bot.send_message(user_id, text="Выбери интересующий тебя предмет:", reply_markup=keyboard)

    bot.register_next_step_handler_by_chat_id(message, level)



@bot.message_handler()
def level(message):
    user_id = message.from_user.id
    text = message.text

    if text == 'Химия':
        sql.update_data(user_id, 'subject', 'химия')
    else:
        sql.update_data(user_id, 'subject', 'физика')

    system_content[user_id] = (f"Ты - дружелюбный помощник для решения задач по {text}."
                               f" Давай подробный ответ с решением на русском языке")

    keyboard = types.ReplyKeyboardMarkup()
    button_1 = types.KeyboardButton(text='Начинающий')
    button_2 = types.KeyboardButton(text='Профессионал')
    keyboard.add(button_1, button_2)
    bot.send_message(user_id, text='Выбери уровень:', reply_markup=keyboard)


    bot.register_next_step_handler(message, solve_task)

@bot.message_handler()
def solve_task(message):
    user_id = message.from_user.id
    if message.text == 'Начинающий':
        sql.update_data(user_id, 'level', 'Начинающий')
    else:
        sql.update_data(user_id, 'level', 'Профессионал')

    text = message.text
    system_content[user_id] += f"Объясняй макисмально подробно и понятно для {text}"
    bot.send_message(user_id, text="Введи свой вопрос.")
    bot.register_next_step_handler(message, get_promtss)


# обработка действий для состояния "Получение ответа"
def get_promtss(message):
    user_id = message.chat.id
    # убеждаемся, что получили текстовое сообщение, а не что-то другое
    if message.content_type != "text":
        bot.send_message(chat_id=message.chat.id, text="Отправь ответ текстовым сообщением")
        # регистрируем следующий "шаг" на эту же функцию
        bot.register_next_step_handler_by_chat_id(message, get_promtss)
        return
    # получаем сообщение-промтом, сохраняем его в таблице
    user_text = message.text
    sql.update_data(user_id, 'task', f'{user_text}')
    sql.update_data(user_id, 'answer', '')

    #проверка количества токенов в сообщении от пользователя (промте)
    if count_tokens(message.text) > max_tokens_in_task:
        bot.send_message(chat_id=message.chat.id, text="Сообщение слишком большое! Напиши вопрос короче")
        bot.register_next_step_handler_by_chat_id(message, get_promtss)
        return

    bot.send_message(chat_id=message.chat.id, text="Ожидай ответ!")

    bot.register_next_step_handler_by_chat_id(user_id, answer_function)
    # дальше идет обработка промта и отправка результата

#Команда, присылающая ответ от нейросети
@bot.message_handler(commands=['answer'])
def answer_function(call):
    user_id = call.message_id
    result = sql.select_info(user_id)
    user_promt = result['task']
    answer = user[user_id]['answer']
    try:
        #запрос к нейросети
        resp = requests.post(
            'http://158.160.135.104:1234/v1/chat/completions',            #ПОМЕНЯТЬ
            headers={"Content-Type": "application/json"},

            json={
                "messages": [
                    {"role": "system", "content": system_content[user_id]},
                    {"role": "user", "content": user_promt},
                    {"role": "assistant", "content": answer},
                ],
                "temperature": 1,
                "max_tokens": 2048
            }
        )
        #обработка ошибок
        if resp.status_code == 200 and 'choices' in user[user_id]['resp'].json():
            result = resp.json()['choices'][0]['message']['content']

        #создание клавиатуры
        keyboard = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton(text='Закончить', callback_data='button1')
        button_2 = types.InlineKeyboardButton(text='Продолжить генерацию', callback_data='button2')
        keyboard.add(button_1, button_2)
        bot.send_message(call.message.chat.id, text=result, reply_markup=keyboard)

        if call.data != 'button2':
            #удаление ненужного
            sql.delete(user_id)

            #возвращение к началу
            bot.register_next_step_handler(call, subject)
        else:
            user[user_id]['answer'] += user[user_id]['result']
            return
    except:
        logging.error(
            f"Не удалось сгенерировать, код состояния {resp.status_code}"
        )
        bot.reply_to(
            call,
            f"Извини, я не смог сгенерировать для тебя ответ сейчас",
        )


bot.polling()
