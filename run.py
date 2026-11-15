import os

found = False
for file in os.listdir('.'):
    if file.startswith('set_up') and file.endswith('.so'):
        mod_name = file.split('.')[0]
        mod = __import__(mod_name)
        if hasattr(mod, 'main'):
            found = True
            mod.main()
        break

if not found:
    print("[!] .so file not found!")
