from selenium import webdriver

CHROMEDRIVER_PATH = "/Users/wirriamm/chromedriver"

driver = webdriver.Chrome(CHROMEDRIVER_PATH)
driver.get("https://mapman.gabipd.org/mercator4")

input_el = driver.find_element("id", "InputSequence")
input_el.send_keys("/Users/wirriamm/Downloads/taxid110835.pep.fasta")

name_el = driver.find_element("id", "name")
name_el.send_keys("taxid110835")

submit_el = driver.find_element("id", "btnSubmit")
submit_el.click()
