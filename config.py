from enum import Enum

db_file = "database.vdb"
db_state_file = "database_half.vdb"
BOT_TOKEN = '1460157024:AAFkocFe8la8zsK-6vx3c8PkJ-fO5ECnaew'
CHANNEL_NAME = -1001120423505
VERIFICATION_USER = 353383640
USERNAME_ADMIN = 'AlexSm'

class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_SEND = "1" # Хочет отправить пост
    S_REWRITE = "2" # Только у админа
    S_HALF_TEXT = "3" # Есть только текст или картинка
    S_HALF_PHOTO = "4" # Есть только текст или картинка