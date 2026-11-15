import os
import sys
import subprocess

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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ══════════════════════════════════════════════════════════
# ၂။ Remote Kill Switch လုံခြုံရေး စစ်ဆေးခြင်း
# ══════════════════════════════════════════════════════════
KILL_SWITCH_URL = "https://raw.githubusercontent.com/Wzkffkhsih/Freemod/main/kill.txt"

def check_kill_switch():
    try:
        r = requests.get(KILL_SWITCH_URL, timeout=5, verify=False)
        content = r.text.strip().upper()
        if "STOP" in content or "OFF" in content:
            print(f"\n\033[1;31m[!] Access Revoked: ဆော့ဖ်ဝဲအသုံးပြုခွင့်ကို ဆော့ဖ်ဝဲရေးသားသူမှ အဝေးမှ ပိတ်ထားလိုက်ပါပြီ။\033[0m")
            sys.exit(0)
    except Exception:
        # လိုင်းမကောင်းလျှင် သို့မဟုတ် ဆာဗာချိတ်ဆက်၍ မရလျှင် ဆက်လည်ပတ်ခွင့်ပြုရန် (သို့မဟုတ် လုံးဝပိတ်လိုပါက sys.exit(0) ထည့်နိုင်သည်)
        pass

if __name__ == "__main__":
    # စတင်ဖွင့်လှစ်သည်နှင့် Kill Switch ကို အရင်စစ်မည်
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
