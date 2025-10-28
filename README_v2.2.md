# Chrome Profile Launcher ULTRA v2.2 🚀

## 🎉 What's New in v2.2

### ✨ Major Features

**1. Email Sorting by Number (Ascending)**
- อีเมลทั้งหมดถูกเรียงตามตัวเลขที่พบในอีเมล (น้อยไปมาก)
- ใช้งานได้ทุกที่: Favorites, Recents, Matches, Quick Launch
- อีเมลที่ไม่มีตัวเลขจะอยู่ท้ายสุด
- ตัวอย่าง: `user1@gmail.com`, `user2@gmail.com`, `user10@gmail.com`, `admin@gmail.com`

**2. Auto-Update System**
- ตรวจสอบ update อัตโนมัติเมื่อเปิดโปรแกรม
- แสดง changelog ของเวอร์ชันใหม่
- Update ได้ด้วยการกดปุ่มเดียว
- ปุ่ม "🔄 Check Updates" สำหรับตรวจสอบด้วยตนเอง
- รองรับ GitHub, Google Drive, Dropbox, หรือ self-hosted server

### 🔧 Improvements

- ปรับปรุงการแสดงผลอีเมลให้สม่ำเสมอ
- เพิ่มข้อความแจ้งเตือนการเรียงลำดับ
- ปรับปรุง UI สำหรับ update notifications
- เพิ่ม logging สำหรับ update process

---

## 📊 Email Sorting Examples

### Before (v2.1)
```
admin@gmail.com
user10@gmail.com
user1@gmail.com
user2@gmail.com
```

### After (v2.2)
```
user1@gmail.com
user2@gmail.com
user10@gmail.com
admin@gmail.com
```

**Logic:**
- Extract first number from email
- Sort by that number (ascending)
- Emails without numbers go to the end

---

## 🔄 Auto-Update Features

### Automatic Checking
- ตรวจสอบ update เมื่อเปิดโปรแกรม (delay 1 วินาที)
- ไม่รบกวนการทำงาน
- สามารถปิดได้ใน config: `AUTO_UPDATE_CHECK=0`

### Manual Checking
- กดปุ่ม "🔄 Check Updates" ที่มุมขวาบน
- หรือเมนู Tools → Check for Updates
- แสดงผลทันที

### Update Dialog
แสดงข้อมูล:
- เวอร์ชันใหม่
- เวอร์ชันปัจจุบัน
- Changelog (รายการการเปลี่ยนแปลง)
- ปุ่ม "Update Now" และ "Later"

### Update Process
1. กด "Update Now"
2. ดาวน์โหลดไฟล์ใหม่
3. Backup ไฟล์เดิม
4. แทนที่ด้วยไฟล์ใหม่
5. แจ้งให้ restart โปรแกรม

### Rollback
- ไฟล์เดิมถูก backup เป็น `.backup`
- ถ้า update ล้มเหลว จะ restore อัตโนมัติ
- สามารถ restore ด้วยตนเองได้

---

## 🛠️ Setup Auto-Update Server

### Quick Start (GitHub - แนะนำ)

1. **สร้าง GitHub Repository**
   ```bash
   # สร้าง repo ชื่อ "chrome-launcher-updates"
   ```

2. **Upload ไฟล์**
   - `version.json`
   - `chrome_launcher_ui_v2.2.py`

3. **แก้ไขโค้ด**
   ```python
   UPDATE_CHECK_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/version.json"
   DOWNLOAD_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/chrome-launcher-updates/main/chrome_launcher_ui_v2.2.py"
   ```

4. **Done!** ผู้ใช้จะได้รับ update อัตโนมัติ

**คู่มือละเอียด**: อ่าน `UPDATE_SERVER_SETUP.md`

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
  ],
  "release_date": "2024-10-26"
}
```

---

## 🎯 Use Cases

### For Developers
- แจกจ่ายโปรแกรมให้ทีม
- Push updates โดยไม่ต้องแจกไฟล์ใหม่
- Centralized version control

### For IT Admins
- Deploy ให้พนักงาน
- Update แบบ centralized
- Monitor usage

### For Personal Use
- ไม่ต้องดาวน์โหลดเวอร์ชันใหม่เอง
- รับ bug fixes อัตโนมัติ
- Always up-to-date

---

## ⚙️ Configuration

### ปิด Auto-Update Check

**วิธีที่ 1: ใน Config File**
```
AUTO_UPDATE_CHECK=0
```

**วิธีที่ 2: ลบโค้ด**
```python
# Comment out ใน __init__
# if self.config.auto_update_check == '1':
#     self.root.after(1000, self.check_for_updates_async)
```

### เปลี่ยน Update Server

แก้ไขบรรทัดต้นๆ ของไฟล์:
```python
UPDATE_CHECK_URL = "https://your-server.com/version.json"
DOWNLOAD_URL = "https://your-server.com/chrome_launcher_ui_v2.2.py"
```

---

## 🔒 Security

### HTTPS Only
- ใช้ HTTPS เท่านั้น
- ห้ามใช้ HTTP

### Backup Automatic
- ไฟล์เดิมถูก backup ก่อน update
- Restore อัตโนมัติถ้า update ล้มเหลว

### Error Handling
- Network errors ไม่ทำให้โปรแกรม crash
- Invalid JSON ถูก handle
- Download failures แสดง error message

---

## 📚 Documentation

- **UPDATE_SERVER_SETUP.md** - คู่มือตั้งค่า update server
- **version.json** - ตัวอย่างไฟล์ version
- **README.md** - คู่มือหลัก
- **CHANGELOG.md** - ประวัติการเปลี่ยนแปลง

---

## 🆙 Upgrading from v2.1

### ไฟล์เดิมใช้ได้
- Config file เดิมใช้ได้เลย
- ไม่ต้องตั้งค่าใหม่

### ฟีเจอร์ใหม่
- Email sorting ทำงานอัตโนมัติ
- Auto-update ทำงานทันที (ถ้า setup server)

### Breaking Changes
- ไม่มี

---

## 🐛 Known Issues

### Update Check Failed
- ตรวจสอบ internet connection
- ตรวจสอบ UPDATE_CHECK_URL ถูกต้อง
- ตรวจสอบ server ทำงาน

### Download Failed
- ตรวจสอบ DOWNLOAD_URL ถูกต้อง
- ตรวจสอบ file permissions
- ตรวจสอบ disk space

---

## 🎓 Technical Details

### Email Sorting Algorithm

```python
def extract_number_from_email(email: str) -> int:
    """Extract first number from email"""
    match = re.search(r'\d+', email)
    if match:
        return int(match.group())
    return 999999  # No number = end of list

emails = sorted(emails, key=extract_number_from_email)
```

### Version Comparison

```python
def is_newer_version(remote: str, local: str) -> bool:
    """Compare semantic versions"""
    remote_parts = [int(x) for x in remote.split('.')]
    local_parts = [int(x) for x in local.split('.')]
    return remote_parts > local_parts
```

### Update Process

1. Check version.json
2. Compare versions
3. Show dialog if newer
4. Download to temp file
5. Backup current file
6. Replace with new file
7. Make executable (Unix)
8. Prompt restart

---

## 📊 Statistics

- **Version**: 2.2.0
- **Release Date**: 2024-10-26
- **Lines of Code**: ~1,800
- **New Features**: 2
- **Bug Fixes**: 0
- **Breaking Changes**: 0

---

## 🙏 Credits

- Email sorting: Natural number sorting algorithm
- Auto-update: Inspired by Electron auto-updater
- UI: tkinter

---

## 📞 Support

ถ้าพบปัญหา:
1. ตรวจสอบ log file: `ChromeLauncherUI.log`
2. อ่าน documentation
3. ตรวจสอบ GitHub issues

---

## 🎯 Roadmap

### v2.3 (Planned)
- [ ] Profile groups
- [ ] Scheduled launches
- [ ] URL templates
- [ ] Export/Import profiles

### v3.0 (Future)
- [ ] Plugin system
- [ ] Cloud sync
- [ ] Mobile companion app

---

**Enjoy Chrome Launcher ULTRA v2.2! 🚀**

แก้ไขปัญหาการเรียงลำดับและเพิ่มระบบ auto-update ที่ทรงพลัง!

