import logging
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import paramiko
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

load_dotenv()
TOKEN = os.getenv('TOKEN')
connection = None

# dotenv_path = Path('D:\\PT-Start\\практика1\\bot\\.env')
# load_dotenv(dotenv_path=dotenv_path)

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def sshConnect():
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)

    return client

def dbConnect():
    connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv('DB_PASSWORD'),
                                  host=os.getenv('DB_HOST'),
                                  port=os.getenv('DB_PORT'), 
                                  database=os.getenv('DB_DATABASE'))

    return connection

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    
def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')
    
state = 0

def find_phone_numberCommand(update: Update, context):
    global state
    state = 0
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

numbers_global = ""

def find_phone_number (update: Update, context):
    logging.critical("ERREOREORSEORKOESFOS")
    global numbers_global, state
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    if(user_input == "да" and state == 1):
        connection = dbConnect()
        cursor = connection.cursor() 
        rowcount = 0
        for i in range(len(numbers_global)):
            cursor.execute(f"INSERT INTO Phones (phone_num) VALUES ('{numbers_global[i]}');")
            rowcount += cursor.rowcount
            connection.commit()
        update.message.reply_text(f"Успешно вставлено {rowcount} номеров из {len(numbers_global)}")    
        cursor.close()
        connection.close()
        return ConversationHandler.END
    elif(state == 1):
        update.message.reply_text("Хорошего дня!")
        return ConversationHandler.END
    
    phoneNumRegex = re.compile(r'(\+7|8)(\s)?(\s|\(|-)?\d{3}(\s|\)|-)?(\s)?\d{3}(\s|-)?\d{2}(\s|-)?\d{2}')
    phoneNumberList = [x.group() for x in re.finditer(phoneNumRegex, user_input)]

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер    
    numbers_global = phoneNumberList
    state = 1
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text("Записать найденные номера в БД? [да | нет]")

def find_emailCommand(update: Update, context):
    global state
    state = 0
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')
    return 'find_email'

def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите только ваш пароль: ')
    return 'verify_password'

def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите название пакета или "all" для получения информации о всех пакетах: ')
    return 'get_apt_list'

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем пароль

    passRegex = re.compile(r'^(?=.*[a-zа-я])(?=.*[A-ZА-Я])(?=.*\d)(?=.*[\!@#\$%\^\&\*\(\)]).{8,}$')
    password = re.search(passRegex, user_input)

    if not password: # Если совпадений не найдено, пароль слабый
        update.message.reply_text('Слабый пароль')
        return ConversationHandler.END

    else: 
        update.message.reply_text("Сильный пароль") # Отправляем сообщение пользователю
        return ConversationHandler.END # Завершаем работу обработчика диалога

addresses_global = ""

def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) почтовые адреса
    global addresses_global, state

    if(user_input == "да" and state == 1):
        connection = dbConnect()
        cursor = connection.cursor() 
        rowcount = 0
        for i in range(len(addresses_global)):
            cursor.execute(f"INSERT INTO Emails (mail_addr) VALUES ('{addresses_global[i]}');")
            rowcount += cursor.rowcount
            connection.commit()
        update.message.reply_text(f"Успешно вставлено {rowcount} адресов из {len(addresses_global)}")    
        cursor.close()
        connection.close()
        return ConversationHandler.END
    elif(state == 1):
        update.message.reply_text("Хорошего дня!")
        return ConversationHandler.END

    mailRegex = re.compile(r'[\w\-\.]+@([\w\-]+\.)+[\w]{2,4}')
    mailList = [x.group() for x in re.finditer(mailRegex, user_input)]
    
    if not mailList: # Обрабатываем случай, когда адресов нет
        update.message.reply_text('Почтовые адреса не найдены')
        return # Завершаем выполнение функции
    
    mailAddresses = '' # Создаем строку, в которую будем записывать почтовые адреса
    for i in range(len(mailList)):
        mailAddresses += f'{i+1}. {mailList[i]}\n' # Записываем очередной адрес
    
    addresses_global = mailList
    state = 1
    update.message.reply_text(mailAddresses) # Отправляем сообщение пользователю
    update.message.reply_text("Записать найденные адреса в БД? [да | нет]")

def get_release (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('lsb_release -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_uname (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_uptime (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_df (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('df')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_free (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_mpstat (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_w (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_auths (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('last | head')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_critical (update: Update, context): # 5 последних ошибок
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('journalctl | grep "error" | tail -5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_ps (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
    return

def get_ss (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('ss')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    max_length = 4096  # Максимальная длина сообщения для Telegram API
    data_parts = [data[i:i+max_length] for i in range(0, len(data), max_length)]
    for part in data_parts:
        update.message.reply_text(part)
    return

def get_apt_list (update: Update, context):
    client = sshConnect()
    user_choice = update.message.text
    if (user_choice == "all"):
        stdin, stdout, stderr = client.exec_command('apt list --installed')
        data = stdout.read() + stderr.read()
    else:
        stdin, stdout, stderr = client.exec_command('apt show ' + user_choice)
        data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    max_length = 4096  # Максимальная длина сообщения для Telegram API
    data_parts = [data[i:i+max_length] for i in range(0, len(data), max_length)]
    for part in data_parts:
        update.message.reply_text(part)
    return ConversationHandler.END

def get_services (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('ps')
    
    data_arr = stdout.readlines() + stderr.readlines()
    data = "".join(str(element) for element in data_arr)
    client.close()
    # data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    max_length = 4096  # Максимальная длина сообщения для Telegram API
    data_parts = [data[i:i+max_length] for i in range(0, len(data), max_length)]
    for part in data_parts:
        update.message.reply_text(part)
    return


def get_repl_logs (update: Update, context):
    client = sshConnect()
    stdin, stdout, stderr = client.exec_command('cat /tmp/pg.log | grep "replication"')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    max_length = 4096  # Максимальная длина сообщения для Telegram API
    data_parts = [data[i:i+max_length] for i in range(0, len(data), max_length)]
    for part in data_parts:
        update.message.reply_text(part)
    return

def get_emails (update: Update, context):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Emails;")
    data = cursor.fetchall()
    message = 'Полученные адреса: \n'
    i = 1
    for row in data:
        message += f"{i}. {row[1]}\n"
        i += 1  
    logging.info("Команда успешно выполнена")
    cursor.close()
    connection.close()
    update.message.reply_text(message)
    return

def get_phone_numbers (update: Update, context):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Phones;")
    data = cursor.fetchall()
    message = 'Полученные телефонные номера: \n'
    i = 1
    for row in data:
        message += f"{i}. {row[1]}\n"
        i += 1  
    logging.info("Команда успешно выполнена")
    cursor.close()
    connection.close()
    update.message.reply_text(message)
    return

def main():
		# Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
		
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
        },
        fallbacks=[]
    )

    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        },
        fallbacks=[]
    )

    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerfind_email)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(convHandlerget_apt_list)

    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
