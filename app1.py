from flask import Flask, jsonify, request
import random

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/") # Это первый url, который мы будем обрабатывать
def hello_world(): # Это функция-обработчик, которая будет вызвана приложением для обработки urlа
    #return "Hello, World!"
    return jsonify(hello="Hello, Studens!!!"), 200

KEYS = ('author', 'text', 'rating')

quotes = [
    {
        "id": 1,
        "author": "Rick Cook",
        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.",
        "rating": 4
    },
    {
        "id": 2,
        "author": "Waldi Ravens",
        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.",
        "rating": 3
    },
    {
        "id": 3,
        "author": "Mosher’s Law of Software Engineering",
        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
        "rating": 2
    },
    {
        "id": 4,
        "author": "Yoggi Berra",
        "text": "В теории, теория и практика неразделимы. На практике это не так.",
        "rating": 1
    },
]


def generate_new_id():
    """Ген id для цитаты"""
    if not quotes:
        return 1
    return quotes[-1]["id"] + 1


@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    new_id = generate_new_id()
    new_quote = {
        "id": new_id,
        "author": data["author"],
        "text": data["text"],
        "rating": data.get("rating", 1)  # Каждая новая цитата должна создаваться с одной звездой
    }
    if new_quote["rating"] < 1 or new_quote["rating"] > 5:
        new_quote["rating"] = 1  # Если некорректный рейтинг(например 10), то оставляем без изменений или устанавливаем значение по умолчанию.
    quotes.append(new_quote)
    return jsonify(new_quote), 201


@app.route("/quotesv2", methods=['POST'])
def create_quotev2():
    new_quote = request.json
    new_id = generate_new_id()
    new_quote["id"] = new_id
    # Каждая новая цитата должна создаваться с одной звездой
    new_quote["rating"] = new_quote.get("rating", 1)
    if new_quote["rating"] < 1 or new_quote["rating"] > 5:
        new_quote["rating"] = 1  # Если некорректный рейтинг(например 10), то оставляем без изменений или устанавливаем значение по умолчанию.
    quotes.append(new_quote)
    return jsonify(new_quote), 201


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
    return jsonify({"error": "Quote with id = {quote_id} not found"}), 404


@app.route("/quotesv2/<int:quote_id>", methods=['PUT'])
def edit_quotev2(quote_id):
    new_data = request.json
    keys = ('author', 'text', 'rating')
    if not set(new_data.keys()) - set(keys):
        for quote in quotes:
            if quote["id"] == quote_id:
                if "rating" in new_data and new_data["rating"] not in range(1, 6):  # Проверяем корректность рейтинга
                    new_data.pop('rating')

                quote.update(new_data)
                return jsonify(quote), 200

    else:
        return jsonify(error="Send bad data"), 200
    return jsonify({"error": "Quote not found"}), 404


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id):
    """Удаление цитат"""
 #   global quotes
    for i, quote in enumerate(quotes):
        if quote["id"] == id:
            del quotes[i]
            return jsonify({"message": f"Quote with id {id} is deleted."}), 200
    return jsonify({"error": "Quote not found"}), 404


@app.get("/quotes")
def get_quotes():
    return jsonify(quotes)


@app.get("/params/<value>")
def get_params(value: str):
    """Пример динамического urlа"""
    return jsonify(param=value, value_type=str(type(value))), 200


@app.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote(quote_id):
    for quote in quotes:
        if quote['id'] == quote_id:
            return jsonify(quote), 200
    # return f"Quote with id={id} not found", 404'
    return jsonify(error=f"Quote with id={quote_id} not found"), 404


@app.route('/quotes/count', methods=['GET'])
def get_quotes_count() -> int:
    count = len(quotes)
    return jsonify({"count": count})


@app.route('/quotes/random', methods=['GET'])
def get_random_quote():
    quote = random.choice(quotes)
    return jsonify(quote)


about_me = {
    "name": "Александр",
    "surname": "Мартынов",
    "email": "sk8alex@mail.ru"
}


@app.route("/about")
def about():
    #return about_me
    return jsonify(about_me), 200


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


@app.route("/quotes/filterv2", methods=['GET'])
def filter_quotesv2():
    """Поиск по фильтру"""
    filtered_quotes = quotes.copy()
    for key, value in request.args.items():
        result = []
        if key not in KEYS:
            return jsonify(error=f'Invalit param={value}'), 400
        if key == 'rating':
            value = int(value)
        for qoute in filter_quotes:
            if qoute[key] == value:
                result.append(qoute)
        filter_quotes = result.copy()

    return jsonify(filtered_quotes), 200


if __name__ == "__main__":
    app.run(debug=True)

