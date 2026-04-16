#!/usr/bin/env python3
"""
Quick script to reset MSantone's password for testing
"""
import json
import bcrypt
from datetime import datetime

def reset_msantone_password(new_password="password123"):
    """Reset MSantone's password to a known value"""
    
    # Load users
    with open("users/users.json", "r") as f:
        users_data = json.load(f)
    
    if "MSantone" not in users_data["users"]:
        print("MSantone user not found!")
        return
    
    # Generate new password hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
    
    # Update MSantone's password
    users_data["users"]["MSantone"]["password_hash"] = password_hash
    users_data["users"]["MSantone"]["last_updated"] = datetime.now().isoformat()
    
    # Save back to file
    with open("users/users.json", "w") as f:
        json.dump(users_data, f, indent=2)
    
    print(f"✅ MSantone's password has been reset to: {new_password}")
    print("Username: MSantone")
    print(f"Password: {new_password}")

if __name__ == "__main__":
    reset_msantone_password()