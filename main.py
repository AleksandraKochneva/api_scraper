import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pymongo import MongoClient
import logging

url = "https://www.fragrantica.com/search/?query=donna"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_api_key():
    logging.info('get_api_key started')
    path = os.path.dirname(os.path.abspath(__file__))+'/chromedriver/chromedriver'
    options = Options()
    options.add_argument("--headless")  # Run headless for CI environments
    s = Service(path)  # Path to ChromeDriver
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (optional)
    options.add_argument("--no-sandbox")  # Bypass OS security model (Linux only)
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems (Linux only)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(service=s, options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': '''
            cdc_adoQpoasnfa76pfcZLmcfl_Array;
            cdc_adoQpoasnfa76pfcZLmcfl_JSON;
            cdc_adoQpoasnfa76pfcZLmcfl_Object;
            cdc_adoQpoasnfa76pfcZlmcfl_Promise;
            cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
            cdc_adoQpoasnfa76pfcZLmcf1_Symbol;
            '''})
    try:
        driver.get(url=url)
        driver.maximize_window()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "link-span"))
        )

        def get_network_logs(driver):
            logs = driver.get_log('performance')
            network_logs = []
            for log in logs:
                log_json = json.loads(log['message'])
                message = log_json['message']
                if message['method'] == 'Network.responseReceived':
                    url = message['params']['response']['url']
                    if 'queries' in url:
                        network_logs.append(message['params'])
            return network_logs

        network_log = get_network_logs(driver)[0]
        driver.quit()
        result = network_log['response']['url']
        logging.info('API key parsed')
        return result
    except:
        logging.error('api key parsing failed')


def upload_url(string):
    try:
        client = MongoClient(
            "mongodb+srv://saleuzi4:PbKd7gLKT70VK0wD@cluster0.2mmbfbi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client['scent_db']
        collection = db['keys']
        query = {"fraga_key": {"$exists": True}}
        new_values = {"$set": {"fraga_key": string}}
        collection.update_one(query, new_values, upsert=True)
        logging.info('New api key uploaded')
        client.close()
    except:
        logging.error('New api key upload failed')


def main():
    string = get_api_key()
    upload_url(string)


if __name__ == '__main__':
    main()
