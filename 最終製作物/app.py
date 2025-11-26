from flask import Flask, jsonify, request, render_template, url_for
import json, math, random, copy

app = Flask(__name__)

# --- データ読み込み ---
with open("data.json", encoding="utf-8") as f:
    DATA = json.load(f)

FEATURES = DATA["features"]  # 質問文（特徴名→質問文）
SAMPLES = DATA["samples"]    # 教員データ


# --- エントロピー計算 ---
def entropy(data):
    names = [d["name"] for d in data]
    total = len(names)
    counts = {n: names.count(n) for n in set(names)}
    return -sum((c/total) * math.log2(c/total) for c in counts.values())


# --- 情報利得を計算 ---
def info_gain(data, feature):
    total_entropy = entropy(data)
    subsets = {True: [], False: []}
    for d in data:
        subsets[d["features"][feature]].append(d)
    weighted_entropy = sum((len(sub) / len(data)) * entropy(sub) for sub in subsets.values() if len(sub) > 0)
    return total_entropy - weighted_entropy


# --- 状態 ---
session_state = {
    "remaining_features": list(FEATURES.keys()),
    "answers": {},
    "data": copy.deepcopy(SAMPLES),
}


@app.route("/")
def index():
    return render_template("enter.html")


@app.route("/play")
def play():
    # 新しいセッションに初期化
    global session_state
    session_state = {
        "remaining_features": list(FEATURES.keys()),
        "answers": {},
        "data": copy.deepcopy(SAMPLES),
    }
    return render_template("play.html")


@app.route("/question", methods=["GET", "POST"])
def question():
    global session_state
    data = request.get_json()

    # 回答を反映
    if data and "answer" in data:
        last_feature = session_state.get("last_feature")
        if last_feature:
            ans = data["answer"] == "yes"
            session_state["answers"][last_feature] = ans
            session_state["data"] = [d for d in session_state["data"] if d["features"][last_feature] == ans]

            # 候補ゼロなら即終了
            if len(session_state["data"]) == 0:
                return jsonify({
                    "end": True,
                    "result": "該当なし",
                    "image": "",
                    "url": None
                })

    # 候補が1人になったら終了
    if len(session_state["data"]) == 1:
        result = session_state["data"][0]
        image_url = url_for('static', filename=result.get("image", ""))
        return jsonify({
            "end": True,
            "result": result["name"],
            "image": image_url,
            "url": result.get("url", None)
        })


    # 特徴が尽きたら終了
    if not session_state["remaining_features"]:
        return jsonify({"end": True, "result": "該当なし", "image": ""})

    # 情報利得を計算
    gains = [(f, info_gain(session_state["data"], f)) for f in session_state["remaining_features"]]
    gains.sort(key=lambda x: x[1], reverse=True)

    # 上位3つからランダムに1つ選ぶ
    top3 = [f for f, _ in gains[:3]] if len(gains) >= 3 else [f for f, _ in gains]
    chosen = random.choice(top3)
    session_state["last_feature"] = chosen
    session_state["remaining_features"].remove(chosen)

    question_text = FEATURES[chosen]
    return jsonify({"end": False, "question": question_text})

import requests
from flask import Response, request
from urllib.parse import urljoin
import re

@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return "URLが指定されていません", 400

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    content_type = r.headers.get("Content-Type", "")

    # HTML の場合のみ書き換え
    if "text/html" in content_type:
        r.encoding = r.apparent_encoding
        html = r.text

        # --- img src の完全変換 ---
        # src="xxx", src='xxx', src=xxx, src=//xxx すべて対応
        def replace_src(match):
            src = match.group(1)
            abs_url = urljoin(url, src)
            return f'src="/proxy_img?url={abs_url}"'

        # img タグの src を置換
        html = re.sub(
            r'src\s*=\s*["\']?([^"\'>\s]+)["\']?',
            replace_src,
            html,
            flags=re.IGNORECASE
        )

        return Response(html, content_type=f"text/html; charset={r.encoding}")

    # HTML 以外は生のまま返す
    return Response(r.content, content_type=content_type)




@app.route("/proxy_img")
def proxy_img():
    img_url = request.args.get("url")
    if not img_url:
        return "", 404

    try:
        r = requests.get(img_url)
        return Response(r.content, content_type=r.headers.get("Content-Type"))
    except:
        return "", 404

if __name__ == "__main__":
    app.run(debug=True)
