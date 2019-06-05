import time
import datetime
import csv
import numpy as np

from trueskill import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os

import graph
    
read_from_csv = True
players = ["Hungrybox", "Armada", "Leffen", "Plup", "Mango", \
           "Mew2King", "Zain", "Wizzrobe", "aMSa", "Axe", \
           "S2J", "SFAT", "Swedish Delight", "Duck", "PewPewU", \
           "n0ne", "Crush", "Lucky", "Bananas", "ARMY", \
           "lloD", "Westballz", "HugS", "AbsentPage", "KJH", \
           "Rishi", "Gahtzu", "Fiction", "Shroomed", "Colbol", \
           "Ryan Ford", "La Luna", "Captain Faceroll", "iBDW", "Trif", \
           "Syrox", "Kalamazhu", "Hax", "Ice", "Ginger", \
           "Michael", "Captain Smuckers", "MikeHaze", "Bladewise", "Junebug", \
           "ChuDat", "Spud", "Santi", "2saint", "Slox", \
           "Rocky (American Player)", "moky", "Spark", "Squid", "Jerry", \
           "Professor Pro", "Overtriforce", "Ka-Master", "Darktooth", "Drephen", \
           "Drunksloth", "Stango", "Abate", "Amsah", "Nintendude", \
           "Android", "Boyd", "42nd", "FatGoku", "Sharkz", \
           "Cactuar", "Tai", "Kels", "DaShizWiz", "Darkatma", \
           "Eddy Mexico", "Prince Abu", "Zamu", "Kalvar", "Uncle Mojo", \
           "HTwa", "Rik", "NMW", "King Momo", "Legend", \
           "Smashdaddy", "Cal", "Jakenshaken", "Ralph", "Flipsy", \
           "TheRealThing", "MilkMan", "Trulliam", "Cob", "Iceman", \
           "vortex", "Magi", "nebbii", "Morsecode762", "Azel"]

def get_driver():
    result = None
    if (os.name == "posix"):
        cwd = os.getcwd()
        cwd += '/chromedriver'
        result = webdriver.Chrome(cwd)
    else:
        result = webdriver.Chrome()
    result.implicitly_wait(15)
    return result

def get_inputs(driver):
    driver.get("https://liquipedia.net/smash/Special:RunQuery/Match_history?Head_to_head_query%5Bgame%5D=Melee")
    inputs = driver.find_element_by_class_name("template-box").find_elements_by_xpath("./*")
    inputs[0] = inputs[0].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
    inputs[1] = inputs[1].find_element_by_class_name("select2-search-field").find_elements_by_xpath("./*")[1]
    inputs[3] = inputs[3].find_element_by_class_name("hasDatepicker")
    inputs[4] = inputs[4].find_element_by_class_name("hasDatepicker")
    return inputs

def input_values(driver, inputs, player1):
    inputs[0].send_keys(players[i])
    time.sleep(1)
    ActionChains(driver).send_keys(Keys.ENTER).perform()
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    inputs[3].send_keys("01/01/2018")
    for k in range(10):
        inputs[4].send_keys(Keys.BACK_SPACE)
    inputs[4].send_keys("31/12/2018")
    inputs[4].submit()

def get_matches(driver, matches, player1):
    match_table = None
    try:
        match_table = driver.find_element_by_class_name("table-responsive").find_elements_by_xpath("./*")[0].find_elements_by_xpath("./*")[0].find_elements_by_xpath("./*")
    except:
        return
    in_match = False
    match_queue = []
    for k in range(len(match_table)-1, -1, -1):
        if match_table[k].get_attribute("class") == "match-row":
            in_match = True
            set_count = match_table[k].find_elements_by_xpath("./*")
            opponent = set_count[3].text
            if not opponent in players:
                continue
            player2 = players.index(opponent)
            if player2 <= player1:
                continue
            set_count = set_count[1:3]
            if set_count[0].text == "W":
                set_count = (player1, player2)
            elif set_count[0].text == "-":
                set_count = (player2, player1)
            else:
                set_count = (int(set_count[0].text), int(set_count[1].text))
                if set_count[0] > set_count[1]:
                    set_count = (player1, player2)
                else:
                    set_count = (player2, player1)
            match_queue.append(set_count)
        elif in_match:
            in_match = False
            date = date_from_text(match_table[k].find_elements_by_xpath("./*")[0].text)
            for match in match_queue:
                matches.append((match[0], match[1], date))
            match_queue = []

def get_matches_csv(file_name="matches.csv"):
    result = []
    with open(file_name, mode="r") as match_file:
        reader = csv.reader(match_file, delimiter=",")
        for row in reader:
            result.append((int(row[0]), int(row[1]), date_from_text(row[2])))
    return result

def store_matches(matches, file_name="matches.csv"):
    try:
        with open(file_name, mode="w", newline="") as match_file:
            writer = csv.writer(match_file, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            matches.sort(key=lambda x: min(x[0], x[1]), reverse=True)
            matches.sort(key=lambda x: x[0] + x[1], reverse=True)
            matches.sort(key=lambda x: x[2])
            writer.writerows(matches)
    except:
        print("File already open")

def apply_matches(matches):
    result = []
    ratings = [Rating() for p in players]
    current_date = matches[0][2]
    for match in matches:
        if current_date != match[2]:
            result.append(ratings)
            ratings = ratings[:]
            current_date = match[2]
        new_r1, new_r2 = rate_1vs1(ratings[match[0]], ratings[match[1]])
        ratings[match[0]] = new_r1
        ratings[match[1]] = new_r2
    result.append(ratings)
    num_dates = len(unique_dates([m[2] for m in matches]))
    date_result = [[None for d in range(num_dates)] for p in players]
    for i in range(len(date_result)):
        for j in range(len(date_result[i])):
            date_result[i][j] = result[j][i]
    return date_result

def display_results(data, safety=0):
    data.sort(key=lambda x: x[1].mu - x[1].sigma*safety, reverse=True)
    max_diff, min_diff = (0, 0), (0, 0)
    avg_diff = 0
    for i in range(len(data)):
        diff = np.log(float(players.index(data[i][0])+1) / (i+1)) / np.log(2)
        if diff > max_diff[0]:
            max_diff = (diff, i)
        elif diff < min_diff[0]:
            min_diff = (diff, i)
        avg_diff += abs(diff)
        print("{0:>3}: {1:<23} ({2:5.2f}, {3:+5.3f})".format(i+1, data[i][0], data[i][1].mu - data[i][1].sigma*safety, diff))
    avg_diff /= len(data)
    print("Most underrated:", data[max_diff[1]][0])
    print("Most overrated:", data[min_diff[1]][0])
    print("Average deviation:", avg_diff)

def date_from_text(text):
    if "-" in text:
        attr = text.split("-")
        return datetime.date(int(attr[0]), int(attr[1]), int(attr[2]))
    else:
        attr = text.split("/")
        return datetime.date(int(attr[2]), int(attr[0]), int(attr[1]))

def copy_rating(rating):
    return Rating(rating.mu, rating.sigma)

def unique_dates(dates):
    result = []
    for date in dates:
        if date not in result:
            result.append(date)
    return result

if __name__ == "__main__":
    env = TrueSkill(draw_probability=0)
    matches = []

    if read_from_csv:
        matches = get_matches_csv()
    else:
        driver = get_driver()
        for i in range(len(ratings)):
            inputs = get_inputs(driver)
            input_values(driver, inputs, players[i])
            get_matches(driver, matches, i)         
        driver.quit()
        store_matches(matches)

    ratings_over_time = apply_matches(matches)
    graph.plot_stats(unique_dates([m[2] for m in matches]), ratings_over_time[::10], players[::10], 3)
    display_results(list(zip(players, [r[-1] for r in ratings_over_time])), 3)
    
