import core
import set_up  # (သို့မဟုတ် သင် compile လုပ်ထားသည့် ပင်မ .so ဖိုင်နာမည်)

if __name__ == "__main__":
    try:
        # ၁။ ပထမဆုံး လုံခြုံရေးစနစ် (Key Authentication & Security Check) ကို စစ်ဆေးမည်
        core.main()
        
        # ၂။ လုံခြုံရေး အောင်မြင်ပါက ပင်မ SApro Scanner Control Panel / Menu ကို စတင်မည်
        if hasattr(set_up, 'main'):
            set_up.main()
        else:
            print("[!] ပင်မ Source ထဲတွင် main() function မတွေ့ရှိပါ။")
            
    except Exception as e:
        print(f"[!] အမှားအယွင်း ဖြစ်ပေါ်ပါသည်: {e}")