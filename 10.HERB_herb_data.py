import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
import pandas as pd
import csv

# 在chrome加载
chrome_options = Options()
#chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
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
    print("Num error,Example: python 10.HERB_herb_data.py term1,term2,term3 output_pathway")
    sys.exit(1)

search_terms = sys.argv[1].split(',')
output_directory = sys.argv[2]


# 初始化
processed_first_column = set() #查重用
df = pd.DataFrame()  # 储存数据
column_names = []  # 存储列名


def extract_table_data():
    table_data = []

    # 等待表格加载
    table = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ant-table-wrapper')][1]//table"))
    )


    # 获取表体数据
    rows = table.find_elements(By.XPATH, ".//tbody/tr")
    for row in rows:
        cells = row.find_elements(By.XPATH, ".//td")
        row_data = [cell.text for cell in cells]
        table_data.append(row_data)

    return table_data


try:
    table_data = extract_table_data()
    for row in table_data:
        print(row)
except Exception as e:
    print(f"An error occurred: {str(e)}")


# 关键词搜索
for index, search_term in enumerate(search_terms):
    search_term = search_term.strip()
    print(f"\nProcessing search term: {search_term}")

    driver.get("http://herb.ac.cn/")  # 定位主页

    # 等待搜索框加载
    search_box = WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ant-select-selection__placeholder"))
    )


    search_input = driver.find_element(By.CSS_SELECTOR, ".ant-select-search__field")
    search_input.send_keys(search_term)
    submit_button = driver.find_element(By.XPATH, "//span[text()='Submit']")
    driver.execute_script("arguments[0].click();", submit_button) # 提交搜索词,JavaScript可以绕过网页交互问题


    driver.execute_script("return document.readyState") # 确定加载完毕
    WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CLASS_NAME, "ant-typography")))
    print("Successfully to search result.")

    # 匹配药材中文名，第二次跳转，到分子页
    try:
        # 找到表格
        table = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # 找到所有行
        rows = table.find_elements(By.TAG_NAME, "tr")

        # 遍历行
        matching_row = None
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 0:
                chinese_name = cells[2].text  # 中文名称在第3列
                if chinese_name == search_term:
                    matching_row = row
                    break

        if matching_row:
            # 点击匹配行的第一个链接
            link = matching_row.find_element(By.TAG_NAME, "a")
            link.click()
            print(f"Successfully clicked on the matching result for {search_term}")
        else:
            print(f"No matching result found for {search_term}")
            continue  # 跳到下一个搜索词


    except Exception as e:
        print(f"Error clicking on the matching search result: {e}")
        continue  # 找不到完全匹配的就不记录


    # 打开组分表格
    # time.sleep(3)
    dropdown = WebDriverWait(driver, 40).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ant-select-arrow"))
    )
    dropdown.click()
    large_page = driver.find_element(By.XPATH, "//li[@class='ant-select-dropdown-menu-item' and text()='50 / page']")
    driver.execute_script("arguments[0].click();", large_page) #扩展页数的窗口是一个弹窗，用Javascript绕过网页交互
    # 等待加载
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "table")))


    # 捕获列名
    if index == 0:
        try:
            for i in range(1, 4):
                element = WebDriverWait(driver, 40).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class=\"ant-table-body\"]/table[1]//thead/tr/th[{i}]")))
                column_names.append(element.text)
            print("get column name.")

        except Exception as e:
            print(f"Error getting column names: {e}")
            column_names = [f"Column {i}" for i in range(1, 4)]


    # 获取总页数
    try:
        #选择第一个匹配到ant-table-wrapper的元素，定位包含ant-pagination-item的所有li元素
        page_elements = WebDriverWait(driver, 40).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//div[contains(@class, 'ant-table-wrapper')])[1]//li[contains(@class, 'ant-pagination-item')]"))
        )
        if page_elements:
            last_page_element = page_elements[-1]  # 取最后一个元素
            total_pages = int(last_page_element.text)
            print("total_pages:", total_pages)
        else:
            print("No pagination found, assuming there's only one page")
            total_pages = 1

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        total_pages = 1


    # 判断翻页
    current_page = 1
    all_data = []

    while True:
        # 获取当前页面所有数据
        page_data = extract_table_data()
        all_data.extend(page_data)

        if current_page >= total_pages:
            break

        # 检查有没有下一页
        try:
            # 网页同属性的按钮太多了，要多定位几个属性
            next_button = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.ant-pagination-next"))
            )
            next_button.click()
            current_page += 1
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

# 只能使用中文检索
# python 10.HERB_herb_data.py 柴胡,黄芩,白芍,半夏,枳实,大黄,大枣,生姜,枳壳,甘草,陈皮,川芎,香附,人参,茵陈蒿,栀子 C:\\Users\\pc\\Desktop\\HERB_herb_data.csv

