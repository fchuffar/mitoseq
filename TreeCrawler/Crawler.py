from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

driver = webdriver.Firefox()
driver.get("https://www.familytreedna.com/public/mt-dna-haplotree/")
sleep(5)

elem = driver.find_elements(By.CLASS_NAME, "branch")

for e in elem:
    sleep(1)
    e.click()


driver.close()