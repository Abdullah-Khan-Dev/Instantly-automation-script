from pandas import json_normalize
from playwright.sync_api import sync_playwright
import requests
import json
import time
import random
import pandas as pd
from lxml import html


def save_session(context):
    storage = context.storage_state(path="session.json")


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
    get_sheet()
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


def get_authorization_email(page, xpath, to_find):
    page.bring_to_front()
    while True:
        page.locator('//span[text()="Primary"]').click()
        random_delay(5, 10)
        page.locator('//span[text()="Others"]').click()
        random_delay()
        first_email = page.locator('//li[contains(@class,"MuiListItem-root")]').first.inner_html()
        tree = html.fromstring(first_email)
        microsoft_email = tree.xpath(xpath)
        if microsoft_email is not None:
            break
    page.locator('//p[text()="account-security-noreply@accountprotection.microsoft.com"]').first.click()
    random_delay()
    text = page.locator().text_content(to_find)
    if text is not None:
        return text
    return None


def get_number():
    number_response = requests.get(
        'https://api.sms-man.com/control/get-number?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&country_id=49206&application_id=2437315')
    if number_response.status_code == 200:
        return number_response.json()['request_id'], number_response.json()['number']


def get_sms(request_id):
    sms_response = requests.get(f'https://api.sms-man.com/control/get-sms?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&request_id={request_id}')
    try:
        number_verification_code = sms_response.json()['sms_code']
        return number_verification_code
    except:
        get_sms(request_id)


def update_sheet(email, new_status):
    df = pd.read_csv('accounts.csv')
    if email in df['email'].values:
        df.loc[df['email'] == email, 'status'] = new_status
        df.to_csv('accounts.csv', index=False)


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
            page.locator('//input[@placeholder="Search..."]').type(each_account['email'])
            random_delay(5, 10)
            page.locator('//button[contains(@class, "css-1yxmbwk")]').click()
            random_delay(2, 5)
            page.locator('//span[text()="Reconnect account"]').click()
            random_delay(4, 7)
            div = page.locator('//div[h5[text()="Connect a new email account"]]')
            div.locator('//p[text()="Microsoft"]').click()
            random_delay()
            page.locator('//button[text()="Yes, SMTP has been enabled"]').click()
            random_delay()
            page.locator('//h6[text()="Back"]').click()
            microsoft_page = context.pages[1]
            random_delay()
            microsoft_page.bring_to_front()
            microsoft_page.locator('//input[@type="email"]').type(each_account['email'])
            random_delay()
            microsoft_page.locator('//input[@value="Next"]').click()
            random_delay()
            try:
                microsoft_page.locator('//input[@type="password"]').type(error_email_password(each_account['email']))
                random_delay()
                microsoft_page.locator('//button[text()="Sign in"]').click()
                random_delay()
                microsoft_page.locator('//input[@name="proof"]').click()
                random_delay()
                page.locator('//button[@id="sidebar_icon_unibox"]').click()
                random_delay()
                recovery_email = get_authorization_email(page,
                                                         '//p[text()="account-security-noreply@accountprotection.microsoft.com"]',
                                                         '//span[contains(text(),"@outlook.com")]')
                random_delay()
                microsoft_page.locator('//input[@type="email"]').type(recovery_email)
                random_delay()
                microsoft_page.locator('//input[@value="Send code"]').click()
                random_delay()
                code = get_authorization_email(page,
                                               '//p[text()="account-security-noreply@accountprotection.microsoft.com"]',
                                               '//td[contains(text(),"Security code:")]/span')
                microsoft_page.locator('//input[@name="iOttText"]').type()
                random_delay()
                microsoft_page.locator('//input[@value="Next"]').click()
                random_delay()
            except:
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                dropdown = microsoft_page.locator('//select[@id="phoneCountry"]')
                dropdown.click()
                dropdown.select_option(value="ID")
                random_delay()
                responses = get_number()
                microsoft_page.locator('//input[@name="proofField"]').type(responses[0])
                random_delay()
                microsoft_page.locator('//button[text()="Next"]').click()
                random_delay()
                requests.get(f'https://api.sms-man.com/control/set-status?token=nB7QCK0NGGVvjajfGyI9iRbmeRRsgm1A&request_id={responses[1]}&status=close')
                save_session(context)
            browser.close()


if __name__ == '__main__':
    get_accounts_from_instantly()
