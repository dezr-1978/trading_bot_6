# === CONFIG ===
$repoName = "trading_bot_6"
$githubUser = "dezr-1978"
$projectPath = "C:\Users\HP\Desktop\trading_bot\trading_bot_6"

# === MOVE TO PROJECT ===
Set-Location $projectPath

# === CREATE .gitignore IF NOT EXISTS ===
if (!(Test-Path ".gitignore")) {
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
}

# === CREATE README IF NOT EXISTS ===
if (!(Test-Path "README.md")) {
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
}

# === INIT GIT IF NOT INITIALIZED ===
if (!(Test-Path ".git")) {
    git init
}

# === REMOVE OLD REMOTE IF EXISTS ===
$remotes = git remote
if ($remotes -contains "origin") {
    git remote remove origin
}

# === ADD NEW REMOTE ===
git remote add origin https://github.com/$githubUser/$repoName.git

# === ADD & COMMIT ONLY IF CHANGES EXIST ===
git add .

# Check if there are changes
$changes = git status --porcelain

if ($changes) {
    git commit -m "Update project"
} else {
    Write-Host "No changes to commit."
}

# === PUSH ===
git branch -M main
git push -u origin main
