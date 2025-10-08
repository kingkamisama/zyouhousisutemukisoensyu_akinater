from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# JSONデータを読み込む
with open("data.json", encoding="utf-8") as f:
    tree = json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    path = data["path"]  # True/False のリストで進行を表す
    node = tree

    # path に従って yes/no をたどる
    for step in path:
        node = node["yes"] if step else node["no"]

    # キャラに到達したら結果を返す
    if "character" in node:
        return jsonify({"result": node["character"]})
    else:
        return jsonify({"question": node["question"]})

if __name__ == "__main__":
    app.run(debug=True)
