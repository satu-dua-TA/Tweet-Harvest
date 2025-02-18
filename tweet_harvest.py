import subprocess
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
email_user = os.getenv("SENDER_EMAIL")
pass_user = os.getenv("SENDER_PASSWORD")
receiver_email = ["zhafarinaufal2@gmail.com", "fathand.hadyan@cs.ui.ac.id", "muhammad.fahreza11@ui.ac.id"]

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = ', '.join(receiver_email)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, pass_user)
            server.sendmail(email_user, receiver_email, msg.as_string())
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Twitter Auth Token
twitter_auth_token = 'abf99ea0fdfd6951aeb5011c1697ae6281955dee'

# File Konfigurasi
keyword_file = 'keywords.txt'
date_file = 'date.txt'
progress_file = 'progress.txt'

# Read keywords
with open(keyword_file, "r") as file:
    keywords = [line.strip() for line in file if line.strip()]

# Read dates
with open(date_file, "r") as file:
    dates = [line.strip() for line in file.readlines()]

# Read progress
if os.path.exists(progress_file):
    with open(progress_file, "r") as file:
        progress_data = file.read().strip().split(',')
        last_keyword = progress_data[0] if len(progress_data) > 0 else None
        last_date_index = int(progress_data[1]) if len(progress_data) > 1 else 0
else:
    last_keyword = None
    last_date_index = 0

resume = False
for keyword in keywords:
    if last_keyword and keyword != last_keyword:
        continue  # Skip until we reach the last processed keyword
    
    resume = True  # Start processing once we reach the last processed keyword
    if not resume:
        continue

    try:
        file_name = keyword.replace("#", "").replace(" ", "_").replace("OR", "_or_")
        
        for i in range(last_date_index, len(dates) - 1):
            since_date = dates[i]
            until_date = dates[i + 1]
            search_keyword = f"{keyword} since:{since_date} until:{until_date} lang:id"
            filename = f"{file_name}_{since_date}.csv"
            data_path = f"tweets-data/{filename}"
            limit = 1000
            tab_option = "LATEST"
            
            # Save progress
            with open(progress_file, "w") as file:
                file.write(f"{keyword},{i}")
            
            # Remove existing file if present
            if os.path.exists(data_path):
                os.remove(data_path)
                print(f"Removed existing file: {data_path}")
            
            command = f"npx -y tweet-harvest@2.6.1 -o {filename} -s \"{search_keyword}\" --tab {tab_option} -l {limit} --token {twitter_auth_token}"
            
            subprocess.run(command, shell=True, check=True)
            
            with open(data_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if not first_line :
                    os.remove(data_path)
                    tab_option = "TOP"
                    command = f"npx -y tweet-harvest@2.6.1 -o {filename} -s \"{search_keyword}\" --tab {tab_option} -l {limit} --token {twitter_auth_token}"
                    subprocess.run(command, shell=True, check=True)
        
        send_email(f"Keyword Processed: {keyword}", f"Keyword '{keyword}' has been successfully processed.")
        
    except subprocess.CalledProcessError as e:
        error_message = f"Error processing keyword '{keyword}': {traceback.format_exc()}"
        send_email("Tweet Harvest Error", error_message)
        print(error_message)
        break