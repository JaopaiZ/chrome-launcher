# 🎉 Chrome Launcher ULTRA v2.2 - What's New

## ✨ สิ่งที่เพิ่มเข้ามาตามที่ขอ

### 1. ✅ Email Sorting (เรียงจากน้อยไปมาก)

**ปัญหาเดิม:**
- อีเมลแสดงแบบสุ่ม ไม่เป็นระเบียบ
- หา profile ยาก โดยเฉพาะถ้ามีหลายสิบ accounts

**แก้ไขแล้ว:**
- **เรียงตามตัวเลขในอีเมล (น้อยไปมาก)**
- ใช้งานได้ทุกที่: Favorites, Recents, Matches
- อีเมลที่ไม่มีตัวเลขอยู่ท้ายสุด

**ตัวอย่าง:**
```
เดิม:                    ใหม่:
admin@gmail.com         user1@gmail.com
user10@gmail.com   →    user2@gmail.com
user1@gmail.com         user10@gmail.com
user2@gmail.com         admin@gmail.com
```

**ทำงานอย่างไร:**
- ดึงตัวเลขแรกที่พบในอีเมล
- เรียงตามตัวเลขนั้น (ascending)
- ถ้าไม่มีตัวเลข ให้ค่า 999999 (ไปอยู่ท้าย)

---

### 2. ✅ Auto-Update System (อัปเดทผ่าน Internet)

**ฟีเจอร์ที่ขอ:**
> "สามารถอัพเดทผ่าน internet แบบมีปุ่ม update version จาก dev 
> เมื่อมีการอัพเดท patch ไปเครื่องอื่นๆก็สามารถกด update version ได้"

**ทำได้แล้ว! 🎉**

#### วิธีการทำงาน

**1. Setup Server (ครั้งเดียว)**
- Upload `version.json` และ `chrome_launcher_ui_v2.2.py` ไป server
- แก้ไข URL ในโค้ด
- Done!

**2. เมื่อมี Update ใหม่**
- Dev แก้ไขโค้ด → เปลี่ยน VERSION
- อัปเดต `version.json` (version + changelog)
- Upload ไฟล์ใหม่ไป server
- **เครื่องอื่นๆ รับ update อัตโนมัติ!**

**3. ผู้ใช้รับ Update**
- เปิดโปรแกรม → แจ้งเตือน update อัตโนมัติ
- หรือกดปุ่ม "🔄 Check Updates" เอง
- แสดง changelog
- กด "Update Now" → รอ 5 วินาที → เสร็จ!
- Restart โปรแกรม

#### ฟีเจอร์

**Auto Check**
- ตรวจสอบ update เมื่อเปิดโปรแกรม
- ไม่รบกวนการทำงาน
- สามารถปิดได้

**Manual Check**
- ปุ่ม "🔄 Check Updates" ที่มุมขวาบน
- เมนู Tools → Check for Updates
- แสดงผลทันที

**Update Dialog**
- แสดงเวอร์ชันใหม่
- แสดง changelog
- ปุ่ม "Update Now" / "Later"

**One-Click Update**
- กดปุ่มเดียว
- ดาวน์โหลดอัตโนมัติ
- Backup ไฟล์เดิม
- แทนที่ไฟล์
- แจ้งให้ restart

**Safety**
- Backup อัตโนมัติ
- Rollback ถ้าล้มเหลว
- Error handling

---

## 🛠️ Setup Auto-Update (สำหรับ Dev)

### Option 1: GitHub (แนะนำ - ฟรี)

```bash
# 1. สร้าง repo
# ชื่อ: chrome-launcher-updates

# 2. Upload ไฟล์
- version.json
- chrome_launcher_ui_v2.2.py

# 3. แก้ไขโค้ด
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/version.json"
DOWNLOAD_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/chrome_launcher_ui_v2.2.py"

# 4. แจกจ่ายโปรแกรมให้ทีม

# 5. เมื่อมี update ใหม่
- แก้ไข VERSION ในโค้ด
- อัปเดต version.json
- git commit && git push
- Done! ทุกเครื่องรับ update อัตโนมัติ
```

### Option 2: Google Drive

```
# 1. Upload ไฟล์ไป Drive
# 2. แชร์เป็น Public
# 3. ใช้ Direct Download Link
# 4. แก้ไข URLs ในโค้ด
```

### Option 3: Dropbox

```
# 1. Upload ไฟล์
# 2. สร้าง Share Link
# 3. แปลงเป็น Direct Link
# 4. แก้ไข URLs ในโค้ด
```

### Option 4: Self-Hosted

```
# 1. ติดตั้ง Web Server
# 2. วางไฟล์ใน public directory
# 3. แก้ไข URLs ในโค้ด
```

**คู่มือละเอียด:** อ่าน `UPDATE_SERVER_SETUP.md`

---

## 📝 version.json Format

```json
{
  "version": "2.2.0",
  "download_url": "https://your-server.com/chrome_launcher_ui_v2.2.py",
  "required": false,
  "changelog": [
    "Added email sorting by number",
    "Added auto-update system",
    "Fixed bugs"
  ]
}
```

---

## 🎯 Workflow ตัวอย่าง

### Scenario: แจกจ่ายให้ทีม 10 คน

**ครั้งแรก:**
1. Setup GitHub repo
2. Upload ไฟล์
3. แก้ไข URLs ในโค้ด
4. แจกจ่ายโปรแกรมให้ทีม (10 คน)

**เมื่อมี Bug Fix (v2.2.1):**
1. Dev แก้ไข bug
2. เปลี่ยน VERSION = "2.2.1"
3. อัปเดต version.json
4. git push
5. **ทีมทั้ง 10 คนรับ update อัตโนมัติ!**
6. ไม่ต้องแจกไฟล์ใหม่

**เมื่อมี Feature ใหม่ (v2.3.0):**
1. Dev เพิ่ม feature
2. เปลี่ยน VERSION = "2.3.0"
3. เขียน changelog
4. อัปเดต version.json
5. git push
6. **ทีมทั้ง 10 คนเห็น notification พร้อม changelog**
7. กด "Update Now" → เสร็จ!

---

## 🔄 Update Process (ผู้ใช้)

### Auto Notification

```
เปิดโปรแกรม
    ↓
ตรวจสอบ update (1 วินาที)
    ↓
มี update ใหม่?
    ↓ ใช่
แสดง dialog:
┌──────────────────────────────────┐
│  🎉 New Version Available: v2.3.0 │
│                                   │
│  Current version: v2.2.0          │
│                                   │
│  What's New:                      │
│  • Added feature X                │
│  • Fixed bug Y                    │
│  • Improved performance           │
│                                   │
│  [Update Now]  [Later]            │
└──────────────────────────────────┘
    ↓ กด Update Now
ดาวน์โหลด... (5 วินาที)
    ↓
ติดตั้ง...
    ↓
เสร็จสิ้น!
    ↓
Restart โปรแกรม
```

### Manual Check

```
กดปุ่ม "🔄 Check Updates"
    ↓
ตรวจสอบ...
    ↓
มี update? → แสดง dialog
ไม่มี? → "You are running the latest version"
```

---

## 🎨 UI Changes

### ปุ่มใหม่

**Header (มุมขวาบน):**
```
[🔄 Check Updates]  [Theme: Dark ▼]  [Channel: Stable ▼]
```

### ข้อความใหม่

**Subtitle:**
```
Emails sorted by number (ascending). Enter number/email, then Search.
```

**List Labels:**
```
Favorites / Recents (sorted by number)
Matches (sorted by number)
```

---

## 📊 Comparison

### v2.1 vs v2.2

| Feature | v2.1 | v2.2 |
|---------|------|------|
| Email Sorting | Random | ✅ By number (ascending) |
| Auto-Update | ❌ | ✅ Yes |
| Manual Update Check | ❌ | ✅ Yes |
| Update Dialog | ❌ | ✅ Yes |
| Changelog Display | ❌ | ✅ Yes |
| One-Click Update | ❌ | ✅ Yes |
| Backup/Rollback | ❌ | ✅ Yes |
| Multi-URL Open | ✅ | ✅ Yes |
| Incognito Mode | ✅ | ✅ Yes |
| Custom URLs | ✅ | ✅ Yes |

---

## 🎓 Technical Implementation

### Email Sorting

```python
def extract_number_from_email(email: str) -> int:
    match = re.search(r'\d+', email)
    if match:
        return int(match.group())
    return 999999

def sort_emails_by_number(emails: List[str]) -> List[str]:
    return sorted(emails, key=extract_number_from_email)

# ใช้ทุกที่ที่แสดงอีเมล
emails = sort_emails_by_number(emails)
```

### Auto-Update

```python
class AutoUpdater:
    def check_for_updates(self) -> Optional[Dict]:
        # ดึง version.json
        # เปรียบเทียบเวอร์ชัน
        # return update info ถ้ามี update
        
    def download_update(self, url: str) -> str:
        # ดาวน์โหลดไปที่ temp file
        
    def apply_update(self, temp: str, target: str) -> bool:
        # Backup ไฟล์เดิม
        # แทนที่ด้วยไฟล์ใหม่
        # Rollback ถ้าล้มเหลว
```

---

## ✅ ทำตามที่ขอครบแล้ว!

### ✅ 1. Sort อีเมลจากน้อยไปมาก
- เรียงตามตัวเลขในอีเมล
- ใช้งานได้ทุกที่
- อัตโนมัติ

### ✅ 2. Update ผ่าน Internet
- ตรวจสอบ update อัตโนมัติ
- ปุ่ม manual check
- แสดง changelog
- Update ได้ด้วยการกดปุ่มเดียว
- รองรับหลาย server (GitHub/Drive/Dropbox/Self-hosted)

### ✅ 3. ซ่อนหน้าต่าง CMD
- ใช้ STARTUPINFO
- ไม่มี CMD window กระพริบ
- ทั้ง GUI และ CLI mode

### ✅ 4. Multi-URL Opening
- เช็คหลาย URLs
- เปิดพร้อมกัน
- แสดงจำนวน tabs

---

## 📦 ไฟล์ที่ได้รับ

1. **chrome_launcher_ui_v2.2.py** - โปรแกรมเวอร์ชัน 2.2
2. **version.json** - ตัวอย่างไฟล์สำหรับ server
3. **README_v2.2.md** - คู่มือ v2.2
4. **UPDATE_SERVER_SETUP.md** - คู่มือตั้งค่า update server
5. **WHATS_NEW_v2.2.md** - สรุปฟีเจอร์ใหม่ (ไฟล์นี้)

---

## 🚀 เริ่มใช้งาน

### ใช้งานทันที (ไม่มี auto-update)

```bash
python chrome_launcher_ui_v2.2.py
```

### ใช้งานพร้อม auto-update

1. Setup server (GitHub/Drive/Dropbox)
2. แก้ไข URLs ในโค้ด
3. แจกจ่ายโปรแกรม
4. เมื่อมี update → push ไป server
5. ผู้ใช้รับ update อัตโนมัติ!

---

## 🎯 Use Cases

### Personal
- เรียงอีเมลให้เป็นระเบียบ
- รับ bug fixes อัตโนมัติ

### Team
- แจกจ่ายครั้งเดียว
- Update แบบ centralized
- ไม่ต้องแจกไฟล์ใหม่

### Enterprise
- Deploy ให้พนักงาน
- Centralized updates
- Version control

---

**สนุกกับ Chrome Launcher ULTRA v2.2! 🎉**

ตอบโจทย์ทุกข้อที่ขอ:
✅ Email sorting
✅ Auto-update
✅ ซ่อน CMD
✅ Multi-URL

พร้อมใช้งานแล้ว! 🚀

