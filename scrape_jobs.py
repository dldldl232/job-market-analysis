import os
import smtplib
import time
import random
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

global total_jobs


def configure_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    return driver


def check_for_captcha(driver):
    try:
        captcha_frame = driver.find_element(By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]')
        if captcha_frame:
            print("CAPTCHA detected. Please solve the CAPTCHA manually.")
            input("Press Enter to continue after solving the CAPTCHA...")
    except NoSuchElementException:
        pass


def search_jobs(driver, country, job_position, job_location, date_posted):
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
    print(full_url)
    driver.get(full_url)
    global total_jobs
    try:
        job_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')))
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"
    except Exception as e:
        print(f"Error finding job count: {e}")
        total_jobs = "Unknown"

    driver.save_screenshot('screenshot.png')
    return full_url


def scrape_job_data(driver, country):
    df = pd.DataFrame({'Link': [''], 'Job Title': [''], 'Company': [''],
                       'Employer Active': [''], 'Location': ['']})
    job_count = 0

    while True:
        try:
            # Wait for job listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'job_seen_beacon')))
        except Exception as e:
            print(f"Error waiting for job listings: {e}")
            break

        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_='job_seen_beacon')

        for i in boxes:
            try:
                link = i.find('a', {'data-jk': True}).get('href')
                link_full = country + link
            except (AttributeError, TypeError):
                link_full = None

            try:
                job_title = i.find('a', class_=lambda x: x and 'JobTitle' in x).text.strip()
            except AttributeError:
                job_title = None

            try:
                company = i.find('span', {'data-testid': 'company-name'}).text.strip()
            except AttributeError:
                company = None

            try:
                employer_active = i.find('span', class_='date').text.strip()
            except AttributeError:
                employer_active = None

            try:
                location_element = i.find('div', {'data-testid': 'text-location'})
                location = location_element.text.strip() if location_element else ''
            except AttributeError:
                location = ''

            new_data = pd.DataFrame({'Link': [link_full], 'Job Title': [job_title],
                                     'Company': [company],
                                     'Employer Active': [employer_active],
                                     'Location': [location]})

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        print(f"Scraped {job_count} of {total_jobs}")

        try:
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')
            next_page = country + next_page
            driver.get(next_page)
            time.sleep(random.uniform(2, 5))  # Random delay to reduce detection
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break

    return df


def clean_data(df):
    def posted(x):
        try:
            x = x.replace('EmployerActive', '').strip()
            return x
        except AttributeError:
            pass

    df['Employer Active'] = df['Employer Active'].apply(posted)
    return df


def save_csv(df, job_position, job_location):
    def get_user_desktop_path():
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        return desktop_path

    file_path = os.path.join(get_user_desktop_path(), '{}_{}'.format(job_position, job_location))
    csv_file = '{}.csv'.format(file_path)
    df.to_csv('{}.csv'.format(file_path), index=False)

    return csv_file


def send_email(df, sender_email, receiver_email, job_position, job_location, password):
    sender = sender_email
    receiver = receiver_email
    password = password
    msg = MIMEMultipart()
    msg['Subject'] = 'New Jobs from Indeed'
    msg['From'] = sender
    msg['To'] = ','.join(receiver)

    attachment_filename = generate_attachment_filename(job_position, job_location)

    csv_content = df.to_csv(index=False).encode()

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(csv_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
    msg.attach(part)

    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user=sender, password=password)

    s.sendmail(sender, receiver, msg.as_string())

    s.quit()


def send_email_empty(sender, receiver_email, subject, body, password):
    msg = MIMEMultipart()
    password = password

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ','.join(receiver_email)

    msg.attach(MIMEText(body, 'plain'))

    s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
    s.login(user=sender, password=password)

    s.sendmail(sender, receiver_email, msg.as_string())

    s.quit()


def generate_attachment_filename(job_title, job_location):
    filename = f"{job_title.replace(' ', '_')}_{job_location.replace(' ', '_')}.csv"
    return filename
