from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load scraped data
df = pd.read_csv("myjobs_detailed.csv")

@app.route("/", methods=["GET", "POST"])
def home():
    query = request.form.get("query", "").lower()
    location = request.form.get("location", "").lower()
    field = request.form.get("field", "").lower()

    results = df.copy()

    # Filter dynamically based on form input
    if query:
        results = results[results['Job Title & Company'].str.lower().str.contains(query, na=False)]
    if location:
        results = results[results['Location'].str.lower().str.contains(location, na=False)]
    if field:
        results = results[results['Field'].str.lower().str.contains(field, na=False)]

    return render_template("index.html", jobs=results.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
