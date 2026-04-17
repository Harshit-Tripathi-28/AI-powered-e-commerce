function getTrustScore() {
  fetch("http://127.0.0.1:5000/trust-score")
    .then(res => res.json())
    .then(data => {
      document.getElementById("score").innerText =
        "Trust Score: " + data.trust_score;
    });
}

function checkReview() {
  const review = document.getElementById("reviewInput").value;

  fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ review })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerText =
      data.genuine ? "Genuine Review ✅" : "Fake Review ❌";
  });
}
