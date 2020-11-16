# -*- coding: utf8 -*- 

import telebot
from telebot import types
import time
import logging
import dbworker
import config

bot = telebot.TeleBot(token = config.BOT_TOKEN)
msg_id = config.VERIFICATION_USER
text_example = '\nПример текста:\n\n#продам #новый #dimensions\n\nПродам новый набор Dimensions “Новорожденные котята». Вскрывался из любопытства, все на месте.\nСтоимость: 2000 рублей\nПересылка из Нижнего Новгорода\n\nЖакова Татьна Владимировна\n89527847337'
text_example_simple = '#продам #новый #dimensions\n\nПродам новый набор Dimensions “Новорожденные котята». Вскрывался из любопытства, все на месте.\nСтоимость: 2000 рублей\nПересылка из Нижнего Новгорода\n\nЖакова Татьна Владимировна\n89527847337'
text_task = 'Для публикации лота отправьте одним сообщением нам информацию:\n1️⃣ Название набора\n2️⃣ Комплектация лота (новый набор, вскрыт, остатки и схема, в каком состоянии и тд)\n3️⃣ Цена набора\n4️⃣ Ваши ФИО\n5️⃣ Откуда будет пересылка\n6️⃣ Ваши контактные данные для связи (лучше всего - телефон, по которому вам можно написать в мессенджеры)\n7️⃣ Проставьте подходящие хэштеги к вашему лоту, например #продам #новый #остатки #риолис #dimensions или любой другой производитель вашего набора\n8️⃣ Прикрепите одну фотографию к лоту'

# Включить ведение журнала
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)
logger = logging.getLogger(__name__)

# Клавиатура
keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)
keyboard1.row('Опубликовать', 'Помощь')

keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)
keyboard2.row('Отмена', 'Помощь')
keyboard2.add('Показать пример')

keyboard3 = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)
keyboard3.row('Помощь')

keyboard4 = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard=True)
keyboard4.row('Отмена', 'Помощь')
keyboard4.add('Показать пример')

# Кнопка в сообщении
button1 = types.InlineKeyboardMarkup()
callback_button = types.InlineKeyboardButton(text="Показать пример текста", callback_data="example_text")
button1.add(callback_button)

button2 = types.InlineKeyboardMarkup()
callback_button1 = types.InlineKeyboardButton(text="Опубликовать", callback_data="push")
callback_button2 = types.InlineKeyboardButton(text="Забраковать", callback_data="delete")
callback_button3 = types.InlineKeyboardButton(text="Отправить на доработку", callback_data="edit")
button2.add(callback_button1)
button2.add(callback_button2)
button2.add(callback_button3)


# Отправка сообщения с изменениями клавиатуры
# Херня сделана для того чтобы строчка казалась меньше
def send_message(message, text, type):
	if type == 1:
		bot.send_message(message.chat.id, text, reply_markup = keyboard1)
	else:
		bot.send_message(message.chat.id, text, reply_markup = keyboard2)
	return

# Команды бота
@bot.message_handler(commands=['start'])
def start_message(message):
	state = dbworker.get_current_state(message.chat.id)
	if state == config.States.S_START.value:
		bot.send_message(message.chat.id, 'Приветствуем вас на Ярмарке «Мир Вышивки»! 🚀 Начнем расхомячку?) \n\nЧтобы опубликовать свой набор (лот) нажмите на кнопку ниже ⬇️', reply_markup = keyboard1)
	elif state == config.States.S_SEND.value:
		bot.send_message(message.chat.id, 'Кажется, Вы хотели отправить свой лот, но я не получил, поэтому я до сих пор жду', reply_markup = keyboard2)
	else:  # Под "остальным" понимаем состояние "0" - начало диалога
		bot.send_message(message.chat.id, 'Привет, это бот с автоматической публикацией вашего лота в канал @yarmarka_mirkrestikom', reply_markup = keyboard1)
		dbworker.set_state(message.chat.id, config.States.S_START.value)

@bot.message_handler(commands=['publish'])
def publish_message(message):
	bot.send_message(message.chat.id, text_task, reply_markup = keyboard2)
	bot.send_message(message.chat.id, 'Если вам нужен пример текста - нажмите кнопку', reply_markup = button1)
	dbworker.set_state(message.chat.id, config.States.S_SEND.value)

@bot.message_handler(commands=['example'])
def example_message(message):
	bot.send_photo(chat_id = message.chat.id, photo = 'https://www.itvoru.ru/upload/iblock/b93/b93dbc7f97f20da61d30021b1e7446ec.jpg', caption = text_example_simple)

@bot.message_handler(commands=['help'])
def help_message(message):
	if message.from_user.username == config.USERNAME_ADMIN:
		bot.send_message(message.chat.id, 'У вас правав Администратора. Вы можете одобрять или браковать посты. Бот сам отправит вам лот\n\n Команда:\n/auto - автопубликация', reply_markup = keyboard3)
	else:
		bot.send_message(message.chat.id, 'Я помогаю опубликовать ваши лоты в Телеграм канале @yarmarka_mirkrestikom\n\nВы можете ввести следующие команды:\n\n🚩 /help - помощь\n🚩 /start - начать все с начала\n🚩 /publish - опубликовать лот\n🚩 /example - показать пример\n🚩 /cancel - отмена\n\n🚩 #bug <сообщение> - сообщить об ошибке\n🚩 #propos <сообщение> - предложение по улучшению\n🚩 #info <сообщение> - хотите нам что-то сообщить? Внимательно слушаем!\n\nПо всем вопросам обращаться к @tanyakurganova', reply_markup = keyboard1)
	dbworker.set_state(message.chat.id, config.States.S_START.value)

@bot.message_handler(commands=['cancel'])
def cancel_message(message):
	bot.send_message(message.chat.id, 'Отмена действия, я могу помощь еще с чем-нибудь?', reply_markup = keyboard1)
	dbworker.set_state(message.chat.id, config.States.S_START.value)

@bot.message_handler(commands=['auto'])
def auto_message(message):
	if message.from_user.username == config.USERNAME_ADMIN:
		state = dbworker.get_current_state(0)
		print("state " + state)
		text = '123'
		if state == "0":
			text = 'Автопубликация ON'
			state = "1"
		else:
			text = 'Автопубликация OFF'
			state = "0"
		if dbworker.set_state(0, state):
			bot.send_message(message.chat.id, text, reply_markup = keyboard1)
		else: 
			bot.send_message(message.chat.id, 'Что-то не так. ', reply_markup = keyboard1)
		dbworker.set_state(message.chat.id, config.States.S_START.value)
	else:
		send_text(message)


# Обработка сообщений
@bot.message_handler(content_types=['text'])
def send_text(message):
	msg_text = message.text.lower()
	state = dbworker.get_current_state(message.chat.id)
	# Команды админа
	if message.from_user.username == config.USERNAME_ADMIN:
		if state == config.States.S_REWRITE.value:
			global msg_id
			send_message(message, 'Комментарий записан и отправлен', 1)
			bot.send_message(int(msg_id), 'Комментарий от Администратора:\n' + str(message.text))
			msg_id = config.VERIFICATION_USER
			dbworker.set_state(message.chat.id, config.States.S_START.value)
		else:
			if msg_text == 'помощь':
				help_message(message)
			elif msg_text == 'авто':
				auto_message(message)
			else:
				help_message(message)
	# Команды пользователей
	else:
		if message.text.find('#bug',0,len(message.text)) >= 0 or message.text.find('#info',0,len(message.text)) >= 0 or message.text.find('#propos',0,len(message.text)) >= 0:
			name = (str(message.from_user.first_name) + " " + str(message.from_user.last_name), "@" + str(message.from_user.username))[message.from_user.username != None]
			bot.send_message(message.chat.id, 'Спасибо за информацию!', reply_markup = keyboard1)
			bot.send_message(chat_id = config.VERIFICATION_USER, text =  'from:\n' + name + '\n\ntext:\n' + str(message.text))
			dbworker.set_state(message.chat.id, config.States.S_START.value)
		else:
			if state == config.States.S_START.value:
				if msg_text == 'привет':
					send_message(message, 'Привет, опубликуем лот?', 1)
				elif msg_text == 'помощь':
					help_message(message)
				elif msg_text == 'показать пример':
					example_message(message)
				elif msg_text == 'опубликовать' or msg_text == 'да' or msg_text ==  'давай':
					publish_message(message)
				else:
					help_message(message)
			else:
				if msg_text == 'отмена':
					cancel_message(message)
				elif msg_text == 'помощь':
					help_message(message)
				elif msg_text == 'показать пример':
					example_message(message)
				else:
					if dbworker.get_current_state(message.chat.id) == config.States.S_HALF_PHOTO.value:
						name = (str(message.from_user.first_name) + " " + str(message.from_user.last_name), "@" + str(message.from_user.username))[message.from_user.username != None]
						text = name + "\n" + str(message.text)
						photo = dbworker.get_half_state(message.chat.id)
						send_post(message, photo, text)
						dbworker.set_half_state(message.chat.id, None)
						dbworker.set_state(message.chat.id, config.States.S_START.value)
					elif dbworker.get_current_state(message.chat.id) == config.States.S_HALF_TEXT.value:
						bot.send_message(message.chat.id, 'Текст перезаписана, остался картинка', reply_to_message_id = message.message_id, reply_markup = keyboard2)
						dbworker.set_half_state(message.chat.id, message.text)
					else:
						bot.send_message(message.chat.id, 'Текст есть, осталась картинка', reply_to_message_id = message.message_id, reply_markup = keyboard2)
						dbworker.set_half_state(message.chat.id, message.text)
						# send_message(message, 'Напоминаю. ' + text_task, 2)
						dbworker.set_state(message.chat.id, config.States.S_HALF_TEXT.value)

# Обработка картинки
@bot.message_handler(content_types=['photo'],
					 func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND.value or  dbworker.get_current_state(message.chat.id) == config.States.S_HALF_TEXT.value or dbworker.get_current_state(message.chat.id) == config.States.S_HALF_PHOTO.value)
def send_new_posts_photo(message):
	if message.caption == None and dbworker.get_current_state(message.chat.id) == config.States.S_SEND.value:
		bot.send_message(message.chat.id, 'Картинка есть, остался текст', reply_to_message_id = message.message_id, reply_markup = keyboard2)
		# send_message(message, 'Напоминаю. ' + text_task, 2)
		dbworker.set_half_state(message.chat.id, message.photo[0].file_id)
		dbworker.set_state(message.chat.id, config.States.S_HALF_PHOTO.value)
	elif message.caption == None and dbworker.get_current_state(message.chat.id) == config.States.S_HALF_PHOTO.value:
		bot.send_message(message.chat.id, 'Картинка перезаписана, остался текст', reply_to_message_id = message.message_id, reply_markup = keyboard2)
		# send_message(message, 'Напоминаю. ' + text_task, 2)
		dbworker.set_half_state(message.chat.id, message.photo[0].file_id)
		dbworker.set_state(message.chat.id, config.States.S_HALF_PHOTO.value)
	else:
		try:
			name = (str(message.from_user.first_name) + " " + str(message.from_user.last_name), "@" + str(message.from_user.username))[message.from_user.username != None]
			if message.caption == None:
				message.caption = dbworker.get_half_state(message.chat.id)
			text = name + "\n" + str(message.caption)
			send_post(message, message.photo[0].file_id, text)
			dbworker.set_half_state(message.chat.id, None)
			dbworker.set_state(message.chat.id, config.States.S_START.value)
		except Exception as e:
			print(e)
			send_message(message, 'Что-то не так. Попробуйте еще раз', 2)
	return
	
@bot.message_handler(content_types=['photo'],
					 func=lambda message: dbworker.get_current_state(message.chat.id) != config.States.S_SEND.value)
def send_photo(message):
	send_message(message, 'Вы хотите опубликовать лот? \nНапишите \'Опубликовать\' или введите команду /publish', 1)
	return


def send_post(message, _photo, _text):
	if dbworker.get_current_state(0) == "1":
		bot.send_photo(chat_id = config.CHANNEL_NAME, photo = _photo, caption = _text)
		time.sleep(1)	
		bot.send_message(message.chat.id, 'Ваш лот опубликован в канале 😎👌🏼', reply_to_message_id = message.message_id, reply_markup = keyboard1)
	else:
		bot.send_photo(chat_id = config.VERIFICATION_USER, photo = _photo, caption = str(message.chat.id) + "\n" + _text, reply_markup = button2)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Отправлено на проверку', reply_to_message_id = message.message_id, reply_markup = keyboard1)



# Обработка кнопок в сообщении
# В большинстве случаев целесообразно разбить этот хэндлер на несколько маленьких
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	# Если сообщение из чата с ботом
	if call.message:
		if call.data == "example_text":
			bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_example)
		elif call.data == "push":
			try:
				msg = call.message.caption.split(maxsplit=1) # [0] - chat_id [1] - text 
				bot.send_photo(chat_id = config.CHANNEL_NAME,  photo = call.message.photo[0].file_id, caption = msg[1])
				time.sleep(1)
				bot.send_message(call.message.chat.id, 'Опубликовано', reply_to_message_id = call.message.message_id, reply_markup = keyboard1)
				bot.send_message(int(msg[0]), 'Опубликовано', reply_markup = keyboard1)
			except:
				send_message(call.message, 'Что-то не так. Попробуйте еще раз', 1)
			return
		elif call.data == "delete":
			msg = call.message.caption.split(maxsplit=1) # [0] - chat_id [1] - text 
			bot.send_message(int(msg[0]), 'Забраковано', reply_markup = keyboard1)
		elif call.data == "edit":
			global msg_id
			msg = call.message.caption.split(maxsplit=1) # [0] - chat_id [1] - text 
			msg_id = msg[0]
			bot.send_message(call.message.chat.id, 'Введите коментарий', reply_markup = keyboard1)
			dbworker.set_state(call.message.chat.id, config.States.S_REWRITE.value)
	# Если сообщение из инлайн-режима
	# НО! Это не включено -> не работает
	elif call.inline_message_id:
		if call.data == "test":
			bot.edit_message_text(inline_message_id=call.inline_message_id, text="Бдыщь")

@bot.message_handler(content_types=['sticker', 'audio', 'document', 'video', 'video_note', 'voice', 'location', 'contact', 'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'])
def sticker_id(message):
    help_message(message)

if __name__ == "__main__":
	bot.infinity_polling()