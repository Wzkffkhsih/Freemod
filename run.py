import core
import scanner  # (သင့်ရဲ့ ပင်မ Source .so ဖိုင်နာမည်က scanner ဆိုရင် import scanner လို့ခေါ်ရပါမယ်)

if __name__ == "__main__":
    try:
        # ၁။ ပထမဆုံး လုံခြုံရေးစနစ် (Key Authentication, Time Sync, Kill Switch) ကို စစ်ဆေးမည်
        core.main()
        
        # ၂။ Key မှန်ကန်ပြီး လုံခြုံရေး အောင်မြင်ပါက ပင်မ Scanner ဆီသို့ ပို့ဆောင်မည်
        if hasattr(scanner, 'main'):
            scanner.main()
        else:
            print("[!] ပင်မ Scanner ထဲတွင် main() function မတွေ့ရှိပါ။")
            
    except Exception as e:
        print(f"[!] အမှားအယွင်း ဖြစ်ပေါ်ပါသည်: {e}")
