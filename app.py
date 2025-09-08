from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Single-page HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Ad Tools Hub</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
    h1 { color: #333; }
    .tool-box { background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    input[type=text] { width: 350px; padding: 8px; }
    button { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
    button:hover { background: #0056b3; }
    .result { margin-top: 15px; padding: 10px; background: #f1f1f1; border-radius: 8px; }
  </style>
</head>
<body>
  <h1>Ad Tools Hub</h1>

  <div class="tool-box">
    <h2>Ad Density Checker</h2>
    <form method="POST">
      <input type="hidden" name="tool" value="density">
      <input type="text" name="url" placeholder="Enter website URL" required>
      <button type="submit">Check</button>
    </form>
    {% if density %}
    <div class="result">
      <p><b>URL:</b> {{ url }}</p>
      <p>Total Elements: {{ density.elements }}</p>
      <p>Ads Found: {{ density.ads }}</p>
      <p>Ad Density: {{ density.density }}%</p>
      {% if density.error %}<p style="color:red;">Error: {{ density.error }}</p>{% endif %}
    </div>
    {% endif %}
  </div>

  <div class="tool-box">
    <h2>Basic Compliance Checker</h2>
    <form method="POST">
      <input type="hidden" name="tool" value="compliance">
      <input type="text" name="url" placeholder="Enter website URL" required>
      <button type="submit">Check</button>
    </form>
    {% if compliance %}
    <div class="result">
      <p><b>URL:</b> {{ url }}</p>
      <p>Inline Ads Found: {{ compliance.inline }}</p>
      <p>Sticky Ads Found: {{ compliance.sticky }}</p>
      <p>Iframe Ads Found: {{ compliance.iframes }}</p>
      {% if compliance.error %}<p style="color:red;">Error: {{ compliance.error }}</p>{% endif %}
    </div>
    {% endif %}
  </div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    density = None
    compliance = None
    url = None

    if request.method == "POST":
        tool = request.form.get("tool")
        url = request.form.get("url")

        try:
            page = requests.get(url, timeout=5).text
            soup = BeautifulSoup(page, "html.parser")

            if tool == "density":
                all_elements = len(soup.find_all())
                ads = len(soup.find_all(["iframe", "ins"], {"class": "adsbygoogle"}))
                density = {
                    "ads": ads,
                    "elements": all_elements,
                    "density": round((ads / all_elements) * 100, 2) if all_elements else 0,
                    "error": None,
                }

            elif tool == "compliance":
                inline = len(soup.find_all("ins", {"class": "adsbygoogle"}))
                sticky = len(soup.find_all("div", {"class": lambda v: v and "sticky" in v}))
                iframes = len(soup.find_all("iframe"))
                compliance = {
                    "inline": inline,
                    "sticky": sticky,
                    "iframes": iframes,
                    "error": None,
                }

        except Exception as e:
            if tool == "density":
                density = {"ads": 0, "elements": 0, "density": 0, "error": str(e)}
            elif tool == "compliance":
                compliance = {"inline": 0, "sticky": 0, "iframes": 0, "error": str(e)}

    return render_template_string(HTML_TEMPLATE, density=density, compliance=compliance, url=url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
