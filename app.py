import json
import os
import threading
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from flask import Flask, jsonify, request, render_template, redirect, url_for

# I tried for 4 hours to make it work, but pycharm refuses to import the package
# import mysql.connector


######## GLOBALS/DEFINES ############

scrapper_urls = []
pair_names = ["RACA/BNB", "ADA/BNB"]

new_price = []


######## CLASSES ############

class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
            with self.app_context():
                th = threading.Thread(target=pair_management_thread)
                th.daemon = True
                th.start()
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

app = MyFlaskApp(__name__)


######## LOGIC ############

def add_pair(url, name):
    new_price.append(0)
    scrapper_urls.append(url)
    pair_names.append(name)
    th = threading.Thread(target=web_scraper_thread, args=(len(pair_names) - 1,))
    th.daemon = True
    th.start()


def remove_pair():
    new_price.pop()
    scrapper_urls.pop()
    pair_names.pop()


def pair_management_thread():
    pair_id = 0
    new_price.append(0)
    scrapper_urls.append(
        'https://www.pancakeswap.finance/swap?outputCurrency=0x12BB890508c125661E03b09EC06E404bc9289040')
    th = threading.Thread(target=web_scraper_thread, args=(pair_id,))
    th.daemon = True
    th.start()
    pair_id = 1
    new_price.append(0)
    scrapper_urls.append(
        'https://www.pancakeswap.finance/swap?outputCurrency=0x3ee2200efb3400fabb9aacf31297cbdd1d435d47')
    th = threading.Thread(target=web_scraper_thread, args=(pair_id,))
    th.daemon = True
    th.start()


# Was supposed to have a db, but oh well, next time

# def db_thread():
#     mydb = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="password"
#     )
#
#     mycursor = mydb.cursor()
#
#     mycursor.execute("CREATE DATABASE mydatabase")


def data_management_thread(my_id):
    print("Started manager")

    old_price = new_price[my_id]

    print(my_id, ": ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "  ", '{0:.11f}'.format(new_price[my_id]), "  ",
          '{0:.5f}'.format((new_price[my_id] - old_price) * 100 / old_price), "%")

    while True:
        if old_price != new_price[my_id]:
            print(my_id, ": ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "  ", '{0:.11f}'.format(new_price[my_id]),
                  "  ", '{0:.5f}'.format((new_price[my_id] - old_price) * 100 / old_price), "%")
            old_price = new_price[my_id]


def web_scraper_thread(my_id):
    global new_price

    print("Started scraper")
    # Initiate the browser
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # Open the Website
    browser.get(scrapper_urls[my_id])

    WebDriverWait(browser, 60).until(ec.presence_of_element_located(
        (By.XPATH, '//*[@id="__next"]/div[1]/div[2]/div[2]/div/div[3]/div/input'))).click()

    sleep(1)  # pray this works, wait for import button to be clickable
    browser.find_element_by_xpath('//*[@id="__next"]/div[1]/div[2]/div[2]/div/div[3]/button').click()

    browser.find_element_by_xpath('//*[@id="swap-currency-input"]/div[2]/div/div[1]/div/input').send_keys("1")

    WebDriverWait(browser, 60).until(ec.presence_of_element_located(
        (By.XPATH, '//*[@id="swap-page"]/div[1]/div[4]/div/div[2]')))
    element = browser.find_element_by_xpath('//*[@id="swap-page"]/div[1]/div[4]/div/div[2]')

    new_price[my_id] = float(element.text.partition(' ')[0])
    some_th = threading.Thread(target=data_management_thread, args=(my_id,))
    some_th.daemon = True
    some_th.start()

    while True:
        new_price[my_id] = float(element.text.partition(' ')[0])
        sleep(1)


######## CONTROLLER ############

### HOME ###
@app.route('/', methods=["GET", "POST"])
def log_in_page():
    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as text
        return redirect(url_for("admin_page"))
    else:
        example_embed = 'Sending data... [this is text from python]'
        # look inside `templates` and serve `index.html`
        return render_template('index.html', embed=example_embed)


@app.route('/adminPage', methods=["GET", "POST"])
def admin_page():
    # POST request
    if request.method == 'POST':
        example_embed = 'Sending data... [this is text from python]'
        print(request.get_json())  # parse as text
        add_pair("https://www.pancakeswap.finance/swap?outputCurrency=0xbe1a001fe942f96eea22ba08783140b9dcc09d28",
                 "BETA/BNB")
        return render_template('adminPage.html', embed=example_embed)
    else:
        example_embed = 'Sending data... [this is text from python]'
        # look inside `templates` and serve `index.html`
        return render_template('adminPage.html', embed=example_embed)


@app.route('/mainPage')
def main_page():
    example_embed = 'Sending data... [this is text from python]'
    # look inside `templates` and serve `index.html`
    return render_template('mainPage.html', embed=example_embed)


@app.route('/graphPage/<transaction_id>')
def graph_page(transaction_id):
    example_embed = pair_names[int(transaction_id)]
    # look inside `templates` and serve `index.html`
    return render_template('graphPage.html', embed=example_embed, my_id=int(transaction_id))


### Data fetch ###
@app.route('/getdata/<transaction_id>', methods=['GET'])
def data_find(transaction_id):
    message = jsonify({
        "transaction_id": transaction_id,
        "new_price": '{0:.11f}'.format(new_price[int(transaction_id)])
    })
    # message = 't_in = %s ; price: %s ' % (transaction_id, '{0:.11f}'.format(new_price))
    return message  # jsonify(message)  # serialize and use JSON headers


@app.route('/gettable', methods=['GET'])
def table_find():
    message = []
    for i, price in enumerate(new_price):
        message.append(json.dumps({
            "id": i,
            "name": pair_names[i],
            "price": '{0:.11f}'.format(price)
        }))
    # message = 't_in = %s ; price: %s ' % (transaction_id, '{0:.11f}'.format(new_price))
    resp = jsonify({"result": message})
    return resp  # jsonify(message)  # serialize and use JSON headers


######## MAIN ############

if __name__ == '__main__':
    # run app
    app.run()
