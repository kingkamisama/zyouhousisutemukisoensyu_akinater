from flask import Flask, render_template, request, jsonify
import json
import copy

app = Flask(__name__)

with open("data.json", encoding="utf-8") as f:
    tree = json.load(f)

session_node = copy.deepcopy(tree)

@app.route("/")
def index():
    return render_template("enter.html")

@app.route("/play")
def play():
    return render_template("play.html")

@app.route("/question")
def get_question():
    global session_node
    session_node = copy.deepcopy(tree)
    return jsonify({"question": session_node["question"]})

@app.route("/answer", methods=["POST"])
def answer():
    global session_node
    data = request.get_json()
    ans = data["answer"]

    next_node = session_node.get(ans)
    if not next_node:
        return jsonify({"end": True, "result": "わかりませんでした…😢"})

    if "character" in next_node:
        return jsonify({"end": True, "result": next_node["character"]})
    else:
        session_node = next_node
        return jsonify({"end": False, "question": session_node["question"]})

if __name__ == "__main__":
    app.run(debug=True)
