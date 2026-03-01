# === CONFIG ===
$repoName = "trading_bot_6"
$githubUser = "YOUR_GITHUB_USERNAME"
$projectPath = "C:\Users\HP\Desktop\trading_bot\trading_bot_6"

# === MOVE TO PROJECT ===
Set-Location $projectPath

# === CREATE .gitignore ===
@"
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual env
venv/
env/
.venv/

# IDE
.vscode/
.idea/

# Logs
logs/
*.log

# Cache
.cache/
*.sqlite3

# Credentials
*.env
config/keys.json
config/api_keys.json

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db
"@ | Out-File -Encoding utf8 ".gitignore"

# === CREATE README ===
@"
# Trading Bot 6

AI-driven trading bot with:
- Strategy engine
- Risk manager
- Portfolio system
- Market filters
- ML filters (optional)
- Tkinter UI
- Binance integration

## Run
python main.py
"@ | Out-File -Encoding utf8 "README.md"

# === INIT GIT ===
git init
git add .
git commit -m "Initial commit: trading bot core"

# === ADD REMOTE ===
git remote add origin https://github.com/$githubUser/$repoName.git

# === PUSH ===
git branch -M main
git push -u origin main
