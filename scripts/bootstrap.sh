#!/usr/bin/env bash
# DailyMoney — Full Bootstrap Script
# ====================================
# Satu perintah untuk restore SEMUA agent dari GitHub.
# Jalankan setelah server reset / clone pertama.
#
# Usage:
#   bash <(curl -s https://raw.githubusercontent.com/funnycatmomentusa-byte/dailymoney-site/main/scripts/bootstrap.sh)
#
# Atau:
#   git clone https://github.com/funnycatmomentusa-byte/dailymoney-site.git
#   cd dailymoney-site && bash scripts/bootstrap.sh

set -e

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERR]${NC} $1"; }

# ── Config ──
PROJECT_DIR="/root/workspace/dailymoney-site"
REPO_URL="https://github.com/funnycatmomentusa-byte/dailymoney-site.git"
BRANCH="main"

# ── 1. Install System Dependencies ──
info "Installing system dependencies..."
apt-get update -qq && apt-get install -y -qq python3 python3-pip git curl >/dev/null 2>&1
ok "System dependencies installed"

# ── 2. Clone/Update Repo ──
if [ -d "$PROJECT_DIR/.git" ]; then
    info "Repo already exists, pulling latest..."
    cd "$PROJECT_DIR" && git pull origin $BRANCH
else
    info "Cloning repo..."
    rm -rf "$PROJECT_DIR"
    git clone --depth 1 -b $BRANCH "$REPO_URL" "$PROJECT_DIR"
fi
ok "Repo ready at $PROJECT_DIR"

# ── 3. Install Python Dependencies ──
info "Installing Python dependencies..."
pip3 install --break-system-packages -q duckduckgo_search requests pillow 2>/dev/null || true
# Verify critical imports
python3 -c "from duckduckgo_search import DDGS; print('duckduckgo_search OK')" 2>/dev/null || {
    warn "duckduckgo_search not importable, retrying..."
    pip3 install --break-system-packages duckduckgo_search 2>/dev/null
}
ok "Python dependencies installed"

# ── 4. Setup Git Credentials ──
info "Setting up git..."
git config --global user.name "DailyMoney Bot"
git config --global user.email "bot@dailymoney.my.id"
ok "Git configured"

# ── 5. Setup Remote with Token (if GH_TOKEN set) ──
if [ -n "$GH_TOKEN" ]; then
    cd "$PROJECT_DIR"
    git remote set-url origin "https://funnycatmomentusa-byte:${GH_TOKEN}@github.com/funnycatmomentusa-byte/dailymoney-site.git"
    ok "Git remote configured with GH_TOKEN"
fi

# ── 6. Register Hermes Cron Jobs ──
info "Registering Hermes cron jobs..."

# Copy scripts to ~/.hermes/scripts/
mkdir -p ~/.hermes/scripts
cp "$PROJECT_DIR"/scripts/*.py ~/.hermes/scripts/ 2>/dev/null || true
cp "$PROJECT_DIR"/scripts/*.sh ~/.hermes/scripts/ 2>/dev/null || true
# Also copy site-level scripts
cp "$PROJECT_DIR"/search_news*.py ~/.hermes/scripts/ 2>/dev/null || true
cp "$PROJECT_DIR"/get_forex_data*.py ~/.hermes/scripts/ 2>/dev/null || true

ok "Agent scripts copied to ~/.hermes/scripts/"

# ── 7. Generate Initial Site ──
info "Generating site..."
cd "$PROJECT_DIR"
python3 generate-site.py 2>/dev/null || warn "Site generation skipped (no new articles)"
ok "Site generated"

# ── 8. Setup Cloudflare (if API token available) ──
if [ -n "$CLOUDFLARE_API_TOKEN" ]; then
    info "Setting up Cloudflare..."
    python3 scripts/cloudflare-auto-setup.py 2>/dev/null || warn "Cloudflare setup skipped"
fi

# ── Summary ──
echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  DailyMoney — Bootstrap Complete! ✅${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo "  📁 Project: $PROJECT_DIR"
echo "  🌐 Site: https://dailymoney.my.id"
echo "  🤖 Agents: Pastikan cron job terdaftar di Hermes"
echo ""
echo "  🔧 Jika GH_TOKEN diset, auto-push akan jalan."
echo "  📱 Telegram bot: @dailymoneyfnd_bot"
echo ""
echo "  Seluruh agent berjalan OTOMATIS — situs hidup sendiri! 🚀"
echo ""
