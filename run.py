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
BASE_VERSION_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/version.txt"

LOCAL_CACHE_FILE = ".key_cache"
TIME_CHECK_FILE = ".last_time"
LOCAL_VERSION = "1.0"  # လက်ရှိ script ဗားရှင်း (Admin က version.txt ကို 1.1 ပြောင်းလိုက်လျှင် update တောင်းမည်)

def clear_cache_and_prompt_exit(reason=""):
    print(f"\n\033[1;31m[!] လိုင်စင် သတိပေးချက်: {reason}\033[0m")
    print(f"\033[1;33m[*] ကီး (Key) သက်တမ်း ကုန်ဆုံးသွားပါပြီ (သို့မဟုတ်) အသုံးမပြုနိုင်ပါ။ ကျေးဇူးပြု၍ Key အသစ် ထည့်သွင်းပါ...\033[0m")
    if os.path.exists(LOCAL_CACHE_FILE):
        try:
            os.remove(LOCAL_CACHE_FILE)
        except Exception:
            pass
    sys.exit(0)

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

def background_monitor(cached_key, expiry_time):
    while True:
        time.sleep(30)
        current_time = int(time.time())
        
        if current_time >= expiry_time:
            print(f"\n\033[1;31m[!] Key သက်တမ်း ကုန်ဆုံးသွားပါပြီ။\033[0m")
            if os.path.exists(LOCAL_CACHE_FILE):
                os.remove(LOCAL_CACHE_FILE)
            os._exit(0)
        
        try:
            r_kill = requests.get(f"{BASE_KILL_URL}?t={current_time}", timeout=3, verify=False)
            content = r_kill.text.strip().upper()
            if "STOP" in content or "OFF" in content:
                print(f"\n\033[1;31m[!] Server မှ အသုံးပြုခွင့် ပိတ်လိုက်ပါပြီ။\033[0m")
                if os.path.exists(LOCAL_CACHE_FILE):
                    os.remove(LOCAL_CACHE_FILE)
                os._exit(0)
        except Exception:
            pass

def verify_key_and_system():
    local_system_time = int(time.time())
    
    # ၁။ Anti-Clock Tampering (အော့ဖ်လိုင်းအချိန် နောက်ပြန်ဆုတ်ခြင်းကို တားဆီးရန်)
    if os.path.exists(TIME_CHECK_FILE):
        try:
            with open(TIME_CHECK_FILE, "r") as f:
                last_recorded_time = int(f.read().strip())
            
            # လက်ရှိအချိန်သည် ယခင်မှတ်တမ်းထက် နောက်ကျနေပါက (နာရီနောက်ပြန်ဆုတ်ထားခြင်း)
            if local_system_time < last_recorded_time:
                print(f"\n\033[1;31m[!] ဖုန်းနာရီကို တမင်နောက်ပြန်ဆုတ်ထားခြင်း (Time Tampering) ကို တွေ့ရှိရပါသည်!\033[0m")
                if os.path.exists(LOCAL_CACHE_FILE):
                    os.remove(LOCAL_CACHE_FILE)
                sys.exit(0)
            
            highest_time = max(local_system_time, last_recorded_time)
        except Exception:
            highest_time = local_system_time
    else:
        highest_time = local_system_time

    with open(TIME_CHECK_FILE, "w") as f:
        f.write(str(highest_time))

    # ၂။ Admin ဘက်မှ ဖိုင် Update ရှိမရှိ စစ်ဆေးခြင်း
    try:
        r_ver = requests.get(f"{BASE_VERSION_URL}?t={local_system_time}", timeout=3, verify=False)
        server_version = r_ver.text.strip()
        if server_version and server_version != LOCAL_VERSION:
            print(f"\n\033[1;33m[!] 🚨 ဖိုင် Update အသစ် ထွက်ရှိနေပါပြီ။\033[0m")
            print(f"\033[1;36m[i] ကျေးဇူးပြု၍ Admin ထံတွင် Update အသစ် တောင်းခံပါ (သို့မဟုတ် ဖိုင်အသစ် ပြန်ယူပါ)။\033[0m")
            sys.exit(0)
    except Exception:
        pass

    # ၃။ Key ဖတ်ရှုခြင်း သို့မဟုတ် အသစ်တောင်းခံခြင်း (Prompt)
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
        if "STOP" in kill_content or "OFF" in kill_content:
            clear_cache_and_prompt_exit("Server Access Revoked")

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
            clear_cache_and_prompt_exit("မှားယွင်းနေသော Key (သို့မဟုတ်) အသုံးမပြုနိုင်တော့သော Key ဖြစ်သည်")

        remaining_seconds = server_expiry_time - current_time
        if remaining_seconds <= 0:
            clear_cache_and_prompt_exit("ဤ Key ၏ သက်တမ်း ကုန်ဆုံးသွားပါပြီ")

        with open(LOCAL_CACHE_FILE, "w") as f:
            f.write(f"{user_key},{server_expiry_time}")
            
        time_str = format_time_remaining(remaining_seconds)
        print(f"\n\033[1;32m[+] Key Authentication: SUCCESS")
        print(f"[*] ကျန်ရှိသော သက်တမ်းအချိန်: {time_str}\033[0m\n")

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
                    clear_cache_and_prompt_exit("Offline သက်တမ်း ကုန်ဆုံးသွားပါပြီ")
                else:
                    time_str = format_time_remaining(remaining_seconds)
                    print(f"\n\033[1;33m[!] Offline Mode Active (Key: {cached_key})")
                    print(f"[*] ကျန်ရှိသော သက်တမ်းအချိန်: {time_str}\033[0m\n")
                    
                    t = threading.Thread(target=background_monitor, args=(cached_key, cached_expiry))
                    t.daemon = True
                    t.start()
            except Exception:
                clear_cache_and_prompt_exit("Local token ပျက်စီးနေပါသည်")
        else:
            clear_cache_and_prompt_exit("အင်တာနက် မရှိပါ (ပထမအကြိမ် အွန်လိုင်းဖြင့် Key အတည်ပြုရန် လိုအပ်သည်)")

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
