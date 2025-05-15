from flask import Flask, jsonify, request, g, abort
from random import choice
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db"  # <- тут путь к БД

# Создаем соедниение
connection = sqlite3.connect(path_to_db)

app = Flask(__name__)
app.json.ensure_ascii = False

#KEYS = ('author', 'text', 'rating')
KEYS = ('author', 'text')


def make_dicts(cursor, row):
    """ Create dicts from db results."""
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    db.row_factory = make_dicts
    return db


def check(data: dict, check_rating=False) -> tuple[bool, dict]:
    keys = ('author', 'text', 'rating')
    if check_rating:
        rating = data.get('rating')    
        if rating and rating not in range(1, 6):
            return False, {"error": "Rating must be between 1 and 5"}
    
    if set(data.keys()) - set(keys):
        return False, {"error": "Invalid fields to create/update"}
    return True, data


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


# @app.get("/quotes_v2/<int:item_id>")
# def get_quote_by_id_v2(item_id: int):
#     select_quotes = "SELECT * from quotes where id={item_id}"
#     connection = sqlite3.connect("store.db")
#     cursor = connection.cursor()
#     cursor.execute(select_quotes)
#  #   cursor.execute(select_quotes, {"item_id": item_id})
#     quotes_db = cursor.fetchone() # get list[tuple]
#     cursor.close()
#     connection.close()
#     result = {"id": quotes_db[0], "author": quotes_db[1], "text": quotes_db[2]}
#     return result, 200


# @app.get("/quotes_v2/{item_id}")
# async def get_quote_by_id_v2(item_id: int):
#     try:
#         with sqlite3.connect("store.db") as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM quotes WHERE id=?", (item_id,))
#             quote_data = cursor.fetchone()
        
#         if not quote_data:
#             return {"message": f"Citation with ID {item_id} not found"}, 404
    
#         result = {
#             "id": quote_data[0],
#             "author": quote_data[1],
#             "text": quote_data[2]
#         }
#         return result, 200
    
#     except Exception as e:
#         print(f"Error fetching citation by ID {item_id}: {e}")
#         return {"message": "Internal server error"}, 500



@app.get("/quotes/count")
def get_quotes_count() -> int:
    """ Return count of quotes in db."""
    quantity_select = """SELECT COUNT(*) as count FROM quotes"""
    cursor = get_db().cursor()
    count = cursor.execute(quantity_select).fetchone()
    return jsonify(count), 200




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


@app.post("/quotes_v4")
def create_quote_v4(): #Версия преподавателя
    """ Function creates new quote and adds it to db."""
    if (result := check(request.json))[0]:
        new_quote = result[1]
        new_quote["rating"] = 1
        insert_quote = "INSERT INTO quotes (author, text, rating) VALUES (?, ?, ?)"
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(insert_quote, tuple(new_quote.values()))
        try:
            conn.commit()
        except Exception as e:
            conn.rollback()
            abort(503, f"error: {str(e)}")
        else:
            new_quote['id'] = cursor.lastrowid
            return jsonify(new_quote), 201
    
    return jsonify(result[1]), 400


@app.put ("/quotes_v3/<int:item_id>")
def edit_quote_v3(item_id: int):
    data = request.json
    if set(data.keys()) - set(KEYS[1:]):
        return {"message": "Bad Request"}, 400

    select_quotes = f"""
    UPDATE quotes SET author="{data["author"]}", text="{data["text"]}"
    WHERE id={item_id}
    """
    connection = sqlite3.connect(path_to_db)
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    connection.commit()
    result = cursor.rowcount
    cursor.close()
    connection.close()
    if result == 0:
        return jsonify(error=f'Not found quote with id={item_id}')
    responce, status = get_quote_by_id(item_id)
    if status == 200:
        return responce, 200
    



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