import os
import sys
import re

def get_saas_flag() -> bool:
    """
    Returns True if SAAS_FLAG is 'true' (case-insensitive).
    """
    val = os.environ.get("SAAS_FLAG", "").lower()
    return val == "true"

def update_chainlit_config(target_css_path: str, target_js_path: str):
    """
    Reads the Chainlit config file and programmatically updates the custom_css and custom_js lines.
    """
    # Chainlit usually stores this in .chainlit/config.toml
    config_file = ".chainlit/config.toml"
    
    # Fallback in case your config is in the root directory
    if not os.path.exists(config_file):
        config_file = "chainlit.toml"
        if not os.path.exists(config_file):
            print("⚠️ Warning: Could not find the Chainlit TOML config file.", flush=True)
            return

    # Read the existing config
    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()

    # Use regex to find `custom_css = "..."` and replace it
    updated_content = re.sub(
        r'custom_css\s*=\s*".*?"', 
        f'custom_css = "{target_css_path}"', 
        config_content
    )

    # Use regex to find `custom_js = "..."` and replace it
    updated_content = re.sub(
        r'custom_js\s*=\s*".*?"', 
        f'custom_js = "{target_js_path}"', 
        updated_content
    )

    # Write the changes back to the TOML file
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"🎨 Updated {config_file} to use CSS: {target_css_path} & JS: {target_js_path}", flush=True)


def main():
    # 1. Run your logic to determine the flag
    is_saas = get_saas_flag()
    print("FINAL VALUE : ", is_saas)
    port = os.environ.get("PORT", "8080")

    # 2. Decide which file, CSS, and JS to run
    if is_saas:
        print("✅ Custom logic evaluated to True. Starting gem3-5.py...", flush=True)
        target_file = "gem3-5.py"
        target_css = "public/style3-5.css"
        target_js = "public/blob3-5.js"
    else:
        print("✅ Custom logic evaluated to False. Starting a.py...", flush=True)
        target_file = "a.py"
        target_css = "public/style.css"
        target_js = "public/blob.js"

    # 3. Dynamically update the TOML file for both CSS and JS
    update_chainlit_config(target_css, target_js)

    # 4. Construct the chainlit command
    cmd = ["chainlit", "run", target_file, "--host", "0.0.0.0", "--port", port]

    # 5. Execute chainlit. 
    os.execvp(cmd[0], cmd)

if __name__ == "__main__":
    main()