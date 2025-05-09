from flask import Flask, jsonify
import random

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/") # Это первый url, который мы будем обрабатывать
def hello_world(): # Это функция-обработчик, которая будет вызвана приложением для обработки urlа
    #return "Hello, World!"
    return jsonify(hello="Hello, Studens!!!"), 200


quotes = [
    {
        "id": 1,
        "author": "Rick Cook",
        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
    },
    {
        "id": 2,
        "author": "Waldi Ravens",
        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
    },
    {
        "id": 3,
        "author": "Mosher’s Law of Software Engineering",
        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
    },
    {
        "id": 4,
        "author": "Yoggi Berra",
        "text": "В теории, теория и практика неразделимы. На практике это не так."
    },
]

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
def get_quotes_count():
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


if __name__ == "__main__":
    app.run(debug=True)

