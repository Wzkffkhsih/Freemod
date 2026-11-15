import os
import sys
import subprocess
import time
import shutil
import threading
import hashlib
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
BASE_VERSION_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/version.txt"

LOCAL_CACHE_FILE = ".key_cache"
TIME_CHECK_FILE = ".last_time"
LOCAL_VERSION = "1.0"
SECRET_SALT = "SAproSuperSecretKey2026"  # Admin ဘက်သုံးသော လျှို့ဝှက်ကုဒ်အတိုင်း ဖြစ်ရပါမည်

def clear_cache_and_prompt_exit(reason=""):
    print(f"\n\033[1;31m[!] လိုင်စင် သတိပေးချက်: {reason}\033[0m")
    print(f"\033[1;33m[*] ကျေးဇူးပြု၍ မှန်ကန်သော Key အသစ် ပြန်လည် ထည့်သွင်းပါ...\033[0m")
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

def background_monitor(expiry_time):
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
    
    # 1. Anti-Clock Tampering (အော့ဖ်လိုင်းအချိန် နောက်ပြန်ဆုတ်ခြင်းကို တားဆီးရန်)
    if os.path.exists(TIME_CHECK_FILE):
        try:
            with open(TIME_CHECK_FILE, "r") as f:
                last_recorded_time = int(f.read().strip())
            
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

    # 2. Admin ဘက်မှ ဖိုင် Update ရှိမရှိ စစ်ဆေးခြင်း
    try:
        r_ver = requests.get(f"{BASE_VERSION_URL}?t={local_system_time}", timeout=3, verify=False)
        server_version = r_ver.text.strip()
        if server_version and server_version != LOCAL_VERSION:
            print(f"\n\033[1;33m[!] 🚨 ဖိုင် Update အသစ် ထွက်ရှိနေပါပြီ။\033[0m")
            print(f"\033[1;36m[i] ကျေးဇူးပြု၍ Admin ထံတွင် Update အသစ် တောင်းခံပါ။\033[0m")
            sys.exit(0)
    except Exception:
        pass

    # Server အချိန်ကို ယူရန်
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
    except Exception:
        current_time = local_system_time

    # 3. Local Cache ရှိမရှိ စစ်ဆေးခြင်း
    user_key = ""
    server_expiry_time = 0
    cache_valid = False

    if os.path.exists(LOCAL_CACHE_FILE):
        try:
            with open(LOCAL_CACHE_FILE, "r") as f:
                saved_data = f.read().strip().split(",")
                if len(saved_data) == 2:
                    user_key = saved_data[0].strip()
                    server_expiry_time = int(saved_data[1].strip())
                    if current_time < server_expiry_time:
                        cache_valid = True
        except Exception:
            pass

    # 4. Cache မရှိပါက Key တောင်းခံပြီး Signature စစ်ဆေးခြင်း
    if not cache_valid:
        print("\n\033[1;36m=========================================")
        print("         🔒 SApro SECURITY SYSTEM        ")
        print("=========================================\033[0m")
        user_key = input("🔑 ကျေးဇူးပြု၍ သင့်၏ Secure Key ကို ထည့်ပါ: ").strip()
        
        if not user_key:
            print("[!] Key ထည့်သွင်းခြင်း မရှိပါ။ ပိတ်လိုက်ပါပြီ။")
            sys.exit(0)

        try:
            # Key ဖွဲ့စည်းပုံကို စစ်ဆေးခြင်း (ဥပမာ: SApro-RANDOM-DURATION-SIG)
            parts = user_key.split("-")
            if len(parts) != 4 or parts[0] != "SApro":
                clear_cache_and_prompt_exit("ပုံစံမမှန်ကန်သော Key ဖြစ်သည်")

            rand_str = parts[1]
            duration_seconds = int(parts[2])
            provided_sig = parts[3].strip().upper()

            # Signature ကို ပြန်လည်တွက်ချက်၍ စစ်ဆေးခြင်း (တမင်ဝင်ပြင်ထားပါက မကိုက်ညီပါ)
            raw_data = f"SApro-{rand_str}-{duration_seconds}-{SECRET_SALT}"
            expected_sig = hashlib.md5(raw_data.encode()).hexdigest()[:6].upper()

            if provided_sig != expected_sig:
                clear_cache_and_prompt_exit("အတုပြုလုပ်ထားသော (သို့မဟုတ်) ပြင်ဆင်ထားသော Key ဖြစ်သည်")

            # အချိန်ကို တွက်ချက်ခြင်း
            server_expiry_time = current_time + duration_seconds

            # Local Cache တွင် သိမ်းဆည်းမည်
            with open(LOCAL_CACHE_FILE, "w") as f:
                f.write(f"{user_key},{server_expiry_time}")

        except Exception as e:
            clear_cache_and_prompt_exit("Key စစ်ဆေးရာတွင် အမှားအယွင်း ရှိသည် (သို့မဟုတ် အင်တာနက် မရှိပါ)")

    # ကျန်ရှိသော သက်တမ်းကို တွက်ချက်ပြသခြင်း
    remaining_seconds = server_expiry_time - current_time
    if remaining_seconds <= 0:
        clear_cache_and_prompt_exit("ဤ Key ၏ သက်တမ်း ကုန်ဆုံးသွားပါပြီ")

    time_str = format_time_remaining(remaining_seconds)
    print(f"\n\033[1;32m[+] Key Authentication: SUCCESS")
    print(f"[*] ကျန်ရှိသော သက်တမ်းအချိန်: {time_str}\033[0m\n")

    # Background Monitoring Thread စတင်ခြင်း
    t = threading.Thread(target=background_monitor, args=(server_expiry_time,))
    t.daemon = True
    t.start()

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
