# Author: Tinkering-Around

import telebot
import config
import time

bot = telebot.TeleBot(config.TOKEN)

questions = ["Order Description:", "Payment type:", "Deadline:", "Confirmation of Payment(Picture Only):"]
answers = []
last_pinned_message = None

@bot.message_handler(commands=['start'])
def welcome(message):
    global last_pinned_message
    last_pinned_message = None  # reset the last pinned message
    answers.clear()  # clear the previous saved messages
    ask_question(message, 0, [message.message_id])  # pass the '/start' message id

def ask_question(message, question_index, message_ids):
    if question_index < len(questions):
        msg = bot.send_message(message.chat.id, questions[question_index])
        message_ids.append(msg.message_id)  # save the bot's message id
        if question_index == len(questions) - 1:  # if it's the last question
            bot.register_next_step_handler(msg, handle_picture, message_ids)
        else:
            bot.register_next_step_handler(msg, handle_answer, message_ids, question_index)
    else:
        # join the questions and answers into a single text
        answer_text = "\n".join(f"{q} {a}" for q, a in zip(questions, answers))
        # delete the entire conversation starting at '/start'
        for msg_id in message_ids:
            bot.delete_message(message.chat.id, msg_id)

def handle_answer(message, message_ids, question_index):
    answers.append(message.text)  # save the user's answer
    message_ids.append(message.message_id)  # save the user's message id
    time.sleep(1)  # wait for a second before asking the next question to ensure messages are deleted
    ask_question(message, question_index + 1, message_ids)

def handle_picture(message, message_ids):
    global last_pinned_message
    if message.content_type == 'photo':
        # join the questions and answers into a single text
        caption_text = "\n".join(f"{q} {a}" for q, a in zip(questions, answers))
        # get the photo id
        photo_id = message.photo[-1].file_id
        # send the photo again with the caption
        msg = bot.send_photo(message.chat.id, photo_id, caption=caption_text)
        # pin the message
        bot.pin_chat_message(message.chat.id, msg.message_id)
        last_pinned_message = msg.message_id  # update the last pinned message
        # delete the original picture sent by the user
        bot.delete_message(message.chat.id, message.message_id)
    # delete the entire conversation starting at '/start'
    for msg_id in message_ids:
        bot.delete_message(message.chat.id, msg_id)

@bot.message_handler(commands=['cancel'])
def cancel(message):
    global last_pinned_message
    # send a message that the order was cancelled
    msg = bot.send_message(message.chat.id, "The order was cancelled.")
    # pin the message
    bot.pin_chat_message(message.chat.id, msg.message_id)
    last_pinned_message = msg.message_id  # update the last pinned message

bot.polling(none_stop=True)