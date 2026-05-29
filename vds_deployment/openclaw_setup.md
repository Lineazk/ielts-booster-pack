# 🚀 Master Setup Manual: Autonomous Python Agent VDS Deployment

Welcome to your **always-on, interactive AI Assistant** deployment manual! We have created a single-file, highly optimized, and robust Python agent (`agent.py`) that brings all the power of OpenClaw-style skills into a lightweight script. 

Running natively on your VDS, it handles:
- **Telegram Interactive Chat**: Talk to `@surveyagentbdbot` 24/7.
- **Proactive Routine Alerts**: Automatically tracks your IELTS study schedule (from `schedule.html`) and notifies you on Telegram as slots transition.
- **Live Scrapes**: Search Google/DuckDuckGo and YouTube dynamically.
- **AgentMail 24/7 Email Client**: Automatically polls your AgentMail inbox (`sourovjoy@agentmail.to`) every 30 seconds, processes incoming emails via LLM, and replies automatically, while also notifying you on Telegram!
- **Daily Web3 Build**: Autonomously brainstorms, compiles, and publishes a new Solidity project to GitHub daily at 9:00 AM.
- **Daily Vocab Digest**: Sends Band 8.5+ IELTS vocabularies to your email and Telegram daily at 8:00 PM.

---

## 🛠️ Step 1: Pre-requisites on VDS

Ensure your Windows VDS has the following tools installed:
1. **Python (v3.10 or higher)**: Make sure it's added to your PATH during installation.
2. **Pip Packages**: Run the following in your VDS PowerShell terminal:
   ```powershell
   pip install requests python-dotenv
   ```

---

## 📂 Step 2: Transfer Agent Files to VDS

Create a folder on your VDS (e.g., `C:\openclaw_agent\`) and copy the pre-scaffolded files from Antigravity:
1. Copy **`agent.py`** to `C:\openclaw_agent\agent.py`
2. Copy **`.env`** to `C:\openclaw_agent\.env`

---

## 🔑 Step 3: Verify Environment Secrets

Open `C:\openclaw_agent\.env` on your VDS and verify the values:
```env
# CLOD.IO AI Configuration
CLOD_API_KEY=eyJhbGciOiJIUzI1Ni... (Already configured)
CLOD_API_BASE=https://api.clod.io/v1
CLOD_MODEL=Qwen/Qwen3.5-9B

# Telegram Configuration
TELEGRAM_BOT_TOKEN=8084758976:AAF14Lv3XNEpfodr3dErAR3KJfK4zg7ZBNg
TELEGRAM_CHAT_ID=1108622318

# AgentMail API Integration Configuration
AGENTMAIL_API_KEY=am_us_a86d80c3d68cc1dce50eeacc7855c62e02ad7939214a2a38edefe3c41f68fc38
AGENTMAIL_INBOX_ID=sourovjoy@agentmail.to

# GitHub Configuration (for auto-posting Web3 projects)
GITHUB_TOKEN=ghp_YourGitHubClassicToken
GITHUB_USERNAME=your_github_username
```

---

## ⚡ Step 4: Validate and Run Your Bot!

### 1. Verification Test
Run a quick diagnostic to ensure the Telegram bot can connect and reach your account:
```powershell
python C:\openclaw_agent\agent.py --test
```
*Expected Output:*
`[+] Test passed! Your agent can reach Telegram.`
*(You will receive a Telegram message from your bot confirming it's active).*

### 2. Run permanently 24/7 on VDS (Self-Healing Daemon)
Instead of running `agent.py` directly, we have created a **supervisor watchdog script (`monitor.py`)**. 

The supervisor starts `agent.py` as a child process. If `agent.py` crashes due to network timeouts, API rate limits, or any uncaught error, `monitor.py` will:
1. Detect the crash exit code.
2. Send a Telegram notification to your bot to warn you (`🚨 Supervisor Warning: Your AI Agent crashed...`).
3. Pause for 10 seconds, then reboot the agent in a loop to guarantee 24/7 uptime!

To run this self-healing system permanently in the background:

#### Option A: Run hidden via VBS script (Easiest & Silently)
Create a file named `start_agent.vbs` in the same folder:
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python C:\openclaw_agent\monitor.py", 0, False
```
Double-clicking `start_agent.vbs` will boot up the supervisor in a completely hidden background process, keeping your bot alive forever!

#### Option B: Windows Task Scheduler (Highly Recommended for VDS reboots)
1. Open **Task Scheduler** on Windows.
2. Click **Create Basic Task** (Name: `OpenClaw-Self-Healing-Agent`).
3. Trigger: **When the computer starts**.
4. Action: **Start a program**.
5. Program/script: `python`
6. Add arguments: `C:\openclaw_agent\monitor.py`
7. Click Finish. In properties, check **Run whether user is logged on or not** and **Run with highest privileges**.

---

## 💬 Step 5: Telegram Commands & Features

Once online, open Telegram and interact with `@surveyagentbdbot`! Here are some commands you can try sending:

### 📅 1. Routine Syncing
*   **User**: *"What should I study right now?"*
*   *Agent response*: Looks up your time slot and replies: *"📅 Active slot: 08:30–09:00 - Morning Prep & English Narration!"*

### 📬 2. AgentMail Inbox Actions
*   **User**: *"Check my inbox for emails"*
*   *Agent response*: Directly fetches recent messages from AgentMail and shows a list of subjects and senders!
*   **Incoming Mail Handling**: Send an email to `sourovjoy@agentmail.to` from your personal address. Within 30 seconds, the agent will receive it, think of a reply, send it back, and notify you on Telegram!

### 🎥 3. Live Scraping
*   **User**: *"Search YouTube for latest IELTS listening test"*
*   *Agent response*: Performs a live YouTube search and returns the top 3 newest Cambridge IELTS Listening links instantly on Telegram!

### 🚀 4. Smart Contract Creation
*   **User**: *"Publish a DeFi flash loan project to my GitHub"*
*   *Agent response*: Brainstorms an advanced ERC-3156 flash loan execution architecture in Solidity, writes NatSpec-documented code, creates the repo, and uploads it live!
