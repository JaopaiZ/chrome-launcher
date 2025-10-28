# Changelog

All notable changes to Chrome Profile Launcher ULTRA.

---

## [2.1] - 2024 (Final Release)

### ✨ Added
- **Multi-URL Opening** - เปิดหลาย URLs พร้อมกันในแท็บแยก
- **7 Default URLs** - YouTube Premium, Google Family, Netflix, Gmail, Disney+, Amazon Prime, HBO Max
- **Custom URL Manager** - จัดการ URL ได้ไม่จำกัด
- **Incognito Mode** - เปิด Chrome ในโหมด Incognito
- **Quick Launch Buttons** - ปุ่มเปิดด่วนสำหรับ 5 profiles ที่ใช้บ่อยที่สุด
- **Search History** - จดจำคำค้นหาล่าสุด 20 รายการ
- **Import/Export Config** - สำรองและย้ายการตั้งค่า
- **Profile Info Dialog** - แสดงข้อมูล profile แบบละเอียด
- **Context Menu** - คลิกขวาเพื่อเข้าถึงฟังก์ชัน
- **CLI Support** - รองรับการใช้งานผ่าน command line
- **Keyboard Navigation** - Arrow keys สำหรับเลื่อนรายการ
- **Enhanced Menu System** - File, Tools, Help menus
- **Auto-select First Match** - เลือกรายการแรกอัตโนมัติ
- **Better Error Messages** - ข้อความ error ที่เข้าใจง่าย

### 🔧 Fixed
- **Custom URL Dialog** - แก้ไขปัญหาการเพิ่ม URL ไม่ได้
- **CMD Window Hiding** - ซ่อนหน้าต่าง CMD บน Windows
- **Dialog Wait** - แก้ไข dialog ไม่ wait ให้เสร็จ
- **URL Display** - แสดง URL แบบย่อถ้ายาวเกินไป

### 🚀 Improved
- **Cross-platform Support** - รองรับ Windows, macOS, Linux
- **Setup Scripts** - Auto setup สำหรับทุก platform
- **Portable Mode** - Windows portable launcher ไม่ต้อง setup
- **Documentation** - คู่มือครบถ้วน 3 ไฟล์
- **Package Distribution** - ZIP file พร้อมใช้งาน

---

## [2.0] - 2024 (Enhanced Version)

### ✨ Added
- **Dark/Light Theme** - เลือกธีมได้
- **Multi-Channel Support** - Stable, Beta, Dev, Canary
- **Custom Chrome Path** - เลือก Chrome executable เอง
- **Usage Tracking** - ติดตามจำนวนครั้งที่ใช้
- **Favorites System** - จัดการรายการโปรด
- **Recents System** - แสดงรายการล่าสุด
- **Per-Profile URL** - กำหนด URL เฉพาะแต่ละ profile
- **Window Position Save** - จำตำแหน่งหน้าต่าง
- **Regex Search** - ค้นหาด้วย regex

### 🔧 Fixed
- **Profile Detection** - ปรับปรุงการตรวจจับ profiles
- **Chrome Path Detection** - ตรวจหา Chrome อัตโนมัติ
- **Config Persistence** - บันทึกการตั้งค่าถาวร

---

## [1.0] - 2024 (Initial Python Version)

### ✨ Added
- **Python Conversion** - แปลงจาก PowerShell เป็น Python
- **GUI with tkinter** - สร้าง UI ด้วย tkinter
- **Profile Search** - ค้นหาด้วยตัวเลขหรืออีเมล
- **Chrome Launch** - เปิด Chrome ด้วย profile ที่เลือก
- **URL Selection** - เลือก URL เริ่มต้น 3 แบบ
- **Config File** - บันทึกการตั้งค่าใน .cfg
- **Logging** - บันทึก log การทำงาน

---

## [0.x] - PowerShell Version (Original)

- PowerShell script สำหรับ Windows
- ฟังก์ชันพื้นฐานสำหรับเปิด Chrome profiles

---

## Legend

- ✨ Added - ฟีเจอร์ใหม่
- 🔧 Fixed - แก้ไขบั๊ก
- 🚀 Improved - ปรับปรุงฟีเจอร์เดิม
- 🗑️ Removed - ลบฟีเจอร์
- ⚠️ Deprecated - เตือนว่าจะลบในอนาคต
- 🔒 Security - แก้ไขความปลอดภัย

