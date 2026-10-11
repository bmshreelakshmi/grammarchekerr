from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Grammar Checker</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: Arial, sans-serif;
}

body {
    background: #f5f7fb;
    color: #202124;
}

header {
    background: white;
    padding: 20px 7%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e5e7eb;
}

.logo {
    font-size: 25px;
    font-weight: bold;
    color: #15a67a;
}

.badge {
    background: #e5f8ef;
    color: #087c55;
    padding: 8px 14px;
    border-radius: 20px;
    font-size: 13px;
}

.hero {
    text-align: center;
    padding: 45px 20px 30px;
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 15px;
}

.hero h1 span {
    color: #13a77a;
}

.hero p {
    color: #667085;
    font-size: 16px;
    line-height: 1.6;
}

.container {
    max-width: 1050px;
    margin: 0 auto;
    padding: 15px 20px 50px;
}

.editor {
    background: white;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.06);
    border: 1px solid #e8ebf0;
}

.label-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    font-weight: bold;
    font-size: 14px;
}

.counter {
    color: #858b98;
    font-weight: normal;
}

textarea {
    width: 100%;
    height: 220px;
    resize: vertical;
    border: 1px solid #dfe3e9;
    border-radius: 10px;
    padding: 18px;
    font-size: 16px;
    line-height: 1.8;
    outline: none;
}

textarea:focus {
    border-color: #13a77a;
    box-shadow: 0 0 0 3px #e4f8ef;
}

.actions {
    display: flex;
    gap: 12px;
    margin-top: 18px;
    flex-wrap: wrap;
}

button {
    border: none;
    cursor: pointer;
    border-radius: 9px;
    padding: 13px 22px;
    font-size: 15px;
    font-weight: bold;
}

.check-btn {
    background: #13a77a;
    color: white;
    flex: 1;
}

.check-btn:hover {
    background: #0b8c64;
}

.clear-btn, .copy-btn {
    background: #eef1f5;
    color: #333b49;
}

button:disabled {
    opacity: 0.6;
    cursor: wait;
}

.result {
    display: none;
    margin-top: 25px;
    background: white;
    padding: 25px;
    border: 1px solid #e8ebf0;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
}

.result h2 {
    margin-bottom: 18px;
    font-size: 22px;
}

.result h3 {
    margin: 20px 0 12px;
    font-size: 17px;
}

.result-text {
    background: #f1fbf6;
    padding: 20px;
    border-radius: 10px;
    line-height: 1.9;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.result-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin: 18px 0;
    flex-wrap: wrap;
}

.status {
    color: #0b8c64;
    font-weight: bold;
    margin-bottom: 15px;
}

.error-card {
    padding: 17px;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    margin-top: 12px;
    background: white;
}

.error-card p {
    margin-bottom: 10px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.error-title {
    color: #d04444;
    font-weight: bold;
    font-size: 16px;
}

.suggestion {
    color: #087c55;
    font-weight: bold;
}

.reason {
    color: #444b57;
}

footer {
    text-align: center;
    padding: 25px;
    color: #858b98;
    font-size: 13px;
}

@media(max-width: 600px) {
    .hero h1 {
        font-size: 29px;
    }

    header {
        padding: 18px;
    }

    .editor, .result {
        padding: 17px;
    }

    .actions button {
        width: 100%;
        flex: auto;
    }
}
</style>
</head>

<body>

<header>
    <div class="logo">✦ GrammarAI</div>
    <div class="badge">AI Writing Assistant</div>
</header>

<section class="hero">
    <h1>Write better with <span>GrammarAI</span></h1>
    <p>
        Check your English grammar, discover mistakes, and improve<br>
        your writing in seconds.
    </p>
</section>

<main class="container">

    <section class="editor">
        <div class="label-row">
            <span>Your text</span>
            <span class="counter" id="counter">0 words</span>
        </div>

        <textarea id="inputText"
        placeholder="Enter your English text here...

Example: im amrutha."></textarea>

        <div class="actions">
            <button class="check-btn" id="checkBtn"
            onclick="checkGrammar()">✦ Check Grammar</button>

            <button class="clear-btn" onclick="clearText()">Clear</button>
        </div>
    </section>

    <section class="result" id="result">

        <h2>✨ Grammar Check Results</h2>

        <div class="status" id="status"></div>

        <h3>Original text</h3>
        <div class="result-text" id="original"></div>

        <div class="result-actions">
            <strong>Corrected text</strong>
            <button class="copy-btn" onclick="copyText()">
                📋 Copy text
            </button>
        </div>

        <div class="result-text" id="corrected"></div>

        <h2 style="margin-top:25px;">Detected Mistakes</h2>
        <div id="errors"></div>

    </section>

</main>

<footer>
    GrammarAI — AI-powered English writing assistance
</footer>

<script>
const input = document.getElementById("inputText");
const counter = document.getElementById("counter");

input.addEventListener("input", function() {
    const text = input.value.trim();
    const words = text ? text.split(/\\s+/).length : 0;
    counter.textContent =
        words + (words === 1 ? " word" : " words");
});

async function checkGrammar() {
    const text = input.value;

    if (!text.trim()) {
        alert("Please enter some English text first.");
        return;
    }

    const button = document.getElementById("checkBtn");
    const result = document.getElementById("result");

    button.disabled = true;
    button.textContent = "Checking grammar...";
    result.style.display = "block";

    document.getElementById("status").textContent =
        "Analyzing your text...";

    document.getElementById("original").textContent = text;
    document.getElementById("corrected").textContent = "";
    document.getElementById("errors").textContent = "";

    try {
        const response = await fetch("/check", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text: text})
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Grammar check failed.");
        }

        document.getElementById("original").textContent =
            data.original;

        document.getElementById("corrected").textContent =
            data.corrected;

        document.getElementById("status").textContent =
            data.errors.length === 0
            ? "✓ No grammar issues detected!"
            : data.errors.length + " issue(s) detected.";

        const errorsBox = document.getElementById("errors");

        if (data.errors.length === 0) {
            errorsBox.textContent = "Your text looks good!";
        } else {
            data.errors.forEach(function(err, index) {
                const card = document.createElement("div");
                card.className = "error-card";

                const title = document.createElement("p");
                title.className = "error-title";
                title.textContent =
                    (index + 1) + ". Mistake: " + err.original;
                card.appendChild(title);

                const correction = document.createElement("p");
                correction.className = "suggestion";
                correction.textContent =
                    "Correction: " +
                    (err.suggestions.length
                    ? err.suggestions.join(", ")
                    : "No suggestion available");
                card.appendChild(correction);

                const reason = document.createElement("p");
                reason.className = "reason";
                reason.textContent = "Reason: " + err.reason;
                card.appendChild(reason);

                errorsBox.appendChild(card);
            });
        }

        result.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        document.getElementById("status").textContent =
            "Unable to check grammar.";

        document.getElementById("errors").textContent =
            error.message +
            " Check your internet connection and try again.";
    } finally {
        button.disabled = false;
        button.textContent = "✦ Check Grammar";
    }
}

function clearText() {
    input.value = "";
    counter.textContent = "0 words";
    document.getElementById("result").style.display = "none";
    input.focus();
}

async function copyText() {
    const text = document.getElementById("corrected").textContent;

    try {
        await navigator.clipboard.writeText(text);
        alert("Corrected text copied!");
    } catch (error) {
        alert("Copy failed. Please copy the text manually.");
    }
}
</script>

</body>
</html>
"""


# Common names and pet names that should not be changed.
KNOWN_NAMES = {
    "amrutha", "amith", "rahul", "priya", "shadow"
}

# Common place names that should not be treated as person names.
PLACE_NAMES = {
    "india", "karnataka", "bangalore", "bengaluru",
    "mysore", "mysuru", "delhi", "mumbai", "chennai",
    "hyderabad", "pune", "london", "paris", "america"
}

# Rules for frequent informal spelling and capitalization mistakes.
CUSTOM_RULES = [
    {
        "pattern": r"(?i)(?<!\\w)im(?!\\w)",
        "correct": "I'm",
        "reason": (
            "The contraction of 'I am' is written as 'I'm'. "
            "An apostrophe replaces the omitted letter 'a'."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)i\s+am(?!\\w)",
        "correct": "I am",
        "reason": (
            "'I am' is the full form. Both words should be "
            "written separately, with 'I' capitalized."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)clg(?!\\w)",
        "correct": "college",
        "reason": (
            "'Clg' is an informal abbreviation. Use 'college' "
            "in standard English writing."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)u(?!\\w)",
        "correct": "you",
        "reason": (
            "'U' is an informal texting abbreviation. "
            "Use 'you' in standard English."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)ur(?!\\w)",
        "correct": "your",
        "reason": (
            "'Ur' is an informal abbreviation. Use 'your' "
            "when indicating possession."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)dont(?!\\w)",
        "correct": "don't",
        "reason": (
            "'Don't' is the standard contraction of 'do not' "
            "and requires an apostrophe."
        )
    },
    {
        "pattern": r"(?i)(?<!\\w)cant(?!\\w)",
        "correct": "can't",
        "reason": (
            "'Can't' is the standard contraction of 'cannot' "
            "and requires an apostrophe."
        )
    }
]


def get_name_spans(text):
    """Find known names and capitalized name candidates."""

    spans = []

    # Protect known names regardless of capitalization.
    for name in KNOWN_NAMES:
        pattern = (
            r"(?<!\\w)" + re.escape(name) + r"(?!\\w)"
        )

        for match in re.finditer(pattern, text, re.IGNORECASE):
            spans.append(match.span())

    # Protect other capitalized words that may be names.
    pattern = r"\\b[A-Z][a-z]+\\b"

    common_words = {
        "hi", "hello", "hey", "today", "yesterday",
        "tomorrow", "the", "this", "that", "my",
        "your", "our", "i", "he", "she", "we",
        "they", "it", "what", "when", "where",
        "why", "how", "who", "after", "before"
    }

    for match in re.finditer(pattern, text):
        word = match.group().lower()

        if word in common_words or word in PLACE_NAMES:
            continue

        spans.append(match.span())

    return sorted(set(spans))


def overlaps(start, end, spans):
    return any(
        start < span_end and end > span_start
        for span_start, span_end in spans
    )


def get_custom_matches(text):
    """Return corrections and explanations for custom rules."""

    results = []

    for rule in CUSTOM_RULES:
        for match in re.finditer(rule["pattern"], text):
            original = match.group()

            # Preserve the user's chosen name capitalization.
            if original.lower() in KNOWN_NAMES:
                continue

            results.append({
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "correct": rule["correct"],
                "reason": rule["reason"]
            })

    return results


def get_capitalization_matches(text):
    """Suggest capitalization for known names without changing identity."""

    results = []

    for name in KNOWN_NAMES:
        pattern = (
            r"(?<!\\w)" + re.escape(name) + r"(?!\\w)"
        )

        for match in re.finditer(pattern, text, re.IGNORECASE):
            original = match.group()

            if original == name.capitalize():
                continue

            results.append({
                "start": match.start(),
                "end": match.end(),
                "original": original,
                "correct": name.capitalize(),
                "reason": (
                    "Names are proper nouns and normally begin "
                    "with a capital letter. This capitalization "
                    "suggestion preserves the name itself."
                )
            })

    return results


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/check", methods=["POST"])
def check_grammar():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not isinstance(text, str) or not text.strip():
        return jsonify({
            "error": "Please enter some text."
        }), 400

    if len(text) > 15000:
        return jsonify({
            "error": "Please keep the text under 15,000 characters."
        }), 400

    name_spans = get_name_spans(text)

    # Apply custom rules first.
    matches = get_custom_matches(text)

    # Add capitalization suggestions for known names.
    matches.extend(get_capitalization_matches(text))

    # Ask LanguageTool for additional grammar suggestions.
    try:
        response = requests.post(
            "https://api.languagetool.org/v2/check",
            data={
                "text": text,
                "language": "en-US"
            },
            timeout=30
        )

        response.raise_for_status()
        language_result = response.json()

        for match in language_result.get("matches", []):
            start = match.get("offset", 0)
            end = start + match.get("length", 0)

            # Never automatically modify detected name spans.
            if overlaps(start, end, name_spans):
                continue

            original = text[start:end]
            replacements = match.get("replacements", [])

            if not replacements:
                continue

            # Avoid duplicating a custom-rule correction.
            if any(
                item["start"] == start and item["end"] == end
                for item in matches
            ):
                continue

            message = match.get("message", "")

            # Use the actual grammar rule message as an explanation.
            reason = (
                message
                if message
                else "The grammar checker identified a possible issue."
            )

            matches.append({
                "start": start,
                "end": end,
                "original": original,
                "correct": replacements[0].get("value", original),
                "reason": reason
            })

    except requests.RequestException:
        # Custom rules can still work without the online service.
        pass

    # Remove duplicate entries.
    unique_matches = []
    seen = set()

    for item in matches:
        key = (
            item["start"],
            item["end"],
            item["correct"].casefold()
        )

        if key not in seen:
            seen.add(key)
            unique_matches.append(item)

    # Apply replacements from right to left.
    corrected = text

    for item in sorted(
        unique_matches,
        key=lambda value: value["start"],
        reverse=True
    ):
        corrected = (
            corrected[:item["start"]]
            + item["correct"]
            + corrected[item["end"]:]
        )

    errors = [
        {
            "original": item["original"],
            "suggestions": [item["correct"]],
            "reason": item["reason"]
        }
        for item in sorted(
            unique_matches,
            key=lambda value: value["start"]
        )
    ]

    return jsonify({
        "original": text,
        "corrected": corrected,
        "errors": errors
    })


if __name__ == "__main__":
    print("=" * 45)
    print("       GrammarAI is starting...")
    print(" Open: http://127.0.0.1:5000")
    print("=" * 45)

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000
    )
    