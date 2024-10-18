from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re


# 初始化
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('enable-automation')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('enable-features=NetworkServiceInProcess')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(chrome_options, service)

# 读取URL
with open('./link_db', 'r') as file:
    urls = file.read().splitlines()

# 保存的文件夹
output_directory = './test'
os.makedirs(output_directory, exist_ok=True)

def find_mol2_links():
    # XPath查找
    links = driver.find_elements(By.XPATH, "//a[contains(@href, '.mol2')]")
    return set(link.get_attribute('href') for link in links)

for url in urls:

    driver.get(url)
    mol2_links = set()  # 防止重复


    # 搜索词
    try:
        search_content_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "hname"))
        )
        search_content = search_content_element.text  # 提取文本
    except Exception as e:
        print(f"Error extracting search content: {e}")
        search_content = "default"

    # 去除无效字符
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', search_content)


    current_page = 1
    while True:
        # 等待加载完成
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # 查找链接
        page_mol2_links = find_mol2_links()
        mol2_links.update(page_mol2_links)
        print(f"Found {len(page_mol2_links)} mol2 links on page {current_page}")

        # 获取总页数
        try:
            last_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[3]/a[4]"))
            )
            total_pages = int(last_page_element.get_attribute('data-page'))
        except:
            print("Unable to find total pages, assuming there's only one page")
            total_pages = 1

        print(f"Processed page {current_page} of {total_pages}")

        if current_page >= total_pages:
            break

        # 翻页
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Go to the next page')]"))
            )
            next_button.click()
            current_page += 1
            time.sleep(2)  # 等待页面加载
        except:
            print("Unable to find or click next page button, ending process")
            break

    # 保存到文件夹
    output_file_path = os.path.join(output_directory, f'{safe_filename}.txt')
    with open(output_file_path, 'a') as f:
        for link in mol2_links:
            f.write(f"{link}\n")
    print(f"\nAll found .mol2 links saved to file for URL: {url}")
    print(f"Total .mol2 links found for this URL: {len(mol2_links)}")

driver.quit()
