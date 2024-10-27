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
import sys
import pandas as pd
import csv

# 在chrome加载
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')  # 禁用GPU
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
chrome_driver_path = "F:\\chromedriver-win64\\chromedriver.exe" # 本地的路径
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 检查参数数量
if len(sys.argv) != 3:
    print("Num error,Example: python get_mol2_2.py term1,term2,term3 output_pathway")
    sys.exit(1)

search_terms = sys.argv[1].split(',')
output_directory = sys.argv[2]

# 初始化
processed_first_column = set() #查重用
df = pd.DataFrame()  # 储存数据
column_names = []  # 存储列名


# 关键词搜索
for index, search_term in enumerate(search_terms):
    search_term = search_term.strip()
    print(f"\nProcessing search term: {search_term}")

    driver.get("https://old.tcmsp-e.com/tcmsp.php")  # 定位主页

    # 等待搜索框加载
    search_box = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[1]/form/div/input[1]"))
    )

    # 清除默认文本
    search_box.clear()

    # 提交搜索词
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)

    # 等待结果加载
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    try:
        first_result_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                # 捕捉页面的跳转网址
                (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[3]/a"))
        )
        first_result_link.click()
        print("Successfully clicked on the first search result.")

        # 跳转新网址
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Navigated to the new page.")
    except Exception as e:
        print(f"Error clicking on the first search result: {e}")


    # 捕获列名
    if index == 0:
        try:
            for i in range(1, 13):  # 12列
                xpath = f"/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[1]/div/table/thead/tr/th[{i}]/a[2]"
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                column_names.append(element.text)
        except Exception as e:
            print(f"Error getting column names: {e}")
            column_names = [f"Column {i}" for i in range(1, 13)]


    def extract_row_data(row_number):
        # 捕获单行数据
        data = []
        for col in range(1, 13):
            try:
                xpath = f"/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[2]/table/tbody/tr[{row_number}]/td[{col}]"
                element = driver.find_element(By.XPATH, xpath)
                data.append(element.text)
            except:
                data.append("")
        return data


    def process_page():
        # 捕获所有行
        new_data = []
        row = 1
        while True:
            try:
                # 获取第一列的数据：分子名称
                first_col_xpath = f"/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[2]/table/tbody/tr[{row}]/td[1]"
                first_col_element = driver.find_element(By.XPATH, first_col_xpath)
                first_col_value = first_col_element.text

                # 以第一列的数据为依据，查重
                if first_col_value not in processed_first_column:
                    row_data = extract_row_data(row) # 捕获目前行的数据
                    new_data.append(row_data)
                    processed_first_column.add(first_col_value)

                row += 1
            except:
                break
        return new_data


    # 判断翻页
    current_page = 1
    all_data = []

    while True:
        # 等待加载
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # 获取当前页面所有数据
        page_data = process_page()
        all_data.extend(page_data)

        # 获取总页数
        try:
            last_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/div[2]/div[2]/div[2]/div[1]/div/div[3]/a[4]"))
            )
            total_pages = int(last_page_element.get_attribute('data-page'))
        except:
            print("Unable to find total pages, assuming there's only one page")
            total_pages = 1

        if current_page >= total_pages:
            break

        # 检查有没有下一页
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Go to the next page')]"))
            )
            next_button.click()
            current_page += 1
            time.sleep(2)
        except:
            break

    # 将新数据添加到DataFrame
    if all_data:
        new_df = pd.DataFrame(all_data)
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

    # 写入csv
    try:
        # 确保写入目录存在
        output_dir = os.path.dirname(output_directory)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 写入
        with open(output_directory, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(df.values)
        print(f"Successfully saved data to {output_directory}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        # 另存到当前目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        alternative_path = os.path.join(current_dir, 'output.csv')
        print(f"Trying to save to alternative path: {alternative_path}")
        df = pd.DataFrame(df.values, columns=column_names)
        df.to_csv(alternative_path, index=False, encoding='utf-8-sig')

driver.quit()


# python 7.molecule_data.py 柴胡,黄芩,白芍,半夏,枳实,大黄,大枣,生姜,枳壳,甘草,陈皮,川芎,香附,人参,茵陈,栀子 C:\\Users\\pc\\Desktop\\mol_data.csv

