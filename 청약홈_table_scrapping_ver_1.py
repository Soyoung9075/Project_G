from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from html_table_parser import parser_functions
import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

URL = "https://www.applyhome.co.kr/co/coa/selectMainView.do"

# Function to extract rows from the table on a given page
def extract_table_rows(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    info = soup.find('div', attrs = {"class" : "mt_10"})
    p = parser_functions.make2d(info)
    df = pd.DataFrame(data = p[1:], columns = p[0])
    return df

browser = webdriver.Chrome(ChromeDriverManager().install())
browser.get(URL)

# remove AD popup
#find = browser.find_element(By.XPATH, '//*[@id="pop_info"]/div/div/div[2]/div[2]/button')
#find.click()

# 분양정보/경쟁률
find = browser.find_element(By.XPATH, '//*[@id="tab1"]/ul/li[1]/a')
find.click()

# 연도 지정하기
start_year = browser.find_element(By.XPATH, '//*[@id="start_year"]')
start_year.click()
year_1 = browser.find_element(By.XPATH, '//*[@id="start_year"]/option[59]') #2018년 9월
browser.execute_script("arguments[0].scrollIntoView(true);", year_1)
year_1.click()

end_year = browser.find_element(By.XPATH, '//*[@id="end_year"]')
end_year.click()
year_2 = browser.find_element(By.XPATH, '//*[@id="end_year"]/option[49]') #2019년 8월
browser.execute_script("arguments[0].scrollIntoView(true);", year_2)
year_2.click()

# 주택 구분
type = browser.find_element(By.XPATH, '//*[@id="cate01"]')
type.click()
type_pv = browser.find_element(By.XPATH, '//*[@id="cate01"]/option[2]') # 민영 선택
type_pv.click()

# 조회
check = browser.find_element(By.XPATH, '//*[@id="pbSearchForm"]/div[2]/button')
check.click()

######################################
# current page
curPage = 1

# entire page
totalPage = 10

final_df = pd.DataFrame()
while curPage <= totalPage:
    try:
        page_source = browser.page_source

        df = extract_table_rows(page_source)
        print(df)
        final_df = pd.concat([final_df,df], axis = 0)

        # 페이지 수 증가
        curPage += 1

        if curPage > totalPage:
            browser.find_element(By.XPATH, '//*[@id="paging"]/a[3]').click() # 화살표 누르기
            curPage = 1

        # 페이지 이동 클릭
        cur_css = '#paging > div > a:nth-child({})'.format(curPage)
        # WebDriverWait(browser,3).until(EC.presence_of_element_located((By.CSS_SELECTOR,cur_css))).send_keys(Keys.ENTER)
        browser.find_element(By.CSS_SELECTOR, cur_css).click()
    except NoSuchElementException:
        print("Table or element not found")
        break

#저장하기
os.chdir('C:/Users/soyou/Desktop/python/web crawling')
final_df.to_csv('apart_table_1809-1908_민영.csv', index = False, encoding='utf-8-sig')





# Find the element that changes when you navigate to the next page
#next_page_element = browser.find_element(By.XPATH, '//*[@id="paging"]/div/a[2]')
#next_page_element.click()

#page_source_2 = browser.page_source
#df2 = extract_table_rows(page_source_2)
#print(df2)


