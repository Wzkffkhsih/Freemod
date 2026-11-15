import os
import sys
import subprocess
import time
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ══════════════════════════════════════════════════════════
# ၁။ လိုအပ်သော Library များကို အလိုအလျောက်စစ်ဆေးပြီး တင်ရန်
# ══════════════════════════════════════════════════════════
required_packages = ['requests']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"[!] '{package}' library မရှိပါ၊ အလိုအလျောက် ဒေါင်းလုဒ်လုပ်နေပါပြီ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[✓] '{package}' ကို အောင်မြင်စွာ ထည့်သွင်းပြီးပါပြီ။")
        except Exception as e:
            print(f"[!] Library ထည့်သွင်းမှု မအောင်မြင်ပါ: {e}")
            sys.exit(1)

import requests

# ══════════════════════════════════════════════════════════
# ၂။ Self-Destruct & Remote Kill Switch
# ══════════════════════════════════════════════════════════
BASE_KILL_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/kill.txt"

def self_destruct_and_exit():
    print(f"\n\033[1;31m[!] Access Revoked: အသုံးပြုခွင့် ရုပ်သိမ်းခံရသဖြင့် ဖိုင်များကို ဖျက်ဆီးနေပါသည်...\033[0m")
    try:
        # လက်ရှိ Freemod ဖိုဒါအတွင်းရှိ ဖိုင်များနှင့် ဖိုဒါများကို အစအနမကျန် ဖျက်မည်
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
        # Cache မမိစေရန် timestamp ဖြင့် ချိတ်ဆက်ခြင်း
        url = f"{BASE_KILL_URL}?t={int(time.time())}"
        r = requests.get(url, timeout=5, verify=False)
        content = r.text.strip().upper()
        
        if "STOP" in content or "OFF" in content:
            self_destruct_and_exit()
    except Exception:
        # အင်တာနက်လိုင်း မရှိလျှင် သို့မဟုတ် ဆာဗာချိတ်ဆက်၍ မရလျှင် လုံခြုံရေးအရ ဖျက်ဆီးပစ်ရန် (သို့မဟုတ် ကျော်သွားရန်)
        pass

if __name__ == "__main__":
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
                print(f"[!] မော်ဂျူးကို ဖတ်ရှုရာတွင် အမှားအယွင်းရှိပါသည်: {e}")
            break

    if not found:
        print("[!] .so ဖိုင်ကို ရှမတွေ့ပါ!")
