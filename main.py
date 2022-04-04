import csv
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager


class Scrapper:
    '''
    Initiliazing the webdriver and the final data format
    '''

    def __init__(self, product, size, pincode):

        self.base = 'https://amazon.in'
        self.final_data = ['Brand', 'Name', 'Price', 'Url', 'Tat']
        self.product = product
        self.size = size
        self.pincode = pincode
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install())

    def get_url(self, item):
        # returns the url for the serached product
        item = item.replace(' ', '+')
        url = 'https://www.amazon.in/s?k={}&ref=nb_sb_noss'
        return url.format(item)

    def get_item_data_link(self, item):
        atag = item.a['href']
        return self.base + atag

    def get_brand(self, item):
        brand = item.find('h5', {'class': 's-line-clamp-1'})
        return brand.get_text() if brand else " "

    def get_name(self, item):
        name = item.find('h2', {'class': 's-line-clamp-2'})
        return name.get_text() if name else " "

    def get_price(self, item):
        price = item.find('span', {'class': 'a-price-whole'})
        return price.get_text() if price else " "

    def get_tat(self, item):
        tat = item.find(
            'div', {'id': 'mir-layout-DELIVERY_BLOCK-slot-DELIVERY_MESSAGE'})

        return list(tat.strings)[3].strip()

    def get_exact_page(self):
        try:
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
        except Exception as e:
            return " "
        '''
        print("tat------->", get_tat(suop))
        brand,name , price ,url,tat
        []
        '''

    def get_next_page(self, suop):
        # extracts the url of the next page and returns
        next_p = suop.find(
            'a', {"class": "s-pagination-next"})
        print("next page ======", next_p)
        return self.base+next_p['href']

    def export_to_csv(self, data):
        with open('products.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            # writer.writerow(self.final_data)

            # write multiple rows
            writer.writerows(data)

    def scrape_page(self):
        suop = BeautifulSoup(self.driver.page_source, "html.parser")
        results = suop.find_all(
            'div', {'data-component-type': "s-search-result"})

        for i in range(len(results)):
            temp = []
            rows = []
            url = self.get_item_data_link(results[i].find(
                'span', {'data-component-type': 's-product-image'}))

            temp.append(self.get_brand(results[i]))
            temp.append(self.get_name(results[i]))
            temp.append(self.get_price(results[i]))
            temp.append(url)
            self.driver.get(url)
            temp.append(self.get_exact_page())
            rows.append(temp)
            self.export_to_csv(rows)

    def main(self):
        try:
            # passing the serach  product url to the drive
            # this takes to the page where all the items are listed
            self.driver.get(self.get_url(self.product))
            time.sleep(3)
            suop = BeautifulSoup(self.driver.page_source, "html.parser")
            # first page
            self.scrape_page()

            # starts from 2nd page if exits

            for i in range(2):
                # going to the next page using the href of next button
                self.driver.get(self.get_next_page(suop))
                self.rows = []
                time.sleep(3)
                suop = BeautifulSoup(self.driver.page_source, "html.parser")
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
