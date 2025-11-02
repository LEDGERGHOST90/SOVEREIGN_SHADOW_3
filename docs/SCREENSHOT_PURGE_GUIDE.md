# 🔥 SCREENSHOT PURGE GUIDE

**Goal**: Delete thousands of portfolio update screenshots sent to AI systems
**Perfect timing**: Before laptop replacement - start fresh!

**⚠️ WHAT WE'RE DELETING:**
- ✅ Screenshots from Google Photos (portfolio spam)
- ✅ Screenshots from Desktop/Downloads
- ✅ CSV exports from Downloads

**🔒 WHAT STAYS SAFE:**
- ❌ Actual photos (exes, personal pics, booty pics, etc.)
- ❌ Videos
- ❌ Documents
- ✅ Google Photos has a "Screenshots" filter - we only nuke those!

---

## 🎯 QUICK PURGE (Run on your Mac)

### 1. Find All Screenshots (Count First)
```bash
# Count screenshots on Desktop
find ~/Desktop -name "Screenshot*.png" -o -name "Screenshot*.jpg" | wc -l

# Count in Downloads
find ~/Downloads -name "Screenshot*.png" -o -name "Screenshot*.jpg" | wc -l

# Count in Documents
find ~/Documents -name "Screenshot*.png" -o -name "Screenshot*.jpg" | wc -l

# Find ALL screenshots (may take a while)
find ~ -type f \( -name "Screenshot*.png" -o -name "Screenshot*.jpg" \) 2>/dev/null | wc -l
```

### 2. Preview Before Deleting
```bash
# See what will be deleted (Desktop)
find ~/Desktop -name "Screenshot 2025-*" -type f

# See what will be deleted (Downloads)
find ~/Downloads -name "Screenshot 2025-*" -type f

# See portfolio-related screenshots
find ~ -type f -name "*portfolio*" -o -name "*Portfolio*" 2>/dev/null | head -50
```

### 3. DELETE Screenshots (Desktop)
```bash
# Delete 2025 screenshots from Desktop
find ~/Desktop -name "Screenshot 2025-*" -type f -delete

# Delete ALL screenshots from Desktop
find ~/Desktop -name "Screenshot*.png" -type f -delete
find ~/Desktop -name "Screenshot*.jpg" -type f -delete
```

### 4. DELETE Screenshots (Downloads)
```bash
# Delete 2025 screenshots from Downloads
find ~/Downloads -name "Screenshot 2025-*" -type f -delete

# Delete ALL screenshots from Downloads
find ~/Downloads -name "Screenshot*.png" -type f -delete
find ~/Downloads -name "Screenshot*.jpg" -type f -delete
```

### 5. DELETE IMG_* Files (Camera Roll uploads)
```bash
# Count IMG files
find ~/Desktop ~/Downloads -name "IMG_*.png" -o -name "IMG_*.jpg" | wc -l

# Delete IMG files from Desktop
find ~/Desktop -name "IMG_*.png" -type f -delete
find ~/Desktop -name "IMG_*.jpg" -type f -delete

# Delete IMG files from Downloads
find ~/Downloads -name "IMG_*.png" -type f -delete
find ~/Downloads -name "IMG_*.jpg" -type f -delete
```

---

## 🔍 AI APP SPECIFIC CLEANUP

### Claude Desktop Uploads
```bash
# Find Claude upload cache
find ~/Library -name "*claude*" -type d 2>/dev/null

# Delete Claude temp files
rm -rf ~/Library/Caches/com.anthropic.claude-desktop/*
```

### ChatGPT/OpenAI Uploads
```bash
# Find ChatGPT cache
find ~/Library -name "*openai*" -type d 2>/dev/null

# Clear ChatGPT cache
rm -rf ~/Library/Caches/com.openai.chat/*
```

### Browser Downloads (AI chat uploads)
```bash
# Delete old browser downloads (2024 and earlier)
find ~/Downloads -type f -newermt "2024-01-01" ! -newermt "2025-01-01" -delete
```

---

## 📊 FIND LARGE IMAGE COLLECTIONS

### Find Directories with Most Images
```bash
# Find folders with 100+ images
find ~ -type d -exec sh -c 'count=$(find "$1" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l); if [ $count -gt 100 ]; then echo "$count images in $1"; fi' _ {} \;
```

### Find Large Image Files
```bash
# Find images larger than 1MB
find ~ -type f \( -name "*.png" -o -name "*.jpg" \) -size +1M 2>/dev/null | head -20

# Find images larger than 5MB
find ~ -type f \( -name "*.png" -o -name "*.jpg" \) -size +5M 2>/dev/null
```

---

## 🗂️ SMART CLEANUP (Portfolio-Specific)

### Delete Portfolio Screenshots (2025 ONLY - Safe)
```bash
# SAFE: Only deletes macOS screenshots from Desktop/Downloads
# Does NOT touch Google Photos, iCloud Photos, or personal folders

# Screenshots from specific months (Oct-Nov portfolio spam)
find ~/Desktop -name "Screenshot 2025-10-*" -type f -delete
find ~/Desktop -name "Screenshot 2025-11-*" -type f -delete
find ~/Downloads -name "Screenshot 2025-10-*" -type f -delete
find ~/Downloads -name "Screenshot 2025-11-*" -type f -delete

# Screenshots at specific times (late night portfolio checks)
find ~/Desktop -name "Screenshot*2025-10-* at 11.*" -type f -delete
find ~/Desktop -name "Screenshot*2025-10-* at 12.*" -type f -delete
find ~/Downloads -name "Screenshot*2025-10-* at 11.*" -type f -delete
find ~/Downloads -name "Screenshot*2025-10-* at 12.*" -type f -delete
```

### Delete CSV Exports (Portfolio data dumps)
```bash
# Find portfolio CSVs
find ~/Downloads -name "*portfolio*.csv" -type f
find ~/Downloads -name "*2025*.csv" -type f

# Delete them
find ~/Downloads -name "202510*.csv" -type f -delete
find ~/Downloads -name "202511*.csv" -type f -delete
```

---

## 🧹 NUCLEAR OPTION (Use with caution!)

### Delete ALL Screenshots and Images from Desktop/Downloads
```bash
# CAREFUL: This deletes EVERYTHING
# Preview first:
find ~/Desktop ~/Downloads -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l

# Then delete:
find ~/Desktop ~/Downloads -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -delete
```

---

## 📱 GOOGLE PHOTOS CLEANUP (Web/Mobile)

**SAFE METHOD**: Google Photos has a built-in "Screenshots" category!

### Via Web (photos.google.com)
1. Go to **photos.google.com**
2. Click **Search** (magnifying glass icon)
3. Scroll down to **Categories** section
4. Click **Screenshots**
5. This shows ONLY screenshots (no actual photos!)
6. Select all screenshots (or filter by date: Oct-Nov 2025)
7. Click trash icon to delete
8. Go to **Trash** and permanently delete

### Via Mobile App
1. Open **Google Photos** app
2. Tap **Library** (bottom right)
3. Tap **Screenshots** album
4. Select screenshots from Oct-Nov 2025
5. Tap **Delete** (trash icon)
6. Empty trash

**⚠️ IMPORTANT**:
- The "Screenshots" category ONLY shows screenshots
- Your actual photos (exes, personal pics, etc.) are in different albums
- If unsure, preview before deleting!

### Quick Date Filter (Oct-Nov 2025 Only)
1. In Screenshots album
2. Use date selector to show only Oct-Nov 2025
3. Select all from those months
4. Delete
5. Earlier screenshots (might have memories) stay safe

---

## 📱 iCloud CLEANUP (Optional)

### Empty iCloud Downloads
```bash
# Find iCloud temp downloads
find ~/Library/Mobile\ Documents -name "Screenshot*.png" 2>/dev/null | wc -l

# Preview them first
find ~/Library/Mobile\ Documents -name "Screenshot*.png" 2>/dev/null | head -20

# Delete only if confirmed to be junk
# (Manual review recommended for iCloud)
```

### Empty Trash After Deletion
```bash
# Empty macOS trash
rm -rf ~/.Trash/*
```

---

## ✅ RECOMMENDED WORKFLOW (SAFE - Preserves Personal Photos)

**BEFORE laptop replacement:**

**⚠️ IMPORTANT**:
- Mac commands ONLY touch Desktop/Downloads screenshots
- Google Photos cleanup uses "Screenshots" category (no actual photos touched)
- All your personal photos (exes, booty pics, etc.) stay 100% SAFE

1. **Count everything first**
   ```bash
   echo "Desktop screenshots:" && find ~/Desktop -name "Screenshot*.png" | wc -l
   echo "Downloads screenshots:" && find ~/Downloads -name "Screenshot*.png" | wc -l
   echo "Total disk usage:" && du -sh ~/Desktop ~/Downloads
   ```

2. **Delete recent portfolio screenshots (Oct-Nov 2025 ONLY)**
   ```bash
   # SAFE: Only 2025 screenshots from Desktop/Downloads
   find ~/Desktop -name "Screenshot 2025-10-*" -type f -delete
   find ~/Desktop -name "Screenshot 2025-11-*" -type f -delete
   find ~/Downloads -name "Screenshot 2025-10-*" -type f -delete
   find ~/Downloads -name "Screenshot 2025-11-*" -type f -delete
   ```

3. **Delete IMG files (camera uploads to AI) - ONLY from Desktop/Downloads**
   ```bash
   # Preview first to make sure they're just AI uploads
   find ~/Desktop -name "IMG_*.png" | head -20
   find ~/Downloads -name "IMG_*.png" | head -20

   # If safe, delete:
   find ~/Desktop -name "IMG_*.png" -type f -delete
   find ~/Desktop -name "IMG_*.jpg" -type f -delete
   find ~/Downloads -name "IMG_*.png" -type f -delete
   find ~/Downloads -name "IMG_*.jpg" -type f -delete
   ```

4. **Delete portfolio CSVs**
   ```bash
   find ~/Downloads -name "202510*.csv" -type f -delete
   find ~/Downloads -name "202511*.csv" -type f -delete
   ```

5. **Empty trash**
   ```bash
   rm -rf ~/.Trash/*
   ```

6. **Clean Google Photos screenshots**
   - Go to photos.google.com
   - Search → Categories → Screenshots
   - Select Oct-Nov 2025 screenshots
   - Delete them
   - Empty trash

7. **Check savings**
   ```bash
   du -sh ~/Desktop ~/Downloads
   ```

**Total cleanup**:
- Local Mac: 2-5GB freed
- Google Photos: Potentially 5-10GB freed (depends on how many uploaded)

---

## 🎯 BEFORE/AFTER TRACKING

```bash
# Save "before" state
echo "=== BEFORE CLEANUP ===" > ~/cleanup_report.txt
echo "Desktop size:" >> ~/cleanup_report.txt
du -sh ~/Desktop >> ~/cleanup_report.txt
echo "Downloads size:" >> ~/cleanup_report.txt
du -sh ~/Downloads >> ~/cleanup_report.txt
echo "Screenshot count:" >> ~/cleanup_report.txt
find ~/Desktop ~/Downloads -name "Screenshot*.png" | wc -l >> ~/cleanup_report.txt

# ... run cleanup commands ...

# Save "after" state
echo "" >> ~/cleanup_report.txt
echo "=== AFTER CLEANUP ===" >> ~/cleanup_report.txt
echo "Desktop size:" >> ~/cleanup_report.txt
du -sh ~/Desktop >> ~/cleanup_report.txt
echo "Downloads size:" >> ~/cleanup_report.txt
du -sh ~/Downloads >> ~/cleanup_report.txt
echo "Screenshot count:" >> ~/cleanup_report.txt
find ~/Desktop ~/Downloads -name "Screenshot*.png" | wc -l >> ~/cleanup_report.txt

# View report
cat ~/cleanup_report.txt
```

---

## 💡 PREVENTION (For New Laptop)

**Don't accumulate screenshots again:**

1. **Use Notion/Obsidian for portfolio tracking** instead of screenshots
2. **Delete screenshots immediately** after uploading to AI
3. **Use clipboard managers** instead of saving screenshots
4. **Set up automated cleanup** (cron job to delete screenshots older than 7 days)

### Auto-cleanup Script (Optional)
```bash
# Create cleanup script
cat > ~/bin/cleanup_screenshots.sh <<'EOF'
#!/bin/bash
# Delete screenshots older than 7 days
find ~/Desktop ~/Downloads -name "Screenshot*.png" -mtime +7 -delete
find ~/Desktop ~/Downloads -name "IMG_*.png" -mtime +7 -delete
echo "Cleanup complete: $(date)"
EOF

chmod +x ~/bin/cleanup_screenshots.sh

# Run weekly (add to crontab)
# 0 9 * * 0 ~/bin/cleanup_screenshots.sh
```

---

**TL;DR Quick Commands:**

```bash
# Count screenshots
find ~/Desktop ~/Downloads -name "Screenshot*.png" | wc -l

# Delete October/November 2025 screenshots
find ~/Desktop ~/Downloads -name "Screenshot 2025-1*.png" -delete

# Delete all screenshots (YOLO)
find ~/Desktop ~/Downloads -name "Screenshot*.png" -delete

# Empty trash
rm -rf ~/.Trash/*
```

**Estimated space savings**: 2-5GB (depends on how many you've accumulated!)
