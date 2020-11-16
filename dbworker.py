from vedis import Vedis
import config

# Автопубликация db[0]
# 0 - нет 
# 1 - да

# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    with Vedis(config.db_file) as db:
        try:
            return db[user_id].decode() # Если используете Vedis версии ниже, чем 0.7.1, то .decode() НЕ НУЖЕН
        except KeyError:  # Если такого ключа почему-то не оказалось
            return config.States.S_START.value  # значение по умолчанию - начало диалога

# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    with Vedis(config.db_file) as db:
        try:
            db[user_id] = value
            return True
        except:
            # тут желательно как-то обработать ситуацию
            return False




# Промежуточные состояния постов
def get_half_state(user_id):
    with Vedis(config.db_state_file) as db_state:
        try:
            return db_state[user_id].decode() 
        except KeyError:  
            return "infinity"             

def set_half_state(user_id, value):
    with Vedis(config.db_state_file) as db_state:
        try:
            db_state[user_id] = value
            return True
        except:

            return False
