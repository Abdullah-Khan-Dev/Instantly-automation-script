from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import requests
import time
import random
import pandas as pd
import html
from bs4 import BeautifulSoup


def save_session(context):
    context.storage_state(path="session.json")


def load_session(browser):
    try:
        context = browser.new_context(storage_state="session.json")
    except FileNotFoundError:
        context = browser.new_context()
    return context


def random_delay(min_delay=3, max_delay=7):
    time.sleep(random.uniform(min_delay, max_delay))


def human_type(element, text):
    for char in text:
        element.type(char)
        time.sleep(random.uniform(0.10, 0.20))
        if random.random() < 0.1:
            element.type(random.choice('abcdefghijklmnopqrstuvwxyz'))
            time.sleep(random.uniform(0.2, 0.5))
            element.press('Backspace')


def get_sheet():
    url = "https://docs.google.com/spreadsheets/d/19HtzmJSpjnIzecL0zRt7T0q9IDvEMph4FF2iHMCiexk/gviz/tq?tqx=out:csv&sheet=Instantly master account sheet"
    response = requests.get(url)
    if response.status_code == 200:
        with open("accounts.csv", 'wb') as file:
            file.write(response.content)


def login(page):
    email = page.locator('//input[@name="email"]')
    human_type(email, "abdullah_khan.dev@proton.me")
    password = page.locator('//input[@name="password"]')
    human_type(password, "Li5b$PEzr.a?Hi3")
    page.locator('//button[text()="Log In"]').click()


def get_accounts_from_instantly():
    pass


def get_error_emails():
    df = pd.read_csv('accounts.csv')
    connection_error_accounts = df[df['status'] == 'connection_error']
    return connection_error_accounts[['email', 'password']].to_dict(orient='records')


def error_email_password(email):
    df = pd.read_csv('accounts.csv')
    matching_row = df[df['email'] == email]
    if not matching_row.empty:
        password = matching_row['password'].values[0]
        if password:
            return password
        else:
            return None
    else:
        return None


def get_authorization_email(page, to_find):
    page.bring_to_front()
    attempts = 0
    while attempts <= 1:
        page.locator('//span[text()="Primary"]').click()
        random_delay(8, 10)
        page.locator('//span[text()="Others"]').click()
        random_delay()
        try:
            page.locator('//p[text()="account-security-noreply@accountprotection.microsoft.com"]').first.click()
            random_delay()
            email_time = page.locator('//div[@class="text-right"]/p').text_content().strip()
            if email_time:
                extracted_time = datetime.strptime(email_time, "%A, %b %d, %Y at %I:%M %p")
                local_timezone = datetime.now().astimezone().tzinfo
                extracted_time = extracted_time.replace(tzinfo=local_timezone)
                extracted_time_utc = extracted_time.astimezone(timezone.utc)
                current_time_utc = datetime.now(timezone.utc)
                if str(extracted_time_utc.strftime('%H:%M')) == str(current_time_utc.strftime('%H:%M')) or abs(
                        (current_time_utc - extracted_time_utc).total_seconds()) <= 130:
                    try:
                        if to_find == '//td[@id="i4"]/span':
                            inner_html = page.inner_html('//div[@class="rounded mt-4"]')
                            unescaped_html = html.unescape(inner_html)
                            soup = BeautifulSoup(unescaped_html, 'html.parser')
                            return soup.find('span').text
                        return page.locator(to_find).text_content()
                    except:
                        attempts += 1
                else:
                    attempts += 1
            else:
                attempts += 1
        except:
            attempts += 1
    return None


def microsoft_verification():
    pass


def get_number():
    number_response = requests.get(
        'https://api.sms-man.com/control/get-number?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&country_id=5&application_id=133')
    if number_response.status_code == 200:
        return number_response.json()['request_id'], number_response.json()['number']


def get_sms(request_id):
    attempts = 0
    while attempts < 2:
        time.sleep(20)
        sms_response = requests.get(
            f'https://api.sms-man.com/control/get-sms?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&request_id={request_id}')
        try:
            number_verification_code = sms_response.json()['sms_code']
            return number_verification_code
        except KeyError:
            attempts += 1
    requests.get(
        f'https://api.sms-man.com/control/set-status?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&request_id={request_id}&status=reject')
    return None


def update_sheet(email):
    df = pd.read_csv('accounts.csv')
    if email in df['email'].values:
        df.loc[df['email'] == email, 'status'] = new_status
        df.to_csv('accounts.csv', index=False)


def get_status(email):
    url = f"https://api.instantly.ai/api/v1/account/status?api_key=6kfpm446cgmqdrm60x0xxmmbk719&email={email}"
    response = requests.request("GET", url)
    return response.json()['status']


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-infobars",
            "--enable-automation",
            "--no-first-run",
            "--enable-webgl",
        ])

        context = load_session(browser)

        page = context.new_page()
        page.goto('https://app.instantly.ai/app/accounts', timeout=600000)
        if "login" in page.url:
            login(page)

        random_delay()
        for each_account in get_error_emails():
            try:
                page.locator('//input[@placeholder="Search..."]').type(each_account['email'])
                random_delay(5, 10)
            except:
                page.locator('//button[@id="sidebar_icon_accounts"]').click()
                continue
            page.locator('//button[contains(@class, "css-1yxmbwk")]').click()
            random_delay(2, 5)
            page.locator('//span[text()="Reconnect account"]').click()
            random_delay(4, 7)
            div = page.locator('//div[h5[text()="Connect a new email account"]]')
            div.locator('//p[text()="Microsoft"]').click()
            random_delay()
            page.locator('//button[text()="Yes, SMTP has been enabled"]').click()
            random_delay(5, 10)
            page.locator('//h6[text()="Back"]').click()
            microsoft_page = context.pages[1]
            random_delay()
            microsoft_page.bring_to_front()
            microsoft_page.locator('//input[@type="email"]').type(each_account['email'])
            random_delay()
            microsoft_page.locator('//input[@value="Next"]').click()
            random_delay()
            if microsoft_page.wait_for_selector('//span[text()="Use your password instead"]', timeout=3000):
                microsoft_page.locator('//span[text()="Use your password instead"]').click()
            microsoft_page.locator('//input[@type="password"]').type(
                error_email_password(each_account['email']))
            random_delay()
            microsoft_page.locator('//button[text()="Sign in"]').click()
            random_delay()
            if microsoft_page.wait_for_selector('//input[@id="iProof0"]', timeout=3000):
                microsoft_page.locator('//input[@id="iProof0"]').click()
                random_delay()
                page.locator('//button[@id="sidebar_icon_unibox"]').click()
                random_delay()
                recovery_email = get_authorization_email(page, '//span[contains(text(),"@outlook.com")]')
                if recovery_email is None:
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    random_delay()
                    continue
                random_delay()
                microsoft_page.bring_to_front()
                microsoft_page.locator('//input[@type="email"]').type(recovery_email)
                random_delay()
                microsoft_page.locator('//input[@value="Send code"]').click()
                random_delay()
                code = get_authorization_email(page, '//td[@id="i4"]/span')
                if code is None:
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    random_delay()
                    continue
                microsoft_page.bring_to_front()
                microsoft_page.locator('//input[@id="iOttText"]').type(code)
                random_delay()
                microsoft_page.locator('//input[@value="Next"]').click()
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                dropdown = microsoft_page.locator('//select[@id="phoneCountry"]')
                dropdown.click()
                dropdown.select_option(value="ID")
                random_delay()
                responses = get_number()
                microsoft_page.locator('//input[@name="proofField"]').type(f"{responses[1][2:]}")
                random_delay()
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                if microsoft_page.locator('//div[@id="SmsBlockTitle"]'):
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    continue
                verification_code = get_sms(responses[0])
                if verification_code is None:
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    random_delay()
                    continue
                microsoft_page.locator('//input[@id="enter-code-input"]').type(verification_code)
                microsoft_page.locator('//button[@id="nextButton"]').click()
                if microsoft_page.locator('//div[text()="Something went wrong."]'):
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    continue
                # Exception Handled Again Email Verification
                if microsoft_page.wait_for_selector('//input[@id="iProof0"]', timeout=3000):
                    microsoft_page.locator('//input[@id="iProof0"]').click()
                    random_delay()
                    page.locator('//button[@id="sidebar_icon_unibox"]').click()
                    random_delay()
                    recovery_email = get_authorization_email(page, '//span[contains(text(),"@outlook.com")]')
                    if recovery_email is None:
                        microsoft_page.close()
                        page.locator('//button[@id="sidebar_icon_accounts"]').click()
                        random_delay()
                        continue
                    random_delay()
                    microsoft_page.bring_to_front()
                    microsoft_page.locator('//input[@type="email"]').type(recovery_email)
                    random_delay()
                    microsoft_page.locator('//input[@value="Send code"]').click()
                    random_delay()
                    code = get_authorization_email(page, '//td[@id="i4"]/span')
                    if code is None:
                        microsoft_page.close()
                        page.locator('//button[@id="sidebar_icon_accounts"]').click()
                        random_delay()
                        continue
                    microsoft_page.bring_to_front()
                    microsoft_page.locator('//input[@id="iOttText"]').type(code)
                    random_delay()
                    microsoft_page.locator('//input[@value="Next"]').click()
                    microsoft_page.locator('//button[text()="Next"]').click()
                    random_delay()
                    dropdown = microsoft_page.locator('//select[@id="phoneCountry"]')
                    dropdown.click()
                    dropdown.select_option(value="ID")
                    random_delay()
                    responses = get_number()
                    microsoft_page.locator('//input[@name="proofField"]').type(f"{responses[1][2:]}")
                    random_delay()
                    microsoft_page.locator('//button[text()="Next"]').click()
                    random_delay()
                    if microsoft_page.locator('//div[@id="SmsBlockTitle"]'):
                        microsoft_page.close()
                        page.locator('//button[@id="sidebar_icon_accounts"]').click()
                        continue
                    verification_code = get_sms(responses[0])
                    if verification_code is None:
                        microsoft_page.close()
                        page.locator('//button[@id="sidebar_icon_accounts"]').click()
                        random_delay()
                        continue
                    microsoft_page.locator('//input[@id="enter-code-input"]').type(verification_code)
                    microsoft_page.locator('//button[@id="nextButton"]').click()
                    if microsoft_page.locator('//div[text()="Something went wrong."]'):
                        microsoft_page.close()
                        page.locator('//button[@id="sidebar_icon_accounts"]').click()
                        continue
            else:
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                dropdown = microsoft_page.locator('//select[@id="phoneCountry"]')
                dropdown.click()
                dropdown.select_option(value="ID")
                random_delay()
                responses = get_number()
                microsoft_page.locator('//input[@name="proofField"]').type(f"{responses[1][2:]}")
                random_delay()
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                if microsoft_page.locator('//div[@id="SmsBlockTitle"]'):
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    continue
                verification_code = get_sms(responses[0])
                if verification_code is None:
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    random_delay()
                    continue
                microsoft_page.locator('//input[@id="enter-code-input"]').type(verification_code)
                microsoft_page.locator('//button[@id="nextButton"]').click()
                if microsoft_page.locator('//div[text()="Something went wrong."]'):
                    microsoft_page.close()
                    page.locator('//button[@id="sidebar_icon_accounts"]').click()
                    continue
            update_sheet(each_account['email'])
        save_session(context)
        browser.close()


if __name__ == '__main__':
    main()



