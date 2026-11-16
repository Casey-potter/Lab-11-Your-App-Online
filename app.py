# IT2025C Week 11 - Week 10's app, ready to go online: a landing page you make yours, and the key in .env.
# Run:    python3 app.py        then open http://127.0.0.1:5001
# Needs:  python3 -m pip install -r requirements.txt
# The whole app is in this one file. Your pictures go in the public/ folder.

import io
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify

# ---------- 1. Settings ----------
load_dotenv()                                           # reads .env from this folder, if it exists
key = os.environ.get("BEARCAT_KEY", "")                    # new: the key lives in .env, not in this file

url = "https://apim-azr-ue2-bgpt-prd-ucin.azure-api.net/openai/deployments/gpt-5.4-ptu/chat/completions?api-version=2024-10-21"
NO_ANSWER = "The file does not answer this question."
instructions = (
    "Answer the question in plain sentences, using the files below. You may summarize, explain, and combine parts of them.\n"
    "Only if nothing in the files is related to the question, reply with exactly this sentence: " + NO_ANSWER
)


# ---------- 2. Read: any file -> text (Week 9) ----------
def read_any(filename, data):
    """data is the raw bytes of the file. Return the text inside it."""# IT2025C Week 11 - Week 10's app, ready to go online: a landing page you make yours, and the key in .env.
# Run:    python3 app.py        then open http://127.0.0.1:5001
# Needs:  python3 -m pip install -r requirements.txt
# The whole app is in this one file. Your pictures go in the public/ folder.

import io
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify

# ---------- 1. Settings ----------
load_dotenv()                                           # reads .env from this folder, if it exists
key = os.environ.get("BEARCAT_KEY", "")                    # new: the key lives in .env, not in this file

url = "https://apim-azr-ue2-bgpt-prd-ucin.azure-api.net/openai/deployments/gpt-5.4-ptu/chat/completions?api-version=2024-10-21"
NO_ANSWER = "The file does not answer this question."
instructions = (
    "Answer the question in plain sentences, using the files below. You may summarize, explain, and combine parts of them.\n"
    "Only if nothing in the files is related to the question, reply with exactly this sentence: " + NO_ANSWER
)


# ---------- 2. Read: any file -> text (Week 9) ----------
def read_any(filename, data):
    """data is the raw bytes of the file. Return the text inside it."""
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))       # treat the bytes as a file
        text = ""
        for page in reader.pages:
            text = text + page.extract_text() + "\n"
        return text
    if name.endswith(".docx"):
        import docx
        document = docx.Document(io.BytesIO(data))
        text = ""
        for paragraph in document.paragraphs:
            text = text + paragraph.text + "\n"
        return text
    return data.decode("utf-8", errors="replace")  # .txt .csv .md: the bytes already are text


# ---------- 3. Ask: send the whole text of every file and the question to GPT-5.4 (Week 10) ----------
def ask_files(file_texts, prompt):
    """file_texts is a list of (file name, text). The model reads all of it."""
    if key in (""):                            # new: no key in .env, so say so instead of calling the model
        return "No key found. Copy .env.example to .env and put your key after BEARCAT_KEY="
    context = ""
    for name, text in file_texts:
        context = context + "File: " + name + "\n" + text + "\n\n"
    payload = {
        "model": "gpt-5.4-ptu",
        "messages": [{"role": "system", "content": instructions}, {"role": "user", "content": "Files:\n" + context + "Question: " + prompt}],
        "max_completion_tokens": 2000
    }
    response = requests.post(url, headers={"api-key": key}, json=payload)
    data = response.json() if "json" in response.headers.get("Content-Type", "") else {}   # some errors are not JSON
    if "choices" not in data:
        return "The API said no (status " + str(response.status_code) + "): " + (str(data) if data else response.text[:300])
    return data["choices"][0]["message"]["content"]


# ---------- 4. The web app: three pages and a health check ----------
app = Flask(__name__, static_folder="public", static_url_path="")   # new: public/hero.png is at /hero.png


@app.route("/")
def home():
    return render_template_string(LANDING_PAGE)            # new: the first page people see


@app.route("/start")
def start():
    return render_template_string(INDEX_PAGE)              # the form (it was at / in Week 10)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Week 11 app is running."})


@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt", "").strip()
    uploads = [u for u in request.files.getlist("file") if u.filename != ""]   # one or more files
    if prompt == "" or uploads == []:
        return render_template_string(RESULT_PAGE, files=[], prompt=prompt,
                                    answer="Choose at least one file and type a question first.")
    file_texts = []
    for upload in uploads:
        file_texts.append((upload.filename, read_any(upload.filename, upload.read())))   # bytes -> text
    answer = ask_files(file_texts, prompt)                  # the model reads every file
    return render_template_string(RESULT_PAGE, files=[u.filename for u in uploads], prompt=prompt, answer=answer)


# ---------- 5. The pages: how they look (STYLE) and what they say ----------
# Change STYLE or a page, save, and refresh the browser.
# Asking BearcatGPT for help? Paste this part. Your key is in .env, not here.

STYLE = """
:root {
  --brand: #0F172A;       /* deep slate navy */
  --accent: #0284C7;      /* crisp security cyan-blue */
  --accent-hover: #0369A1;
  --page: #F1F5F9;        /* cool light gray background */
  --surface: #FFFFFF;     /* card surface */
  --text: #0F172A;        /* primary dark slate text */
  --muted: #475569;       /* secondary muted text */
  --border: #E2E8F0;      /* subtle border */
}

* {
  box-sizing: border-box;
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text);
  background: var(--page);
  max-width: 920px;
  margin: 0 auto;
  padding: 0 20px 48px;
  line-height: 1.6;
}

/* Top navigation bar shared across all pages */
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
}
.nav a {
  color: var(--brand);
  text-decoration: none;
  padding: 6px 10px;
  border-radius: 6px;
}
.nav a:hover {
  background: var(--border);
}

/* Shared header used on INDEX_PAGE and RESULT_PAGE */
.header {
  background: linear-gradient(135deg, var(--brand) 0%, #1E3A8A 100%);
  color: white;
  padding: 24px 28px;
  border-radius: 14px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
}
.header h1 { margin: 0 0 6px; font-size: 1.75rem; }
.header p { margin: 0; opacity: 0.9; }

/* Landing Page Hero Split Layout */
.hero-box {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 28px;
  align-items: center;
  background: linear-gradient(135deg, var(--brand) 0%, #1E293B 100%);
  color: white;
  padding: 36px 32px;
  border-radius: 16px;
  margin-bottom: 28px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
}
.hero-badge {
  display: inline-block;
  background: rgba(2, 132, 199, 0.25);
  color: #7DD3FC;
  border: 1px solid rgba(125, 211, 252, 0.3);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 12px;
}
.hero-content h1 {
  margin: 0 0 12px;
  font-size: 2.1rem;
  line-height: 1.2;
}
.hero-content p {
  margin: 0 0 22px;
  color: #CBD5E1;
  font-size: 1.05rem;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.hero {
  width: 100%;
  border-radius: 12px;
  display: block;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: white;
}

/* Feature grid on landing page */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.feature-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.feature-card h3 {
  margin: 0 0 8px;
  font-size: 1.05rem;
  color: var(--brand);
}
.feature-card p {
  margin: 0;
  font-size: 0.92rem;
  color: var(--muted);
}

/* Cards and Steps (shared with INDEX_PAGE and RESULT_PAGE) */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 24px 28px;
  margin-bottom: 24px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}
.card h2 {
  margin-top: 0;
  font-size: 1.35rem;
}
.steps {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin: 18px 0 8px;
}
.step {
  flex: 1;
  min-width: 180px;
  background: var(--page);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}
.step-num {
  display: inline-block;
  background: var(--accent);
  color: white;
  font-weight: bold;
  font-size: 0.85rem;
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  border-radius: 50%;
  margin-bottom: 8px;
}

/* Forms and Buttons */
label { display: block; font-weight: bold; margin: 14px 0 6px; }
input, textarea {
  width: 100%;
  font: inherit;
  padding: 10px 12px;
  border: 1px solid #CBD5E1;
  border-radius: 8px;
  background: #F8FAFC;
}
button, .button {
  display: inline-block;
  margin-top: 16px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 22px;
  font: inherit;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
}
button:hover, .button:hover {
  background: var(--accent-hover);
}
.hero-actions .button {
  margin-top: 0;
}
.button-secondary {
  display: inline-block;
  background: rgba(255, 255, 255, 0.12);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  padding: 12px 20px;
  font: inherit;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
}
.button-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.answer { font-size: 18px; white-space: pre-wrap; border-left: 6px solid var(--accent); }
.note { color: var(--muted); font-size: 14px; }

.footer {
  margin-top: 32px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--muted);
  font-size: 0.88rem;
}

/* Mobile rules: 720px or less -> single column & full-width buttons */
@media (max-width: 720px) {
  .hero-box {
    grid-template-columns: 1fr;
    padding: 24px 20px;
  }
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .steps {
    flex-direction: column;
  }
  .hero-actions {
    flex-direction: column;
  }
  button, .button, .button-secondary {
    display: block;
    width: 100%;
  }
}
"""

# The landing page: redesigned hero, 3 feature cards, 3-step workflow, and footer
LANDING_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ask a cybersecurity question</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav">
      <a href="/">Home</a>
      <a href="/start">Ask a cybersecurity question</a>
    </nav>

    <section class="hero-box">
      <div class="hero-content">
        <span class="hero-badge">Document-Grounded Security Q&amp;A</span>
        <h1>Ask a cybersecurity question</h1>
        <p>Upload security policies, audit logs, or technical notes and get plain-language answers grounded strictly in your files.</p>
        <div class="hero-actions">
          <a class="button" href="/start">Analyze Your Files</a>
          <a class="button-secondary" href="#how-it-works">How It Works</a>
        </div>
      </div>
      <img class="hero" src="/hero.png" alt="A stack of pages and a question bubble">
    </section>

    <section class="feature-grid">
      <div class="feature-card">
        <h3>Multi-File Support</h3>
        <p>Upload one or multiple .txt, .csv, .md, .pdf, or .docx documents at once to cross-reference details.</p>
      </div>
      <div class="feature-card">
        <h3>Source-Bound Answers</h3>
        <p>Responses rely strictly on the files you provide rather than outside guesses or unverified sources.</p>
      </div>
      <div class="feature-card">
        <h3>Plain-English Clarity</h3>
        <p>Turn dense policy jargon or technical logs into clear, direct sentences you can verify immediately.</p>
      </div>
    </section>

    <div class="card" id="how-it-works">
      <h2>How it works</h2>
      <div class="steps">
        <div class="step">
          <span class="step-num">1</span><br>
          <strong>Upload your documents</strong><br>
          Select one or more PDF, Word, Markdown, CSV, or text files.
        </div>
        <div class="step">
          <span class="step-num">2</span><br>
          <strong>Ask a specific question</strong><br>
          Type what you need to find in plain, everyday words.
        </div>
        <div class="step">
          <span class="step-num">3</span><br>
          <strong>Verify the answer</strong><br>
          Read a concise response generated only from your uploaded files.
        </div>
      </div>
      <a class="button" href="/start">Start Asking Questions</a>
    </div>

    <footer class="footer">
      <span>Ask a cybersecurity question</span>
      <span>Reminder: Upload fictional or public files only.</span>
    </footer>
  </body>
</html>"""

# The form page: updated title, header, and nav link
INDEX_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ask a cybersecurity question</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a cybersecurity question</a></nav>
    <header class="header">
      <h1>Ask a cybersecurity question</h1>
      <p>Upload one or more files and ask one question about them.</p>
    </header>
    <form class="card" action="/ask" method="post" enctype="multipart/form-data"
          onsubmit="this.querySelector('button').textContent = 'Reading your files...';">
      <label for="file">Your files: one or more (.txt, .csv, .md, .pdf, .docx)</label>
      <input type="file" id="file" name="file" accept=".txt,.csv,.md,.pdf,.docx" multiple>
      <label for="prompt">Your question</label>
      <textarea id="prompt" name="prompt" rows="3"></textarea>
      <button type="submit">Ask</button>
    </form>
    <p class="note">Use fictional or public files only.</p>
  </body>
</html>"""

# The answer page. {{ name }} prints a value from Python.
RESULT_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Answer</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a cybersecurity question</a></nav>
    <header class="header">
      <h1>Answer</h1>
      <p><strong>Files:</strong> {{ files|join(", ") }} &middot; <strong>Question:</strong> {{ prompt }}</p>
    </header>
    <div class="card answer">{{ answer }}</div>
    <a class="button" href="/start">Ask another question</a>
  </body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5001)   # 5001, not 5000: on a Mac, AirPlay already uses 5000
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))       # treat the bytes as a file
        text = ""
        for page in reader.pages:
            text = text + page.extract_text() + "\n"
        return text
    if name.endswith(".docx"):
        import docx
        document = docx.Document(io.BytesIO(data))
        text = ""
        for paragraph in document.paragraphs:
            text = text + paragraph.text + "\n"
        return text
    return data.decode("utf-8", errors="replace")  # .txt .csv .md: the bytes already are text


# ---------- 3. Ask: send the whole text of every file and the question to GPT-5.4 (Week 10) ----------
def ask_files(file_texts, prompt):
    """file_texts is a list of (file name, text). The model reads all of it."""
    if key in (""):                            # new: no key in .env, so say so instead of calling the model
        return "No key found. Copy .env.example to .env and put your key after BEARCAT_KEY="
    context = ""
    for name, text in file_texts:
        context = context + "File: " + name + "\n" + text + "\n\n"
    payload = {
        "model": "gpt-5.4-ptu",
        "messages": [{"role": "system", "content": instructions}, {"role": "user", "content": "Files:\n" + context + "Question: " + prompt}],
        "max_completion_tokens": 2000
    }
    response = requests.post(url, headers={"api-key": key}, json=payload)
    data = response.json() if "json" in response.headers.get("Content-Type", "") else {}   # some errors are not JSON
    if "choices" not in data:
        return "The API said no (status " + str(response.status_code) + "): " + (str(data) if data else response.text[:300])
    return data["choices"][0]["message"]["content"]


# ---------- 4. The web app: three pages and a health check ----------
app = Flask(__name__, static_folder="public", static_url_path="")   # new: public/hero.png is at /hero.png


@app.route("/")
def home():
    return render_template_string(LANDING_PAGE)            # new: the first page people see


@app.route("/start")
def start():
    return render_template_string(INDEX_PAGE)              # the form (it was at / in Week 10)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Week 11 app is running."})


@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt", "").strip()
    uploads = [u for u in request.files.getlist("file") if u.filename != ""]   # one or more files
    if prompt == "" or uploads == []:
        return render_template_string(RESULT_PAGE, files=[], prompt=prompt,
                                    answer="Choose at least one file and type a question first.")
    file_texts = []
    for upload in uploads:
        file_texts.append((upload.filename, read_any(upload.filename, upload.read())))   # bytes -> text
    answer = ask_files(file_texts, prompt)                  # the model reads every file
    return render_template_string(RESULT_PAGE, files=[u.filename for u in uploads], prompt=prompt, answer=answer)


# ---------- 5. The pages: how they look (STYLE) and what they say ----------
# Change STYLE or a page, save, and refresh the browser.
# Asking BearcatGPT for help? Paste this part. Your key is in .env, not here.

STYLE = """
/* Make it yours: change these values first. */
:root {
  --brand: #1E3A8A;      /* changed from red to Navy blue */
  --page: #f4f5f7;       /* the page background */
  --text: #1f2933;       /* normal text */
  --muted: #6b7280;      /* small, less important text */
}

/* One readable column in the middle of the page */
body {
  font-family: Arial, sans-serif;
  color: var(--text);
  background: var(--page);
  max-width: 760px;
  margin: 0 auto;
  padding: 0 16px 40px;
  line-height: 1.5;
}

/* A bar at the top of every page */
.nav { display: flex; gap: 16px; padding: 12px 0; font-weight: bold; }
.nav a { color: var(--brand); text-decoration: none; }

/* The header: the biggest thing on the page says what the app is */
.header {
  background: var(--brand);
  color: white;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}
.header h1 { margin: 0 0 4px; }
.header p { margin: 0; }

/* The picture on the landing page */
.hero { width: 100%; border-radius: 12px; margin-bottom: 24px; display: block; }

/* Cards: a white box groups things that belong together */
.card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
.steps { display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }
.step { flex: 1; min-width: 160px; background: var(--page); border-radius: 10px; padding: 12px 14px; }
label { display: block; font-weight: bold; margin: 12px 0 6px; }
input, textarea { width: 100%; box-sizing: border-box; font: inherit; padding: 8px; }
button, .button {
  display: inline-block;
  margin-top: 16px;
  background: var(--brand);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font: inherit;
  font-weight: bold;
  text-decoration: none;
}
.answer { font-size: 18px; white-space: pre-wrap; border-left: 6px solid var(--brand); }
.note { color: var(--muted); font-size: 14px; }
"""

# The landing page: updated title, header, removed "Who it is for", updated nav link
LANDING_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ask a cybersecurity question</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a cybersecurity question</a></nav>
    <header class="header">
      <h1>Ask a cybersecurity question</h1>
      <p>Ask a question about your own files and get an answer in plain sentences.</p>
    </header>
    <img class="hero" src="/hero.png" alt="A stack of pages and a question bubble">
    <div class="card">
      <h2>How it works</h2>
      <div class="steps">
        <div class="step"><strong>1. Upload</strong><br>One or more files: PDF, Word, or text.</div>
        <div class="step"><strong>2. Ask</strong><br>One question, in plain words.</div>
        <div class="step"><strong>3. Read</strong><br>An answer that uses only your files.</div>
      </div>
      <a class="button" href="/start">Start</a>
    </div>
    <p class="note">Use fictional or public files only.</p>
  </body>
</html>"""

# The form page: updated title, header, and nav link
INDEX_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ask a cybersecurity question</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a cybersecurity question</a></nav>
    <header class="header">
      <h1>Ask a cybersecurity question</h1>
      <p>Upload one or more files and ask one question about them.</p>
    </header>
    <form class="card" action="/ask" method="post" enctype="multipart/form-data"
          onsubmit="this.querySelector('button').textContent = 'Reading your files...';">
      <label for="file">Your files: one or more (.txt, .csv, .md, .pdf, .docx)</label>
      <input type="file" id="file" name="file" accept=".txt,.csv,.md,.pdf,.docx" multiple>
      <label for="prompt">Your question</label>
      <textarea id="prompt" name="prompt" rows="3"></textarea>
      <button type="submit">Ask</button>
    </form>
    <p class="note">Use fictional or public files only.</p>
  </body>
</html>"""

# The answer page. {{ name }} prints a value from Python.
RESULT_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Answer</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a cybersecurity question</a></nav>
    <header class="header">
      <h1>Answer</h1>
      <p><strong>Files:</strong> {{ files|join(", ") }} &middot; <strong>Question:</strong> {{ prompt }}</p>
    </header>
    <div class="card answer">{{ answer }}</div>
    <a class="button" href="/start">Ask another question</a>
  </body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5001)   # 5001, not 5000: on a Mac, AirPlay already uses 5000
