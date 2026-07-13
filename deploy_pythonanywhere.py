import requests
import time
import sys

USERNAME = 'Mirmaruf07'
TOKEN = '7610a52f196e46c67587ad9f6352710055a6fb40'
REPO_URL = 'https://github.com/mithun41/Dravon-server.git'

HEADERS = {'Authorization': f'Token {TOKEN}'}
BASE_URL = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}'

def main():
    print("Creating a new bash console on PythonAnywhere...")
    response = requests.post(
        f'{BASE_URL}/consoles/', 
        headers=HEADERS, 
        json={'executable': 'bash'}
    )
    
    if response.status_code != 201:
        print(f"Error creating console: {response.status_code} - {response.text}")
        sys.exit(1)
        
    console_id = response.json()['id']
    print(f"Console created (ID: {console_id}). Waiting for console to start...")
    
    # Wait for console to be ready
    for _ in range(10):
        time.sleep(2)
        out = requests.get(f'{BASE_URL}/consoles/{console_id}/get_latest_output/', headers=HEADERS)
        if out.status_code == 200:
            break
            
    # We will use python 3.10 and --nuke to overwrite if it exists
    command = f"pa_autoconfigure_django.py --python=3.10 {REPO_URL} --nuke\n"
    
    send_resp = requests.post(
        f'{BASE_URL}/consoles/{console_id}/send_input/',
        headers=HEADERS,
        json={'input': command}
    )
    
    if send_resp.status_code != 200:
        print(f"Error sending command: {send_resp.status_code} - {send_resp.text}")
        sys.exit(1)
        
    print("Command sent successfully! Please wait while PythonAnywhere sets up the server.")
    print("This usually takes 2-5 minutes...")
    
    last_printed_len = 0
    
    for i in range(120): # wait up to 20 minutes
        time.sleep(10)
        out_resp = requests.get(
            f'{BASE_URL}/consoles/{console_id}/get_latest_output/', 
            headers=HEADERS
        )
        
        if out_resp.status_code == 200:
            output = out_resp.json().get('output', '')
            
            # Print only new output
            new_output = output[last_printed_len:]
            if new_output:
                sys.stdout.write(new_output)
                sys.stdout.flush()
                last_printed_len = len(output)
            
            if 'All done!' in output:
                print("\n\nSUCCESS! Your site is live at: https://Mirmaruf07.pythonanywhere.com")
                break
        else:
            print(f"Failed to fetch output: {out_resp.status_code}")
            
    print("\nDeployment script finished.")

if __name__ == '__main__':
    main()
