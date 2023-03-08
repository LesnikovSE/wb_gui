from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as ec
from time import sleep
# import json
# import fake_useragent

URL = 'https://www.wildberries.ru/catalog/muzhchinam/odezhda/dzhempery-i-kardigany'


class MySelenium:
    db = dict()
    name_category = ''

    def __init__(self):
        self.driver = Chrome()
        chrome_options = Options()
        chrome_options.page_load_strategy = 'normal'
        chrome_options.add_argument("--disable-extensions")
        chrome_options.headless = True
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

    def scroll_up(self, obj):
        while not obj.is_displayed():
            self.driver.execute_script("window.scrollBy(0,-50)", "")

    def scroll_down(self, obj):
        while not obj.is_displayed():
            self.driver.execute_script("window.scrollBy(0,50)", "")
        # for i in range(250):
        #     self.driver.execute_script("window.scrollBy(0,50)", "")
        # WebDriverWait(self.driver, 1)

    # collect all product links from the specified number of pages
    def parse_pages(self, url, count_page=0):
        current_page = 1
        indx = 1

        for number in range(count_page):
            self.driver.get(url)
            WebDriverWait(self.driver, 5).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, "div.catalog-title-wrap>span>span")))
            footer = self.driver.find_element(By.CLASS_NAME, 'footer__copyrights')

            self.scroll_down(footer)
            if not footer.is_displayed():
                self.scroll_down(footer)

            cards = self.driver.find_elements(By.XPATH, "//div[@class='product-card__wrapper']/a")
            for card in cards:
                try:
                    link = card.get_attribute('href')
                    self.db[indx] = [link]
                    indx += 1
                except Exception as e:
                    print(e)
                    continue

            if current_page <= count_page:
                current_page += 1
            else:
                break

            # pagination
            next_page_url = self.driver.find_element(By.CSS_SELECTOR, 'a.j-next-page')
            if next_page_url:
                url = next_page_url.get_attribute('href')
            else:
                print("This is the last page. Data collection completed")
                break

    # set number of pages / start crawling pages
    def set_count_pages_and_run(self, url, count_page=0):
        self.driver.get(url)
        WebDriverWait(self.driver, 5).until(
            ec.visibility_of_element_located((By.CSS_SELECTOR, "div.catalog-title-wrap>span>span")))

        self.name_category = self.driver.find_element(
            By.CSS_SELECTOR, "div.catalog-title-wrap>h1"
        ).text.strip()

        count_all_items = self.driver.find_element(By.CSS_SELECTOR, "div.catalog-title-wrap>span>span").text
        count_all_items = int(count_all_items.replace(' ', ''))

        pages = round(count_all_items / 100)
        if count_page == 0:
            # parse all product links by category
            self.parse_pages(url=url, count_page=pages)
        else:
            # parse links from the specified number of pages
            self.parse_pages(url=url, count_page=count_page)

    # collection of all information from the list of links
    def page_item_info(self):
        """
        Collects product information:
        name, brand, article, size, color, price, certified_quality,
        additional information, compound, description
        :return: dict(id: [item_info])
        """
        for k, v in self.db.items():
            self.driver.get(v[0])
            WebDriverWait(self.driver, 5).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, 'div.details-section__inner-wrap')))

            # block - name, brand, article
            raw_name = self.driver.find_element(
                By.CSS_SELECTOR, 'div.product-page__header-wrap>div:nth-child(1)')
            brand = raw_name.find_element(By.TAG_NAME, 'span').text.strip()
            name = raw_name.find_element(By.TAG_NAME, 'h1').text.strip()
            article = self.driver.find_element(By.CSS_SELECTOR, 'p.product-article').text.strip()

            # block - size, color, price
            size_list = self.driver.find_elements(By.XPATH, "//label[@class='j-size']")
            size_list = [i.text.replace('\n', ' ') for i in size_list]
            color_list = self.driver.find_elements(By.CSS_SELECTOR, "li.j-color>a>img")
            color_list = [img.get_attribute('title').strip() for img in color_list]
            price_now = self.driver.find_elements(By.CSS_SELECTOR, 'div.price-block__content>p>span')[1].text
            # price_old = self.driver.find_element(By.CSS_SELECTOR, "div.price-block__content>p>del")

            # block - about the product (left side)
            buttons_unwrap = self.driver.find_elements(By.CSS_SELECTOR, 'div.collapsible__toggle-wrap>button')
            while not buttons_unwrap[1].is_displayed():
                self.driver.execute_script("window.scrollBy(0,25)", "")
            # unwrap characteristic and description
            buttons_unwrap[1].click()
            buttons_unwrap[0].click()

            try:
                certified_quality = self.driver.find_element(By.CSS_SELECTOR, 'p.certificate-check__text').text
            except ExceptionGroup:
                certified_quality = "missing"

            table_info = self.driver.find_elements(By.CSS_SELECTOR, '.j-add-info-section>div>table>tbody>tr')
            additional_info = {}
            for tr in table_info:
                th = tr.find_element(By.CSS_SELECTOR, 'th.product-params__cell').text.strip()
                td = tr.find_element(By.CSS_SELECTOR, 'td.product-params__cell').text.strip()
                additional_info[th] = td

            # block - about the product (right side)
            sections = self.driver.find_elements(By.CSS_SELECTOR, 'section.details-section__details')
            # len(sections) = 3
            description = {
                sections[0].find_element(By.CSS_SELECTOR, 'h3.details__header').text.strip():
                    sections[0].find_element(By.CSS_SELECTOR, 'p.collapsable__text').text.strip()}
            compound = {
                sections[1].find_element(By.CSS_SELECTOR, 'h3.details__header').text.strip():
                    sections[1].find_element(By.CSS_SELECTOR, 'div.j-consist').text.strip()}

            print(brand,
                  name,
                  article,
                  size_list,
                  color_list,
                  price_now,
                  certified_quality,
                  additional_info,
                  description,
                  compound, sep='\n')

            break


if __name__ == '__main__':
    HOST = f"https://www.wildberries.ru/"
    # FAKE_USER = fake_useragent.FakeUserAgent().random
    # HEADERS = {'User-Agent': FAKE_USER}

    s = MySelenium()
    # s.set_count_pages_and_run(URL, 3)

    item_link = 'https://www.wildberries.ru/catalog/141012690/detail.aspx'
    s.db[1] = [item_link, ]
    s.page_item_info()

    sleep(1)
    s.driver.quit()
