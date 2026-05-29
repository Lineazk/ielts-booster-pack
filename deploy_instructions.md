# 🚀 Setup & Launch Manual: $0 IELTS Marketplace

This document outlines the final steps to fully set up your payment links and have your OpenClaw agent autonomously deploy this website to the internet!

---

## 🛠️ Step 1: Link Your Gumroad Payments (Takes 2 Minutes)
Gumroad handles payments and delivers your files automatically. Setup is **100% free**:
1. Go to [Gumroad.com](https://gumroad.com) and create a free account.
2. Click **New Product** -> Choose **Digital Product**.
    * **Name:** `Ultimate Band 8.5+ IELTS Vocab & Speaking Booster Pack`
    * **Price:** `$9.99`
3. In the **Content** section, upload the compiled vocabulary database (`vocab_pack_preview.json`) or your study files.
4. Click **Publish** and copy your unique Product Link (e.g., `https://gum.co/your-product-id`).
5. Open your local `index.html` and replace `href="https://gumroad.com"` on line 527 with your actual Gumroad product link:
   ```html
   <a href="https://gum.co/your-product-id" class="checkout-btn" id="buyBtn">Get Instant Access</a>
   ```

---

## 🌎 Step 2: OpenClaw Autonomous GitHub Deployment
Since you do not want to execute commands manually, your OpenClaw agent can handle the entire deployment!

### Send this message to your Telegram bot `@surveyagentbdbot`:
> *"Hey! I have created my IELTS storefront locally in `C:\Users\soura\.gemini\antigravity\scratch\ielts-marketplace`. Please use your `github_poster` skill to create a new GitHub repository called 'ielts-booster-pack' on my account, upload all files in this directory, and enable GitHub Pages on the main branch so the site goes live immediately!"*

### What OpenClaw will do:
1. Initialize a Git repository inside `C:\Users\soura\.gemini\antigravity\scratch\ielts-marketplace`.
2. Authenticate using your pre-configured `GITHUB_TOKEN` in your `.env`.
3. Create the new remote repository `ielts-booster-pack` on your account.
4. Push all assets (`index.html`, `vocab_pack_preview.json`) live.
5. Notify you on Telegram once the site is fully active!

Your live site will then be accessible to the world at:
`https://your-github-username.github.io/ielts-booster-pack/`

---

## 💸 Step 3: Run Free Lead Generation
To make sales with $0 ad spend, let your OpenClaw agent automate traffic generation:
* Send this to your Telegram bot:
  > *"Use your web_research skill to find the 3 most popular IELTS or student preparation groups on Facebook, Reddit, or Quora. Let me know their names and links, and draft a high-value educational post sharing our free vocab cards to attract buyers."*
