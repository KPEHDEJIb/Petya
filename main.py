import json
import logging
from params import *
from sqlite3 import connect
from random import choice, randint
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)


def group_maker_five(update: Update):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    if len(players_info['available_players']['Five']) >= 2:
        next_group_id = players_info['next_group_id']['Five']

        if next_group_id != 0:
            for i in range(next_group_id + 1):
                if i not in players_info['groups']['Five']:
                    group_id = i
                    break
            else:
                group_id = players_info['next_group_id']['Five']
                players_info['next_group_id']['Five'] += 1
        else:
            group_id = players_info['next_group_id']['Five']
            players_info['next_group_id']['Five'] += 1

        player1_id = str(update.message.from_user.id)
        players_info['available_players']['Five'].remove(player1_id)
        players_info['players_in_play']['Five']['group'][player1_id] = group_id

        player2_id = choice(players_info['available_players']['Five'])
        players_info['available_players']['Five'].remove(player2_id)
        players_info['players_in_play']['Five']['group'][player2_id] = group_id

        players_info['groups']['Five'].append(int(group_id))

        with open(f'data/Five/game/groups/{group_id}.json', 'w', encoding='UTF-8') as f:
            json.dump({'player1': [player1_id, 5], 'player2': [player2_id, 5], 'exer': randint(1, FIVE_EXERCISES)}, f,
                      ensure_ascii=False, indent=2)

        update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n'
                                                         f'Образована сессия со следующими участниками:\n'
                                                         f'{player1_id}, {player2_id}')

        if player1_id not in ['2', '3', '4']:
            update.message.bot.send_message(player1_id, 'Игра началась!')
        if player2_id not in ['2', '3', '4']:
            update.message.bot.send_message(player2_id, 'Игра началась!')

        with open('data/players.json', 'w', encoding='UTF-8') as f:
            json.dump(players_info, f, ensure_ascii=False, indent=2)

        game_group_five_bot(update)


def group_maker_fofd(update: Update):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    exer_id = randint(1, FOFD_EXERCISES)

    with open(f'data/FofD/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    if len(players_info['available_players']['FofD']) >= 2:
        next_group_id = players_info['next_group_id']['FofD']

        if next_group_id != 0:
            for i in range(next_group_id + 1):
                if i not in players_info['groups']['FofD']:
                    group_id = i
                    break
            else:
                group_id = players_info['next_group_id']['FofD']
                players_info['next_group_id']['FofD'] += 1
        else:
            group_id = players_info['next_group_id']['FofD']
            players_info['next_group_id']['FofD'] += 1

        player1_id = str(update.message.from_user.id)
        players_info['available_players']['FofD'].remove(player1_id)
        players_info['players_in_play']['FofD']['group'][player1_id] = group_id

        player2_id = choice(players_info['available_players']['FofD'])
        players_info['available_players']['FofD'].remove(player2_id)
        players_info['players_in_play']['FofD']['group'][player2_id] = group_id

        players_info['groups']['FofD'].append(int(group_id))

        exer_word = exer_info['exer'][0]

        turn1 = choice(['writ', 'wait'])
        turn2 = 'wait' if turn1 == 'writ' else 'writ'

        with open(f'data/FofD/game/groups/{group_id}.json', 'w', encoding='UTF-8') as f:
            json.dump({'player1': [player1_id, turn1], 'player2': [player2_id, turn2],
                       'exer': [exer_id, ['\_' for _ in range(len(exer_word))], []]}, f, ensure_ascii=False, indent=2)

        update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==FOFD->GROUP==\n'
                                                         f'Образована сессия со следующими участниками:\n'
                                                         f'{player1_id} и {player2_id}')

        if player1_id not in ['1', '2', '3', '4']:
            update.message.bot.send_message(player1_id, 'Игра началась!')
        if player2_id not in ['1', '2', '3', '4']:
            update.message.bot.send_message(player2_id, 'Игра началась!')

        with open('data/players.json', 'w', encoding='UTF-8') as f:
            json.dump(players_info, f, ensure_ascii=False, indent=2)

        game_group_fofd_bot(update)


def group_deleter_five(update: Update, players_info, group_id):
    with open(f'data/Five/game/groups/{group_id}.json', 'r', encoding='UTF-8') as f:
        group = json.load(f)

    user1_id = str(group['player1'][0])
    user2_id = str(group['player2'][0])

    players_info['groups']['Five'].remove(int(group_id))

    next_group_id = players_info['next_group_id']['Five']

    if next_group_id != 0:
        for i in range(next_group_id - 1, -1, -1):
            if i not in players_info['groups']['Five']:
                players_info['next_group_id']['Five'] -= 1
            else:
                break
    else:
        group_id = 0

    with open(f'data/Five/game/groups/{group_id}.json', 'w', encoding='UTF-8'):
        pass

    del players_info['players_in_play']['Five']['group'][user1_id]
    del players_info['players_in_play']['Five']['group'][user2_id]

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==FOFD->GROUP==\n'
                                                     f'Группа с игроками:\n'
                                                     f'{user1_id}, {user2_id}\n'
                                                     f'закончила сессию.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def group_deleter_fofd(update: Update, players_info, group_id):
    with open(f'data/FofD/game/groups/{group_id}.json', 'r', encoding='UTF-8') as f:
        group_info = json.load(f)

    user1_id = group_info['player1'][0]
    user2_id = group_info['player2'][0]

    players_info['groups']['FofD'].remove(int(group_id))

    next_group_id = players_info['next_group_id']['FofD']

    if next_group_id != 0:
        for i in range(next_group_id - 1, -1, -1):
            if i not in players_info['groups']['FofD']:
                players_info['next_group_id']['FofD'] -= 1
            else:
                break
    else:
        group_id = 0

    with open(f'data/FofD/game/groups/{group_id}.json', 'w', encoding='UTF-8'):
        pass

    del players_info['players_in_play']['FofD']['group'][user1_id]
    del players_info['players_in_play']['FofD']['group'][user2_id]

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==FOFD->GROUP==\n'
                                                     f'Группа с игроками:\n'
                                                     f'{user1_id} и {user2_id}\n'
                                                     f'закончила сессию.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def room_maker_five(update: Update, case):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    next_room_id = players_info['next_room_id']['Five']

    if next_room_id != 0:
        for i in range(next_room_id + 1):
            if i not in players_info['rooms']['Five']:
                room_id = i
                break
        else:
            room_id = players_info['next_room_id']['Five']
            players_info['next_room_id']['Five'] += 1
    else:
        room_id = players_info['next_room_id']['Five']
        players_info['next_room_id']['Five'] += 1

    player_id = str(update.message.from_user.id)
    players_info['rooms']['Five'].append(int(room_id))
    players_info['players_in_play']['Five']['room'][player_id] = room_id

    with open(f'data/Five/game/rooms/{room_id}.json', 'w', encoding='UTF-8') as f:
        json.dump({'player': [player_id, 5, 0], 'case': [case, 1]}, f, ensure_ascii=False, indent=2)

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==ROOM->FIVE==\n'
                                                     f'Образована комната со следующим участником:\n'
                                                     f'{player_id}')

    update.message.bot.send_message(player_id, 'Игра началась!')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    game_room_five_bot(update)


def room_maker_fofd(update: Update):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    exer_id = randint(1, FOFD_EXERCISES)

    with open(f'data/FofD/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    next_room_id = players_info['next_room_id']['FofD']

    if next_room_id != 0:
        for i in range(next_room_id + 1):
            if i not in players_info['rooms']['FofD']:
                room_id = i
                break
        else:
            room_id = players_info['next_room_id']['FofD']
            players_info['next_room_id']['FofD'] += 1
    else:
        room_id = players_info['next_room_id']['FofD']
        players_info['next_room_id']['FofD'] += 1

    player_id = str(update.message.from_user.id)
    players_info['players_in_play']['FofD']['room'][player_id] = room_id

    players_info['rooms']['FofD'].append(str(room_id))

    exer_word = exer_info['exer'][0]
    exer_word_ln = count_letters_FofD(exer_word)

    with open(f'data/FofD/game/rooms/{room_id}.json', 'w', encoding='UTF-8') as f:
        json.dump({'player': [player_id, exer_word_ln], 'exer': [exer_id, ['\_' for _ in range(len(exer_word))]]},
                  f, ensure_ascii=False, indent=2)

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n==ROOM->FOFD==\n'
                                                     f'Образована комната со следующим участником:\n'
                                                     f'{player_id}')

    update.message.bot.send_message(player_id, 'Игра началась!')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    game_room_fofd_bot(update)


def room_deleter_five(update: Update, players_info, room_id):
    with open(f'data/Five/game/rooms/{room_id}.json', 'r', encoding='UTF-8') as f:
        room_info = json.load(f)

    user_id = room_info['player'][0]

    players_info['rooms']['Five'].remove(int(room_id))

    next_room_id = players_info['next_room_id']['Five']

    if next_room_id != 0:
        for i in range(next_room_id - 1, -1, -1):
            if i not in players_info['rooms']['Five']:
                players_info['next_room_id']['Five'] -= 1
            else:
                break
    else:
        room_id = 0

    with open(f'data/Five/game/rooms/{room_id}.json', 'w', encoding='UTF-8'):
        pass

    del players_info['players_in_play']['Five']['room'][user_id]

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==FIVE->ROOM==\n'
                                                     f'Комната с игроком:\n'
                                                     f'{user_id}\n'
                                                     f'закончила сессию.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def room_deleter_fofd(update: Update, players_info, room_id):
    with open(f'data/FofD/game/rooms/{room_id}.json', 'r', encoding='UTF-8') as f:
        room_info = json.load(f)

    user_id = room_info['player'][0]

    players_info['next_room_id']['FofD'] -= 1
    players_info['rooms']['FofD'].remove(str(room_id))

    with open(f'data/FofD/game/rooms/{room_id}.json', 'w', encoding='UTF-8'):
        pass

    del players_info['players_in_play']['FofD']['room'][user_id]

    update.message.bot.send_message(SERVER_GROUP_ID, f'{date_maker(update)}\n\n==FOFD->ROOM==\n'
                                                     f'Комната с игроком:\n'
                                                     f'{user_id}\n'
                                                     f'закончила сессию.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def gaming(update: Update, context: CallbackContext):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    if update.message.chat.type == 'private':
        if user_id in players_info['starting_players']:
            text = update.message.text

            player_status = players_info['starting_players'][user_id]

            if player_status == 'choosing':
                if text == '5':
                    players_info['starting_players'][user_id] = 'five_gamemode'
                    update.message.reply_text('В какой режим ты хочешь поиграть?', reply_markup=GAMEMODE_MARKUP)

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                elif text == 'Поле Чудес':
                    players_info['starting_players'][user_id] = 'fofd_gamemode'
                    update.message.reply_text('В какой режим ты хочешь поиграть?', reply_markup=GAMEMODE_MARKUP)

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                else:
                    update.message.reply_text(
                        'Я тебя не понимаю. Просто нажми на кнопку с названием игры, в которую хочешь поиграть.')

            elif player_status == 'five_gamemode':
                if text.lower() == 'групповой':
                    del players_info['starting_players'][user_id]

                    update.message.reply_text('Игра: "5"\nРежим: Групповой.\n\nЗапрос принят, выполняю...',
                                              reply_markup=ReplyKeyboardRemove())

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False)

                    start_five_group(update)

                elif text.lower() == 'одиночный':
                    players_info['starting_players'][user_id] = 'five_room_case'

                    update.message.reply_text('Какой кейс хочешь пройти?', reply_markup=FIVEROOMCASE_MARKUP)

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                else:
                    update.message.reply_text('Я тебя не совсем понимаю. Нажми на одну из предложенных кнопок, или напи'
                                              'ши "групповой" или "одиночный", чтобы начать игры с соответствующим назв'
                                              'анию режимом.')

            elif player_status == 'five_room_case':
                if text.lower() == 'случайный':
                    case = randint(1, CASES)
                    update.message.reply_text('Игра: "5"\nРежим: Одиночный\nКейс: Случайный.\n\nЗапрос принят, выполняю'
                                              '...', reply_markup=ReplyKeyboardRemove())

                elif text.isnumeric():
                    if 0 < int(text) < (CASES + 1):
                        case = int(text)
                        update.message.reply_text(f'Игра: "5"\nРежим: Одиночный\nКейс: {case}.\n\nЗапрос принят, выполн'
                                                  f'яю...', reply_markup=ReplyKeyboardRemove())

                    else:
                        update.message.reply_text(f'Я тебя не совсем понимаю. Напиши число от 1 до {CASES} или "случайн'
                                                  f'о".')
                        return

                else:
                    update.message.reply_text(f'Я тебя не совсем понимаю. Напиши число от 1 до {CASES} или "случайно".')
                    return

                del players_info['starting_players'][user_id]

                with open('data/players.json', 'w', encoding='UTF-8') as f:
                    json.dump(players_info, f, ensure_ascii=False, indent=2)

                start_five_room(update, case)

            elif player_status == 'fofd_gamemode':
                if text.lower() == 'групповой':
                    del players_info['starting_players'][user_id]

                    update.message.reply_text('Игра: "Поле Чудес"\nРежим: Групповой\n\nЗапрос принят, выполняю...',
                                              reply_markup=ReplyKeyboardRemove())

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                    start_fofd_group(update)

                elif text.lower() == 'одиночный':
                    del players_info['starting_players'][user_id]

                    update.message.reply_text('Игра: "Поле Чудес"\nРежим: Одиночный\n\nЗапрос принят, выполняю...',
                                              reply_markup=ReplyKeyboardRemove())

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                    start_fofd_room(update)

                else:
                    update.message.reply_text('Я тебя не совсем понимаю. Нажми на одну из предложенных кнопок, или напи'
                                              'ши "групповой" или "одиночный", чтобы начать игры с соответствующим назв'
                                              'анию режимом.')

            elif player_status == 'viewscore':
                text = update.message.text

                if text == '5':
                    gn, game = '5', 'Five'

                elif text.lower() == 'поле чудес':
                    gn, game = 'Поле Чудес', 'FofD'

                else:
                    gn, game = None, None

                if gn is not None:
                    del players_info['starting_players'][user_id]
                    update.message.reply_text(f'Понял, игра "{gn}". Выполняю...', reply_markup=ReplyKeyboardRemove())

                    with open('data/players.json', 'w', encoding='UTF-8') as f:
                        json.dump(players_info, f, ensure_ascii=False, indent=2)

                    db_viewscore(update, game)

            return

        if user_id in players_info['players_in_play']['Five']['group']:
            game_group_five_bot(update, True)

        elif user_id in players_info['players_in_play']['Five']['room']:
            game_room_five_bot(update, True)

        elif user_id in players_info['players_in_play']['FofD']['group']:
            game_group_fofd_bot(update, True)

        elif user_id in players_info['players_in_play']['FofD']['room']:
            game_room_fofd_bot(update, True)


def bstart(update: Update, context: CallbackContext):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    if update.message.chat.type == 'private':
        if user_id in players_info['starting_players']:
            if players_info['starting_players'][user_id] == 'choosing':
                update.message.reply_text(
                    'Ты уже написал эту команду. Просто нажми на кнопку с названием игры, в которую хочешь поиграть.')
            elif players_info['starting_players'][user_id] == 'viewscore':
                update.message.reply_text('Если ты передумал смотреть свою статистику, то напиши */stop*, чтобы останов'
                                          'ить выбор статистики\.', parse_mode='MarkdownV2')
            return

        elif user_id in players_info['available_players']['Five'] or \
                user_id in players_info['available_players']['FofD']:
            update.message.reply_text('Ты уже состоишь в поиске сессии.')
            return

        elif user_id in players_info['players_in_play']['Five']['group'] or \
                user_id in players_info['players_in_play']['Five']['room'] or \
                user_id in players_info['players_in_play']['FofD']['group'] or \
                user_id in players_info['players_in_play']['FofD']['room']:
            update.message.reply_text('Ты уже состоишь в игре. Доиграй эту, после чего сможешь начать следующую. :)')
            return

        else:
            players_info['starting_players'][user_id] = 'choosing'

            update.message.reply_text('В какую игру хочешь поиграть?', reply_markup=GAMECHOOSE_MARKUP)

    else:
        update.message.reply_text('Пиши мне в личные сообщения, пожалуйста.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def bhelp(update: Update, context: CallbackContext):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    if update.message.chat.type == 'private':
        if user_id in players_info['starting_players']:
            if players_info['starting_players'][user_id] == 'choosing':
                update.message.reply_text('Выбери игру на клавиатуре, или напиши "5" или "Поле Чудес", чтобы выбрать иг'
                                          'ру.\n\nКраткое описание "5": тебе нужно угадать слово за наименьшее количест'
                                          'во подсказок (всего их 5). Чем больше подсказок использовано (чем больше нев'
                                          'ерных предположений), тем меньше очков ты заработаешь.\n\nКраткое описание "'
                                          'Поле Чудес": существует слово, которое тебе нужно угадать, называя разные бу'
                                          'квы русского алфавита. Поможет тебе в этом подсказка, описывающее значение э'
                                          'того слова.')

            elif players_info['starting_players'][user_id] == 'five_gamemode':
                update.message.reply_text('Выбери режим на клавиатуре, или напиши "Групповой" или "Одиночный", чтобы вы'
                                          'брать соответствующий режим игры.\n\nВ групповом режиме ты будешь соревноват'
                                          'ься 1 на 1 с другим человеком. Кто быстрее отгадает слово, тот победил. Такж'
                                          'е потеря всех попыток тоже ведёт к проигрышу.\n\nВ одиночном режиме ты будеш'
                                          'ь решать кейсы, в каждом из которых 5 загаданных слов.')

            elif players_info['starting_players'][user_id] == 'fofd_gamemode':
                update.message.reply_text('Выбери режим на клавиатуре, или напиши "Групповой" или "Одиночный", чтобы вы'
                                          'брать соответствующий режим игры.\n\nВ групповом режиме ты будешь соревноват'
                                          'ься 1 на 1 с другим человеком. Каждый игрок играет по очереди и видит действ'
                                          'ия второго.\n\nВ одиночном режиме ты будешь отгадывать одно слово с ограниче'
                                          'нным количеством попыток.')

            elif players_info['starting_players'][user_id] == 'five_room_case':
                update.message.reply_text('Сложность кейсов:\n1, 2 - лёгкие,\n3, 4 - нормальные,\n5 - сложный.\nСлучайн'
                                          'ый - случайный.')

            elif players_info['starting_players'][user_id] == 'viewscore':
                update.message.reply_text('Выбери игру на клавиатуре, или напиши "5" или "Поле Чудес", чтобы посмотреть'
                                          ' статистику по выбранной игре.')

        elif (user_id in players_info['available_players']['Five'] or
              user_id in players_info['available_players']['FofD']):
            update.message.reply_text('Ты стоишь в очереди на поиск группы. Когда появится ещё один игрок в очереди, иг'
                                      'ра начнётся.')

        elif user_id in players_info['players_in_play']['Five']['room']:
            update.message.reply_text('Загадывается слово. Сначала даётся одна подсказка. Если ты по ней не угадываешь '
                                      'слово, то даётся следующая, но и убавляется число очков (с 5 до 4, то есть на 1)'
                                      '. Также и со второй, если не угадываешь, то даётся следующая и потенциальные очк'
                                      'и убавляются на 1. Если ты угадываешь слово, то тебе даётся столько очков, сколь'
                                      'ко было насчитано в процессе игры (изначально их 5, с каждой использованной подс'
                                      'казкой, не считая первой, убавляется на 1). Если ты не угадываешь слово совсем, '
                                      'то игра заканчивается твоим проигрышем. В игре используются кейсы, в которых 5 т'
                                      'аких слов. Чтобы победить, нужно отгадать все 5.')

        elif user_id in players_info['players_in_play']['FofD']['room']:
            update.message.reply_text('Загадывается слово. Даётся подсказка, которая описывает его. Ты можешь писать лю'
                                      'бые буквы из русского алфавита (в единичном количестве!). Если такая буква есть '
                                      'в слове, то подчёркивания меняются на эту букву (может быть такое, что такая бук'
                                      'ва в слове не одна, тогда открываются все). Если такой буквы нет, то количество '
                                      'попыток уменшается на 1. Число попыток ограничено. Можно отгадать слово целиком,'
                                      ' для этого нужно написать его без лишних символов.')

        elif user_id in players_info['players_in_play']['Five']['group']:
            update.message.reply_text('Загадывается слово. Сначала даётся одна подсказка. Если ты по ней не угадываешь '
                                      'слово, то даётся следующая, но и убавляется число очков (с 5 до 4, то есть на 1)'
                                      '. Также и со второй, если не угадываешь, то даётся следующая и потенциальные очк'
                                      'и убавляются на 1. Если ты угадываешь слово, то игра заканчивается твоей победой'
                                      ', и тебе даётся столько очков, сколько было насчитано в процессе игры (изначальн'
                                      'о их 5, с каждой использованной подсказкой, не считая первой, убавляется на 1). '
                                      'Если ты угадываешь слово, . Если же твои подсказки кончаются, то победа засчитыв'
                                      'ается оппоненту.')

        elif user_id in players_info['players_in_play']['FofD']['group']:
            update.message.reply_text('Загадывается слово. Даётся подсказка, которая описывает его. Ты можешь писать лю'
                                      'бые буквы из русского алфавита (в единичном количестве!). Если такая буква есть '
                                      'в слове, то подчёркивания меняются на эту букву (может быть такое, что такая бук'
                                      'ва в слове не одна, тогда открываются все). Если такой буквы нет, то количество '
                                      'попыток уменшается на 1. Игроки работают поочерёдно. Если один угадывает букву, '
                                      'то другой это видит, но ход не переключается. Если буквы нет, то очередь идёт да'
                                      'льше. Побеждает тот, кто угадывает слово любым допустимым способом.')

        else:
            update.message.reply_text('Напиши /start для выбора игры.')

    else:
        update.message.reply_text('За информацией обращайся мне в личные сообщения, пожалуйста.')


def bstop(update: Update, context: CallbackContext):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    if user_id in players_info['starting_players']:
        update.message.reply_text('Не хочешь, как хочешь. :)', reply_markup=ReplyKeyboardRemove())
        del players_info['starting_players'][user_id]

    elif user_id in players_info['available_players']['Five']:
        players_info['available_players']['Five'].remove(user_id)
        update.message.reply_text('Поиск сессии остановлен.')

    elif user_id in players_info['players_in_play']['Five']['group']:
        if update.message.chat.type == 'private':
            group_deleter_five(update, players_info, str(players_info['players_in_play']['Five']['group'][user_id]))

            update.message.reply_text('Победа присвоена твоему противнику, так как ты покинул сессию. :(')

            return

        else:
            update.message.reply_text('Игра в "5" начата! Пиши мне в личные сообщения, пожалуйста.')

    elif user_id in players_info['players_in_play']['Five']['room']:
        if update.message.chat.type == 'private':
            room_deleter_five(update, players_info, str(players_info['players_in_play']['Five']['room'][user_id]))

            update.message.reply_text('Жаль, что ты решил остановить игру, но ничего, всегда можно начать ещё разок!')

            return

        else:
            update.message.reply_text('Игра в "5" начата! Пиши мне в личные сообщения, пожалуйста.')

    elif user_id in players_info['players_in_play']['FofD']['group']:
        if update.message.chat.type == 'private':
            group_deleter_fofd(update, players_info, str(players_info['players_in_play']['FofD']['group'][user_id]))

            update.message.reply_text('Жаль, что ты решил остановить игру, но ничего, всегда можно начать ещё разок!')

            return

        else:
            update.message.reply_text('Игра в "Поле Чудес" начата! Пиши мне в личные сообщения, пожалуйста.')

    elif user_id in players_info['players_in_play']['FofD']['room']:
        if update.message.chat.type == 'private':
            room_deleter_fofd(update, players_info, str(players_info['players_in_play']['FofD']['room'][user_id]))

            update.message.reply_text('Жаль, что ты решил остановить игру, но ничего, всегда можно начать ещё разок!')

            return

        else:
            update.message.reply_text('Игра в "Поле Чудес" начата! Пиши мне в личные сообщения, пожалуйста.')

    else:
        if update.message.chat.type == 'private':
            update.message.reply_text('Ты и так не находишься ни в игре, ни в поиске сессии. ;)')

        else:
            update.message.reply_text('Пиши мне в личные сообщения, пожалуйста.')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)


def viewscore(update: Update, context: CallbackContext):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)
    command = update.message.text.split()

    if update.message.chat.type == 'private':
        user_id = str(update.message.from_user.id)

        if user_id in players_info['starting_players']:
            if players_info['starting_players'][user_id] == 'choosing':
                update.message.reply_text('Если хочешь остановить выбор игры для начала сессии, то напиши */stop*\.',
                                          parse_mode='MarkdownV2')

            elif players_info['starting_players'][user_id] == 'viewscore':
                update.message.reply_text('Ты уже написал эту команду. Выбери игру, по которой тебя интересует твоя ста'
                                          'тистика.')
            return

        game = None

        if len(command) == 2:
            if command[1] == '5':
                game = 'Five'
            elif command[1].lower() == 'поле-чудес':
                game = 'FofD'

        if game is None:
            update.message.reply_text('Статистика по какой игре тебя интересует?', reply_markup=GAMECHOOSE_MARKUP)
            players_info['starting_players'][user_id] = 'viewscore'

            with open('data/players.json', 'w', encoding='UTF-8') as f:
                json.dump(players_info, f, ensure_ascii=False, indent=2)

        else:
            db_viewscore(update, game)

    else:
        update.message.reply_text('Пиши мне в личные сообщения, пожалуйста.')


def date_maker(update: Update):
    date = f'{update.message.date.date().strftime("%Y-%m-%d")} ' \
           f'{update.message.date.time().strftime("%H:%M:%S")}'
    date = date[:11] + str(int(date[11:13]) + 5) + date[13:]
    return date


def game_group_five_bot(update: Update, texting=False):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    group_id = str(players_info['players_in_play']['Five']['group'][str(update.message.from_user.id)])

    with open(f'data/Five/game/groups/{group_id}.json', 'r', encoding='UTF-8') as f:
        group_info = json.load(f)

    exer_id = group_info['exer']

    with open(f'data/Five/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    if str(update.message.from_user.id) == group_info['player1'][0]:
        cur_player, cur_player_id = 'player1', str(group_info['player1'][0])
        els_player, els_player_id = 'player2', str(group_info['player2'][0])
        cur_player_stage = group_info['player1'][1]
        els_player_stage = group_info['player2'][1]
    else:
        cur_player, cur_player_id = 'player2', str(group_info['player2'][0])
        els_player, els_player_id = 'player1', str(group_info['player1'][0])
        cur_player_stage = group_info['player2'][1]
        els_player_stage = group_info['player1'][1]

    if texting:
        text = update.message.text.lower()

        if text in exer_info['exer'][0]:
            group_deleter_five(update, players_info, group_id)
            update.message.bot.send_message(cur_player_id, 'Игра окончена! Молодец, ты выиграл, угадав загаданное слово'
                                                           '!\nТак держать, друг! :)')
            update.message.bot.send_message(els_player_id, 'Игра окончена! Твой противник обогнал тебя и отгадал слово '
                                                           'раньше. Что ж, повезёт в следующий раз! :)')

            db_score_editor(cur_player_id, cur_player_stage, 'Five', els_player_id)

        else:
            group_info[cur_player][1] -= 1

            if group_info[cur_player][1] == 0:
                group_deleter_five(update, players_info, group_id)
                update.message.bot.send_message(cur_player_id, 'Игра окончена! Ты израсходовал все свои подсказки.\nЧто'
                                                               ' ж, повезёт в следующий раз! :)')
                update.message.bot.send_message(els_player_id, 'Игра окончена! Твой противник израсходовал все свои под'
                                                               'сказки. Да, это считается за победу. :)')

                db_score_editor(els_player_id, els_player_stage, 'Five', cur_player_id)

                return

            else:
                update.message.bot.send_message(cur_player_id, f'Ответ неправильный! Следующая подсказка:\n'
                                                               f'{exer_info["exer"][7 - cur_player_stage]}')
    else:
        update.message.bot.send_message(cur_player_id, exer_info['exer'][1])
        update.message.bot.send_message(els_player_id, exer_info['exer'][1])

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    with open(f'data/Five/game/groups/{group_id}.json', 'w', encoding='UTF-8') as f:
        json.dump(group_info, f, ensure_ascii=False, indent=2)


def game_room_five_bot(update: Update, texting=False):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    room_id = str(players_info['players_in_play']['Five']['room'][str(update.message.from_user.id)])

    with open(f'data/Five/game/rooms/{room_id}.json', 'r', encoding='UTF-8') as f:
        room_info = json.load(f)

    case_id = room_info['case'][0]
    cur_exer = str(room_info['case'][1])

    with open(f'data/Five/cases/{case_id}.json', 'r', encoding='UTF-8') as f:
        case_info = json.load(f)

    exer_id = case_info['case']['exercises'][cur_exer]

    with open(f'data/Five/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    player_id = room_info['player'][0]
    player_stage = room_info['player'][1]

    if texting:
        text = update.message.text.lower()

        if text in exer_info['exer'][0]:
            room_info['player'][2] += player_stage
            update.message.reply_text('Правильно, молодец!')

            if room_info['case'][1] == 5:
                score = room_info['player'][2]
                room_deleter_five(update, players_info, room_id)

                update.message.reply_text('Поздравляю, ты прошёл кейс! Если захочешь, то можешь его перепройти, или выб'
                                          'рать что-то совершенно другое.')

                db_score_editor(player_id, score, 'Five')

                return

            else:
                room_info['case'][1] += 1
                room_info['player'][1] = 5

                update.message.reply_text(f'Подготавливаю кейс №{room_info["case"][1]}...')

                exer_id = case_info['case']['exercises'][str(int(cur_exer) + 1)]
                with open(f'data/Five/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
                    exer_info = json.load(f)

                update.message.reply_text(f'Первая подсказка:\n{exer_info["exer"][1]}')

        else:
            room_info['player'][1] -= 1
            update.message.reply_text('Неправильно!')

            if room_info['player'][1] == 0:
                room_deleter_five(update, players_info, room_id)

                update.message.reply_text('Игра окончена! Ты израсходовал все свои подсказки.\nЧто ж, повезёт в следующ'
                                          'ий раз! :)')

                db_score_editor(None, None, 'Five', player_id)

                return

            update.message.reply_text(f'Следующая подсказка:\n{exer_info["exer"][7 - player_stage]}')

    else:
        update.message.reply_text(f'Первая подсказка:\n{exer_info["exer"][1]}')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    with open(f'data/Five/game/rooms/{room_id}.json', 'w', encoding='UTF-8') as f:
        json.dump(room_info, f, ensure_ascii=False, indent=2)


def game_group_fofd_bot(update: Update, texting=False):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    group_id = str(players_info['players_in_play']['FofD']['group'][str(update.message.from_user.id)])

    with open(f'data/FofD/game/groups/{group_id}.json', 'r', encoding='UTF-8') as f:
        group_info = json.load(f)

    exer_id = group_info['exer'][0]

    with open(f'data/FofD/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    player1_id, player1_turn = group_info['player1']
    player2_id, player2_turn = group_info['player2']

    player_cur = str(update.message.from_user.id)
    player_els = player2_id if player_cur == player1_id else player1_id

    blocker = True

    if texting:
        if player1_id == player_cur and player1_turn != 'writ':
            update.message.reply_text('Сейчас не твой ход.')
            return

        elif player2_id == player_cur and player2_turn != 'writ':
            update.message.reply_text('Сейчас не твой ход.')
            return

        text = update.message.text.upper()

        if len(text) == 1:
            if text in ALPHABET:
                if text in group_info['exer'][2]:
                    if text in group_info['exer'][1]:
                        update.message.reply_text('Эту букву уже угадывали! Попробуй другую.')
                    else:
                        update.message.reply_text('Эту букву уже называли! Попробуй другую.')
                    return

                group_info['exer'][2].append(text)

                if text in exer_info['exer'][0]:
                    group_info['exer'][1] = open_letters(exer_info['exer'][0], text, group_info['exer'][1])

                    if '\_' in group_info['exer'][1]:
                        update.message.reply_text(f'*Есть такая буква\!*\n\n*{" ".join(group_info["exer"][1])}*'
                                                  f'\n\n{choice(LETTER_QUESTIONS)}', parse_mode='MarkdownV2')
                        update.message.bot.send_message(player_els, f'_Противник:_ __{text}__\n\n*Буква угадана\!*\n'
                                                                    f'*{" ".join(group_info["exer"][1])}*',
                                                        parse_mode='MarkdownV2')
                        blocker = False

                    else:
                        group_deleter_fofd(update, players_info, group_id)

                        update.message.reply_text(f'*{" ".join(group_info["exer"][1])}*\n\n'
                                                  f'*Верно\!\nИгра окончена\!*\n\nТы угадал последнюю букву загаданного'
                                                  f' слова\!\nТы можешь снова поиграть в эту игру, или попробовать друг'
                                                  f'ую\. :\)', parse_mode='MarkdownV2')
                        update.message.bot.send_message(player_els, f'_Противник:_ __{text}__\n\n*Буква угадана\!*\n'
                                                                    f'*{" ".join(group_info["exer"][1])}*\n\n'
                                                                    f'*Игра окончена\!*\n\nТвой противник угадал послед'
                                                                    f'нюю букву слова\. Но ничего страшного, повезёт в '
                                                                    f'другой раз\. :\)', parse_mode='MarkdownV2')

                        db_score_editor(player_cur, len(exer_info['exer'][0]), 'FofD', player_els)

                        return

                else:
                    update.message.reply_text(f'*Нет такой буквы\!*\n\n'
                                              f'*{" ".join(group_info["exer"][1])}*', parse_mode='MarkdownV2')
                    update.message.bot.send_message(player_els, f'_Противник:_ __{text}__\n\n*Нет такой буквы\!*\n'
                                                                f'*{" ".join(group_info["exer"][1])}*',
                                                    parse_mode='MarkdownV2')

            else:
                update.message.reply_text('_Ты отправил некорректный символ_\.\nПроверь, буква должна быть буквой р'
                                          'усского алфавита\.', parse_mode='MarkdownV2')
                return

        else:
            if check_correct(text) and text == exer_info['exer'][0]:
                group_deleter_fofd(update, players_info, group_id)

                update.message.reply_text(f'*{" ".join(list(text.upper()))}*\n\n'
                                          f'*Точно\!*\n\nТы верно угадал слово и выиграл в этой сессии, поздравляю'
                                          f'\!\nТы можешь снова поиграть в эту игру, или попробовать другую\. :\)',
                                          parse_mode='MarkdownV2')

                update.message.bot.send_message(player_els, f'*{" ".join(list(text.upper()))}*\n\n'
                                                            f'*Игра окончена\!*\n\nТвой противник угадал слово\. Ничего'
                                                            f' страшного, повезёт в другой раз\. :\)',
                                                parse_mode='MarkdownV2')

                db_score_editor(player_cur, 5 + len(exer_info['exer'][0]), 'FofD', player_els)

                return

            elif check_correct(text):
                group_deleter_fofd(update, players_info, group_id)

                update.message.reply_text('*Неверно\!*\nИгра окончена\!\n\nТы назвал неправильное слово\. Что ж, в '
                                          'следующий раз повезёт\! :\)', parse_mode='MarkdownV2')
                update.message.bot.send_message(player_els, '*Игра окончена\!*\n\nТвой противник назвал неправильно'
                                                            'е слово\. Поздравляю, ты победил в этой сессии\! :\)',
                                                parse_mode='MarkdownV2')

                db_score_editor(player_els, 5 + len(exer_info['exer'][0]) // 2, 'FofD', player_cur)

                return

            else:
                update.message.reply_text('_Ты отправил некорректное сообщение\._\nПроверь его содержание, в нём до'
                                          'лжны содержаться только буквы русского алфавита в единичном кол\-ве\.',
                                          parse_mode='MarkdownV2')
                return

    else:
        update.message.bot.send_message(player_cur, f'{exer_info["exer"][1]}\n\n{choice(LETTER_QUESTIONS)}')
        update.message.bot.send_message(player_els, f'{exer_info["exer"][1]}\n\n{choice(LETTER_QUESTIONS)}')

    if blocker:
        turn1 = '*Твой ход\!*' if player1_turn == 'wait' else '*Ожидай свой ход\.*'
        update.message.bot.send_message(player1_id, turn1, parse_mode='MarkdownV2')

        turn2 = '*Твой ход\!*' if player2_turn == 'wait' else '*Ожидай свой ход\.*'
        update.message.bot.send_message(player2_id, turn2, parse_mode='MarkdownV2')

        group_info['player1'][1] = 'writ' if group_info['player1'][1] == 'wait' else 'wait'
        group_info['player2'][1] = 'writ' if group_info['player2'][1] == 'wait' else 'wait'

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    with open(f'data/FofD/game/groups/{group_id}.json', 'w', encoding='UTF-8') as f:
        json.dump(group_info, f, ensure_ascii=False, indent=2)


def game_room_fofd_bot(update: Update, texting=False):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    player_id = str(update.message.from_user.id)
    room_id = str(players_info['players_in_play']['FofD']['room'][player_id])

    with open(f'data/FofD/game/rooms/{room_id}.json', 'r', encoding='UTF-8') as f:
        room_info = json.load(f)

    player_attempts = room_info['player'][1]
    exer_id = room_info['exer'][0]

    with open(f'data/FofD/exercise/{exer_id}.json', 'r', encoding='UTF-8') as f:
        exer_info = json.load(f)

    if texting:
        text = update.message.text.upper()

        if len(text) == 1:
            if text in ALPHABET:
                if text in exer_info['exer'][0]:
                    room_info['exer'][1] = open_letters(exer_info['exer'][0], text, room_info['exer'][1])

                    if '\_' in room_info['exer'][1]:
                        update.message.reply_text(f'*Есть такая буква\!*\n\n'
                                                  f'Осталось попыток: {room_info["player"][1]}\n'
                                                  f'*{" ".join(room_info["exer"][1])}*', parse_mode='MarkdownV2')

                    else:
                        room_deleter_fofd(update, players_info, room_id)

                        update.message.reply_text(f'*{" ".join(room_info["exer"][1])}*\n\n'
                                                  f'*Верно\!\nИгра окончена\!*\n\nТы угадал последнюю букву загаданного'
                                                  f' слова\!\nТы можешь снова поиграть в эту игру, или попробовать друг'
                                                  f'ую\. :\)', parse_mode='MarkdownV2')

                        db_score_editor(player_id, player_attempts, 'FofD')

                        return

                else:
                    room_info['player'][1] -= 1

                    if room_info['player'][1] != 0:
                        update.message.reply_text(f'*Нет такой буквы\!*\n\n'
                                                  f'Осталось попыток: {room_info["player"][1]}\n'
                                                  f'*{" ".join(room_info["exer"][1])}*', parse_mode='MarkdownV2')

                    else:
                        room_deleter_fofd(update, players_info, room_id)

                        update.message.reply_text('*Нет такой буквы\!*\nИгра окончена\!\n\nТы израсходовал все подсказк'
                                                  'и\. Что ж, повезёт в следующий раз\. :\)', parse_mode='MarkdownV2')

                        db_score_editor(None, None, 'FofD', player_id)

                        return

            else:
                update.message.reply_text('_Ты отправил некорректный символ_\.\nПроверь, буква должна быть буквой русск'
                                          'ого алфавита\.', parse_mode='MarkdownV2')

        else:
            if check_correct(text) and text == exer_info['exer'][0]:
                room_deleter_fofd(update, players_info, room_id)

                update.message.reply_text(f'*{" ".join(list(text.upper()))}*\n\n'
                                          f'*Точно\!*\n\nТы верно угадал слово, поздравляю\!\nТы можешь снова поиграть '
                                          f'в эту игру, или попробовать другую\. :\)', parse_mode='MarkdownV2')

                db_score_editor(player_id, 5 + player_attempts, 'FofD')

                return

            elif check_correct(text):
                room_deleter_fofd(update, players_info, room_id)

                update.message.reply_text('*Неверно\!*\nИгра окончена\!\n\nТы назвал неправильное слово\. Что ж, в след'
                                          'ующий раз повезёт\! :\)', parse_mode='MarkdownV2')

                db_score_editor(None, None, 'FofD', player_id)

                return

            else:
                update.message.reply_text('_Ты отправил некорректное сообщение\._\nПроверь его содержание, в нём должны'
                                          ' содержаться только буквы русского алфавита в единичном количестве\.',
                                          parse_mode='MarkdownV2')

    else:
        update.message.reply_text(f'{exer_info["exer"][1]}\n\n{choice(LETTER_QUESTIONS)}')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    with open(f'data/FofD/game/rooms/{room_id}.json', 'w', encoding='UTF-8') as f:
        json.dump(room_info, f, ensure_ascii=False, indent=2)


def start_five_group(update: Update):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    players_info['available_players']['Five'].append(user_id)

    update.message.reply_text('Ты добавлен в очередь поиска игры...')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    group_maker_five(update)


def start_fofd_group(update: Update):
    with open('data/players.json', 'r', encoding='UTF-8') as f:
        players_info = json.load(f)

    user_id = str(update.message.from_user.id)

    players_info['available_players']['FofD'].append(user_id)

    update.message.reply_text('Ты добавлен в очередь поиска игры...')

    with open('data/players.json', 'w', encoding='UTF-8') as f:
        json.dump(players_info, f, ensure_ascii=False, indent=2)

    group_maker_fofd(update)


def start_five_room(update: Update, case):
    update.message.reply_text('Инициализация комнаты...')
    room_maker_five(update, case)


def start_fofd_room(update: Update):
    update.message.reply_text('Инициализация комнаты...')
    room_maker_fofd(update)


def db_score_editor(winplr_id, winplr_score, game: str, defplr_id=None):
    db_con = connect('data/data.db')
    db_cur = db_con.cursor()

    if winplr_id is not None:
        db_winplr_id = db_cur.execute(f'SELECT player_id FROM Players WHERE user_id == {winplr_id}').fetchone()

        if not db_winplr_id:
            db_cur.execute(f'INSERT INTO Players(user_id) VALUES({winplr_id})')
            db_con.commit()
            for i in ['Five', 'FofD']:
                db_cur.execute(f'INSERT INTO {i}(player_id, score, games, wins, defeats) '
                               f'VALUES({winplr_id}, 0, 0, 0, 0)')
                db_con.commit()
            db_winplr_id = db_cur.execute(f'SELECT player_id FROM Players WHERE user_id == {winplr_id}').fetchone()[0]

        else:
            db_winplr_id = db_winplr_id[0]

    else:
        db_winplr_id = None

    if defplr_id is not None:
        db_defplr_id = db_cur.execute(f'SELECT player_id FROM Players WHERE user_id == {defplr_id}').fetchone()

        if not db_defplr_id:
            db_cur.execute(f'INSERT INTO Players(user_id) VALUES({defplr_id})')
            db_con.commit()
            for i in ['Five', 'FofD',]:
                db_cur.execute(f'INSERT INTO {i}(player_id, score, games, wind, defeats) '
                               f'VALUES({defplr_id}, 0, 0, 0 ,0)')
                db_con.commit()
            db_defplr_id = db_cur.execute(f'SELECT player_id FROM Players WHERE user_id == {defplr_id}').fetchone()[0]

        else:
            db_defplr_id = db_defplr_id[0]

    else:
        db_defplr_id = None

    if db_winplr_id is not None:
        db_cur.execute(f'UPDATE {game} SET score = score + {winplr_score}, games = games + 1, wins = wins + 1 '
                       f'WHERE player_id == {db_winplr_id}')
        db_con.commit()

    if db_defplr_id is not None:
        db_cur.execute(f'UPDATE {game} SET games = games + 1, defeats = defeats + 1 '
                       f'WHERE player_id == {db_defplr_id}')
        db_con.commit()


def db_viewscore(update: Update, game):
    db_con = connect('data/data.db')
    db_cur = db_con.cursor()

    user_id = update.message.from_user.id
    db_player_id = db_cur.execute(f'SELECT player_id FROM Players WHERE user_id == {user_id}').fetchone()

    if db_player_id:
        score = db_cur.execute(f'SELECT score, games, wins, defeats FROM {game} '
                               f'WHERE player_id == {db_player_id[0]}').fetchone()

        if score:
            update.message.reply_text(f'__Данные про игру__ "*{game}*":\n'
                                      f'_Кол\-во очков:_ *{score[0]}*;\n'
                                      f'_Кол\-во сыгранных сессий:_ *{score[1]}*;\n'
                                      f'_Кол\-во выигранных сессий:_ *{score[2]}*;\n'
                                      f'_Кол\-во проигранных сессий:_ *{score[3]}*\.',
                                      parse_mode='MarkdownV2')
        else:
            update.message.reply_text('У тебя нет ни одного очка в этой игре. Скорее всего, ты не играл в неё.')

    else:
        update.message.reply_text('Тебя нет в базе данных игр. Скорее всего, ты не играл ни в одну игру.')


def count_letters_FofD(word):
    letters, new_letters = list(word), list()
    for i in letters:
        if i not in new_letters:
            new_letters.append(i)
    return len(new_letters)


def check_correct(word):
    letters = list(word)
    for i in letters:
        if i not in ALPHABET:
            return False
    return True


def open_letters(word, letter, work):
    done, letter = list(), letter.upper()
    for i in range(len(word)):
        if word[i] == letter:
            done.append(letter)
        else:
            done.append(work[i])
    return done


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, gaming))
    dp.add_handler(CommandHandler('start', bstart))
    dp.add_handler(CommandHandler('help', bhelp))
    dp.add_handler(CommandHandler('stop', bstop))
    dp.add_handler(CommandHandler('viewscore', viewscore))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
