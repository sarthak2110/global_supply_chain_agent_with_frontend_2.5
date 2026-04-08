import os
import sys
import re
import json
import time
import signal
import subprocess
from flag_config import get_saas_flag_value

# Global variable to keep track of the Chainlit process
current_process = None

def handle_shutdown_signal(signum, frame):
    """
    Catches Cloud Run's SIGTERM signal and gracefully shuts down the Chainlit server.
    """
    global current_process
    print("🛑 Received shutdown signal from Cloud Run. Terminating app...", flush=True)
    if current_process:
        current_process.terminate()
        current_process.wait()
    sys.exit(0)

# Register the signal handlers
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

def update_chainlit_config(target_css_path: str, target_js_path: str):
    """
    Reads the Chainlit config file and programmatically updates the custom_css and custom_js lines.
    """
    config_file = ".chainlit/config.toml"
    
    if not os.path.exists(config_file):
        config_file = "chainlit.toml"
        if not os.path.exists(config_file):
            print("⚠️ Warning: Could not find the Chainlit TOML config file.", flush=True)
            return

    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()

    updated_content = re.sub(
        r'custom_css\s*=\s*".*?"', 
        f'custom_css = "{target_css_path}"', 
        config_content
    )

    updated_content = re.sub(
        r'custom_js\s*=\s*".*?"', 
        f'custom_js = "{target_js_path}"', 
        updated_content
    )

    with open(config_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"🎨 Updated {config_file} to use CSS: {target_css_path} & JS: {target_js_path}", flush=True)

def main():
    global current_process
    port = os.environ.get("PORT", "8080")
    last_flag_value = None

    print("🚀 Starting Feature Flag Watcher...", flush=True)

    while True:
        try:
            # 1. Fetch the latest flag value
            is_saas = get_saas_flag_value()
            
            # 2. Check if the flag changed (or if this is the first run)
            if is_saas != last_flag_value:
                print(f"🔄 Routing change required. Old state: {last_flag_value}, New state: {is_saas}", flush=True)

                # Terminate existing Chainlit server if it is running
                if current_process:
                    print("🛑 Terminating existing Chainlit server...", flush=True)
                    current_process.terminate()
                    current_process.wait()

                # Determine which files to load based on the flag
                if is_saas:
                    print("✅ Loading SaaS App (app_2.5_pro.py)...", flush=True)
                    target_file = "app_2.5_pro.py"
                    target_css = "public/style3-5.css"
                    target_js = "public/blob3-5.js"
                else:
                    print("✅ Loading Default App (app_2_flash.py)...", flush=True)
                    target_file = "app_2_flash.py"
                    target_css = "public/style.css"
                    target_js = "public/blob.js"

                # Update the TOML config
                update_chainlit_config(target_css, target_js)

                # Start the new Chainlit server in the background
                cmd = ["chainlit", "run", target_file, "--host", "0.0.0.0", "--port", port]
                
                # subprocess.Popen runs the command without blocking the while loop
                current_process = subprocess.Popen(cmd, env=os.environ.copy())
                
                # Save the current state so we don't restart it on the next loop iteration
                last_flag_value = is_saas

        except Exception as e:
            print(f"⚠️ Error evaluating feature flag: {e}", flush=True)

        # 3. Wait 15 seconds before pinging GCP for the flag again
        time.sleep(15)

if __name__ == "__main__":
    main()







# import os
# import sys
# import re
# import json
# import time
# from flag_config import get_saas_flag_value


# def update_chainlit_config(target_css_path: str, target_js_path: str):
#     """
#     Reads the Chainlit config file and programmatically updates the custom_css and custom_js lines.
#     """
#     # Chainlit usually stores this in .chainlit/config.toml
#     config_file = ".chainlit/config.toml"
    
#     # Fallback in case your config is in the root directory
#     if not os.path.exists(config_file):
#         config_file = "chainlit.toml"
#         if not os.path.exists(config_file):
#             print("⚠️ Warning: Could not find the Chainlit TOML config file.", flush=True)
#             return

#     # Read the existing config
#     with open(config_file, "r", encoding="utf-8") as f:
#         config_content = f.read()

#     # Use regex to find `custom_css = "..."` and replace it
#     updated_content = re.sub(
#         r'custom_css\s*=\s*".*?"', 
#         f'custom_css = "{target_css_path}"', 
#         config_content
#     )

#     # Use regex to find `custom_js = "..."` and replace it
#     updated_content = re.sub(
#         r'custom_js\s*=\s*".*?"', 
#         f'custom_js = "{target_js_path}"', 
#         updated_content
#     )

#     # Write the changes back to the TOML file
#     with open(config_file, "w", encoding="utf-8") as f:
#         f.write(updated_content)
        
#     print(f"🎨 Updated {config_file} to use CSS: {target_css_path} & JS: {target_js_path}", flush=True)


# def main():
#     # 1. Run your logic to determine the flag
#     is_saas = get_saas_flag_value()
#     print("FINAL VALUE : ", is_saas)
#     port = os.environ.get("PORT", "8080")

#     # 2. Decide which file, CSS, and JS to run
#     if is_saas:
#         print("✅ Custom logic evaluated to True. Starting app_2.5_pro...", flush=True)
#         target_file = "app_2.5_pro.py"
#         target_css = "public/style3-5.css"
#         target_js = "public/blob3-5.js"
#     else:
#         print("✅ Custom logic evaluated to False. Starting app_2_flash.py...", flush=True)
#         target_file = "app_2_flash.py"
#         target_css = "public/style.css"
#         target_js = "public/blob.js"

#     # 3. Dynamically update the TOML file for both CSS and JS
#     update_chainlit_config(target_css, target_js)

#     # 4. Construct the chainlit command
#     cmd = ["chainlit", "run", target_file, "--host", "0.0.0.0", "--port", port]

#     # 5. Execute chainlit. 
#     os.execvp(cmd[0], cmd)

# if __name__ == "__main__":
#     main()