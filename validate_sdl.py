import sys

def validate_sdl_syntax(filepath):
    print(f"[INFO] Inspecting SDL manifest: {filepath}")
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            
        # Basic structural checks for Akash SDL v2.0
        content = "".join(lines)
        has_version = "version:" in content
        has_services = "services:" in content
        has_profiles = "profiles:" in content
        has_deployment = "deployment:" in content
        
        print(f"   -> Version block present    : {has_version}")
        print(f"   -> Services block present   : {has_services}")
        print(f"   -> Profiles block present   : {has_profiles}")
        print(f"   -> Deployment block present : {has_deployment}")
        
        if has_version and has_services and has_profiles and has_deployment:
            print("[SUCCESS] akash/deploy.yaml contains all mandatory Akash SDL v2.0 blocks.")
            sys.exit(0)
        else:
            print("[ERROR] Missing one or more mandatory Akash SDL v2.0 blocks.")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to read deployment manifest: {e}")
        sys.exit(1)

if __name__ == "__main__":
    validate_sdl_syntax("akash/deploy.yaml")
