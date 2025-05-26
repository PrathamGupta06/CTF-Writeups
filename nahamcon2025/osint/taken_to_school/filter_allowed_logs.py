#!/usr/bin/env python3

import re
import os
import sys
from collections import defaultdict

def parse_log_file(file_path):
    """Parse the CEF log file and extract entries with act=allowed."""
    allowed_entries = []
    
    with open(file_path, 'r') as f:
        for line in f:
            # Skip comment lines or empty lines
            if line.strip().startswith('//') or not line.strip():
                continue
                
            # Check if this log entry has act=allowed
            if 'act=allowed' in line:
                # Extract the eventHash
                event_hash_match = re.search(r'eventHash=([a-f0-9]{32})', line)
                if event_hash_match:
                    event_hash = event_hash_match.group(1)
                    
                    # Extract other useful information
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                    
                    # Extract source IP
                    src_match = re.search(r'src=(\d+\.\d+\.\d+\.\d+)', line)
                    src_ip = src_match.group(1) if src_match else "Unknown"
                    
                    # Extract other fields that might be useful
                    device_match = re.search(r'CEF:0\|([^|]+)\|([^|]+)', line)
                    device = device_match.group(1) if device_match else "Unknown"
                    
                    # Extract threat name or signature
                    threat_match = re.search(r'\|([^|]+)\|[0-9]+\|', line)
                    threat = threat_match.group(1) if threat_match else "Unknown"
                    
                    # Extract filename if present
                    filename_match = re.search(r'fileName=([^ ]+)', line)
                    filename = filename_match.group(1) if filename_match else "N/A"
                    
                    # For entries with usernames/passwords (Remote Desktop or Network Logon)
                    username_match = re.search(r'cs1Label=username cs1=([^ ]+)', line)
                    username = username_match.group(1) if username_match else "N/A"
                    
                    password_match = re.search(r'cs2Label=password cs2=([^ ]+)', line)
                    password = password_match.group(1) if password_match else "N/A"
                    
                    allowed_entries.append({
                        'timestamp': timestamp,
                        'device': device,
                        'threat': threat,
                        'src_ip': src_ip,
                        'filename': filename,
                        'username': username,
                        'password': password,
                        'eventHash': event_hash,
                        'full_log': line.strip()
                    })
    
    return allowed_entries

def analyze_entries(entries):
    """Perform basic analysis on the allowed entries."""
    print(f"Total 'act=allowed' entries: {len(entries)}")
    
    # Group by device type
    device_count = defaultdict(int)
    for entry in entries:
        device_count[entry['device']] += 1
    
    print("\nDevice Distribution:")
    for device, count in device_count.items():
        print(f"  - {device}: {count}")
    
    # Group by threat type
    threat_count = defaultdict(int)
    for entry in entries:
        threat_count[entry['threat']] += 1
    
    print("\nThreat Distribution:")
    for threat, count in threat_count.items():
        print(f"  - {threat}: {count}")
    
    # Check for unusual usernames or passwords
    print("\nCredentials in allowed entries:")
    for entry in entries:
        if entry['username'] != "N/A":
            print(f"  - Username: {entry['username']}, Password: {entry['password']}")
    
    # List all event hashes for reference
    print("\nAll event hashes from allowed entries:")
    for entry in entries:
        print(f"  - {entry['eventHash']} | {entry['timestamp']} | {entry['threat']} | {entry['src_ip']}")
        if entry['filename'] != "N/A":
            print(f"      File: {entry['filename']}")
        print()

def main():
    log_file = 'network-log.cef'
    if not os.path.exists(log_file):
        print(f"Error: File {log_file} not found.")
        sys.exit(1)
    
    allowed_entries = parse_log_file(log_file)
    
    print("\n===== ALLOWED ENTRIES ANALYSIS =====\n")
    analyze_entries(allowed_entries)
    
    print("\nPotential steps for OSINT analysis to find anomalous entries:")
    print("1. Research the source IPs using tools like IPinfo or VirusTotal")
    print("2. Check if any usernames/passwords match known data breaches")
    print("3. Look for suspicious file names or unusual download patterns")
    print("4. Cross-reference timestamps with known attack campaigns")
    print("5. Search for these usernames on social media platforms")
    print("6. Look for inconsistencies in user behavior (e.g., access times, file types)")
    print("7. Check for unusual country origins of source IPs")
    
    print("\nTo get the flag, identify the anomalous entry and submit flag{<eventHash>}")

if __name__ == "__main__":
    main()
