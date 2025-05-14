from flask import Flask, jsonify, request
from random import choice
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db"  # <- тут путь к БД

# Создаем соедниение
connection = sqlite3.connect(path_to_db)

app = Flask(__name__)
app.json.ensure_ascii = False

KEYS = ('author', 'text', 'rating')



@app.get("/quotes")
def get_quotes():
    """ Функция возвращает все цитаты из БД. """
    select_quotes = "SELECT * from quotes"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall() # get list[tuple]
    cursor.close()
    connection.close()
    # Подготовка данных для отправки в правильной формате.
    # Необходимо выполнить преобразование:
    # list[tuple] -> list[dict]
    keys = ('id', 'author', 'text', 'rating')
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)
    return jsonify(quotes), 200


@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id: int):
    select_quotes = "SELECT * from quotes"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall() # get list[tuple]
    cursor.close()
    connection.close()
    """ Return quote by id from 'quotes' list."""
    keys = ('id', 'author', 'text')
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        if quote["id"] == quote_id:
            return jsonify(quote), 200
    return jsonify(error=f"Quote with id={quote_id} not found"), 404



def generate_new_id():
    """Генерирует новый идентификатор для цитаты"""
    select_quotes = "SELECT MAX(id) FROM quotes"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    max_id = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    if max_id is None:
        return 1
    else:
        return max_id + 1


@app.route("/quotes", methods=['POST'])
def create_quote():
    """Function creates new quote and adds it to the database"""
    data = request.json
    keys = ('author', 'text', 'rating')
    if not set(data.keys()) - set(keys):
        new_id = generate_new_id()
        new_quote = {
            "id": new_id,
            "author": data['author'],
            "text": data['text'],
            "rating": 1
        }
        select_quotes = "INSERT INTO quotes (id, author, text, rating) VALUES (?, ?, ?, ?)"
        connection = sqlite3.connect("store.db")
        cursor = connection.cursor()
        cursor.execute(select_quotes, (new_id, data['author'], data['text'], 1))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(new_quote), 201
    else:
        return jsonify(error="Send bad data to create new quote"), 400


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    new_data = request.json
    for quote in quotes:
        if quote["id"] == id:
            if "author" in new_data:
                quote["author"] = new_data["author"]
            if "text" in new_data:
                quote["text"] = new_data["text"]
            if "rating" in new_data:
                if 1 <= new_data["rating"] <= 5:  # Проверяем корректность рейтинга
                    quote["rating"] = new_data["rating"]
                else:
                    quote["rating"] = quote["rating"]  # Оставляем без изменений, если рейтинг некорректный
            return jsonify(quote), 200
    return jsonify({"error": "Quote not found"}), 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    """Удаление цитат"""
    select_quotes = "DELETE FROM quotes WHERE id=?"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes, (quote_id,))
    connection.commit()
    cursor.close()
    connection.close()

    if cursor.rowcount > 0:
        return jsonify({"message": f"Quote with id {quote_id} is deleted."}), 200
    else:
        return jsonify({"error": "Quote not found"}), 404

@app.route("/quotes/filter", methods=['GET'])
def filter_quotes():
    """Поиск по фильтру"""
    author = request.args.get('author')
    rating = request.args.get('rating')
    filtered_quotes = quotes[:]

    if author:
        filtered_quotes = [quote for quote in filtered_quotes if quote['author'] == author]
    if rating:
        filtered_quotes = [quote for quote in filtered_quotes if str(quote['rating']) == rating]

    return jsonify(filtered_quotes), 200


@app.route("/quotes/filter_v2", methods=['GET'])
def filter_quotes_v2():
    """Поиск по фильтру"""
    filtered_quotes = quotes.copy()
    # Цикл по query parameters
    for key, value in request.args.items():
        result = []
        if key not in KEYS:
            return jsonify(error=f"Invalid param={value}"), 400
        if key == 'rating':
            value = int(value)
        for quote in filtered_quotes:
            if quote[key] == value:
                result.append(quote)     
        filtered_quotes = result.copy()

    return jsonify(filtered_quotes), 200


if __name__ == "__main__":
    app.run(debug=True)