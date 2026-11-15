import os
import sys
import subprocess
import time
import shutil
import threading
from email.utils import parsedate_to_datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

required_packages = ['requests']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import requests

BASE_KILL_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/kill.txt"
BASE_KEYS_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/keys.txt"
LOCAL_CACHE_FILE = ".key_cache"
TIME_CHECK_FILE = ".last_time"

def self_destruct_and_exit(reason=""):
    print(f"\n\033[1;31m[!] Security Alert: {reason}. ဖိုင်များကို ဖျက်ဆီးနေပါသည်...\033[0m")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(current_dir):
            file_path = os.path.join(current_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception:
                pass
    except Exception:
        pass
    os._exit(0)

def format_time_remaining(seconds):
    if seconds <= 0:
        return "သက်တမ်းကုန်ဆုံးသွားပါပြီ"
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} ရက်")
    if hours > 0 or days > 0:
        parts.append(f"{hours} နာရီ")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes} မိနစ်")
    parts.append(f"{secs} စက္ကန့်")
    return " ".join(parts)

# 💡 Background Thread: ကိရိယာ သုံးနေစဉ်အတွင်း အချိန်ပြည့် စောင့်ကြည့်ပေးမည့်စနစ်
def background_monitor(cached_key, expiry_time):
    while True:
        time.sleep(30) # ప్రతి 30 စက္ကန့်တစ်ကြိမ် စစ်ဆေးမည်
        current_time = int(time.time())
        
        # သက်တမ်းကုန်သွားပါက ချက်ချင်း ဖျက်မည်
        if current_time >= expiry_time:
            print(f"\n\033[1;31m[!] သက်တမ်းကုန်ဆုံးသွားပါပြီ။ ဖိုင်များကို ဖျက်ဆီးနေပါသည်...\033[0m")
            self_destruct_and_exit("Key သက်တမ်း ကုန်ဆုံးသွားပါပြီ")
        
        # အင်တာနက်ရှိလျှင် Kill Switch ကိုပါ အမြဲစစ်မည်
        try:
            r_kill = requests.get(f"{BASE_KILL_URL}?t={current_time}", timeout=3, verify=False)
            content = r_kill.text.strip().upper()
            if "STOP" in content or "OFF" in content or "RUN" not in content:
                print(f"\n\033[1;31m[!] Server မှ အသုံးပြုခွင့် ပိတ်လိုက်ပါပြီ။ ဖိုင်များကို ဖျက်ဆီးနေပါသည်...\033[0m")
                self_destruct_and_exit("Server Access Revoked")
        except Exception:
            pass

def verify_key_and_system():
    local_system_time = int(time.time())
    
    # Anti-Clock Tampering (နာရီနောက်ပြန်ဆုတ်မှု စစ်ဆေးခြင်း)
    if os.path.exists(TIME_CHECK_FILE):
        try:
            with open(TIME_CHECK_FILE, "r") as f:
                last_recorded_time = int(f.read().strip())
            if local_system_time < last_recorded_time:
                self_destruct_and_exit("ဖုန်းနာရီကို တမင်နောက်ပြန်ဆုတ်ထားခြင်း (Time Tampering)")
        except Exception:
            pass

    with open(TIME_CHECK_FILE, "w") as f:
        f.write(str(local_system_time))

    user_key = ""
    if os.path.exists(LOCAL_CACHE_FILE):
        try:
            with open(LOCAL_CACHE_FILE, "r") as f:
                saved_data = f.read().strip().split(",")
                if len(saved_data) == 2:
                    user_key = saved_data[0]
        except Exception:
            pass

    if not user_key:
        print("\n\033[1;36m=========================================")
        print("         🔒 SApro SECURITY SYSTEM        ")
        print("=========================================\033[0m")
        raw_input_key = input("🔑 ကျေးဇူးပြု၍ သင့်၏ Key ကို ထည့်ပါ: ").strip()
        
        # 💡 အကယ်၍ အသုံးပြုသူက comma ပါတာတွေပါ ကူးထည့်မိပါက Key ကို သီးသန့်ခွဲထုတ်ပေးမည်
        if "," in raw_input_key:
            user_key = raw_input_key.split(",")[0].strip()
        else:
            user_key = raw_input_key
            
        if not user_key:
            print("[!] Key ထည့်သွင်းခြင်း မရှိပါ။ ပိတ်လိုက်ပါပြီ။")
            sys.exit(0)

    try:
        r_kill = requests.get(f"{BASE_KILL_URL}?t={local_system_time}", timeout=4, verify=False)
        server_date_str = r_kill.headers.get('Date')
        if server_date_str:
            current_time = int(parsedate_to_datetime(server_date_str).timestamp())
        else:
            current_time = local_system_time

        kill_content = r_kill.text.strip().upper()
        if "STOP" in kill_content or "OFF" in kill_content or "RUN" not in kill_content:
            self_destruct_and_exit("အသုံးပြုခွင့် ရုပ်သိမ်းထားသည် (Kill Switch Active)")

        r_keys = requests.get(f"{BASE_KEYS_URL}?t={local_system_time}", timeout=4, verify=False)
        keys_lines = r_keys.text.strip().split("\n")
        
        valid_key_found = False
        server_expiry_time = 0
        
        for line in keys_lines:
            if "," in line:
                k, exp = line.strip().split(",")
                if k.strip() == user_key:
                    valid_key_found = True
                    server_expiry_time = int(exp.strip())
                    break
        
        if not valid_key_found:
            self_destruct_and_exit("မှားယွင်းနေသော Key (သို့မဟုတ်) အသုံးမပြုနိုင်တော့သော Key ဖြစ်သည်")

        remaining_seconds = server_expiry_time - current_time
        if remaining_seconds <= 0:
            self_destruct_and_exit("ဤ Key ၏ သက်တမ်း ကုန်ဆုံးသွားပါပြီ")

        with open(LOCAL_CACHE_FILE, "w") as f:
            f.write(f"{user_key},{server_expiry_time}")
            
        time_str = format_time_remaining(remaining_seconds)
        print(f"\n\033[1;32m[+] Key Authentication: SUCCESS")
        print(f"[*] ကျန်ရှိသော သက်တမ်းအချိန်: {time_str}\033[0m\n")

        # 💡 Background Monitoring Thread စတင်ခြင်း (အလုပ်လုပ်နေစဉ် အချိန်ပြည့်စစ်ဆေးပေးရန်)
        t = threading.Thread(target=background_monitor, args=(user_key, server_expiry_time))
        t.daemon = True
        t.start()

    except Exception as e:
        print(f"[*] Offline Mode: Local cache ကို စစ်ဆေးနေပါသည်...")
        if os.path.exists(LOCAL_CACHE_FILE):
            try:
                with open(LOCAL_CACHE_FILE, "r") as f:
                    saved_data = f.read().strip().split(",")
                    cached_key = saved_data[0]
                    cached_expiry = int(saved_data[1])
                
                remaining_seconds = cached_expiry - local_system_time
                if remaining_seconds <= 0:
                    self_destruct_and_exit("Offline သက်တမ်း ကုန်ဆုံးသွားပါပြီ")
                else:
                    time_str = format_time_remaining(remaining_seconds)
                    print(f"\n\033[1;33m[!] Offline Mode Active (Key: {cached_key})")
                    print(f"[*] ကျန်ရှိသော သက်တမ်းအချိန်: {time_str}\033[0m\n")
                    
                    # Offline ဖြစ်နေရင်တောင် Background မှ ဆက်စစ်ပေးမည့် Thread
                    t = threading.Thread(target=background_monitor, args=(cached_key, cached_expiry))
                    t.daemon = True
                    t.start()
            except Exception:
                self_destruct_and_exit("Local token ပျက်စီးနေပါသည်")
        else:
            self_destruct_and_exit("အင်တာနက် မရှိပါ (ပထမအကြိမ် အွန်လိုင်းဖြင့် Key အတည်ပြုရန် လိုအပ်သည်)")

if __name__ == "__main__":
    verify_key_and_system()
    
    found = False
    for file in os.listdir('.'):
        if file.startswith('set_up') and file.endswith('.so'):
            mod_name = file.split('.')[0]
            try:
                mod = __import__(mod_name)
                if hasattr(mod, 'main'):
                    found = True
                    mod.main()
            except Exception as e:
                print(f"[!] မော်ဂျူး အမှား: {e}")
            break

    if not found:
        print("[!] .so ဖိုင်ကို ရှမတွေ့ပါ!")
