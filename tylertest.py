import time
from trueskill import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

players = ["Hungrybox", "Armada", "Leffen", "Plup", "Mango"]#, \
           #"Mew2King", "Zain", "Wizzrobe", "aMSa", "Axe"]

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    
    env = TrueSkill(draw_probability=0)

    ratings = [Rating() for p in players]

    for i in range(len(ratings)):
        for j in range(i+1, len(ratings)):
            driver.get("https://liquipedia.net/smash/Special:RunQuery/Match_history?Head_to_head_query%5Bgame%5D=Melee")
            inputs = driver.find_element_by_class_name("template-box").find_elements_by_xpath("./*")
            inputs[0] = inputs[0].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
            inputs[1] = inputs[1].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
            inputs[3] = inputs[3].find_element_by_class_name("hasDatepicker")
            button = driver.find_element_by_id("wpRunQuery")

            inputs[0].send_keys(players[i])
            time.sleep(1)
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            ActionChains(driver).send_keys(Keys.ENTER).perform()

            inputs[1].send_keys(players[j])
            time.sleep(1)
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            ActionChains(driver).send_keys(Keys.ENTER).perform()

            inputs[3].send_keys("27/05/2018")
            inputs[3].submit()

            set_count = driver.find_elements_by_class_name("stats-value")[0].text.split()
            wins = int(set_count[0])
            losses = int(set_count[2])

            for w in range(wins):
                new_r1, new_r2 = rate_1vs1(ratings[j], ratings[i])
                ratings[i] = new_r1
                ratings[j] = new_r2
                
            for l in range(losses):
                new_r1, new_r2 = rate_1vs1(ratings[j], ratings[i])
                ratings[j] = new_r1
                ratings[i] = new_r2
                
    driver.quit()
