let path = []; // True:はい, False:いいえ

function showQuestion(text) {
  document.getElementById("question").textContent = text;
  const buttons = document.getElementById("buttons");
  buttons.innerHTML = "";

  const yesBtn = document.createElement("button");
  yesBtn.textContent = "はい";
  yesBtn.onclick = () => answer(true);

  const noBtn = document.createElement("button");
  noBtn.textContent = "いいえ";
  noBtn.onclick = () => answer(false);

  buttons.appendChild(yesBtn);
  buttons.appendChild(noBtn);
}

function showResult(text) {
  document.getElementById("question").textContent = `あなたが思い浮かべたのは「${text}」ですね？`;
  const buttons = document.getElementById("buttons");
  buttons.innerHTML = "";

  const restartBtn = document.createElement("button");
  restartBtn.textContent = "もう一度";
  restartBtn.onclick = () => {
    path = [];
    fetchQuestion();
  };
  buttons.appendChild(restartBtn);
}

function answer(yes) {
  path.push(yes);
  fetch("/answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path })
  })
  .then(res => res.json())
  .then(data => {
    if (data.result) showResult(data.result);
    else showQuestion(data.question);
  });
}

// 初回読み込み
fetch("/answer", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ path: [] })
})
  .then(res => res.json())
  .then(data => showQuestion(data.question));
