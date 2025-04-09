import pandas as pd
import requests
import os

LOCAL_DATASET = 'data.csv'
USER_DATASET = 'users-link.csv'

def load_dataset(filepath):
    """Load URLs from a dataset CSV file."""
    try:
        df = pd.read_csv(filepath)
        if 'url' not in df.columns:
            print(f"[!] '{filepath}' must contain a 'url' column.")
            return []
        return df['url'].dropna().astype(str).str.strip().str.lower().tolist()
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"[!] Error loading '{filepath}': {e}")
        return []

def load_openphish_github_feed():
    """Fetch phishing URLs from OpenPhish GitHub feed."""
    try:
        url = 'https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.strip().lower().split('\n')
        else:
            print(f"[!] Failed to fetch OpenPhish GitHub feed. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"[!] Error fetching OpenPhish GitHub feed: {e}")
        return []

def insert_url_to_user_dataset(new_url, filepath=USER_DATASET):
    """Insert a new URL into the user dataset file."""
    new_url = new_url.strip().lower()
    existing_urls = load_dataset(filepath)

    if new_url in existing_urls:
        print("ℹ️ This URL already exists in the user-submitted dataset.")
        return

    df_new = pd.DataFrame([[new_url]], columns=['url'])

    # Create or append
    if not os.path.exists(filepath):
        df_new.to_csv(filepath, index=False)
    else:
        df_new.to_csv(filepath, mode='a', header=False, index=False)

    print(f"URL added to '{filepath}'.")

def check_phishing_url():
    print("🔍 Phishing URL Detector (Local + User + GitHub Feed)")
    user_url = input("Enter a suspicious URL: ").strip().lower()

    print("\n[+] Loading local phishing URLs...")
    local_urls = load_dataset(LOCAL_DATASET)

    print("[+] Loading user-submitted phishing URLs...")
    user_urls = load_dataset(USER_DATASET)

    print("[+] Fetching OpenPhish GitHub feed...")
    openphish_urls = load_openphish_github_feed()

    all_urls = set(local_urls + user_urls + openphish_urls)
    print(f"[✓] Total URLs loaded: {len(all_urls)}\n")

    if user_url in all_urls:
        print(" ALERT: This URL is malicious! Found in a known dataset.")
    else:
        print("SAFE: This URL was not found in known phishing datasets.")

def main():
    print("📌 What would you like to do?")
    print("1. Check a suspicious URL")
    print("2. Insert a phishing URL into the user dataset")
    choice = input("Enter 1 or 2: ").strip()

    if choice == '1':
        check_phishing_url()
    elif choice == '2':
        new_url = input("Enter the phishing URL to insert: ").strip()
        insert_url_to_user_dataset(new_url)
    else:
        print("[!] Invalid option. Please enter 1 or 2.")

if __name__ == '__main__':
    main()
