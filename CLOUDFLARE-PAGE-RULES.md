# Cloudflare Page Rules untuk dailymoney.my.id
# Masuk: Cloudflare Dashboard → Rules → Page Rules → Create Page Rule

# Page Rule 1: Always Use HTTPS
URL: *dailymoney.my.id/*
Setting: Always Use HTTPS → ON

# Page Rule 2: Security Headers (via Worker)
URL: *dailymoney.my.id/*
Setting: Worker Route → dailymoney-security-headers

# Page Rule 3: Cache Static Assets
URL: *dailymoney.my.id/assets/*
Setting: Cache Level → Standard
         Edge Cache TTL → 1 month
         Browser Cache TTL → 4 hours

# Page Rule 4: Sitemap & RSS No Cache
URL: *dailymoney.my.id/*.xml
Setting: Cache Level → Bypass

# Page Rule 5: Auto Minify
URL: *dailymoney.my.id/*
Setting: Auto Minify → HTML: ON, CSS: ON, JS: ON
