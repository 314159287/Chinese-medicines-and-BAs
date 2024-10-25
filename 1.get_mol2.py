from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import re
import sys
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


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
# ChromeDriverManager().install()只能下载到114版本的driver
# chrome114版本后需要手动下载https://registry.npmmirror.com/binary.html?path=chrome-for-testing/
# service = Service(ChromeDriverManager().install())
chrome_driver_path = "F:\\chromedriver-win64\\chromedriver.exe" # 本地的路径，要修改
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 检查参数数量
if len(sys.argv) != 4:
    print("Num error,Example: python get_mol2_2.py term1,term2,term3 output_pathway download_pathway")
    sys.exit(1)

search_terms = sys.argv[1].split(',')
output_directory = sys.argv[2]
download_directory = sys.argv[3]


# 关键词搜索
for search_term in search_terms:
    search_term = search_term.strip()  # 移除空白字符
    print(f"\nProcessing search term: {search_term}")

    driver.get("https://old.tcmsp-e.com/tcmsp.php")  # 定位主页

    # 等待搜索框加载
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[1]/form/div/input[1]"))
    )

    # 清除默认文本
    search_box.clear()

    # 提交搜索词
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    # 等待结果加载
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    try:
        first_result_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                # 捕捉页面的跳转网址
                (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[3]/a"))
        )
        first_result_link.click()
        print("Successfully clicked on the first search result.")

        # 跳转新网址
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Navigated to the new page.")
    except Exception as e:
        print(f"Error clicking on the first search result: {e}")

    # 确保写入目录存在
    os.makedirs(output_directory, exist_ok=True)

    def find_mol2_links():
        # XPath查找
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '.mol2')]")
        return set(link.get_attribute('href') for link in links)

    mol2_links = set()  # 防止重复

    # 搜索词
    try:
        search_content_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "hname"))
        )
        search_content = search_content_element.text  # 提取文本
    except Exception as e:
        print(f"Error extracting search content: {e}")
        search_content = search_term

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
    with open(output_file_path, 'w') as f:
        for link in mol2_links:
            f.write(f"{link}\n")

    print(f"\nAll found .mol2 links saved to file: {output_file_path}")
    print(f"Total .mol2 links found: {len(mol2_links)}")


# 下载
# 确保下载目录存在
os.makedirs(download_directory, exist_ok=True)

def download_file(url, output_dir):
    try:
        response = requests.get(url, stream=True) # 发起下载请求
        response.raise_for_status() # 检查
        filename = os.path.basename(urlparse(url).path)
        filepath = os.path.join(output_dir, filename) # 完整文件路径
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"Successfully downloaded: {filename}"
    except Exception as e:
        return f"Failed to download {url}: {str(e)}"

print("\nStarting download...")
all_links = set()
for filename in os.listdir(output_directory):
    if filename.endswith('.txt'):
        with open(os.path.join(output_directory, filename), 'r') as f:
            links = set(line.strip() for line in f if line.strip()) # 确保链接不重复且不含空行
            all_links.update(links) # 确保链接不重复

print(f"Total unique links found: {len(all_links)}")

# 多线程
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(download_file, url, download_directory): url for url in all_links} #提交下载链接
    for future in as_completed(future_to_url): # 迭代下载任务
        url = future_to_url[future]
        try: # 输出下载结果
            print(future.result())
        except Exception as exc:
            print(f'{url} generated an exception: {exc}')

print("Download process completed.")


driver.quit()


# .\get_mol2_2.py 柴胡,黄芩,白芍,半夏,枳实,大黄,大枣,生姜,枳壳,甘草,陈皮,川芎,香附,人参,茵陈,栀子 C:\\Users\\pc\\Desktop\\mol2 C:\\Users\\pc\\Desktop\\download
