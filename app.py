from flask import Flask, jsonify

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/") # Это первый url, который мы будем обрабатывать
def hello_world(): # Это функция-обработчик, которая будет вызвана приложением для обработки urlа
    #return "Hello, World!"
    return jsonify(hello="Hello, Studens!!!"), 200


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

