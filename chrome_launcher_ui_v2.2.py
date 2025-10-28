#!/usr/bin/env python3
"""
Chrome Profile Launcher ULTRA - Version 2.2
Added: Email sorting and Auto-update system
"""

import os
import sys
import json
import re
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import urllib.request
import urllib.error
import hashlib
import tempfile
import shutil

# Version information
VERSION = "2.3"
# TODO: Replace with your actual URLs after setting up update server
# See UPDATE_SERVER_SETUP.md for instructions
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/JaopaiZ/chrome-launcher/main/version.json"  
# Example: "https://raw.githubusercontent.com/JaopaiZ/chrome-launcher/main/version.json"
DOWNLOAD_URL = "https://raw.githubusercontent.com/JaopaiZ/chrome-launcher/main/chrome_launcher_ui_v2.2.py"  
# Example: "https://raw.githubusercontent.com/JaopaiZ/chrome-launcher/main/chrome_launcher_ui_v2.2.py"


def extract_number_from_email(email: str) -> int:
    """Extract first number from email for sorting, return 999999 if no number"""
    match = re.search(r'\d+', email)
    if match:
        return int(match.group())
    return 999999  # Emails without numbers go to the end


def sort_emails_by_number(emails: List[str]) -> List[str]:
    """Sort emails by the first number found in them (ascending)"""
    return sorted(emails, key=extract_number_from_email)


class AutoUpdater:
    """Handle automatic updates from remote server"""
    
    def __init__(self, current_version: str, update_url: str, download_url: str):
        self.current_version = current_version
        self.update_url = update_url
        self.download_url = download_url
    
    def check_for_updates(self) -> Optional[Dict]:
        """Check if updates are available"""
        # Skip if URLs not configured
        if not self.update_url or not self.update_url.strip():
            return None
        
        try:
            with urllib.request.urlopen(self.update_url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                remote_version = data.get('version', '0.0.0')
                
                if self.is_newer_version(remote_version, self.current_version):
                    return {
                        'version': remote_version,
                        'changelog': data.get('changelog', []),
                        'download_url': data.get('download_url', self.download_url),
                        'required': data.get('required', False)
                    }
                
                return None
        except (urllib.error.URLError, json.JSONDecodeError, Exception):
            return None
    
    def is_newer_version(self, remote: str, local: str) -> bool:
        """Compare version strings"""
        try:
            remote_parts = [int(x) for x in remote.split('.')]
            local_parts = [int(x) for x in local.split('.')]
            
            # Pad to same length
            while len(remote_parts) < 3:
                remote_parts.append(0)
            while len(local_parts) < 3:
                local_parts.append(0)
            
            return remote_parts > local_parts
        except Exception:
            return False
    
    def download_update(self, download_url: str) -> Optional[str]:
        """Download update file to temp location"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
            temp_path = temp_file.name
            temp_file.close()
            
            urllib.request.urlretrieve(download_url, temp_path)
            
            return temp_path
        except Exception:
            return None
    
    def apply_update(self, temp_path: str, target_path: str) -> bool:
        """Apply update by replacing current file"""
        try:
            # Backup current file
            backup_path = target_path + '.backup'
            if os.path.exists(target_path):
                shutil.copy2(target_path, backup_path)
            
            # Replace with new file
            shutil.copy2(temp_path, target_path)
            
            # Make executable on Unix
            if sys.platform != 'win32':
                os.chmod(target_path, 0o755)
            
            return True
        except Exception:
            # Restore backup if failed
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, target_path)
            return False


class ChromeLauncherConfig:
    """Configuration manager for Chrome Launcher"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.url_choice = '1'
        self.last_email = ''
        self.favorites = []
        self.recents = []
        self.channel = 'Stable'
        self.window_x = ''
        self.window_y = ''
        self.window_w = ''
        self.window_h = ''
        self.per_url = {}
        self.usage = {}
        self.use_perurl = '1'
        self.theme = 'Dark'
        self.custom_chrome = ''
        self.custom_urls = {}
        self.search_history = []
        self.quick_launch_profiles = []
        self.auto_update_check = '1'
        self.last_update_check = ''
        
    def load(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            return
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if match := re.match(r'URL_CHOICE=(\d)', line):
                    self.url_choice = match.group(1)
                elif match := re.match(r'LAST_EMAIL=(.+)', line):
                    self.last_email = match.group(1).strip()
                elif match := re.match(r'CHANNEL=(.+)', line):
                    self.channel = match.group(1).strip()
                elif match := re.match(r'WINDOW_X=(.+)', line):
                    self.window_x = match.group(1).strip()
                elif match := re.match(r'WINDOW_Y=(.+)', line):
                    self.window_y = match.group(1).strip()
                elif match := re.match(r'WINDOW_W=(.+)', line):
                    self.window_w = match.group(1).strip()
                elif match := re.match(r'WINDOW_H=(.+)', line):
                    self.window_h = match.group(1).strip()
                elif match := re.match(r'FAVORITES=(.*)', line):
                    favs = match.group(1).split(',')
                    self.favorites = [f for f in favs if '@' in f]
                elif match := re.match(r'RECENTS=(.*)', line):
                    recs = match.group(1).split(',')
                    self.recents = [r for r in recs if '@' in r]
                elif match := re.match(r'USE_PERURL=(\d)', line):
                    self.use_perurl = match.group(1)
                elif match := re.match(r'THEME=(.+)', line):
                    self.theme = match.group(1).strip()
                elif match := re.match(r'CUSTOM_CHROME=(.*)', line):
                    self.custom_chrome = match.group(1).strip()
                elif match := re.match(r'AUTO_UPDATE_CHECK=(\d)', line):
                    self.auto_update_check = match.group(1)
                elif match := re.match(r'LAST_UPDATE_CHECK=(.+)', line):
                    self.last_update_check = match.group(1).strip()
                elif match := re.match(r'PER_URL_(.+?)=(.+)', line):
                    self.per_url[match.group(1)] = match.group(2)
                elif match := re.match(r'USAGE_(.+?)=(\d+)', line):
                    self.usage[match.group(1)] = int(match.group(2))
                elif match := re.match(r'CUSTOM_URL_(.+?)=(.+)', line):
                    self.custom_urls[match.group(1)] = match.group(2)
                elif match := re.match(r'SEARCH_HISTORY=(.*)', line):
                    hist = match.group(1).split('|')
                    self.search_history = [h for h in hist if h]
                elif match := re.match(r'QUICK_LAUNCH=(.*)', line):
                    profiles = match.group(1).split(',')
                    self.quick_launch_profiles = [p for p in profiles if '@' in p]
    
    def save(self):
        """Save configuration to file"""
        lines = [
            f"URL_CHOICE={self.url_choice}",
            f"LAST_EMAIL={self.last_email}",
            f"CHANNEL={self.channel}",
            f"WINDOW_X={self.window_x}",
            f"WINDOW_Y={self.window_y}",
            f"WINDOW_W={self.window_w}",
            f"WINDOW_H={self.window_h}",
            f"USE_PERURL={self.use_perurl}",
            f"THEME={self.theme}",
            f"CUSTOM_CHROME={self.custom_chrome}",
            f"AUTO_UPDATE_CHECK={self.auto_update_check}",
            f"LAST_UPDATE_CHECK={self.last_update_check}",
            f"FAVORITES={','.join(self.favorites)}",
            f"RECENTS={','.join(self.recents)}",
            f"SEARCH_HISTORY={'|'.join(self.search_history[:20])}",
            f"QUICK_LAUNCH={','.join(self.quick_launch_profiles)}",
        ]
        
        for key, val in self.per_url.items():
            lines.append(f"PER_URL_{key}={val}")
            
        for key, val in self.usage.items():
            lines.append(f"USAGE_{key}={val}")
        
        for key, val in self.custom_urls.items():
            lines.append(f"CUSTOM_URL_{key}={val}")
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    
    def add_search_history(self, query: str):
        """Add to search history"""
        if query and query not in self.search_history:
            self.search_history.insert(0, query)
            self.search_history = self.search_history[:20]


class ChromePathFinder:
    """Find Chrome executable paths for different channels"""
    
    @staticmethod
    def get_chrome_path_for_channel(channel: str) -> Optional[str]:
        """Get Chrome path for specific channel"""
        candidates = []
        
        if sys.platform == 'win32':
            program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
            program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            
            if channel == 'Stable':
                candidates = [
                    f"{program_files}\\Google\\Chrome\\Application\\chrome.exe",
                    f"{program_files_x86}\\Google\\Chrome\\Application\\chrome.exe"
                ]
            elif channel == 'Beta':
                candidates = [
                    f"{program_files}\\Google\\Chrome Beta\\Application\\chrome.exe",
                    f"{program_files_x86}\\Google\\Chrome Beta\\Application\\chrome.exe"
                ]
            elif channel == 'Dev':
                candidates = [
                    f"{program_files}\\Google\\Chrome Dev\\Application\\chrome.exe",
                    f"{program_files_x86}\\Google\\Chrome Dev\\Application\\chrome.exe"
                ]
            elif channel == 'Canary':
                candidates = [f"{local_appdata}\\Google\\Chrome SxS\\Application\\chrome.exe"]
        elif sys.platform == 'darwin':
            if channel == 'Stable':
                candidates = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
            elif channel == 'Beta':
                candidates = ['/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta']
            elif channel == 'Dev':
                candidates = ['/Applications/Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev']
            elif channel == 'Canary':
                candidates = ['/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary']
        else:
            if channel == 'Stable':
                candidates = ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable']
            elif channel == 'Beta':
                candidates = ['/usr/bin/google-chrome-beta']
            elif channel == 'Dev':
                candidates = ['/usr/bin/google-chrome-unstable']
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def get_chrome_path_auto(preferred: str, custom: str = '') -> Optional[str]:
        """Get Chrome path automatically"""
        if custom and os.path.exists(custom):
            return custom
        
        path = ChromePathFinder.get_chrome_path_for_channel(preferred)
        if path:
            return path
        
        for channel in ['Stable', 'Beta', 'Dev', 'Canary']:
            path = ChromePathFinder.get_chrome_path_for_channel(channel)
            if path:
                return path
        
        return None


class ChromeProfileManager:
    """Manage Chrome profiles"""
    
    @staticmethod
    def get_local_state_path() -> str:
        """Get path to Chrome Local State file"""
        if sys.platform == 'win32':
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            return os.path.join(local_appdata, 'Google', 'Chrome', 'User Data', 'Local State')
        elif sys.platform == 'darwin':
            home = os.path.expanduser('~')
            return os.path.join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'Local State')
        else:
            home = os.path.expanduser('~')
            return os.path.join(home, '.config', 'google-chrome', 'Local State')
    
    @staticmethod
    def get_profile_directory_by_email(email: str) -> Optional[str]:
        """Get profile directory name by email"""
        try:
            local_state_path = ChromeProfileManager.get_local_state_path()
            if not os.path.exists(local_state_path):
                return None
            
            with open(local_state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cache = data.get('profile', {}).get('info_cache', {})
            
            for profile_dir, profile_info in cache.items():
                gaia_email = profile_info.get('gaia_info', {}).get('email', '')
                user_name = profile_info.get('user_name', '')
                
                if gaia_email == email or user_name == email:
                    return profile_dir
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_profile_info(email: str) -> Dict:
        """Get detailed profile information"""
        try:
            local_state_path = ChromeProfileManager.get_local_state_path()
            if not os.path.exists(local_state_path):
                return {}
            
            with open(local_state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cache = data.get('profile', {}).get('info_cache', {})
            
            for profile_dir, profile_info in cache.items():
                gaia_email = profile_info.get('gaia_info', {}).get('email', '')
                user_name = profile_info.get('user_name', '')
                
                if gaia_email == email or user_name == email:
                    return {
                        'email': email,
                        'name': profile_info.get('name', ''),
                        'profile_dir': profile_dir,
                        'user_name': user_name,
                        'gaia_name': profile_info.get('gaia_info', {}).get('given_name', '')
                    }
            
            return {}
        except Exception:
            return {}
    
    @staticmethod
    def get_emails_from_local_state() -> List[str]:
        """Get all emails from Chrome Local State"""
        try:
            local_state_path = ChromeProfileManager.get_local_state_path()
            if not os.path.exists(local_state_path):
                return []
            
            with open(local_state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            cache = data.get('profile', {}).get('info_cache', {})
            emails = []
            
            for profile_dir, profile_info in cache.items():
                gaia_email = profile_info.get('gaia_info', {}).get('email', '')
                user_name = profile_info.get('user_name', '')
                
                if gaia_email:
                    emails.append(gaia_email)
                elif user_name:
                    emails.append(user_name)
            
            emails = [e for e in emails if '@' in e]
            emails = list(set(emails))
            
            # Sort by number (ascending)
            emails = sort_emails_by_number(emails)
            
            return emails
        except Exception:
            return []


class Logger:
    """Simple logger"""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
    
    def write(self, msg: str):
        """Write log message"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {msg}\n")
        except Exception:
            pass


class URLEntryDialog:
    """Dialog for entering URL name and address"""
    
    def __init__(self, parent, title: str, name: str = '', url: str = ''):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry('600x150')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Name
        tk.Label(self.dialog, text='Name:').grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.name_entry = tk.Entry(self.dialog, width=60)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.name_entry.insert(0, name)
        
        # URL
        tk.Label(self.dialog, text='URL:').grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.url_entry = tk.Entry(self.dialog, width=60)
        self.url_entry.grid(row=1, column=1, padx=10, pady=10)
        self.url_entry.insert(0, url)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(btn_frame, text='OK', command=self.ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text='Cancel', command=self.cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        self.name_entry.focus()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def ok(self):
        """OK button"""
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if not name or not url:
            messagebox.showwarning('Invalid input', 'Both name and URL are required')
            return
        
        self.result = (name, url)
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel button"""
        self.result = None
        self.dialog.destroy()


class CustomURLDialog:
    """Dialog for managing custom URLs"""
    
    def __init__(self, parent, custom_urls: Dict[str, str]):
        self.result = None
        self.custom_urls = custom_urls.copy()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Manage Custom URLs')
        self.dialog.geometry('700x450')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Instructions
        instructions = tk.Label(
            self.dialog,
            text='Add custom URLs here. You can use them in "Open Multiple URLs" section.',
            font=('Segoe UI', 9),
            fg='#666'
        )
        instructions.pack(padx=10, pady=(10, 5))
        
        # List frame
        list_frame = tk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Segoe UI', 9))
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Double-click to edit
        self.listbox.bind('<Double-Button-1>', lambda e: self.edit_url())
        
        # Populate listbox
        self.refresh_list()
        
        # Button frame
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        tk.Button(btn_frame, text='Add', command=self.add_url, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text='Edit', command=self.edit_url, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text='Delete', command=self.delete_url, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text='OK', command=self.ok, width=10).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text='Cancel', command=self.cancel, width=10).pack(side=tk.RIGHT, padx=5)
    
    def refresh_list(self):
        """Refresh URL list"""
        self.listbox.delete(0, tk.END)
        for name, url in sorted(self.custom_urls.items()):
            # Truncate long URLs for display
            display_url = url if len(url) <= 80 else url[:77] + '...'
            self.listbox.insert(tk.END, f"{name}: {display_url}")
    
    def add_url(self):
        """Add new URL"""
        dialog = URLEntryDialog(self.dialog, 'Add Custom URL')
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            name, url = dialog.result
            if name and url:
                self.custom_urls[name] = url
                self.refresh_list()
    
    def edit_url(self):
        """Edit selected URL"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo('No selection', 'Select a URL to edit')
            return
        
        text = self.listbox.get(selection[0])
        name = text.split(':', 1)[0].strip()
        url = self.custom_urls.get(name, '')
        
        dialog = URLEntryDialog(self.dialog, 'Edit Custom URL', name, url)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            new_name, new_url = dialog.result
            if new_name and new_url:
                if new_name != name and name in self.custom_urls:
                    del self.custom_urls[name]
                self.custom_urls[new_name] = new_url
                self.refresh_list()
    
    def delete_url(self):
        """Delete selected URL"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo('No selection', 'Select a URL to delete')
            return
        
        text = self.listbox.get(selection[0])
        name = text.split(':', 1)[0].strip()
        
        if messagebox.askyesno('Confirm', f'Delete "{name}"?'):
            if name in self.custom_urls:
                del self.custom_urls[name]
                self.refresh_list()
    
    def ok(self):
        """OK button"""
        self.result = self.custom_urls
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel button"""
        self.result = None
        self.dialog.destroy()


class ProfileInfoDialog:
    """Dialog showing profile information"""
    
    def __init__(self, parent, email: str):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f'Profile Info: {email}')
        self.dialog.geometry('500x300')
        self.dialog.transient(parent)
        
        info = ChromeProfileManager.get_profile_info(email)
        
        if not info:
            tk.Label(self.dialog, text='Profile information not available').pack(pady=20)
        else:
            frame = tk.Frame(self.dialog)
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            row = 0
            for key, value in info.items():
                tk.Label(frame, text=f'{key.replace("_", " ").title()}:', font=('Segoe UI', 10, 'bold')).grid(
                    row=row, column=0, sticky=tk.W, pady=5
                )
                tk.Label(frame, text=str(value), font=('Segoe UI', 10)).grid(
                    row=row, column=1, sticky=tk.W, padx=10, pady=5
                )
                row += 1
        
        tk.Button(self.dialog, text='Close', command=self.dialog.destroy).pack(pady=10)


class UpdateDialog:
    """Dialog for showing update information"""
    
    def __init__(self, parent, update_info: Dict):
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Update Available')
        self.dialog.geometry('500x400')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Header
        header = tk.Label(
            self.dialog,
            text=f'🎉 New Version Available: v{update_info["version"]}',
            font=('Segoe UI', 12, 'bold'),
            fg='#00AEDB'
        )
        header.pack(pady=20)
        
        # Current version
        current = tk.Label(
            self.dialog,
            text=f'Current version: v{VERSION}',
            font=('Segoe UI', 10)
        )
        current.pack()
        
        # Changelog
        changelog_label = tk.Label(
            self.dialog,
            text='What\'s New:',
            font=('Segoe UI', 10, 'bold')
        )
        changelog_label.pack(pady=(20, 5))
        
        # Changelog text
        changelog_frame = tk.Frame(self.dialog)
        changelog_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        scrollbar = tk.Scrollbar(changelog_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        changelog_text = tk.Text(
            changelog_frame,
            height=10,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 9)
        )
        changelog_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=changelog_text.yview)
        
        for item in update_info.get('changelog', []):
            changelog_text.insert(tk.END, f'• {item}\n')
        
        changelog_text.config(state=tk.DISABLED)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=20)
        
        update_btn = tk.Button(
            btn_frame,
            text='Update Now',
            command=self.update,
            width=15,
            bg='#00AEDB',
            fg='white',
            font=('Segoe UI', 10, 'bold')
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        later_btn = tk.Button(
            btn_frame,
            text='Later',
            command=self.later,
            width=15
        )
        later_btn.pack(side=tk.LEFT, padx=5)
    
    def update(self):
        """Update button"""
        self.result = True
        self.dialog.destroy()
    
    def later(self):
        """Later button"""
        self.result = False
        self.dialog.destroy()


# Continue with ChromeLauncherUI class...
# (Due to length, I'll create this in a second part)




class ChromeLauncherUI:
    """Main UI for Chrome Launcher"""
    
    def __init__(self, cli_args=None):
        self.cli_args = cli_args
        
        # Setup paths
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, 'ChromeLauncherUI.cfg')
        self.log_path = os.path.join(self.script_dir, 'ChromeLauncherUI.log')
        
        # Initialize components
        self.config = ChromeLauncherConfig(self.config_path)
        self.config.load()
        self.logger = Logger(self.log_path)
        self.emails = ChromeProfileManager.get_emails_from_local_state()
        self.updater = AutoUpdater(VERSION, UPDATE_CHECK_URL, DOWNLOAD_URL)
        
        # Default URLs
        self.default_urls = {
            '1': 'https://www.youtube.com/paid_memberships?ybp=mAEK',
            '2': 'https://myaccount.google.com/family/details',
            '3': 'https://www.netflix.com/account',
            '4': 'https://mail.google.com/mail/u/0/?tab=rm&ogbl#inbox',
            '5': 'https://www.apps.disneyplus.com/th/home',
            '6': 'primevideo.com/-/th/signup',
            # '7': 'https://media.tenor.com/QpIBfnIvRLcAAAAj/i-love-you-love.gif'
            '7': 'https://auth.hbomax.com/login'
        }
        
        # Handle CLI mode
        if cli_args and cli_args.email:
            self.launch_from_cli()
            return
        
        # Create UI
        self.root = tk.Tk()
        self.root.title(f'Chrome Profile Launcher v{VERSION}')
        
        # Apply theme
        self.apply_theme(self.config.theme)
        
        # Setup window
        self.setup_window()
        
        # Create menu
        self.create_menu()
        
        # Create widgets
        self.create_widgets()
        
        # Bind events
        self.bind_events()
        
        # Auto-search timer
        self.search_timer = None
        
        # Populate initial data
        self.populate_fav_list()
        self.update_quick_launch_buttons()
        
        # Check for updates (only if URLs are configured)
        if self.config.auto_update_check == '1' and UPDATE_CHECK_URL and UPDATE_CHECK_URL.strip():
            self.root.after(1000, self.check_for_updates_async)
    
    def check_for_updates_async(self):
        """Check for updates asynchronously"""
        try:
            update_info = self.updater.check_for_updates()
            
            if update_info:
                self.show_update_dialog(update_info)
            
            # Update last check time
            self.config.last_update_check = datetime.now().isoformat()
            self.config.save()
        except Exception as e:
            self.logger.write(f'Update check failed: {str(e)}')
    
    def show_update_dialog(self, update_info: Dict):
        """Show update dialog"""
        dialog = UpdateDialog(self.root, update_info)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.perform_update(update_info)
    
    def perform_update(self, update_info: Dict):
        """Perform the update"""
        try:
            # Show progress
            self.status_label.config(text='Downloading update...')
            self.root.update()
            
            # Download update
            download_url = update_info.get('download_url', DOWNLOAD_URL)
            temp_path = self.updater.download_update(download_url)
            
            if not temp_path:
                messagebox.showerror('Update Failed', 'Failed to download update')
                self.status_label.config(text='Update failed')
                return
            
            self.status_label.config(text='Installing update...')
            self.root.update()
            
            # Apply update
            current_file = os.path.abspath(__file__)
            success = self.updater.apply_update(temp_path, current_file)
            
            # Clean up
            try:
                os.remove(temp_path)
            except Exception:
                pass
            
            if success:
                messagebox.showinfo(
                    'Update Complete',
                    f'Successfully updated to v{update_info["version"]}!\n\n'
                    'Please restart the application.'
                )
                self.on_exit()
            else:
                messagebox.showerror('Update Failed', 'Failed to install update')
                self.status_label.config(text='Update failed')
        
        except Exception as e:
            messagebox.showerror('Update Error', f'Update error: {str(e)}')
            self.status_label.config(text='Update error')
            self.logger.write(f'Update error: {str(e)}')
    
    def manual_check_update(self):
        """Manually check for updates"""
        try:
            self.status_label.config(text='Checking for updates...')
        except Exception:
            pass
        
        try:
            self.root.update()
        except Exception:
            pass
        
        try:
            update_info = self.updater.check_for_updates()
            
            if update_info:
                self.show_update_dialog(update_info)
            else:
                messagebox.showinfo(
                    'No Updates',
                    f'You are running the latest version (v{VERSION})'
                )
            
            try:
                self.status_label.config(text='')
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('Update Check Failed', 'Could not check for updates.\nPlease check your internet connection.')
            try:
                self.status_label.config(text='')
            except Exception:
                pass
            self.logger.write(f'Manual update check failed: {str(e)}')
    
    def launch_from_cli(self):
        """Launch Chrome from command line"""
        email = self.cli_args.email
        incognito = self.cli_args.incognito
        url = self.cli_args.url
        
        if email not in self.emails:
            print(f"Error: Profile '{email}' not found")
            sys.exit(1)
        
        chrome = ChromePathFinder.get_chrome_path_auto(
            self.config.channel,
            self.config.custom_chrome
        )
        
        if not chrome:
            print("Error: Chrome not found")
            sys.exit(1)
        
        profile = ChromeProfileManager.get_profile_directory_by_email(email)
        
        if not profile:
            print(f"Error: Profile directory not found for '{email}'")
            sys.exit(1)
        
        # Build arguments
        args = [chrome, f'--profile-directory={profile}']
        
        if incognito:
            args.append('--incognito')
        
        if url:
            args.append(url)
        else:
            choice = self.config.url_choice
            if self.config.use_perurl == '1' and email in self.config.per_url:
                choice = self.config.per_url[email]
            args.append(self.default_urls.get(choice, self.default_urls['1']))
        
        # Launch without CMD window on Windows
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(args, startupinfo=startupinfo)
        else:
            subprocess.Popen(args)
        
        print(f"Launched Chrome for {email}")
        sys.exit(0)
    
    def apply_theme(self, theme: str):
        """Apply color theme"""
        if theme == 'Light':
            self.bg = '#F5F5F5'
            self.panel_bg = '#EBEBEB'
            self.accent = '#0078D7'
            self.text = '#1E1E1E'
            self.muted = '#646464'
            self.input_bg = '#FFFFFF'
            self.input_fg = '#000000'
        else:
            self.bg = '#14171C'
            self.panel_bg = '#1E2228'
            self.accent = '#00AEDB'
            self.text = '#FFFFFF'
            self.muted = '#A0A0A0'
            self.input_bg = '#2D323A'
            self.input_fg = '#FFFFFF'
    
    def setup_window(self):
        """Setup window size and position"""
        width = 900
        height = 750
        
        if self.config.window_w and self.config.window_h:
            try:
                width = int(self.config.window_w)
                height = int(self.config.window_h)
                x = int(self.config.window_x)
                y = int(self.config.window_y)
                self.root.geometry(f"{width}x{height}+{x}+{y}")
            except Exception:
                self.root.geometry(f"{width}x{height}")
        else:
            self.root.geometry(f"{width}x{height}")
        
        self.root.configure(bg=self.bg)
        self.root.resizable(True, True)
    
    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Export Config...', command=self.export_config)
        file_menu.add_command(label='Import Config...', command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.on_exit)
        
        # Tools menu
        tools_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Tools', menu=tools_menu)
        tools_menu.add_command(label='Manage Custom URLs...', command=self.manage_custom_urls)
        tools_menu.add_command(label='Clear Search History', command=self.clear_search_history)
        tools_menu.add_separator()
        tools_menu.add_command(label='Refresh Profiles', command=self.refresh_profiles)
        tools_menu.add_separator()
        tools_menu.add_command(label='Check for Updates...', command=self.manual_check_update)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='Keyboard Shortcuts', command=self.show_shortcuts)
        help_menu.add_command(label='About', command=self.show_about)
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.bg)
        header_frame.pack(fill=tk.X, padx=20, pady=(18, 0))
        
        title_label = tk.Label(
            header_frame,
            text=f'Chrome Profile Launcher ULTRA v{VERSION}',
            font=('Segoe UI', 12, 'bold'),
            fg=self.accent,
            bg=self.bg
        )
        title_label.pack(side=tk.LEFT)
        
        # Update button
        update_btn = tk.Button(
            header_frame,
            text='🔄 Check Updates',
            font=('Segoe UI', 9),
            fg=self.text,
            bg=self.accent,
            command=self.manual_check_update
        )
        update_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Theme selector
        theme_label = tk.Label(
            header_frame,
            text='Theme:',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.bg
        )
        theme_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.theme_var = tk.StringVar(value=self.config.theme)
        theme_combo = ttk.Combobox(
            header_frame,
            textvariable=self.theme_var,
            values=['Dark', 'Light'],
            state='readonly',
            width=10
        )
        theme_combo.pack(side=tk.RIGHT)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_changed)
        
        # Channel selector
        channel_label = tk.Label(
            header_frame,
            text='Channel:',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.bg
        )
        channel_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.channel_var = tk.StringVar(value=self.config.channel)
        channel_combo = ttk.Combobox(
            header_frame,
            textvariable=self.channel_var,
            values=['Stable', 'Beta', 'Dev', 'Canary'],
            state='readonly',
            width=10
        )
        channel_combo.pack(side=tk.RIGHT)
        
        # Subtitle
        subtitle_label = tk.Label(
            self.root,
            text='Emails sorted by number (ascending). Enter number/email, then Search.',
            font=('Segoe UI', 9),
            fg=self.muted,
            bg=self.bg
        )
        subtitle_label.pack(anchor=tk.W, padx=22, pady=(5, 0))
        
        # Options frame
        options_frame = tk.Frame(self.root, bg=self.bg)
        options_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        custom_chrome_btn = tk.Button(
            options_frame,
            text='Custom Chrome...',
            font=('Segoe UI', 9),
            fg=self.text,
            bg=self.accent,
            command=self.pick_custom_chrome
        )
        custom_chrome_btn.pack(side=tk.LEFT)
        
        # Incognito mode checkbox
        self.incognito_var = tk.BooleanVar()
        incognito_cb = tk.Checkbutton(
            options_frame,
            text='🕵️ Incognito Mode',
            variable=self.incognito_var,
            fg=self.text,
            bg=self.bg,
            selectcolor=self.bg,
            font=('Segoe UI', 9)
        )
        incognito_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # Quick Launch Buttons Frame
        quick_frame = tk.LabelFrame(
            self.root,
            text='⚡ Quick Launch (Top 5 Most Used)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.panel_bg
        )
        quick_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.quick_buttons_frame = tk.Frame(quick_frame, bg=self.panel_bg)
        self.quick_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # URL Group with Multiple URLs
        url_frame = tk.LabelFrame(
            self.root,
            text='URLs - Select profile below, check URLs to open, then click "Open Multiple URLs"',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.panel_bg
        )
        url_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        # Create checkboxes for all URLs
        self.url_vars = {}
        urls_to_show = [
            ('1', 'YouTube Premium | ดูวันตัดบัตร'),
            ('2', 'YouTube Family | เพิ่ม/ลบ สมาชิก'),
            ('3', 'Netflix | เพิ่ม/ลบ สมาชิก'),
            ('4', 'Gmail | ดูเมล'),
            ('5', 'Disney+ | เพิ่ม/ลบ สมาชิก'),
            ('6', 'Prime Video | เพิ่ม/ลบ สมาชิก'),
            ('7', 'HBO Max | เพิ่ม/ลบ สมาชิก')
        ]
        
        # First row
        row1_frame = tk.Frame(url_frame, bg=self.panel_bg)
        row1_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        for i, (key, label) in enumerate(urls_to_show[:4]):
            var = tk.BooleanVar()
            self.url_vars[key] = var
            cb = tk.Checkbutton(
                row1_frame,
                text=label,
                variable=var,
                fg=self.text,
                bg=self.panel_bg,
                selectcolor=self.panel_bg
            )
            cb.pack(side=tk.LEFT, padx=(0, 15))
        
        # Second row
        row2_frame = tk.Frame(url_frame, bg=self.panel_bg)
        row2_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        for i, (key, label) in enumerate(urls_to_show[4:]):
            var = tk.BooleanVar()
            self.url_vars[key] = var
            cb = tk.Checkbutton(
                row2_frame,
                text=label,
                variable=var,
                fg=self.text,
                bg=self.panel_bg,
                selectcolor=self.panel_bg
            )
            cb.pack(side=tk.LEFT, padx=(0, 15))
        
        # Buttons frame
        btn_frame_url = tk.Frame(url_frame, bg=self.panel_bg)
        btn_frame_url.pack(fill=tk.X, padx=20, pady=(5, 10))
        
        open_multi_btn = tk.Button(
            btn_frame_url,
            text='Open Multiple URLs',
            font=('Segoe UI', 10, 'bold'),
            fg=self.text,
            bg=self.accent,
            command=self.open_multiple_urls
        )
        open_multi_btn.pack(side=tk.LEFT)
        
        manage_urls_btn = tk.Button(
            btn_frame_url,
            text='Manage Custom URLs...',
            font=('Segoe UI', 9),
            fg=self.text,
            bg=self.accent,
            command=self.manage_custom_urls
        )
        manage_urls_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.url_status_label = tk.Label(
            btn_frame_url,
            text='',
            font=('Segoe UI', 9),
            fg=self.muted,
            bg=self.panel_bg
        )
        self.url_status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Main panel
        main_panel = tk.Frame(self.root, bg=self.panel_bg)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        # Input section
        input_frame = tk.Frame(main_panel, bg=self.panel_bg)
        input_frame.pack(fill=tk.X, padx=16, pady=(16, 0))
        
        input_label = tk.Label(
            input_frame,
            text='Number or Email:',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.panel_bg
        )
        input_label.pack(side=tk.LEFT)
        
        # Use Combobox for search history
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Combobox(
            input_frame,
            textvariable=self.input_var,
            font=('Segoe UI', 10),
            width=30,
            values=self.config.search_history
        )
        self.input_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.input_entry.bind('<KeyRelease>', self.on_input_changed)
        self.input_entry.bind('<Return>', lambda e: self.do_search())
        self.input_entry.bind('<Control-a>', self.select_all_input)
        
        self.regex_var = tk.BooleanVar()
        regex_cb = tk.Checkbutton(
            input_frame,
            text='Use Regex',
            variable=self.regex_var,
            fg=self.text,
            bg=self.panel_bg,
            selectcolor=self.panel_bg
        )
        regex_cb.pack(side=tk.LEFT, padx=(10, 0))
        
        search_btn = tk.Button(
            input_frame,
            text='Search (Enter)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.do_search
        )
        search_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        refresh_btn = tk.Button(
            input_frame,
            text='Refresh (F5)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.refresh_profiles
        )
        refresh_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Lists section
        lists_frame = tk.Frame(main_panel, bg=self.panel_bg)
        lists_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(16, 0))
        
        # Favorites/Recents list
        fav_frame = tk.Frame(lists_frame, bg=self.panel_bg)
        fav_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        fav_label = tk.Label(
            fav_frame,
            text='Favorites / Recents (sorted by number)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.panel_bg
        )
        fav_label.pack(anchor=tk.W)
        
        fav_scroll = tk.Scrollbar(fav_frame)
        fav_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.fav_listbox = tk.Listbox(
            fav_frame,
            font=('Segoe UI', 10),
            fg=self.input_fg,
            bg=self.input_bg,
            yscrollcommand=fav_scroll.set
        )
        self.fav_listbox.pack(fill=tk.BOTH, expand=True)
        fav_scroll.config(command=self.fav_listbox.yview)
        self.fav_listbox.bind('<Double-Button-1>', self.on_fav_double_click)
        self.fav_listbox.bind('<Button-3>', self.show_context_menu)
        
        # Matches list
        matches_frame = tk.Frame(lists_frame, bg=self.panel_bg)
        matches_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        matches_label = tk.Label(
            matches_frame,
            text='Matches (sorted by number)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.panel_bg
        )
        matches_label.pack(anchor=tk.W)
        
        matches_scroll = tk.Scrollbar(matches_frame)
        matches_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.matches_listbox = tk.Listbox(
            matches_frame,
            font=('Segoe UI', 10),
            fg=self.input_fg,
            bg=self.input_bg,
            yscrollcommand=matches_scroll.set
        )
        self.matches_listbox.pack(fill=tk.BOTH, expand=True)
        matches_scroll.config(command=self.matches_listbox.yview)
        self.matches_listbox.bind('<Return>', lambda e: self.open_selected())
        self.matches_listbox.bind('<Button-3>', self.show_context_menu)
        
        # Action buttons
        action_frame = tk.Frame(main_panel, bg=self.panel_bg)
        action_frame.pack(fill=tk.X, padx=16, pady=(10, 0))
        
        open_btn = tk.Button(
            action_frame,
            text='Open (Ctrl+O)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.open_selected
        )
        open_btn.pack(side=tk.LEFT)
        
        fav_btn = tk.Button(
            action_frame,
            text='★ Fav',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.toggle_favorite
        )
        fav_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        info_btn = tk.Button(
            action_frame,
            text='ℹ️ Info',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.show_profile_info
        )
        info_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        quick_btn = tk.Button(
            action_frame,
            text='Quick Launch Last',
            font=('Segoe UI', 10),
            fg=self.text,
            bg=self.accent,
            command=self.quick_launch_last
        )
        quick_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        exit_btn = tk.Button(
            action_frame,
            text='Exit (Esc)',
            font=('Segoe UI', 10),
            fg=self.text,
            bg='#781E1E',
            command=self.on_exit
        )
        exit_btn.pack(side=tk.RIGHT)
        
        # Status label
        self.status_label = tk.Label(
            main_panel,
            text='',
            font=('Segoe UI', 9),
            fg=self.muted,
            bg=self.panel_bg
        )
        self.status_label.pack(anchor=tk.W, padx=16, pady=(10, 10))
        
        # Footer
        footer_label = tk.Label(
            self.root,
            text='Shortcuts: Ctrl+O=Open, Ctrl+F=Focus, Ctrl+I=Incognito Toggle, F5=Refresh, Esc=Exit',
            font=('Segoe UI', 9),
            fg=self.muted,
            bg=self.bg
        )
        footer_label.pack(anchor=tk.W, padx=20, pady=(10, 10))
        
        # Context menu
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label='Open', command=self.open_selected)
        self.context_menu.add_command(label='Open in Incognito', command=self.open_selected_incognito)
        self.context_menu.add_separator()
        self.context_menu.add_command(label='Toggle Favorite', command=self.toggle_favorite)
        self.context_menu.add_command(label='Show Info', command=self.show_profile_info)
    
    def bind_events(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.open_selected())
        self.root.bind('<Control-f>', lambda e: self.input_entry.focus())
        self.root.bind('<Control-i>', lambda e: self.incognito_var.set(not self.incognito_var.get()))
        self.root.bind('<F5>', lambda e: self.refresh_profiles())
        self.root.bind('<Escape>', lambda e: self.on_exit())
        
        # Arrow key navigation
        self.root.bind('<Up>', self.navigate_up)
        self.root.bind('<Down>', self.navigate_down)
        
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
    
    def navigate_up(self, event):
        """Navigate up in lists"""
        if self.matches_listbox.size() > 0:
            current = self.matches_listbox.curselection()
            if current:
                idx = max(0, current[0] - 1)
                self.matches_listbox.selection_clear(0, tk.END)
                self.matches_listbox.selection_set(idx)
                self.matches_listbox.see(idx)
    
    def navigate_down(self, event):
        """Navigate down in lists"""
        if self.matches_listbox.size() > 0:
            current = self.matches_listbox.curselection()
            if current:
                idx = min(self.matches_listbox.size() - 1, current[0] + 1)
            else:
                idx = 0
            self.matches_listbox.selection_clear(0, tk.END)
            self.matches_listbox.selection_set(idx)
            self.matches_listbox.see(idx)
    
    def update_quick_launch_buttons(self):
        """Update quick launch buttons"""
        for widget in self.quick_buttons_frame.winfo_children():
            widget.destroy()
        
        usage_list = [(email, count) for email, count in self.config.usage.items() if email in self.emails]
        usage_list.sort(key=lambda x: x[1], reverse=True)
        top_profiles = [email for email, _ in usage_list[:5]]
        
        if not top_profiles:
            tk.Label(
                self.quick_buttons_frame,
                text='No profiles used yet. Start using profiles to see quick launch buttons here.',
                font=('Segoe UI', 9),
                fg=self.muted,
                bg=self.panel_bg
            ).pack()
            return
        
        for email in top_profiles:
            count = self.config.usage.get(email, 0)
            btn = tk.Button(
                self.quick_buttons_frame,
                text=f'{email} (x{count})',
                font=('Segoe UI', 9),
                fg=self.text,
                bg=self.accent,
                command=lambda e=email: self.open_for(e)
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def populate_fav_list(self):
        """Populate favorites and recents list"""
        self.fav_listbox.delete(0, tk.END)
        
        # Sort favorites by number
        favorites = sort_emails_by_number(list(set(self.config.favorites)))
        for email in favorites:
            count = self.config.usage.get(email, 0)
            self.fav_listbox.insert(tk.END, f"★ {email}  (x{count})")
        
        # Sort recents by number
        recents = [r for r in self.config.recents if r not in favorites]
        recents = sort_emails_by_number(recents)
        for email in recents:
            count = self.config.usage.get(email, 0)
            self.fav_listbox.insert(tk.END, f"⏱ {email}  (x{count})")
    
    def populate_matches(self, matches: List[str]):
        """Populate matches list (already sorted)"""
        self.matches_listbox.delete(0, tk.END)
        # Sort matches by number
        sorted_matches = sort_emails_by_number(matches)
        for match in sorted_matches:
            self.matches_listbox.insert(tk.END, match)
        
        if len(sorted_matches) > 0:
            self.matches_listbox.selection_set(0)
    
    def normalize_digits(self, s: str) -> Tuple[str, str]:
        """Extract and normalize digits"""
        if not s or not s.strip():
            return ('', '')
        
        digits = ''.join(c for c in s if c.isdigit())
        normalized = digits.lstrip('0')
        if not normalized:
            normalized = '0'
        
        return (digits, normalized)
    
    def do_search(self):
        """Perform search"""
        key = self.input_var.get().strip()
        self.status_label.config(text='')
        self.matches_listbox.delete(0, tk.END)
        
        if not key:
            self.status_label.config(text='Enter a number or email first.')
            return
        
        self.config.add_search_history(key)
        self.input_entry['values'] = self.config.search_history
        
        if self.regex_var.get():
            try:
                pattern = re.compile(key)
                matches = [e for e in self.emails if pattern.search(e)]
            except re.error:
                self.status_label.config(text=f'Invalid regex: {key}')
                return
            
            if not matches:
                self.status_label.config(text='No match (regex).')
                return
            
            self.populate_matches(matches)
            return
        
        if '@' in key:
            if key in self.emails:
                self.populate_matches([key])
                return
            
            matches = [e for e in self.emails if key.lower() in e.lower()]
            if not matches:
                self.status_label.config(text='No emails contain that text.')
                return
            
            self.populate_matches(matches)
            return
        
        digits, normalized = self.normalize_digits(key)
        if not digits:
            self.status_label.config(text='No digits found in input.')
            return
        
        matches = [e for e in self.emails if digits in e or normalized in e]
        matches = list(set(matches))
        
        if not matches:
            self.status_label.config(text=f'No emails contain: {digits} (or {normalized})')
            return
        
        self.populate_matches(matches)
    
    def get_selected_email_from_fav(self) -> Optional[str]:
        """Get selected email from favorites list"""
        selection = self.fav_listbox.curselection()
        if not selection:
            return None
        
        text = self.fav_listbox.get(selection[0])
        email = re.sub(r'^[^\s]+\s+', '', text)
        email = re.sub(r'\s+\(x\d+\)\s*$', '', email)
        return email
    
    def get_selected_email(self) -> Optional[str]:
        """Get currently selected email"""
        selection = self.matches_listbox.curselection()
        if selection:
            return self.matches_listbox.get(selection[0])
        
        return self.get_selected_email_from_fav()
    
    def toggle_favorite(self):
        """Toggle favorite status"""
        email = self.get_selected_email()
        
        if not email:
            return
        
        if email in self.config.favorites:
            self.config.favorites = [f for f in self.config.favorites if f != email]
            self.status_label.config(text=f'Removed from favorites: {email}')
        else:
            self.config.favorites.append(email)
            self.config.favorites = list(set(self.config.favorites))
            self.status_label.config(text=f'Added to favorites: {email}')
        
        self.config.save()
        self.populate_fav_list()
    
    def add_recent(self, email: str):
        """Add email to recents"""
        if not email:
            return
        
        recents = [r for r in self.config.recents if r != email]
        recents.insert(0, email)
        self.config.recents = recents[:10]
    
    def bump_usage(self, email: str):
        """Increment usage count"""
        if email not in self.config.usage:
            self.config.usage[email] = 0
        self.config.usage[email] += 1
    
    def open_for(self, email: str, extra_urls: List[str] = None, incognito: bool = None):
        """Open Chrome for specific email"""
        if extra_urls is None:
            extra_urls = []
        
        if incognito is None:
            incognito = self.incognito_var.get()
        
        try:
            if not email:
                return
            
            chrome = ChromePathFinder.get_chrome_path_auto(
                self.channel_var.get(),
                self.config.custom_chrome
            )
            
            if not chrome:
                messagebox.showerror(
                    'Chrome missing',
                    'Chrome not found (any channel).\n\n'
                    'Please install Google Chrome or use "Custom Chrome..." to select the executable.'
                )
                return
            
            profile = ChromeProfileManager.get_profile_directory_by_email(email)
            
            if not profile:
                messagebox.showwarning(
                    'Profile missing',
                    f'Profile not found in Chrome Local State.\n\n'
                    f'Please log in to "{email}" in Chrome on this machine first.'
                )
                return
            
            # Get URLs - if extra_urls is provided, use only those
            if not extra_urls:
                # Use default URL
                choice = self.config.url_choice
                if self.config.use_perurl == '1' and email in self.config.per_url:
                    choice = self.config.per_url[email]
                extra_urls = [self.default_urls.get(choice, self.default_urls['1'])]
            
            # Launch Chrome for each URL
            for url in extra_urls:
                args = [chrome, f'--profile-directory={profile}']
                
                if incognito:
                    args.append('--incognito')
                
                args.append(url)
                
                self.logger.write(
                    f'Open: email={email}, profile={profile}, '
                    f'channel={self.channel_var.get()}, incognito={incognito}, url={url}'
                )
                
                # Hide CMD window on Windows
                if sys.platform == 'win32':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.Popen(args, startupinfo=startupinfo)
                else:
                    subprocess.Popen(args)
            
            self.config.last_email = email
            self.add_recent(email)
            self.bump_usage(email)
            self.config.save()
            
            mode = ' (Incognito)' if incognito else ''
            self.status_label.config(text=f'Opened {len(extra_urls)} tab(s) for {email}{mode}.')
            self.populate_fav_list()
            self.update_quick_launch_buttons()
            
        except Exception as e:
            messagebox.showerror('Error', f'Error: {str(e)}')
            self.logger.write(f'Error Opening: {str(e)}')
    
    def open_selected(self):
        """Open Chrome for selected email"""
        email = self.get_selected_email()
        
        if not email:
            messagebox.showinfo('No selection', 'Select an email first.')
            return
        
        self.open_for(email)
    
    def open_selected_incognito(self):
        """Open in incognito"""
        email = self.get_selected_email()
        
        if not email:
            messagebox.showinfo('No selection', 'Select an email first.')
            return
        
        self.open_for(email, incognito=True)
    
    def on_fav_double_click(self, event):
        """Handle double-click"""
        email = self.get_selected_email_from_fav()
        if email:
            self.open_for(email)
    
    def quick_launch_last(self):
        """Quick launch last"""
        if self.config.last_email:
            self.open_for(self.config.last_email)
        else:
            self.status_label.config(text='No last email recorded yet.')
    
    def open_multiple_urls(self):
        """Open multiple URLs"""
        email = self.get_selected_email()
        
        if not email:
            messagebox.showinfo('No selection', 'Select an email first.')
            return
        
        # Collect selected URLs
        urls = []
        for key, var in self.url_vars.items():
            if var.get():
                urls.append(self.default_urls[key])
        
        if not urls:
            messagebox.showinfo('No URLs selected', 'Please check at least one URL to open.')
            return
        
        self.open_for(email, extra_urls=urls)
    
    def refresh_profiles(self):
        """Refresh profiles"""
        self.emails = ChromeProfileManager.get_emails_from_local_state()
        self.status_label.config(text=f'Profiles refreshed: {len(self.emails)} found (sorted by number).')
        self.populate_fav_list()
        
        if self.input_var.get():
            self.do_search()
    
    def pick_custom_chrome(self):
        """Pick custom Chrome"""
        if sys.platform == 'win32':
            filetypes = [('Chrome', 'chrome.exe'), ('All files', '*.*')]
        else:
            filetypes = [('All files', '*')]
        
        filename = filedialog.askopenfilename(
            title='Select Chrome executable',
            filetypes=filetypes
        )
        
        if filename:
            self.config.custom_chrome = filename
            self.config.save()
            self.status_label.config(text='Custom Chrome set.')
    
    def on_theme_changed(self, event):
        """Handle theme change"""
        messagebox.showinfo(
            'Theme Changed',
            'Please restart the application for theme changes to take effect.'
        )
    
    def select_all_input(self, event):
        """Select all text"""
        self.input_entry.select_range(0, tk.END)
        return 'break'
    
    def on_input_changed(self, event):
        """Handle input change"""
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        
        self.search_timer = self.root.after(250, self.do_search)
    
    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_profile_info(self):
        """Show profile info"""
        email = self.get_selected_email()
        
        if not email:
            messagebox.showinfo('No selection', 'Select a profile first.')
            return
        
        ProfileInfoDialog(self.root, email)
    
    def manage_custom_urls(self):
        """Manage custom URLs"""
        dialog = CustomURLDialog(self.root, self.config.custom_urls)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result is not None:
            self.config.custom_urls = dialog.result
            self.config.save()
            self.status_label.config(text=f'Custom URLs updated. Total: {len(self.config.custom_urls)}')
    
    def clear_search_history(self):
        """Clear search history"""
        if messagebox.askyesno('Confirm', 'Clear all search history?'):
            self.config.search_history = []
            self.config.save()
            self.input_entry['values'] = []
            self.status_label.config(text='Search history cleared.')
    
    def export_config(self):
        """Export config"""
        try:
            filename = filedialog.asksaveasfilename(
                title='Export Config',
                defaultextension='.cfg',
                filetypes=[('Config files', '*.cfg'), ('All files', '*.*')],
                initialfile='ChromeLauncherUI.cfg'
            )
            
            if filename:
                import shutil
                shutil.copy(self.config_path, filename)
                self.status_label.config(text='Config exported.')
                messagebox.showinfo('Success', f'Configuration exported to:\n{filename}')
        except Exception as e:
            messagebox.showerror('Error', f'Export failed:\n{str(e)}')
    
    def import_config(self):
        """Import config"""
        try:
            filename = filedialog.askopenfilename(
                title='Import Config',
                filetypes=[('Config files', '*.cfg'), ('All files', '*.*')]
            )
            
            if filename:
                import shutil
                shutil.copy(filename, self.config_path)
                self.config.load()
                
                self.channel_var.set(self.config.channel)
                self.theme_var.set(self.config.theme)
                self.input_entry['values'] = self.config.search_history
                
                self.populate_fav_list()
                self.update_quick_launch_buttons()
                self.status_label.config(text='Config imported.')
                messagebox.showinfo('Success', 'Configuration imported successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Import failed:\n{str(e)}')
    
    def show_shortcuts(self):
        """Show shortcuts"""
        shortcuts = """
Keyboard Shortcuts:

Ctrl+O      - Open Chrome for selected profile
Ctrl+F      - Focus search box
Ctrl+I      - Toggle Incognito mode
F5          - Refresh profiles
Esc         - Exit application
Enter       - Search / Open selected
Up/Down     - Navigate matches list
        """
        messagebox.showinfo('Keyboard Shortcuts', shortcuts.strip())
    
    def show_about(self):
        """Show about"""
        about_text = f"""
Chrome Profile Launcher ULTRA
Version {VERSION}

A powerful tool for managing and launching
Chrome profiles with multiple URLs.

Features:
• Email sorting by number (ascending)
• Automatic update checking
• Quick profile search and launch
• Multiple URL opening
• Custom URL management
• Incognito mode support
• Import/Export configuration
• Cross-platform support

© 2024 - Open Source
        """
        messagebox.showinfo('About', about_text.strip())
    
    def on_exit(self):
        """Exit"""
        self.on_closing()
    
    def on_closing(self):
        """Handle closing"""
        try:
            self.config.window_x = str(self.root.winfo_x())
            self.config.window_y = str(self.root.winfo_y())
            self.config.window_w = str(self.root.winfo_width())
            self.config.window_h = str(self.root.winfo_height())
            self.config.channel = self.channel_var.get()
            self.config.theme = self.theme_var.get()
            self.config.save()
        except Exception:
            pass
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.input_entry.focus()
        
        if not self.emails:
            messagebox.showinfo(
                'No Profiles',
                'No Chrome profiles found on this machine.\n\n'
                'Please sign in at least one profile in Chrome first.'
            )
        
        self.root.mainloop()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Chrome Profile Launcher ULTRA')
    parser.add_argument('--email', '-e', help='Email of profile to launch')
    parser.add_argument('--url', '-u', help='URL to open')
    parser.add_argument('--incognito', '-i', action='store_true', help='Open in incognito mode')
    
    args = parser.parse_args()
    
    try:
        app = ChromeLauncherUI(cli_args=args)
        if not args.email:
            app.run()
    except Exception as e:
        messagebox.showerror('Fatal', f'UI error: {str(e)}')
        print('Press Enter to exit...')
        input()


if __name__ == '__main__':
    main()

