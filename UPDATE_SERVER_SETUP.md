# Auto-Update Server Setup Guide

คู่มือการตั้งค่า Update Server สำหรับ Chrome Launcher ULTRA v2.2

---

## 🎯 ภาพรวม

Chrome Launcher ULTRA v2.2 มีระบบ auto-update ที่สามารถตรวจสอบและดาวน์โหลด update จาก server อัตโนมัติ

### วิธีการทำงาน

1. **Check for Updates** - โปรแกรมดึง `version.json` จาก server
2. **Compare Versions** - เปรียบเทียบเวอร์ชันปัจจุบันกับเวอร์ชันบน server
3. **Show Update Dialog** - ถ้ามี update ใหม่ แสดง dialog พร้อม changelog
4. **Download Update** - ดาวน์โหลดไฟล์ใหม่จาก server
5. **Apply Update** - แทนที่ไฟล์เดิมด้วยไฟล์ใหม่
6. **Restart** - ผู้ใช้ restart โปรแกรมเพื่อใช้เวอร์ชันใหม่

---

## 📁 ไฟล์ที่ต้องมีบน Server

### 1. version.json
ไฟล์ข้อมูลเวอร์ชันล่าสุด

```json
{
  "version": "2.2.0",
  "download_url": "https://your-server.com/chrome_launcher_ui_v2.2.py",
  "required": false,
  "changelog": [
    "Added email sorting by number",
    "Added automatic update checking",
    "Fixed bugs"
  ],
  "release_date": "2024-10-26",
  "min_python_version": "3.7"
}
```

**ฟิลด์:**
- `version` - เวอร์ชันล่าสุด (ต้องใช้ semantic versioning: X.Y.Z)
- `download_url` - URL สำหรับดาวน์โหลดไฟล์ใหม่
- `required` - บังคับให้ update หรือไม่ (true/false)
- `changelog` - รายการการเปลี่ยนแปลง (array)
- `release_date` - วันที่ release (optional)
- `min_python_version` - Python version ต่ำสุดที่รองรับ (optional)

### 2. chrome_launcher_ui_v2.2.py
ไฟล์โปรแกรมเวอร์ชันใหม่

---

## 🌐 ตัวเลือก Server

### Option 1: GitHub (แนะนำ - ฟรี)

**ข้อดี:**
- ฟรี
- CDN ทั่วโลก
- Version control
- Easy to update

**วิธีตั้งค่า:**

1. **สร้าง GitHub Repository**
   ```bash
   # สร้าง repo ใหม่ชื่อ "chrome-launcher"
   ```

2. **Upload ไฟล์**
   ```
   chrome-launcher/
   ├── version.json
   └── chrome_launcher_ui_v2.2.py
   ```

3. **ใช้ Raw URLs**
   ```
   https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher/main/version.json
   https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher/main/chrome_launcher_ui_v2.2.py
   ```

4. **อัปเดตโค้ดในโปรแกรม**
   
   แก้ไขบรรทัดต้นๆ ของไฟล์:
   ```python
   UPDATE_CHECK_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher/main/version.json"
   DOWNLOAD_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher/main/chrome_launcher_ui_v2.2.py"
   ```

5. **เมื่อมี Update ใหม่**
   - อัปเดต `version.json` (เปลี่ยน version และ changelog)
   - Upload ไฟล์ `.py` เวอร์ชันใหม่
   - Commit และ push

### Option 2: Google Drive

**ข้อดี:**
- ฟรี
- ง่าย
- มี storage เยอะ

**วิธีตั้งค่า:**

1. **Upload ไฟล์ไป Google Drive**

2. **แชร์ไฟล์เป็น Public**
   - คลิกขวา → Share → Anyone with the link

3. **ใช้ Direct Download Link**
   ```
   https://drive.google.com/uc?export=download&id=FILE_ID
   ```

4. **หา FILE_ID**
   - จาก share link: `https://drive.google.com/file/d/FILE_ID/view`

### Option 3: Dropbox

**วิธีตั้งค่า:**

1. **Upload ไฟล์ไป Dropbox**

2. **สร้าง Share Link**

3. **แปลงเป็น Direct Link**
   - เปลี่ยน `www.dropbox.com` เป็น `dl.dropboxusercontent.com`
   - เปลี่ยน `?dl=0` เป็น `?dl=1`

### Option 4: Self-Hosted Server

**ข้อดี:**
- ควบคุมเต็มที่
- ไม่พึ่ง third-party

**วิธีตั้งค่า:**

1. **ติดตั้ง Web Server** (Apache, Nginx, etc.)

2. **วางไฟล์ใน public directory**
   ```
   /var/www/html/chrome-launcher/
   ├── version.json
   └── chrome_launcher_ui_v2.2.py
   ```

3. **ตั้งค่า CORS** (ถ้าจำเป็น)
   ```nginx
   add_header Access-Control-Allow-Origin *;
   ```

4. **ใช้ URLs**
   ```
   https://your-domain.com/chrome-launcher/version.json
   https://your-domain.com/chrome-launcher/chrome_launcher_ui_v2.2.py
   ```

---

## 🔧 การตั้งค่าในโปรแกรม

### แก้ไข URLs

เปิดไฟล์ `chrome_launcher_ui_v2.2.py` และแก้ไขบรรทัดต้นๆ:

```python
# Version information
VERSION = "2.2.0"
UPDATE_CHECK_URL = "https://YOUR-SERVER/version.json"
DOWNLOAD_URL = "https://YOUR-SERVER/chrome_launcher_ui_v2.2.py"
```

**ตัวอย่าง (GitHub):**
```python
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/john/chrome-launcher/main/version.json"
DOWNLOAD_URL = "https://raw.githubusercontent.com/john/chrome-launcher/main/chrome_launcher_ui_v2.2.py"
```

### ปิด Auto-Update

ถ้าไม่ต้องการ auto-update:

1. **ปิดการตรวจสอบอัตโนมัติ:**
   - ใน config file เพิ่ม: `AUTO_UPDATE_CHECK=0`

2. **หรือลบโค้ด auto-check:**
   ```python
   # Comment out บรรทัดนี้ใน __init__
   # if self.config.auto_update_check == '1':
   #     self.root.after(1000, self.check_for_updates_async)
   ```

---

## 📝 Workflow การ Release Version ใหม่

### 1. เตรียมไฟล์

```bash
# แก้ไข VERSION ในโค้ด
VERSION = "2.3.0"

# ทดสอบโปรแกรม
python chrome_launcher_ui_v2.2.py

# เปลี่ยนชื่อไฟล์ (optional)
mv chrome_launcher_ui_v2.2.py chrome_launcher_ui_v2.3.py
```

### 2. อัปเดต version.json

```json
{
  "version": "2.3.0",
  "download_url": "https://your-server/chrome_launcher_ui_v2.3.py",
  "required": false,
  "changelog": [
    "New feature X",
    "Fixed bug Y",
    "Improved performance Z"
  ],
  "release_date": "2024-11-01"
}
```

### 3. Upload ไป Server

**GitHub:**
```bash
git add version.json chrome_launcher_ui_v2.3.py
git commit -m "Release v2.3.0"
git push
```

**Google Drive/Dropbox:**
- Upload ไฟล์ใหม่
- แทนที่ไฟล์เดิม

### 4. ทดสอบ Update

1. เปิดโปรแกรมเวอร์ชันเก่า
2. กด "Check Updates"
3. ตรวจสอบว่า dialog แสดงถูกต้อง
4. ทดสอบ update

---

## 🔒 Security Considerations

### 1. HTTPS Only

ใช้ HTTPS เท่านั้น ห้ามใช้ HTTP:
```python
# ✅ Good
UPDATE_CHECK_URL = "https://your-server.com/version.json"

# ❌ Bad
UPDATE_CHECK_URL = "http://your-server.com/version.json"
```

### 2. Verify Downloads (Advanced)

เพิ่มการตรวจสอบ checksum:

**ใน version.json:**
```json
{
  "version": "2.3.0",
  "download_url": "https://...",
  "sha256": "abc123..."
}
```

**ในโค้ด:**
```python
def verify_download(file_path, expected_sha256):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        sha256.update(f.read())
    return sha256.hexdigest() == expected_sha256
```

### 3. Code Signing (Advanced)

สำหรับ production ควร sign โค้ด

---

## 🧪 การทดสอบ

### Test Scenarios

1. **No Update Available**
   - เวอร์ชันปัจจุบัน = เวอร์ชันบน server
   - ควรแสดง "You are running the latest version"

2. **Update Available**
   - เวอร์ชันปัจจุบัน < เวอร์ชันบน server
   - ควรแสดง update dialog

3. **Network Error**
   - Server ไม่ตอบสนอง
   - ควร fail gracefully (ไม่ crash)

4. **Invalid JSON**
   - version.json มี syntax error
   - ควร handle error

5. **Download Failed**
   - ไฟล์ดาวน์โหลดไม่สำเร็จ
   - ควรแสดง error message

### Test Commands

```bash
# ทดสอบ version check
python -c "from chrome_launcher_ui_v2.2 import AutoUpdater; u = AutoUpdater('2.1.0', 'URL', 'URL'); print(u.check_for_updates())"

# ทดสอบ version comparison
python -c "from chrome_launcher_ui_v2.2 import AutoUpdater; u = AutoUpdater('2.1.0', '', ''); print(u.is_newer_version('2.2.0', '2.1.0'))"
```

---

## 📊 Monitoring

### ติดตาม Update Usage

**ใช้ Google Analytics / Server Logs:**
- จำนวนครั้งที่ check update
- จำนวนครั้งที่ download
- เวอร์ชันที่ใช้งานมากที่สุด

**ตัวอย่าง (Server Log):**
```
2024-10-26 10:00:00 - GET /version.json - 200 - v2.1.0
2024-10-26 10:05:00 - GET /chrome_launcher_ui_v2.2.py - 200
```

---

## 🎯 Best Practices

1. **Semantic Versioning**
   - MAJOR.MINOR.PATCH (e.g., 2.3.1)
   - MAJOR = breaking changes
   - MINOR = new features
   - PATCH = bug fixes

2. **Clear Changelog**
   - เขียนให้เข้าใจง่าย
   - ระบุ breaking changes
   - จำกัด 5-10 รายการ

3. **Test Before Release**
   - ทดสอบบนทุก platform
   - ทดสอบ update process
   - Backup เวอร์ชันเก่า

4. **Gradual Rollout**
   - Release ให้กลุ่มเล็กก่อน
   - รอ feedback
   - Release ทั้งหมด

5. **Rollback Plan**
   - เก็บเวอร์ชันเก่าไว้
   - สามารถ rollback ได้ทันที
   - แจ้งผู้ใช้ถ้ามีปัญหา

---

## 🚨 Troubleshooting

### ปัญหา: Update check ไม่ทำงาน

**สาเหตุ:**
- URL ผิด
- Network blocked
- CORS issue

**วิธีแก้:**
```python
# เพิ่ม debug logging
print(f"Checking: {self.update_url}")
print(f"Response: {response.read()}")
```

### ปัญหา: Download failed

**สาเหตุ:**
- URL ผิด
- File ไม่มี
- Permission denied

**วิธีแก้:**
- ตรวจสอบ URL
- ตรวจสอบ file permissions
- ลอง download ด้วย browser

### ปัญหา: Update แล้วไม่เปลี่ยน

**สาเหตุ:**
- ไม่ได้ restart
- File ถูก lock
- Permission issue

**วิธีแก้:**
- Restart โปรแกรม
- ปิดโปรแกรมก่อน update
- ตรวจสอบ file permissions

---

## 📚 ตัวอย่าง Complete Setup (GitHub)

### 1. สร้าง Repository

```bash
# Local
mkdir chrome-launcher-updates
cd chrome-launcher-updates
git init

# Add files
cp chrome_launcher_ui_v2.2.py .
cp version.json .

# Commit
git add .
git commit -m "Initial release v2.2.0"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/chrome-launcher-updates.git
git push -u origin main
```

### 2. แก้ไขโค้ด

```python
# ใน chrome_launcher_ui_v2.2.py
VERSION = "2.2.0"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/version.json"
DOWNLOAD_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/chrome_launcher_ui_v2.2.py"
```

### 3. Release Update ใหม่

```bash
# แก้ไข VERSION ในโค้ด
# VERSION = "2.3.0"

# แก้ไข version.json
# "version": "2.3.0"

# Commit
git add .
git commit -m "Release v2.3.0 - Added feature X"
git push

# Done! ผู้ใช้จะได้รับ notification อัตโนมัติ
```

---

## ✅ Checklist

- [ ] เลือก server (GitHub/Drive/Dropbox/Self-hosted)
- [ ] Upload version.json และ .py file
- [ ] แก้ไข UPDATE_CHECK_URL และ DOWNLOAD_URL ในโค้ด
- [ ] ทดสอบ check for updates
- [ ] ทดสอบ download และ install update
- [ ] เตรียม rollback plan
- [ ] เขียน changelog ชัดเจน
- [ ] ทดสอบบนทุก platform
- [ ] Release!

---

**พร้อมใช้งาน Auto-Update แล้ว! 🎉**

