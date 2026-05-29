#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  OPENCLAW-STYLE AUTONOMOUS AI AGENT — SINGLE-FILE VDS DEPLOYMENT
  Runs 24/7 on your VDS. Talks to you on Telegram. Searches the web.
  Posts Web3 code to GitHub daily. Sends vocab emails. Tracks routine.
═══════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import json
import re
import base64
import random
import datetime
import threading
import smtplib
import urllib.parse
import urllib.request
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── UTF-8 fix for Windows console ────────────────────────────────────
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

try:
    import requests
except ImportError:
    print("[!] Installing 'requests' library...")
    os.system(f"{sys.executable} -m pip install requests python-dotenv")
    import requests

try:
    from dotenv import load_dotenv
except ImportError:
    os.system(f"{sys.executable} -m pip install python-dotenv")
    from dotenv import load_dotenv

# ═════════════════════════════════════════════════════════════════════
#  CONFIGURATION — Edit .env file or set these directly
# ═════════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

CLOD_API_KEY    = os.getenv("CLOD_API_KEY", "")
CLOD_API_BASE   = os.getenv("CLOD_API_BASE", "https://api.clod.io/v1")
CLOD_MODEL      = os.getenv("CLOD_MODEL", "Qwen/Qwen3.5-9B")

TG_TOKEN        = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID      = os.getenv("TELEGRAM_CHAT_ID", "")

GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "")
GITHUB_USER     = os.getenv("GITHUB_USERNAME", "")

SMTP_SERVER     = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT       = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER       = os.getenv("SMTP_USER", "")
SMTP_PASS       = os.getenv("SMTP_PASSWORD", "")
SMTP_RECIPIENT  = os.getenv("DEFAULT_RECIPIENT", "")

AGENTMAIL_API_KEY  = os.getenv("AGENTMAIL_API_KEY", "")
AGENTMAIL_INBOX_ID = os.getenv("AGENTMAIL_INBOX_ID", "sourovjoy@agentmail.to")

GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")

DASHBOARD_USER      = os.getenv("DASHBOARD_USERNAME", "admin")
DASHBOARD_PASS      = os.getenv("DASHBOARD_PASSWORD", "sourovclaw123")



# ═════════════════════════════════════════════════════════════════════
#  DAILY ROUTINE (from schedule.html)
# ═════════════════════════════════════════════════════════════════════
ROUTINE = [
    {"id":"a1","s":510,"e":540,"t":"08:30–09:00","title":"🌅 Morning Prep & English Narration","desc":"আয়নার সামনে ৫ মিনিট English-এ বলুন: 'Today I will study...'","cat":"prep"},
    {"id":"a2","s":540,"e":600,"t":"09:00–10:00","title":"⚙️ ME Book — Part 1","desc":"ME textbook chapter পড়ুন, English-এ notes নিন।","cat":"me"},
    {"id":"a3","s":600,"e":660,"t":"10:00–11:00","title":"⚙️ ME Book — Part 2 + Problems","desc":"Problems solve, derivation বুঝুন। Total ME = ২ ঘণ্টা।","cat":"me"},
    {"id":"a4","s":660,"e":720,"t":"11:00–12:00","title":"🔧 Dept Job Study — MCQ + Written","desc":"Engineering dept subjects, past BCS/Job questions solve।","cat":"dept"},
    {"id":"a5","s":720,"e":750,"t":"12:00–12:30","title":"🔧 Dept Study — Mock Exam","desc":"Online MCQ exam with timer.","cat":"dept"},
    {"id":"b1","s":750,"e":810,"t":"12:30–01:30","title":"🌊 Bath + Prayer + Lunch","desc":"স্নান, পূজা, হালকা আহার। বেশি ভাত নয়।","cat":"break"},
    {"id":"c1","s":810,"e":840,"t":"01:30–02:00","title":"🗣️ IELTS Speaking — Topic Timer","desc":"speaking.html খুলুন, ৩টি topic-এ জোরে কথা বলুন!","cat":"speaking"},
    {"id":"c2","s":840,"e":855,"t":"02:00–02:15","title":"⚡ Anti-Sleep Break","desc":"দ্রুত হাঁটুন, ঠান্ডা পানি, AC বাড়ান।","cat":"break"},
    {"id":"c3","s":855,"e":900,"t":"02:15–03:00","title":"🎧 IELTS Listening — Cambridge CBT","desc":"Headphone দিয়ে Listening Test দিন।","cat":"listening"},
    {"id":"c4","s":900,"e":960,"t":"03:00–04:00","title":"📋 Non-Dept Study — Block 1","desc":"আজকের rotation-এর ১ম বিষয়, MCQ practice।","cat":"nondept"},
    {"id":"c5","s":960,"e":1020,"t":"04:00–05:00","title":"📋 Non-Dept Study — Block 2","desc":"Rotation-এর ২য় বিষয়, MCQ সলভ।","cat":"nondept"},
    {"id":"c6","s":1020,"e":1040,"t":"05:00–05:20","title":"☕ Snack + Fresh Air","desc":"হালকা খাবার, পানি, বাইরে natural light নিন।","cat":"break"},
    {"id":"d1","s":1040,"e":1070,"t":"05:20–05:50","title":"🪔 Evening Prayer","desc":"সন্ধ্যার আরতি ও পূজা।","cat":"prayer"},
    {"id":"d2","s":1070,"e":1120,"t":"05:50–06:40","title":"📖 IELTS Reading — CBT Passage","desc":"১টি full passage, SPQA method, timer দিন।","cat":"reading"},
    {"id":"d3","s":1120,"e":1170,"t":"06:40–07:30","title":"✍️ IELTS Writing — CBT Practice","desc":"Task 1 or 2 টাইপ করুন, IODD/PEEL follow করুন।","cat":"writing"},
    {"id":"d4","s":1170,"e":1200,"t":"07:30–08:00","title":"🍽️ Dinner & Family","desc":"রাতের খাওয়া ও পরিবার। সম্পূর্ণ rest।","cat":"break"},
    {"id":"e1","s":1200,"e":1245,"t":"08:00–08:45","title":"📚 IELTS Vocab + Grammar Lab","desc":"১৫টি flashcard + grammar daily drill।","cat":"vocab"},
    {"id":"e2","s":1245,"e":1305,"t":"08:45–09:45","title":"🔧 Dept Revision — Weak Topics","desc":"কঠিন engineering topics রিভিশন।","cat":"dept"},
    {"id":"e3","s":1305,"e":1350,"t":"09:45–10:30","title":"📋 Non-Dept Weak Subject Drill","desc":"কঠিন BCS topic, ছোট summary নোটস।","cat":"nondept"},
    {"id":"e4","s":1350,"e":1395,"t":"10:30–11:15","title":"🗣️ Speaking Review + Chunk Drill","desc":"Recording শুনে ভুল ধরুন, ৩টি chunk ১০ বার বলুন।","cat":"speaking"},
    {"id":"e5","s":1395,"e":1440,"t":"11:15–12:00","title":"✍️ Writing Review + Correction","desc":"আজকের লেখা চেক, linking words অ্যাড (SCC rule)।","cat":"writing"},
    {"id":"e6","s":1440,"e":1485,"t":"12:00–12:45","title":"📖 Mock Test / Extra Study","desc":"সোম/বৃহ: Full Mock. অন্য দিন: ME revision।","cat":"extra"},
    {"id":"e7","s":1485,"e":1500,"t":"12:45–01:00","title":"🎧 Passive Listening — Sleep","desc":"Cambridge audio headphone-এ, script ছাড়া।","cat":"listening"},
]

# ═════════════════════════════════════════════════════════════════════
#  CORE TOOLS
# ═════════════════════════════════════════════════════════════════════

def get_bdt_now():
    """Return the current time in Bangladesh Standard Time (BDT, UTC+6) dynamically."""
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=6)

START_TIME = get_bdt_now()
LOG_BUFFER = []

def log(msg):
    ts = get_bdt_now().strftime("%H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted)
    LOG_BUFFER.append(formatted)
    if len(LOG_BUFFER) > 100:
        LOG_BUFFER.pop(0)

# ── Telegram ─────────────────────────────────────────────────────────
def tg_send(text, chat_id=None):
    """Send a Telegram message. Splits long messages automatically."""
    cid = chat_id or TG_CHAT_ID
    if not TG_TOKEN or not cid:
        log("[-] Telegram credentials missing")
        return False
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    # Telegram limit is 4096 chars
    chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            r = requests.post(url, json={
                "chat_id": cid, "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }, timeout=10)
            if r.status_code != 200:
                # Retry without markdown (in case of parse errors)
                requests.post(url, json={
                    "chat_id": cid, "text": chunk,
                    "disable_web_page_preview": True
                }, timeout=10)
        except Exception as e:
            log(f"[-] TG send error: {e}")
            return False
    return True

def tg_get_updates(offset=0):
    """Long-poll Telegram for new messages from user."""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={
            "offset": offset, "timeout": 30, "allowed_updates": '["message"]'
        }, timeout=35)
        if r.status_code == 200:
            return r.json().get("result", [])
    except Exception:
        pass
    return []

# ── Clod.io LLM ─────────────────────────────────────────────────────
def ask_llm(prompt, system="You are a helpful AI assistant.", temperature=0.7):
    """Call Clod.io chat completions API with automatic cascading failovers to Gemini, Groq, and OpenRouter."""
    # Attempt 1: Clod.io
    if CLOD_API_KEY:
        try:
            log("[*] Querying LLM via Clod.io...")
            r = requests.post(
                f"{CLOD_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {CLOD_API_KEY}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                json={
                    "model": CLOD_MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                },
                timeout=30
            )
            if r.status_code == 200:
                log("[+] Success via Clod.io")
                return r.json()["choices"][0]["message"]["content"]
            else:
                log(f"[-] Clod.io failed (Status {r.status_code})")
        except Exception as e:
            log(f"[-] Clod.io exception: {e}")

    # Attempt 2: Google Gemini (High performance free tier)
    if GEMINI_API_KEY:
        try:
            log("[*] Failover: Querying LLM via Google Gemini...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            full_prompt = f"{system}\n\nUser Request:\n{prompt}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"temperature": temperature}
            }
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                log("[+] Success via Google Gemini")
                return text
            else:
                log(f"[-] Gemini failed (Status {r.status_code})")
        except Exception as e:
            log(f"[-] Gemini exception: {e}")

    # Attempt 3: Groq (Fastest Llama-3.3 standard dev key)
    if GROQ_API_KEY:
        try:
            log("[*] Failover: Querying LLM via Groq...")
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                log("[+] Success via Groq")
                return r.json()["choices"][0]["message"]["content"]
            else:
                log(f"[-] Groq failed (Status {r.status_code})")
        except Exception as e:
            log(f"[-] Groq exception: {e}")

    # Attempt 4: OpenRouter (Generous free tier selection)
    if OPENROUTER_API_KEY:
        try:
            log("[*] Failover: Querying LLM via OpenRouter...")
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/openclaw/openclaw",
                "X-Title": "OpenClaw Agent"
            }
            payload = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                log("[+] Success via OpenRouter")
                return r.json()["choices"][0]["message"]["content"]
            else:
                log(f"[-] OpenRouter failed (Status {r.status_code})")
        except Exception as e:
            log(f"[-] OpenRouter exception: {e}")

    log("[-] All LLM providers exhausted and failed.")
    return None

# ── Web Search (DuckDuckGo) ─────────────────────────────────────────
def search_web(query, max_results=5):
    """Scrape DuckDuckGo HTML for search results without API keys."""
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        links = re.findall(r'class="result__url"[^>]*href="([^"]+)"', html)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
        results = []
        seen = set()
        for i, link in enumerate(links[:max_results*2]):
            if "uddg=" in link:
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
            if link in seen:
                continue
            seen.add(link)
            snip = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
            results.append({"url": link, "snippet": snip})
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        log(f"[-] Web search error: {e}")
        return []

# ── YouTube Search ───────────────────────────────────────────────────
def search_youtube(query, max_results=5):
    """Scrape YouTube search results page for video links."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
        if not ids:
            ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        seen = set()
        results = []
        for vid in ids:
            if vid not in seen:
                seen.add(vid)
                results.append(f"https://www.youtube.com/watch?v={vid}")
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        log(f"[-] YouTube search error: {e}")
        return []

# ── Email ────────────────────────────────────────────────────────────
def agentmail_send_email(subject, body_text, body_html=None, to=None):
    """Send email via AgentMail API."""
    if not AGENTMAIL_API_KEY:
        log("[-] AgentMail API key missing")
        return False
    inbox_id = AGENTMAIL_INBOX_ID or "sourovjoy@agentmail.to"
    url = f"https://api.agentmail.to/v0/inboxes/{inbox_id}/messages/send"
    headers = {
        "Authorization": f"Bearer {AGENTMAIL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to or SMTP_RECIPIENT or inbox_id,
        "subject": subject,
        "text": body_text
    }
    if body_html:
        payload["html"] = body_html
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        if r.status_code in [200, 201]:
            log("[+] Email sent via AgentMail!")
            return True
        else:
            log(f"[-] AgentMail send error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log(f"[-] AgentMail send failed: {e}")
    return False

def send_email(subject, body, to=None):
    """Send email - tries AgentMail if configured, else falls back to SMTP."""
    if AGENTMAIL_API_KEY:
        log("[*] Attempting to send email via AgentMail...")
        if agentmail_send_email(subject, body, to=to):
            return True
    
    log("[*] Falling back to SMTP...")
    recipient = to or SMTP_RECIPIENT
    if not SMTP_USER or not SMTP_PASS or not recipient:
        log("[-] SMTP credentials missing in .env")
        return False
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    try:
        srv = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        srv.starttls()
        srv.login(SMTP_USER, SMTP_PASS)
        srv.sendmail(SMTP_USER, recipient, msg.as_string())
        srv.quit()
        log("[+] Email sent!")
        return True
    except Exception as e:
        log(f"[-] Email error: {e}")
        return False


# ── GitHub ───────────────────────────────────────────────────────────
def github_create_repo(name, desc):
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        return False
    try:
        r = requests.post("https://api.github.com/user/repos",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
            json={"name": name, "description": desc, "private": False}, timeout=15)
        return r.status_code in [200, 201, 422]
    except Exception:
        return False

def github_push_file(repo, path, content):
    if not GITHUB_TOKEN:
        return False
    url = f"https://api.github.com/repos/{GITHUB_USER}/{repo}/contents/{path}"
    hdrs = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    sha = None
    try:
        r = requests.get(url, headers=hdrs, timeout=5)
        if r.status_code == 200:
            sha = r.json()["sha"]
    except Exception:
        pass
    payload = {"message": f"Add {path}", "content": base64.b64encode(content.encode("utf-8")).decode()}
    if sha:
        payload["sha"] = sha
    try:
        r = requests.put(url, headers=hdrs, json=payload, timeout=15)
        return r.status_code in [200, 201]
    except Exception:
        return False

# ═════════════════════════════════════════════════════════════════════
#  HIGH-LEVEL AGENT ACTIONS
# ═════════════════════════════════════════════════════════════════════

def get_current_slot():
    """Return the active routine slot based on Bangladesh Standard Time (BDT)."""
    now = get_bdt_now()
    mins = now.hour * 60 + now.minute
    if mins < 510:  # before 8:30 AM
        mins += 1440
    for s in ROUTINE:
        if s["s"] <= mins < s["e"]:
            return s
    return None

def action_generate_vocab():
    """Generate 5 advanced IELTS vocabulary words using LLM."""
    log("[*] Generating daily IELTS vocabulary...")
    prompt = """Generate exactly 5 advanced IELTS Band 8.5+ vocabulary words for today.
For each word provide:
1. Word (Part of Speech) /phonetics/
2. Bengali meaning (বাংলা অর্থ) + English definition
3. 3 Synonyms + 1 Antonym
4. One premium IELTS example sentence (Academic topic)
Format beautifully with emojis for Telegram. Keep compact."""
    result = ask_llm(prompt, "You are a world-class IELTS lexicographer.", 0.7)
    return result or "⚠️ Could not generate vocabulary today. API may be busy."

def action_search_for_slot(slot):
    """Dynamically search YouTube for resources matching the current study slot."""
    cat = slot["cat"]
    queries = {
        "speaking": [
            "IELTS speaking band 9 cue card practice test latest",
            "IELTS speaking part 2 actual exam cue card sample",
            "Cambridge IELTS speaking test band 8.5 mock interview"
        ],
        "listening": [
            "IELTS listening practice test Cambridge latest 2026",
            "IELTS listening test actual exam practice academic",
            "Cambridge IELTS listening test with answers high quality"
        ],
        "reading": [
            "IELTS reading passage practice academic test band 9",
            "IELTS reading test actual exam passage with answers",
            "Cambridge IELTS academic reading test full walkthrough"
        ],
        "writing": [
            "IELTS writing task 2 band 9 sample essay academic",
            "IELTS writing task 1 academic report band 9 structure",
            "Cambridge IELTS writing task 2 template band 8.5+"
        ],
        "vocab": [
            "IELTS vocabulary advanced band 8 flashcards active recall",
            "Advanced IELTS band 8.5 words list with sentences",
            "IELTS collocation master class academic vocabulary"
        ]
    }
    
    query_list = queries.get(cat)
    if not query_list:
        return None
        
    # Select a high-quality query randomly to keep resources fresh without costing tokens
    query = random.choice(query_list)
    log(f"[*] Searching YouTube: {query}")
    links = search_youtube(query, 3)
    if links:
        txt = "\n".join([f"  ▸ {url}" for url in links])
        return f"🎥 *Fresh {cat.title()} Resources:*\n{txt}"
    return None

def action_daily_github_post():
    """Brainstorm + generate + publish a Web3 repo to GitHub."""
    log("[*] === DAILY GITHUB WEB3 POST ===")
    if not GITHUB_TOKEN or GITHUB_TOKEN == "YOUR_GITHUB_TOKEN":
        tg_send("⚠️ GitHub token not configured. Skipping daily post.")
        return

    # Step 1: Brainstorm unique concept
    log("[*] Step 1: Brainstorming unique Web3 concept...")
    idea_raw = ask_llm(
        "Brainstorm a completely unique, rare, advanced Web3/Solidity smart contract project concept. "
        "It must solve a complex real-world decentralized challenge. Avoid basic ERC-20/721 tutorials. "
        "Output JSON with keys: \"name\" (kebab-case repo name), \"description\" (one sentence). Nothing else.",
        "You are a senior Web3 architect. Output clean JSON only.", 0.9
    )
    name, desc = "advanced-solidity-project", "An advanced Solidity smart contract solution."
    if idea_raw:
        try:
            cleaned = idea_raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            data = json.loads(cleaned)
            name = data.get("name", name)
            desc = data.get("description", desc)
        except Exception:
            pass

    date_str = get_bdt_now().strftime("%Y-%m-%d")
    repo_name = f"{name}-{date_str}"
    tg_send(f"🚀 *Daily Web3 Build Started!*\n📦 Repo: `{repo_name}`\n💡 {desc}")

    # Step 2: Generate code
    log("[*] Step 2: Generating Solidity code via LLM...")
    code_prompt = f"""Create a complete, production-grade Solidity smart contract project:
Theme: {name}
Description: {desc}

Output files using delimiters:
=== FILE: filepath ===
[content]

Include:
1. README.md — beautiful, with architecture ASCII diagram, security notes, deploy guide
2. contracts/Main.sol — full Solidity code (>0.8.20), NatSpec comments, security guards

Write complete files, zero placeholders."""

    raw = ask_llm(code_prompt, "You are an elite Web3 Solidity engineer. Output multi-file projects using === FILE: path === delimiters.", 0.2)
    if not raw:
        tg_send("❌ Code generation failed. Clod.io API may be overloaded.")
        return

    # Step 3: Parse files
    parts = re.split(r'===+\s*FILE:\s*([\w\-./]+)\s*===+', raw)
    files = {}
    if len(parts) >= 3:
        for i in range(1, len(parts), 2):
            fp = parts[i].strip()
            fc = parts[i+1].strip()
            if fc.startswith("```"):
                lines = fc.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                fc = "\n".join(lines)
            files[fp] = fc
    else:
        # Fallback: try JSON
        try:
            cleaned = raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            files = json.loads(cleaned)
        except Exception:
            tg_send("❌ Could not parse generated code. Will retry tomorrow.")
            return

    if not files:
        tg_send("❌ No files generated. Will retry tomorrow.")
        return

    # Step 4: Push to GitHub
    log(f"[*] Step 3: Creating repo {repo_name} and pushing {len(files)} files...")
    if not github_create_repo(repo_name, desc):
        tg_send("❌ Could not create GitHub repo. Check your token.")
        return

    ok = 0
    for path, content in files.items():
        if github_push_file(repo_name, path, content):
            ok += 1
        time.sleep(1)  # Rate limit

    gh_url = f"https://github.com/{GITHUB_USER}/{repo_name}"
    if ok == len(files):
        tg_send(f"🎉 *Daily Web3 Repo Published!*\n🔥 [{repo_name}]({gh_url})\n📄 {ok} files uploaded\n⭐ Go star it!")
    else:
        tg_send(f"⚠️ Partial upload: {ok}/{len(files)} files → [{repo_name}]({gh_url})")
    log(f"[+] GitHub post complete: {ok}/{len(files)} files")

def action_daily_vocab_email():
    """Generate vocab and send via email + Telegram."""
    log("[*] === DAILY VOCAB EMAIL ===")
    vocab = action_generate_vocab()
    tg_send(f"📚 *Daily IELTS Vocabulary Cards:*\n\n{vocab}")
    if SMTP_USER and SMTP_PASS and SMTP_RECIPIENT:
        subject = f"🎯 IELTS Daily Vocab — {datetime.datetime.now().strftime('%b %d, %Y')}"
        send_email(subject, vocab)
        tg_send("📧 Vocab also sent to your email!")
    else:
        log("[!] Email not configured, sent to Telegram only.")

# ═════════════════════════════════════════════════════════════════════
#  TELEGRAM CHAT HANDLER — Interactive AI conversation
# ═════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are the user's personal AI assistant running 24/7 on his VDS. You are an expert IELTS Coach (Band 9), a senior Web3/Solidity architect, and a highly skilled job preparation guide.

You have access to these tools (call them by outputting the exact tag):
- [TOOL:SEARCH_WEB:query] — Search Google/DuckDuckGo for information
- [TOOL:SEARCH_YOUTUBE:query] — Search YouTube for videos
- [TOOL:CHECK_SCHEDULE] — Check what the user should be studying right now
- [TOOL:GENERATE_VOCAB] — Generate 5 advanced IELTS vocabulary words
- [TOOL:POST_GITHUB] — Brainstorm and publish a Web3 repo to GitHub now
- [TOOL:SEND_EMAIL:subject|||body] — Send an email to the user
- [TOOL:CHECK_INBOX] — Check the AgentMail inbox for any new emails

TOKEN-SAVING RULES (CRITICAL):
1. **Be highly concise and direct.** Do not explain what you are about to do (e.g., NEVER say "Searching the web for..." or "Checking your schedule..."). Output the tool tag immediately without preambles or filler.
2. **Limit responses to 1-2 paragraphs max** for general chat, unless a longer output (like a code block or writing review) is explicitly requested.
3. Skip conversational pleasantries (e.g., "Certainly, I'd be happy to help!"). Get straight to the value.

When the user asks you to search, find, or look up anything — USE THE TOOLS. Do not hallucinate URLs.
When giving IELTS advice, be specific, provide examples, and be motivational.
Keep responses clean, formatted with emojis, and optimized for Telegram mobile screens.
Respond in English, but you can mix Bengali when helpful for the user."""

def check_agentmail_inbox():
    """List recent messages in the inbox."""
    if not AGENTMAIL_API_KEY or not AGENTMAIL_INBOX_ID:
        return "⚠️ AgentMail is not configured."
    url = f"https://api.agentmail.to/v0/inboxes/{AGENTMAIL_INBOX_ID}/messages"
    headers = {"Authorization": f"Bearer {AGENTMAIL_API_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            messages = data.get("messages", [])
            if not messages:
                return "📬 Your inbox is empty!"
            lines = []
            for m in messages[:5]:
                sender = m.get("from", "Unknown")
                subject = m.get("subject", "No Subject")
                date_str = m.get("created_at", "")[:16].replace("T", " ")
                lines.append(f"• *{subject}* from {sender} ({date_str})")
            return "📬 *Recent Emails in Inbox:*\n" + "\n".join(lines)
        else:
            return f"⚠️ Failed to fetch messages (Status {r.status_code})"
    except Exception as e:
        return f"⚠️ Inbox error: {e}"

def handle_tool_calls(response_text):
    """Parse and execute any tool calls embedded in the LLM response."""
    results = []
    
    # Search Web
    for match in re.finditer(r'\[TOOL:SEARCH_WEB:(.*?)\]', response_text):
        query = match.group(1)
        log(f"[*] Tool: Searching web for '{query}'")
        web_results = search_web(query)
        if web_results:
            txt = "\n".join([f"  🔗 {r['url']}\n     _{r['snippet'][:100]}_" for r in web_results[:3]])
            results.append(f"🌐 *Web Results for '{query}':*\n{txt}")
        else:
            results.append(f"🌐 No results found for '{query}'")

    # Search YouTube
    for match in re.finditer(r'\[TOOL:SEARCH_YOUTUBE:(.*?)\]', response_text):
        query = match.group(1)
        log(f"[*] Tool: Searching YouTube for '{query}'")
        yt = search_youtube(query, 3)
        if yt:
            txt = "\n".join([f"  ▸ {url}" for url in yt])
            results.append(f"🎥 *YouTube Results:*\n{txt}")
        else:
            results.append("🎥 No YouTube results found.")

    # Check Schedule
    if "[TOOL:CHECK_SCHEDULE]" in response_text:
        slot = get_current_slot()
        if slot:
            results.append(f"📅 *Active Now:* `{slot['t']}`\n📌 *{slot['title']}*\n💡 _{slot['desc']}_")
        else:
            results.append("😴 No active slot right now. Off-hours or sleep time!")

    # Generate Vocab
    if "[TOOL:GENERATE_VOCAB]" in response_text:
        vocab = action_generate_vocab()
        results.append(vocab)

    # Post GitHub
    if "[TOOL:POST_GITHUB]" in response_text:
        threading.Thread(target=action_daily_github_post, daemon=True).start()
        results.append("🚀 GitHub Web3 post is being generated in the background! You'll get a notification when it's done.")

    # Send Email
    for match in re.finditer(r'\[TOOL:SEND_EMAIL:(.*?)\|\|\|(.*?)\]', response_text, re.DOTALL):
        subject = match.group(1).strip()
        body = match.group(2).strip()
        if send_email(subject, body):
            results.append(f"📧 Email sent: *{subject}*")
        else:
            results.append("📧 Failed to send email. Check SMTP config.")

    # Check Inbox
    if "[TOOL:CHECK_INBOX]" in response_text:
        results.append(check_agentmail_inbox())

    return results

def process_user_message(text, chat_id):
    """Process a user message: call LLM, execute tools, respond."""
    log(f"[>] User: {text[:80]}...")

    # Get LLM response
    response = ask_llm(text, SYSTEM_PROMPT)
    if not response:
        tg_send("⚠️ I'm having trouble connecting to my AI brain right now. Please try again in a minute!", chat_id)
        return

    # Check for tool calls
    tool_results = handle_tool_calls(response)

    # Clean tool tags from response for display
    clean = re.sub(r'\[TOOL:[^\]]+\]', '', response).strip()

    # Send main response
    if clean:
        tg_send(clean, chat_id)

    # Send tool results
    for result in tool_results:
        tg_send(result, chat_id)

# ═════════════════════════════════════════════════════════════════════
#  BACKGROUND SCHEDULER — Runs in separate thread
# ═════════════════════════════════════════════════════════════════════

def scheduler_loop():
    """Background loop: routine alerts, daily GitHub post, daily vocab email."""
    log("[*] Background scheduler started.")
    last_slot_id = None
    last_github_date = None
    last_vocab_date = None

    while True:
        try:
            now = get_bdt_now()
            today = now.strftime("%Y-%m-%d")

            # ── Routine tracking (every 30s) ───────────────────────
            slot = get_current_slot()
            if slot and slot["id"] != last_slot_id:
                last_slot_id = slot["id"]
                log(f"[+] Slot transition: {slot['title']}")
                msg = f"🔔 *Routine Alert!*\n⏰ `{slot['t']}`\n📌 *{slot['title']}*\n💡 _{slot['desc']}_"

                # Auto-search for IELTS content slots
                extra = action_search_for_slot(slot)
                if extra:
                    msg += f"\n\n{extra}"

                tg_send(msg)

            elif not slot and last_slot_id is not None:
                last_slot_id = None
                tg_send("😴 *Routine complete!* Rest well for tomorrow's study session.")

            # ── Daily GitHub post at 9:00 AM ───────────────────────
            if now.hour == 9 and now.minute < 2 and last_github_date != today:
                last_github_date = today
                threading.Thread(target=action_daily_github_post, daemon=True).start()

            # ── Daily vocab email at 8:00 PM ───────────────────────
            if now.hour == 20 and now.minute < 2 and last_vocab_date != today:
                last_vocab_date = today
                threading.Thread(target=action_daily_vocab_email, daemon=True).start()

        except Exception as e:
            log(f"[-] Scheduler error: {e}")

        time.sleep(30)

# ═════════════════════════════════════════════════════════════════════
#  INBOUND EMAIL PROCESSING (AgentMail Integration)
# ═════════════════════════════════════════════════════════════════════
PROCESSED_EMAILS_FILE = os.path.join(BASE_DIR, "processed_emails.json")

def load_processed_emails():
    if os.path.exists(PROCESSED_EMAILS_FILE):
        try:
            with open(PROCESSED_EMAILS_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_processed_emails(email_ids):
    try:
        with open(PROCESSED_EMAILS_FILE, "w") as f:
            json.dump(list(email_ids), f)
    except Exception as e:
        log(f"[-] Failed to save processed emails: {e}")

def inbox_polling_loop():
    """Background loop: poll AgentMail for incoming emails, process and reply."""
    if not AGENTMAIL_API_KEY or not AGENTMAIL_INBOX_ID:
        log("[-] AgentMail is not configured for polling.")
        return
    log("[*] Background AgentMail inbox polling started.")
    processed_ids = load_processed_emails()
    
    # On first run, mark existing emails as already processed to avoid backlog spam
    first_run = True

    while True:
        try:
            url = f"https://api.agentmail.to/v0/inboxes/{AGENTMAIL_INBOX_ID}/messages"
            headers = {"Authorization": f"Bearer {AGENTMAIL_API_KEY}"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                messages = data.get("messages", [])
                
                # Check messages
                new_messages_found = False
                for msg in reversed(messages):  # process oldest to newest
                    msg_id = msg.get("message_id")
                    if not msg_id or msg_id in processed_ids:
                        continue
                    
                    sender = msg.get("from", "")
                    # Ignore our own messages
                    if AGENTMAIL_INBOX_ID in sender or "sourovjoy@agentmail.to" in sender:
                        processed_ids.add(msg_id)
                        continue
                    
                    if first_run:
                        processed_ids.add(msg_id)
                        continue
                    
                    new_messages_found = True
                    subject = msg.get("subject", "No Subject")
                    body = msg.get("text", "") or msg.get("html", "")
                    log(f"[+] New email received from {sender} - Subject: {subject}")
                    
                    # Notify on Telegram about incoming email
                    tg_send(f"📬 *New Email Received!*\n👤 *From:* {sender}\n📌 *Subject:* {subject}\n\n🤖 *Thinking of a response...*")
                    
                    # Brainstorm response using Clod.io LLM
                    email_system_prompt = (
                        "You are the user's personal autonomous AI assistant. You have received an email. "
                        "Respond to this email in a highly professional, helpful, and concise manner. "
                        "Mix English and Bengali naturally if the sender used both, or reply in professional English. "
                        "Do not include email signatures. Keep it clean."
                    )
                    email_prompt = f"From: {sender}\nSubject: {subject}\nBody:\n{body}"
                    reply_text = ask_llm(email_prompt, email_system_prompt, temperature=0.7)
                    
                    if reply_text:
                        # Send reply using AgentMail reply endpoint!
                        reply_url = f"https://api.agentmail.to/v0/inboxes/{AGENTMAIL_INBOX_ID}/messages/{msg_id}/reply"
                        reply_payload = {"text": reply_text}
                        rep = requests.post(reply_url, json=reply_payload, headers=headers, timeout=15)
                        if rep.status_code in [200, 201]:
                            log(f"[+] Replied successfully to email {msg_id}!")
                            tg_send(f"✉️ *Replied successfully to {sender}!*\n💬 *My AI Reply:* {reply_text[:500]}...")
                        else:
                            log(f"[-] Failed to reply to email {msg_id}: {rep.text[:200]}")
                            tg_send(f"❌ Failed to reply to email from {sender} (Status {rep.status_code})")
                    else:
                        log("[-] Could not generate AI reply for email.")
                    
                    processed_ids.add(msg_id)
                
                if new_messages_found or first_run:
                    save_processed_emails(processed_ids)
                    first_run = False
            else:
                log(f"[-] Inbox polling error (Status {r.status_code})")
        except Exception as e:
            log(f"[-] Inbox polling exception: {e}")
        
        time.sleep(30)

# ═════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═════════════════════════════════════════════════════════════════════


# ═════════════════════════════════════════════════════════════════════
#  HTTP WEB SERVER DASHBOARD
# ═════════════════════════════════════════════════════════════════════
from http.server import HTTPServer, BaseHTTPRequestHandler

class DashboardHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def check_auth(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="OpenClaw Dashboard"')
            self.end_headers()
            self.wfile.write(b"Unauthorized: Authentication Required")
            return False
        try:
            encoded = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            user, password = decoded.split(":", 1)
            if user == DASHBOARD_USER and password == DASHBOARD_PASS:
                return True
        except Exception:
            pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="OpenClaw Dashboard"')
        self.end_headers()
        self.wfile.write(b"Unauthorized: Invalid Credentials")
        return False

    def do_GET(self):
        if not self.check_auth():
            return
        if self.path == "/":

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(get_dashboard_html().encode("utf-8"))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            slot = get_current_slot()
            status_data = {
                "uptime": str(datetime.datetime.now() - START_TIME).split(".")[0],
                "model": CLOD_MODEL,
                "current_slot": slot["title"] if slot else "Off-hours / Sleep",
                "slot_time": slot["t"] if slot else "",
                "slot_desc": slot["desc"] if slot else "",
                "telegram": "✅ Active" if TG_TOKEN else "❌ Missing",
                "github": "✅ Active" if GITHUB_TOKEN and GITHUB_TOKEN != "YOUR_GITHUB_TOKEN" else "❌ Missing",
                "agentmail": "✅ Active" if AGENTMAIL_API_KEY else "❌ Missing",
                "gemini": "✅ Configured" if GEMINI_API_KEY else "❌ Missing",
                "groq": "✅ Configured" if GROQ_API_KEY else "❌ Missing",
                "logs": LOG_BUFFER[-30:]
            }
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
        elif self.path == "/speaking":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            speaking_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speaking.html")
            with open(speaking_path, "r", encoding="utf-8") as file:
                self.wfile.write(file.read().encode("utf-8"))
                elif self.path == "/api/inbox":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            emails_json = []
            if AGENTMAIL_API_KEY and AGENTMAIL_INBOX_ID:
                url = f"https://api.agentmail.to/v0/inboxes/{AGENTMAIL_INBOX_ID}/messages"
                headers = {"Authorization": f"Bearer {AGENTMAIL_API_KEY}"}
                try:
                    r = requests.get(url, headers=headers, timeout=10)
                    if r.status_code == 200:
                        emails_json = r.json().get("messages", [])[:10]
                except Exception:
                    pass
            self.wfile.write(json.dumps(emails_json).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self.check_auth():
            return
        if self.path == "/api/action":

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                action = json.loads(post_data).get("action")
                if action == "vocab":
                    threading.Thread(target=action_daily_vocab_email, daemon=True).start()
                    msg = "📚 Triggered vocabulary cards generation!"
                elif action == "github":
                    threading.Thread(target=action_daily_github_post, daemon=True).start()
                    msg = "🚀 Triggered daily Web3 GitHub auto-post!"
                elif action == "test_tg":
                    log("[*] Manual Telegram Test triggered from Web Dashboard")
                    slot = get_current_slot()
                    slot_info = f"📅 Slot: {slot['title']}" if slot else "😴 Off-hours"
                    tg_send(f"🤖 *Web Dashboard Diagnostic!*\n{slot_info}\n✅ Connection fully verified!")
                    msg = "🔔 Sent test notification to Telegram!"
                else:
                    msg = "Unknown action"
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": msg}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())

def get_dashboard_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw AI Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090a0f;
            --card-bg: rgba(22, 26, 43, 0.65);
            --border: rgba(255, 255, 255, 0.05);
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
            --accent: #8b5cf6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: radial-gradient(circle at 10% 20%, rgba(90, 50, 180, 0.1) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(6, 180, 212, 0.1) 0%, transparent 40%);
        }
        header {
            padding: 24px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(10px);
            background: rgba(9, 10, 15, 0.8);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-title h1 {
            font-size: 24px;
            font-weight: 800;
            background: var(--primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header-title span {
            background: rgba(139, 92, 246, 0.15);
            color: #a78bfa;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .system-info {
            display: flex;
            gap: 24px;
            font-size: 14px;
            color: var(--text-muted);
        }
        .system-info strong { color: var(--text); }
        
        main {
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            padding: 32px;
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 24px;
            flex-grow: 1;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        .card:hover {
            border-color: rgba(139, 92, 246, 0.2);
            transform: translateY(-2px);
        }
        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: #fff;
        }
        
        .col-4 { grid-column: span 4; }
        .col-6 { grid-column: span 6; }
        .col-8 { grid-column: span 8; }
        .col-12 { grid-column: span 12; }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        .status-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .status-label {
            font-size: 14px;
            color: var(--text-muted);
            font-weight: 500;
        }
        .status-value {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            font-weight: 600;
        }
        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-green { background-color: var(--success); box-shadow: 0 0 8px var(--success); animation: pulse 2s infinite; }
        .dot-red { background-color: var(--danger); box-shadow: 0 0 8px var(--danger); }
        .dot-yellow { background-color: var(--warning); box-shadow: 0 0 8px var(--warning); }
        
        .routine-slot {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(6, 180, 212, 0.08) 100%);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .slot-time {
            font-size: 13px;
            color: #a78bfa;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .slot-title {
            font-size: 20px;
            font-weight: 800;
            color: #fff;
        }
        .slot-desc {
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.5;
        }
        
        .btn-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        .btn {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 12px;
            padding: 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .btn:hover {
            background: var(--primary);
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            transform: translateY(-1px);
        }
        
        .inbox-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 250px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .inbox-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            transition: background 0.2s ease;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .inbox-item:hover {
            background: rgba(255, 255, 255, 0.04);
        }
        .inbox-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .inbox-sender {
            font-size: 14px;
            font-weight: 600;
            color: #fff;
        }
        .inbox-time {
            font-size: 12px;
            color: var(--text-muted);
        }
        .inbox-subject {
            font-size: 13px;
            color: #d1d5db;
            font-weight: 500;
        }
        
        .console-container {
            background: #06070a;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            height: 250px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            position: relative;
        }
        .console-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
            font-family: 'JetBrains Mono', monospace;
        }
        .console-body {
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #10b981;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex-grow: 1;
            scroll-behavior: smooth;
        }
        .log-line {
            line-height: 1.4;
            white-space: pre-wrap;
        }
        
        .toast-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 1000;
        }
        .toast {
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid rgba(139, 92, 246, 0.3);
            color: #fff;
            padding: 14px 24px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            animation: slideIn 0.3s ease forwards;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
        
        @media (max-width: 1024px) {
            .col-4, .col-6, .col-8 { grid-column: span 12; }
            main { padding: 16px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-title">
            <h1>OpenClaw AI</h1>
            <span>v2.5 Active</span>
        </div>
        <div class="system-info">
            <div>Uptime: <strong id="uptime">00:00:00</strong></div>
            <div>Model: <strong id="model">Qwen/Qwen3.5-9B</strong></div>
        </div>
    </header>

    <main>
        <div class="card col-4">
            <div class="card-title">Live API Status 🌐</div>
            <div class="status-grid">
                <div class="status-item">
                    <span class="status-label">Telegram Bot</span>
                    <span class="status-value"><span id="tg-dot" class="dot"></span><span id="tg-text">-</span></span>
                </div>
                <div class="status-item">
                    <span class="status-label">AgentMail API</span>
                    <span class="status-value"><span id="am-dot" class="dot"></span><span id="am-text">-</span></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Google Gemini</span>
                    <span class="status-value"><span id="gemini-dot" class="dot"></span><span id="gemini-text">-</span></span>
                </div>
                <div class="status-item">
                    <span class="status-label">Groq API</span>
                    <span class="status-value"><span id="groq-dot" class="dot"></span><span id="groq-text">-</span></span>
                </div>
            </div>
        </div>

        <div class="card col-4">
            <div class="card-title">Current Study Slot 📅</div>
            <div class="routine-slot">
                <div class="slot-time" id="slot-time">OFF-HOURS / SLEEP</div>
                <div class="slot-title" id="slot-title">No Active Slot</div>
                <div class="slot-desc" id="slot-desc">Relax and rest. Your OpenClaw agent is currently running active background schedules.</div>
            </div>
        </div>

        <div class="card col-4">
            <div class="card-title">Control Center ⚙️</div>
            <div class="btn-grid">
                <button class="btn" onclick="triggerAction('test_tg')">🔔 Test TG Bot</button>
                <button class="btn" onclick="triggerAction('vocab')">📚 Daily Vocab</button>
                <button class="btn" onclick="triggerAction('github')">🚀 Daily Web3</button>
                <button class="btn" onclick="window.open('https://t.me/surveyagentbdbot', '_blank')">💬 Go to TG</button>
            </div>
        </div>

        <div class="card col-6">
            <div class="card-title">
                <span>AgentMail Live Inbox 📬</span>
                <span style="font-size: 13px; color: var(--text-muted); font-weight: normal;">sourovjoy@agentmail.to</span>
            </div>
            <div class="inbox-list" id="inbox-list">
                <div style="text-align: center; color: var(--text-muted); padding: 40px 0; font-size: 14px;">Loading emails...</div>
            </div>
        </div>

        <div class="card col-6">
            <div class="card-title">Administrative Live Logs 🖥️</div>
            <div class="console-container">
                <div class="console-header">
                    <span>VDS shell (realtime logs)</span>
                    <span style="color: var(--success); font-weight: bold;">● ONLINE</span>
                </div>
                <div class="console-body" id="console-logs">
                    <div class="log-line">Initializing console stream...</div>
                </div>
            </div>
        </div>
    </main>

    <div class="toast-container" id="toast-container"></div>

    <script>
        function showToast(text) {
            const container = document.getElementById("toast-container");
            const toast = document.createElement("div");
            toast.className = "toast";
            toast.innerHTML = `✨ ${text}`;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.animation = "slideIn 0.3s ease reverse forwards";
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        async function triggerAction(actionName) {
            try {
                const r = await fetch('/api/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: actionName })
                });
                const res = await r.json();
                showToast(res.message);
            } catch(e) {
                showToast("Failed to trigger action!");
            }
        }

        async function updateStatus() {
            try {
                const r = await fetch('/api/status');
                const data = await r.json();

                document.getElementById("uptime").innerText = data.uptime;
                document.getElementById("model").innerText = data.model;

                if (data.slot_time) {
                    document.getElementById("slot-time").innerText = data.slot_time;
                    document.getElementById("slot-title").innerText = data.current_slot;
                    document.getElementById("slot-desc").innerText = data.slot_desc;
                } else {
                    document.getElementById("slot-time").innerText = "OFF-HOURS / SLEEP";
                    document.getElementById("slot-title").innerText = "No Active Slot";
                    document.getElementById("slot-desc").innerText = "Relax and rest. Your OpenClaw agent is currently running active background schedules.";
                }

                updateBadge("tg", data.telegram);
                updateBadge("am", data.agentmail);
                updateBadge("gemini", data.gemini);
                updateBadge("groq", data.groq);

                const consoleBody = document.getElementById("console-logs");
                const oldScrollHeight = consoleBody.scrollHeight;
                const oldScrollTop = consoleBody.scrollTop;
                const oldClientHeight = consoleBody.clientHeight;
                
                consoleBody.innerHTML = data.logs.map(line => `<div class="log-line">${line}</div>`).join('');
                
                if (oldScrollTop + oldClientHeight >= oldScrollHeight - 10) {
                    consoleBody.scrollTop = consoleBody.scrollHeight;
                }
            } catch(e) {}
        }

        function updateBadge(prefix, value) {
            const dot = document.getElementById(`${prefix}-dot`);
            const txt = document.getElementById(`${prefix}-text`);
            txt.innerText = value.replace('✅ ', '').replace('❌ ', '').replace('⚠️ ', '');
            
            dot.className = "dot";
            if (value.includes("✅") || value.includes("Active") || value.includes("Configured")) {
                dot.classList.add("dot-green");
            } else if (value.includes("❌") || value.includes("Missing")) {
                dot.classList.add("dot-red");
            } else {
                dot.classList.add("dot-yellow");
            }
        }

        async function updateInbox() {
            try {
                const r = await fetch('/api/inbox');
                const emails = await r.json();
                const inboxList = document.getElementById("inbox-list");
                
                if (emails.length === 0) {
                    inboxList.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 40px 0; font-size: 14px;">📬 Inbox is currently empty. No messages received.</div>`;
                    return;
                }

                inboxList.innerHTML = emails.map(email => {
                    const senderName = email.from.split('<')[0].trim() || email.from;
                    const dateStr = email.created_at ? email.created_at.slice(11, 16) : '';
                    return `
                        <div class="inbox-item">
                            <div class="inbox-header">
                                <span class="inbox-sender">👤 ${senderName}</span>
                                <span class="inbox-time">${dateStr}</span>
                            </div>
                            <div class="inbox-subject">📌 ${email.subject || 'No Subject'}</div>
                        </div>
                    `;
                }).join('');
            } catch(e) {}
        }

        updateStatus();
        updateInbox();
        setInterval(updateStatus, 2000);
        setInterval(updateInbox, 5000);
    </script>
</body>
</html>"""

def web_server_loop():
    server_address = ('', 18789)
    try:
        httpd = HTTPServer(server_address, DashboardHTTPRequestHandler)
        log("[*] OpenClaw Web Dashboard successfully loaded and running at http://localhost:18789")
        httpd.serve_forever()
    except Exception as e:
        log(f"[-] Web server failed to start: {e}")

def main():
    parser = argparse.ArgumentParser(description="OpenClaw-style Autonomous AI Agent")
    parser.add_argument("--test", action="store_true", help="Send a test message to Telegram and exit")
    args = parser.parse_args()

    if args.test:
        log("[*] Sending test message to Telegram...")
        slot = get_current_slot()
        slot_info = f"📅 Current slot: {slot['title']}" if slot else "😴 Off-hours"
        
        # Test LLM response via the failover cascade
        log("[*] Testing LLM API cascade...")
        llm_response = ask_llm("Say 'Hello! LLM test passed!' and state which provider you are responding from.", "You are a test agent.")
        llm_status = f"\n🧠 *LLM Response:* {llm_response}" if llm_response else "\n❌ *LLM Response:* Failed on all providers!"
        
        ok = tg_send(f"🤖 *Agent Online Test!*\n{slot_info}\n✅ Telegram connection working!{llm_status}")
        if ok:
            log("[+] Test passed! Your agent can reach Telegram and models are responsive.")
        else:
            log("[-] Test failed. Check TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
            log("[-] Also make sure you've sent /start to @surveyagentbdbot on Telegram!")
        return

    # ── Startup ──────────────────────────────────────────────────
    log("═" * 60)
    log("  AUTONOMOUS AI AGENT — Starting up...")
    log(f"  Model: {CLOD_MODEL}")
    log(f"  Telegram Bot: {'✅ configured' if TG_TOKEN else '❌ missing'}")
    log(f"  GitHub: {'✅ configured' if GITHUB_TOKEN and GITHUB_TOKEN != 'YOUR_GITHUB_TOKEN' else '❌ missing'}")
    log(f"  SMTP Email: {'✅ configured' if SMTP_USER and SMTP_PASS else '❌ missing'}")
    log(f"  AgentMail API: {'✅ configured' if AGENTMAIL_API_KEY else '❌ missing'}")
    log(f"  AgentMail Inbox: {AGENTMAIL_INBOX_ID}")
    log("═" * 60)

    # Start background Web Server Dashboard
    web_thread = threading.Thread(target=web_server_loop, daemon=True)
    web_thread.start()

    # Start background scheduler
    sched = threading.Thread(target=scheduler_loop, daemon=True)

    sched.start()

    # Start background AgentMail inbox polling
    if AGENTMAIL_API_KEY:
        inbox_thread = threading.Thread(target=inbox_polling_loop, daemon=True)
        inbox_thread.start()

    # Notify user
    tg_send("🤖 *Your AI Agent is now ONLINE!*\n\n"
            "I'm running 24/7 on your VDS. Here's what I do automatically:\n"
            "• 📅 Track your IELTS/Job routine & alert you on slot changes\n"
            "• 🎥 Search YouTube for fresh study resources during IELTS slots\n"
            "• 🚀 Publish a unique Web3 smart contract to GitHub daily at 9 AM\n"
            "• 📧 Send you IELTS vocab & daily digest via AgentMail/SMTP daily at 8 PM\n"
            "• 📬 Monitor your AgentMail inbox (`" + AGENTMAIL_INBOX_ID + "`) 24/7 and reply to emails automatically!\n\n"
            "💬 *You can also chat with me anytime!* Try:\n"
            "• _\"Search YouTube for latest IELTS listening test\"_\n"
            "• _\"What should I study right now?\"_\n"
            "• _\"Generate 5 advanced vocab words\"_\n"
            "• _\"Check my inbox for emails\"_\n"
            "• _\"Publish a DeFi flash loan project to my GitHub\"_")

    # ── Telegram polling loop ────────────────────────────────────
    log("[*] Telegram polling loop started. Waiting for messages...")
    ALLOWED_USERS = {"619662881", "1108622318"}
    offset = 0
    while True:
        try:
            updates = tg_get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id", ""))
                user_id = str(msg.get("from", {}).get("id", ""))
                
                if text and chat_id:
                    # Security Check: Ignore unauthorized users completely
                    if chat_id not in ALLOWED_USERS and user_id not in ALLOWED_USERS:
                        log(f"[-] Blocked unauthorized access attempt from Chat: {chat_id}, User: {user_id}")
                        continue
                        
                    # Handle /start command
                    if text.strip() == "/start":
                        tg_send("👋 Hello! I'm your personal AI agent. Ask me anything about IELTS, Web3, or just say hi!", chat_id)
                        continue
                    # Process in a thread to not block polling
                    threading.Thread(
                        target=process_user_message,
                        args=(text, chat_id),
                        daemon=True
                    ).start()
        except Exception as e:
            log(f"[-] Polling error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
