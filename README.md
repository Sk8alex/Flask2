Flask1_04052025
Инструкция по развертыванию проекта
Создать виртуальное окружение
python3 -m venv flask_venv

Активировать виртуальное окружение
source flask_venv/bin/activate

Установить нужные библиотеки
python -m pip install -r requirements.txt

Запустить приложение
python app.py

Работа с sqlite3
Установка CLI для sqlite:
sudo apt install sqlite3

Создать дамп БД (схема + данные):
sqlite3 store.db .dump > db_sql/db_data.sql

Создать дамп БД (только схема):
sqlite3 store.db ".schema quotes" > db_sql/db_schema.sql

Загрузить данные в БД:
sqlite3 new_store.db ".read db_sql/db_data.sql"

Установка флага для окрытия приложения chmod u+x имя приложения