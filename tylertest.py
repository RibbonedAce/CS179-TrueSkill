import time
import datetime
from trueskill import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

players = ["Hungrybox", "Armada", "Leffen", "Plup", "Mango", \
           "Mew2King", "Zain", "Wizzrobe", "aMSa", "Axe"]

def get_inputs(driver):
    driver.get("https://liquipedia.net/smash/Special:RunQuery/Match_history?Head_to_head_query%5Bgame%5D=Melee")
    inputs = driver.find_element_by_class_name("template-box").find_elements_by_xpath("./*")
    inputs[0] = inputs[0].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
    inputs[1] = inputs[1].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
    inputs[3] = inputs[3].find_element_by_class_name("hasDatepicker")
    inputs[4] = inputs[4].find_element_by_class_name("hasDatepicker")
    return inputs

def input_values(driver, inputs, player1, player2):
    inputs[0].send_keys(players[i])
    time.sleep(1)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    inputs[1].send_keys(players[j])
    time.sleep(1)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    inputs[3].send_keys("01/01/2018")
    for k in range(10):
        inputs[4].send_keys(Keys.BACK_SPACE)
    inputs[4].send_keys("31/12/2018")
    inputs[4].submit()

def get_matches(driver, matches):
    match_table = None
    try:
        match_table = driver.find_element_by_class_name("table-responsive").find_elements_by_xpath("./*")[0].find_elements_by_xpath("./*")[0].find_elements_by_xpath("./*")
    except:
        return
    date = None
    for k in range(len(match_table)):
        if match_table[k].get_attribute("class") == "match-row":
            set_count = match_table[k].find_elements_by_xpath("./*")[1:3]
            set_count = (int(set_count[0].text), int(set_count[1].text))
            if set_count[0] > set_count[1]:
                set_count = (i, j)
            else:
                set_count = (j, i)
            if not date:
                date = date_from_text(match_table[k-1].find_elements_by_xpath("./*")[0].text)
            matches.append((set_count, date))
        else:
            date = None

def apply_matches(matches, ratings):
    matches.sort(key=lambda x: x[1])
    for match in matches:
        new_r1, new_r2 = rate_1vs1(ratings[match[0][0]], ratings[match[0][1]])
        ratings[match[0][0]] = new_r1
        ratings[match[0][1]] = new_r2

def date_from_text(text):
    attr = text.split("-")
    return datetime.date(int(attr[0]), int(attr[1]), int(attr[2]))

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    
    env = TrueSkill(draw_probability=0)
    ratings = [Rating() for p in players]
    matches = []
    
    for i in range(len(ratings)):
        for j in range(i+1, len(ratings)):
            inputs = get_inputs(driver)
            input_values(driver, inputs, players[i], players[j])
            get_matches(driver, matches)         
    driver.quit()
    
    apply_matches(matches, ratings)
    print(dict(zip(players, ratings)))

