# 🤖 AutoVibe - Cause why using your system UI when you can do it hard way?

### (yes, this entire file was vibed one shot no scope)

> _"Why remember commands when you can just ask AI to do it?"_ - Every developer ever

## What's This Thing? 💭

Bruh, tired of googling "how to check if port is open" for the 47th time? AutoVibe is your lazy person's dream - it turns your random computer questions into actual scripts and runs them instantly.

Need to find that chunky file eating your disk space? Just ask. Want to check what's hogging port 8080? Say less. This AI bestie writes the script, runs it, and gives you the answer faster than you can type `ps aux | grep`.

## Real Talk - What This Actually Does 🎯

This isn't for building the next Facebook. This is for:

-   **"Check if port 3000 is busy"** → Instant port scan
-   **"Find files bigger than 1GB in my home folder"** → Disk space detective mode
-   **"Show me what's eating my CPU right now"** → Process monitoring on demand
-   **"List all Python processes running"** → Quick system checks
-   **"Find all .log files from last week"** → File hunting without the headache
-   **"Check my internet speed"** → Network diagnostics
-   **"Show me folder sizes in /var"** → Storage analysis instantly

It's like having a sysadmin friend who never gets tired of your random "quick check this" requests.

## Features That Hit Different 🔥

-   **🧠 Natural Language → Code**: Speak human, get scripts
-   **⚡ Instant Execution**: Writes and runs immediately (no save/compile BS)
-   **🔍 Safety Checks**: Won't `rm -rf /` your life away
-   **🛠️ Self-Healing**: If script breaks, AI fixes it automatically
-   **📊 Clean Output**: Just the info you need, no code spam
-   **🔄 Retry Logic**: Keeps trying until it works or gives up gracefully
-   **🏠 Isolated Environment**: Runs in venv so it can't mess up your system

## Installation (EZ Mode) 📥

```bash
# Grab the goods
git clone <repo-url>
cd autovibe

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI key
export OPENAI_API_KEY="sk-your-key-here"

# Start vibing
python autovibe.py
```

## Usage Examples (The Good Stuff) 🎮

Just run it and start asking for stuff:

### System Monitoring Vibes

```
💬 "check what's using port 8080"
💬 "show me top 5 CPU processes"
💬 "find processes with 'python' in the name"
💬 "check if docker is running"
```

### File System Detective Work

```
💬 "find the biggest files in my Downloads folder"
💬 "show me all files modified today"
💬 "find empty directories in /tmp"
💬 "list files larger than 500MB"
```

### Network Stuff

```
💬 "ping google and tell me if internet works"
💬 "check which ports are open on localhost"
💬 "show me my IP address"
💬 "test if I can reach reddit.com"
```

### Quick System Info

```
💬 "how much disk space do I have left"
💬 "show me memory usage"
💬 "what's my CPU temperature"
💬 "list all users logged in"
```

## How It Works (The Magic) ✨

1. **You**: "yo check if nginx is running"
2. **AI**: _writes a script to check nginx status_
3. **Safety**: _validates script won't nuke anything_
4. **Execute**: _runs script immediately_
5. **Results**: _shows you clean output_
6. **Vibe Check**: "Did that answer your question?"

If something breaks, AI automatically tries to fix it. If you say "nah that's not what I wanted," it tries again.

## Real Conversation Example 📱

```
🤖 AI Code Generator & Executor
💬 State your request: find files bigger than 1GB in my home

🧠 ⌨️ Generating code...
💾 Code saved to: ./vibe_scripts/find_large_files_a1b2c3d4.py
🔍 Validating code...
📋 Risk Level: ALLOW ✅
🚀 Executing...

📤 Output:
/home/user/old_backup.tar.gz - 2.1 GB
/home/user/Downloads/movie.mp4 - 1.8 GB
/home/user/vm_disk.img - 3.2 GB

✅ Execution completed successfully
😃 Vibe check: success or no? y
🤗 YA WE DID IT!
```

## Safety First (We're Not Completely Reckless) 🛡️

-   **ALLOW**: Script looks clean, runs automatically
-   **CHECK**: Kinda sus, asks for your permission first
-   **DENY**: Absolutely not, this could break things

The AI won't run anything that could:

-   Delete important stuff
-   Mess with system files
-   Install random packages
-   Open sketchy network connections

## Pro Tips (Wisdom Drop) 🎓

-   **Be specific**: "check port 80" > "check ports"
-   **Include context**: "find large video files" > "find large files"
-   **Ask follow-ups**: If output is weird, just say "that's not right"
-   **Use it for quick checks**: Perfect for one-off diagnostic stuff
-   **Don't overthink it**: Just ask like you're texting a friend

## When This Slaps vs When It Doesn't 📊

### ✅ Perfect For:

-   Quick system checks
-   File hunting missions
-   Process monitoring
-   Network diagnostics
-   Disk space analysis
-   "Is X running?" questions

### ❌ Not Great For:

-   Complex multi-step workflows
-   Permanent scripts you want to keep
-   Interactive applications
-   Long-running monitoring
-   Anything that needs user input mid-execution

## Common Questions (FAQ Vibes) ❓

**Q: Does it save the scripts?**  
A: Yeah but with random hash names. You probably won't need them again anyway.

**Q: Can it install packages?**  
A: Yep, in its own venv so it won't mess up your main Python.

**Q: What if the script breaks?**  
A: AI tries to fix it automatically. If it keeps failing, maybe ask differently.

**Q: Is this safe?**  
A: Has safety checks but don't ask it to `sudo rm -rf /` obviously.

## Troubleshooting (When Things Go Sideways) 🔧

-   **"Failed to generate code"**: Check OpenAI API key/billing
-   **Script keeps failing**: Try being more specific with your request
-   **"Too many retries"**: The AI gave up, try a simpler ask
-   **Weird output**: Say "that's not right" and it'll try again

---

**TLDR**: Ask it to check stuff on your computer, it writes and runs the script instantly, gives you the answer. Like having a terminal wizard who never judges your questions. 🧙‍♂️

_Built for the "I just need to check one thing real quick" moments that happen 50 times a day._
