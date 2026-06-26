import os
import glob
import subprocess
import platform
from pathlib import Path
import json
import time
import urllib.request

# ==========================================================
# 🧪 THE SAFETY SWITCH (SIMULATION MODE)
# ==========================================================
SIMULATION_MODE = True
# ==========================================================

# 📋 OUR TWO SEPARATE NOTEPAD FILES
CUSTOM_FILE = "custom_apps.json"  # Holds your manual creations
GLOBAL_FILE = "global_apps.json"  # Holds the apps downloaded from GitHub

# 🌐GITHUB RAW URL LINK
GITHUB_DATABASE_URL = "https://raw.githubusercontent.com/enabledhero/QBR-Cached-/refs/heads/main/apps.json"

def return_to_menu_animation():
    """Prints a neat loading dot pause before going back to the menu."""
    print("\nReturning", end="", flush=True)
    for _ in range(5):
        time.sleep(0.3)
        print(" .", end="", flush=True)
    print(" load main menu again!\n")
    time.sleep(0.5)

def load_json_file(file_name):
    """Helper room: Opens a specific JSON file safely if it exists."""
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file: return json.load(file)
        except: return {}
    return {}

def save_json_file(file_name, data):
    """Helper room: Saves data into a specific JSON file."""
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def get_smart_app_registry():
    """🌟 The Master Merge: Layers Firefox, Global Cloud Apps, and Custom Apps together!"""
    home = Path.home()
    current_os = platform.system()
    appdata = os.environ.get('APPDATA', '')
    
    registry = {}

    # 1. Start with the built-in Firefox standard
    registry["firefox"] = {
        "description": "Firefox Cookies & Active Sessions",
        "process_name": "firefox.exe" if current_os == "Windows" else "firefox",
        "paths": [str(Path(appdata) / "Mozilla/Firefox/Profiles/*.default-release/cookies.sqlite")] if current_os == "Windows" else []
    }

    # 2. Layer on top the Globally downloaded apps from the internet
    global_apps = load_json_file(GLOBAL_FILE)
    for app_id, app_info in global_apps.items():
        registry[app_id] = app_info

    # 3. Layer on top your personal manual apps (This guarantees your custom entries win!)
    custom_apps = load_json_file(CUSTOM_FILE)
    for app_id, app_info in custom_apps.items():
        registry[app_id] = app_info

    return registry

def check_for_cloud_updates():
    """🌟 NEW: The Update Engine! Downloads the master list and checks for new apps."""
    current_os = platform.system().lower()
    print("\n🌐 Checking GitHub for database updates...")
    time.sleep(0.5) # Give it a tiny, realistic pause
    
    try:
        # 1. Try to open the internet stream connection to your GitHub link
        with urllib.request.urlopen(GITHUB_DATABASE_URL, timeout=5) as response:
            internet_data = json.loads(response.read().decode())
            
        # 2. Open what we currently have stored locally in global_apps.json
        local_global_registry = load_json_file(GLOBAL_FILE)
        
        new_apps_found = 0
        
        # 3. Loop through every app on the internet list to see if we are missing any
        for app_id, cloud_info in internet_data.items():
            if app_id not in local_global_registry:
                # Format it nicely so our script can read it later!
                raw_path = cloud_info.get(current_os, "")
                
                local_global_registry[app_id] = {
                    "description": f"{app_id.replace('_', ' ').title()} (Cloud Updated)",
                    "process_name": cloud_info["process"],
                    "paths": [os.path.expandvars(raw_path) if "%" in raw_path else raw_path]
                }
                new_apps_found += 1
                print(f"   ✨ Detected new application: [{app_id.replace('_', ' ').title()}]")

        # 4. If we found brand new content, save it to our global file!
        if new_apps_found > 0:
            save_json_file(GLOBAL_FILE, local_global_registry)
            print(f"\n🎉 Success! Automatically integrated {new_apps_found} new application(s) into your engine!")
        else:
            # If no updates were found, give the user the exact text and dot animation requested!
            print("✔️ Your database is already up-to-date! No new content found.")
            return_to_menu_animation()
            
    except Exception as e:
        print(f"❌ Could not connect to the internet server. (Error: {e})")
        print("Please check your Wi-Fi connection or your GITHUB_DATABASE_URL link!")
        return_to_menu_animation()

def interactive_add_custom_app():
    """Option [0]: Manually add your own apps."""
    print("\n🛠️ [MANUAL APPLICATION ADDITION] 🛠️")
    name = input("1. Enter the App Name: ")
    proc = input("2. Enter its process name (e.g., app.exe): ")
    path = input("3. Paste the exact folder path to clean: ")
    
    if name and path:
        new_app_data = {
            "description": f"{name} (User Custom)",
            "process_name": proc,
            "paths": [path]
        }
        app_id = name.lower().replace(" ", "_")
        
        # Load your custom notepad, stick the new app inside, and save it!
        custom_registry = load_json_file(CUSTOM_FILE)
        custom_registry[app_id] = new_app_data
        save_json_file(CUSTOM_FILE, custom_registry)
        
        print(f"\n🎉 Saved manually to your personal '{CUSTOM_FILE}' file!")
    return_to_menu_animation()

def check_is_path_safe(path_to_check):
    clean_path = str(path_to_check).lower()
    danger_zones = ["windows", "system32", "program files", "/bin", "/sbin", "/etc", "/System"]
    for zone in danger_zones:
        if zone in clean_path: return False
    return True

def simulate_or_run_action(action_type, target):
    if SIMULATION_MODE:
        if action_type == "kill": print(f"   [SIMULATION] Would force close process: {target}")
        elif action_type == "delete": print(f"   [SIMULATION] Would check and wipe path: {target}")
    else:
        if action_type == "kill":
            if platform.system() == "Windows": subprocess.run(f"taskkill /f /im {target}", shell=True, capture_output=True)
            else: subprocess.run(f"pkill -f {target}", shell=True, capture_output=True)
        elif action_type == "delete":
            if not check_is_path_safe(target):
                print(f"   ⚠️ [SAFETY BLOCK] Refused to clear path: {target}")
                return
            found_files = glob.glob(str(target))
            for file_path in found_files:
                try:
                    if os.path.isdir(file_path): os.rmdir(file_path)
                    else: os.remove(file_path)
                    print(f"   [SUCCESS] Cleaned: {file_path}")
                except: pass

def alarm_full_wipe():
    print("\n🚨 [ALARM MODE INITIATED] 🚨")
    are_you_sure = input("Are you absolutely sure? (Y/N): ")
    if are_you_sure.lower() == 'y':
        registry = get_smart_app_registry()
        for app_name, app_info in registry.items():
            if app_info.get("process_name"): simulate_or_run_action("kill", app_info["process_name"])
            for path in app_info.get("paths", []): simulate_or_run_action("delete", path)
        print("\n⚡ Emergency ALARM wipe completed successfully!")

def selective_wipe():
    print("\n📋 [SELECTIVE CHECKLIST MODE] 📋")
    registry = get_smart_app_registry()
    for app_name, app_info in registry.items():
        choice = input(f"\nClear data for {app_info['description']}? (Y/N): ")
        if choice.lower() == 'y':
            if app_info.get("process_name"): simulate_or_run_action("kill", app_info["process_name"])
            for path in app_info.get("paths", []): simulate_or_run_action("delete", path)
    print("\n📋 Selective cleaning checklist completed!")

def main_menu():
    while True:
        print("==========================================")
        print("       SMART SECURITY ENGINE (ALARM)      ")
        print("==========================================")
        if SIMULATION_MODE: print("🔬 NOTE: [SIMULATION MODE IS ACTIVE] 🔬\n")

        print("Options:")
        print("  [0] - 🛠️ Add an App Manually (Your Custom List)")
        print("  [1] - 🚨 Trigger Emergency ALARM (Wipe Everything)")
        print("  [2] - 📋 Run Selective Checklist (Go 1-by-1)")
        print("  [3] - 🔄 Check for Cloud Database Updates")
        print("  [4] - 🚪 Exit Program Safely")

        user_choice = input("\nWhat would you like to do? (0-4): ")
        
        if user_choice == '0':
            interactive_add_custom_app()
        elif user_choice == '1':
            alarm_full_wipe()
            return_to_menu_animation()
        elif user_choice == '2':
            selective_wipe()
            return_to_menu_animation()
        elif user_choice == '3':
            check_for_cloud_updates()
        elif user_choice == '4':
            print("\nExiting script safely. Stay secure! Goodbye! 👋")
            break
        else:
            print("\n❌ Invalid choice! Please type a number between 0 and 4.")
            return_to_menu_animation()

if __name__ == "__main__":
    main_menu()