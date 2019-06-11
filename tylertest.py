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
           "Rocky (American player)", "moky", "Spark", "Squid", "Jerry", \
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
    inputs[0].send_keys(player1)
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
    weight = 1
    for k in range(len(match_table)-1, -1, -1):
        # If match stats, use them
        if match_table[k].get_attribute("class") == "match-row":
            in_match = True
            set_count = match_table[k].find_elements_by_xpath("./*")
            opponent = set_count[3].text
            # If not important, ignore weight change, but still record loss
            if not opponent in players:
                set_count = set_count[1:3]
                # If game count not recorded
                if set_count[0].text == "-":
                    weight *= 0.5
                elif set_count[0].text != "W":
                    # If game count recorded, winner has higher number
                    set_count = (int(set_count[0].text), int(set_count[1].text))
                    if set_count[0] < set_count[1]:
                        weight *= 0.5
                continue
            # Prevents repeated match records
            player2 = players.index(opponent)
            if player2 <= player1:
                continue
            set_count = set_count[1:3]
            # If game count not recorded
            if set_count[0].text == "W":
                set_count = (player1, player2, weight)
            elif set_count[0].text == "-":
                set_count = (player2, player1, weight)
                weight *= 0.5
            else:
                # If game count recorded, winner has higher number
                set_count = (int(set_count[0].text), int(set_count[1].text))
                if set_count[0] > set_count[1]:
                    set_count = (player1, player2, weight)
                else:
                    set_count = (player2, player1, weight)
                    weight *= 0.5
            match_queue.append(set_count)
        elif in_match:
            in_match = False
            # Get current date of tournament
            date = date_from_text(match_table[k].find_elements_by_xpath("./*")[0].text)
            for i in range(len(match_queue) - 2):
                match_weight = match_queue[i][2]
                # Speical cases for different bracket tournaments
                if date == date_from_text("2018-05-06") or date == date_from_text("2018-11-18"):
                    match_weight = 0.5
                matches.append((match_queue[i][0], match_queue[i][1], match_weight, date))
            if len(match_queue) >= 2:
                match1 = match_queue[len(match_queue)-2]
                match2 = match_queue[len(match_queue)-1]
                # If last 2 matches are in grand finals, weigh differently
                if match1[:2] == match2[:2] or match1[:2] == (match2[1], match2[0]):
                    matches.append((match1[0], match1[1], 0.5, date))
                    matches.append((match2[0], match2[1], 1, date))
                else:
                    match_weight = match1[2]
                    if date == date_from_text("2018-05-06") or date == date_from_text("2018-11-18"):
                        match_weight = 0.5
                    matches.append((match1[0], match1[1], match_weight, date))
                    match_weight = match2[2]
                    if date == date_from_text("2018-05-06") or date == date_from_text("2018-11-18"):
                        match_weight = 0.5
                    matches.append((match2[0], match2[1], match_weight, date))
            # If too few matches, weigh like normal
            else:
                for i in range(len(match_queue)):
                    match_weight = match_queue[i][2]
                    # Speical cases for different bracket tournaments
                    if date == date_from_text("2018-05-06") or date == date_from_text("2018-11-18"):
                        match_weight = 0.5
                    matches.append((match_queue[i][0], match_queue[i][1], match_weight, date))
            match_queue = []
            weight = 1

def get_matches_csv(file_name="matches.csv"):
    result = []
    with open(file_name, mode="r") as match_file:
        reader = csv.reader(match_file, delimiter=",")
        for row in reader:
            result.append((int(row[0]), int(row[1]), float(row[2]), date_from_text(row[3])))
    return result

def store_matches(matches, file_name="matches.csv"):
    try:
        with open(file_name, mode="w", newline="") as match_file:
            writer = csv.writer(match_file, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
            matches.sort(key=lambda x: min(x[0], x[1]), reverse=True)
            matches.sort(key=lambda x: x[0] + x[1], reverse=True)
            matches.sort(key=lambda x: x[3])
            writer.writerows(matches)
    except:
        print("File already open")

def apply_matches(matches, use_weights=False):
    result = []
    ratings = [Rating() for p in players]
    current_date = matches[0][3]
    for match in matches:
        if current_date != match[3]:
            result.append(ratings)
            ratings = ratings[:]
            current_date = match[3]
        new_r1, new_r2 = rate([(ratings[match[0]],), (ratings[match[1]],)], weights=[(1,), (match[2] if use_weights else 1,)])
        ratings[match[0]] = new_r1[0]
        ratings[match[1]] = new_r2[0]
    result.append(ratings)
    num_dates = len(unique_dates([m[3] for m in matches]))
    date_result = [[None for d in range(num_dates)] for p in players]
    for i in range(len(date_result)):
        for j in range(len(date_result[i])):
            date_result[i][j] = result[j][i]
    return date_result

def display_results(data):
    data.sort(key=lambda x: env.expose(x[1]), reverse=True)
    max_diff, min_diff = (0, 0), (0, 0)
    avg_diff = 0
    for i in range(len(data)):
        diff = np.log(float(players.index(data[i][0])+1) / (i+1)) / np.log(2)
        if diff > max_diff[0]:
            max_diff = (diff, i)
        elif diff < min_diff[0]:
            min_diff = (diff, i)
        avg_diff += abs(diff)
        print("{0:>3}: {1:<23} ({2:5.2f}, {3:+5.3f})".format(i+1, data[i][0], env.expose(data[i][1]), diff))
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
        for i in range(len(players)):
            inputs = get_inputs(driver)
            input_values(driver, inputs, players[i])
            get_matches(driver, matches, i)         
        driver.quit()
        store_matches(matches)

    ratings_over_time = apply_matches(matches, False)
    graph.plot_stats(unique_dates([m[3] for m in matches]), ratings_over_time[:10], players[:10], 3)
    display_results(list(zip(players, [r[-1] for r in ratings_over_time])))
    
