import csv
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager


class Scrapper:
    def __init__(self, product, size, pincode):
        self.base = 'https://amazon.in'
        self.final_data = ['Brand', 'Name', 'Price', 'Url', 'Tat']
        self.product = product
        self.size = size
        self.pincode = pincode
        self.rows = []
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install())

    def get_url(self, item):
        item = item.replace(' ', '+')
        url = 'https://www.amazon.in/s?k={}&ref=nb_sb_noss'
        return url.format(item)

    def get_item_data_link(self, item):
        atag = item.a['href']
        return self.base + atag

    def get_brand(self, item):
        brand = item.find('h5', {'class': 's-line-clamp-1'})
        return brand.get_text()

    def get_name(self, item):
        name = item.find('h2', {'class': 's-line-clamp-2'})
        return name.get_text()

    def get_price(self, item):
        price = item.find('span', {'class': 'a-price-whole'})
        return price.get_text()

    def get_tat(self, item):
        tat = item.find(
            'div', {'id': 'mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE'})

        return list(tat.strings)[3].strip()

    def get_exact_page(self):
        drop = self.driver.find_element(
            By.NAME, value="dropdown_selected_size_name")
        down = Select(drop)
        time.sleep(3)
        down.select_by_visible_text(self.size)
        time.sleep(3)

        location = self.driver.find_element(
            By.XPATH, value='//*[@id="contextualIngressPtLabel_deliveryShortLine"]')
        location.click()
        time.sleep(3)
        inp_text = self.driver.find_element(
            By.XPATH, value=' //input[@id="GLUXZipUpdateInput"]')
        inp_text.send_keys(self.pincode)
        sub = self.driver.find_element(
            By.XPATH, value='//*[@id="GLUXZipUpdate"]')
        time.sleep(3)
        sub.click()
        time.sleep(2)

        suop = BeautifulSoup(self.driver.page_source, "html.parser")

        return self.get_tat(suop)
        '''
        print("tat------->", get_tat(suop))
        brand,name , price ,url,tat
        []
        '''

    def get_next_page(self):
        print("going to the next page --------23444")
        suop = BeautifulSoup(self.driver.page_source, "html.parser")
        next_page = suop.find(
            'a', {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"})
        print("link-----------", self.base+next_page['href'])
        return self.base+next_page['href']

    def export_to_csv(self):
        with open('products.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            #writer.writerow(self.final_data)

            # write multiple rows
            writer.writerows(self.rows)

    def scrape_page(self):
        suop = BeautifulSoup(self.driver.page_source, "html.parser")
        results = suop.find_all(
            'div', {'data-component-type': "s-search-result"})

        for i in range(2):
            temp = []
            url = self.get_item_data_link(results[i].find(
                'span', {'data-component-type': 's-product-image'}))

            temp.append(self.get_brand(results[i]))
            temp.append(self.get_name(results[i]))
            temp.append(self.get_price(results[i]))
            temp.append(url)
            self.driver.get(url)
            temp.append(self.get_exact_page())
            self.rows.append(temp)

        self.export_to_csv()

    def main(self):
        try:
            self.driver.get(self.get_url(self.product))
            time.sleep(3)

            # first page
            self.scrape_page()

            # starts from 2nd page if exits

            for i in range(2):
                print("going to the next page----------------")
                self.rows = []
                self.driver.get(self.get_next_page())
                time.sleep(3)
                self.scrape_page()

        except Exception as e:
            print(e)
        '''
        url 
        brand 
        name 
        price
        '''


if __name__ == '__main__':
    scrapper = Scrapper("Tshirts", "M", "761211")
    scrapper.main()
