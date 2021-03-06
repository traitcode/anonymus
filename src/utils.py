import storage
from string import Template
from telegram import ChatMember, TelegramError, InlineKeyboardButton, InlineKeyboardMarkup, TelegramError, MessageEntity
import logging
import time


def get_timestamp():
    return int(time.time())


def admins_only(f, bot, *largs):
    def anonymized(update, context, *largs):
        if storage.is_admin(update.message.from_user.id):
            f(update, context, *largs)
        else:
            update.message.reply_text(storage.get_string("USER_NOT_ADMIN"))
    return anonymized


def send_to_admins(message, bot, **kwargs):
    for admin in storage.get_admin_set():
        try:
            bot.send_message(
                admin,
                message,
                **kwargs,
            )
        except TelegramError as err:
            logging.error("Got telegram error: " + err.message)


def send_to_manager(message, bot, **kwargs):
    try:
        bot.send_message(
            storage.get_bot_manager(),
            message,
            **kwargs,
        )
    except TelegramError as err:
        logging.error("Got telegram error: " + err.message)


def user_is_in_group(user_id, bot):
    try:
        chat = bot.get_chat_member(storage.get_target_chat(), user_id)
        return chat.status != ChatMember.LEFT and chat.status != ChatMember.KICKED and chat.status != ChatMember.RESTRICTED
    except TelegramError as e:
        return False


def strip_message_cmd(text):
    pos = text.find(' ')
    if pos == -1:
        return ''
    else:
        return text[pos:].strip()


def get_username(user_id, bot):
    try:
        chat = bot.get_chat_member(storage.get_target_chat(), user_id)
        user = chat.user
        if user.username != None:
            return "@" + user.username
        else:
            user_name = user.first_name + \
                (" " + user.last_name if user.last_name else "")
            telegram_html = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
            return telegram_html
    except TelegramError as e:
        logging.error(
            "Error trying to get the chat member with id " + user_id + ": " + e.message)
    return "UsernameNotFound"


def make_report_keyboard(id):
    data = "report,%d, %d" % (id, get_timestamp())
    keyboard = [[
        InlineKeyboardButton(storage.get_string("REPORT"),
                             callback_data=data)
    ]]
    return InlineKeyboardMarkup(keyboard)


def make_admin_keyboard(id, reporter, message_id):
    data = "ban,%s,%s" % (id, message_id)
    buttons = [[
        InlineKeyboardButton(storage.get_string(
            "WARN_REPORTER"), callback_data="warn,%s,%s,0" % (reporter, message_id)),
        InlineKeyboardButton(storage.get_string(
            "BAN"), callback_data=data),
        InlineKeyboardButton(storage.get_string(
            "WARN_AUTHOR"), callback_data="warn,%s,%s,1" % (id, message_id)),
    ]]
    return InlineKeyboardMarkup(buttons)


def strip_unwanted_chars(string):
    char_map = {
        '&': "&amp;",
        '<': "&lt;",
        '>': "&gt;",
    }
    for char in char_map:
        string = string.replace(char, char_map[char])
    return string


def format_message(message):
    # Read the fucking API documentation next time, Crax
    return message.text_html
