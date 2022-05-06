from telegram import ReplyKeyboardMarkup

TOKEN = '5388230660:AAHA8MHORuTOXIvc6CXDr2wAW1f0yd1o61U'
ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
LETTER_QUESTIONS = ['Ваша буква?', 'Какую букву назовёте?', 'Буква?', 'Букву в студию\!']
WHITELIST = ['1009462304']
SERVER_GROUP_ID = -1001687577422
GAMECHOOSE_MARKUP = ReplyKeyboardMarkup([['5', 'Поле Чудес']], resize_keyboard=True)
GAMEMODE_MARKUP = ReplyKeyboardMarkup([['Групповой', 'Одиночный']], resize_keyboard=True)
FIVEROOMCASE_MARKUP = ReplyKeyboardMarkup([['1', '2', '3'], ['4', 'Случайный', '5']], resize_keyboard=True)
CASES, FIVE_EXERCISES = 5, 25
FOFD_EXERCISES = 5
