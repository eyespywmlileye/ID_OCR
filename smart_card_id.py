from paddleocr import PaddleOCR  # main OCR dependencies
from matplotlib import pyplot as plt  # plot images
import pandas as pd
import numpy as np
import cv2  # opencv
import os


# load model
ocr_model = PaddleOCR(lang='en')

# image path
IMAGE_PATH = r"/images/Khumo.JPG"
# function to extract ocr from image


def test_ocr(file):
    return ocr_model.ocr(file)


# run fucntion to perform ocr on image
result = test_ocr(IMAGE_PATH)


def test_ocr_new_id(text):

    #################################### Auto correct ####################################
    def create_bigrams(word):
        return [word[i] + word[i+1] for i in range(len(word) - 1)]

    def get_similary_ratio(word1, word2):
        word1, word2 = word1.lower(), word2.lower()

        common = []

        bigram1, bigram2 = create_bigrams(word1), create_bigrams(word2)

        for i in range(len(bigram1)):
            # find commone elemnt

            try:
                cm_elt = bigram2.index(bigram1[i])
                common.append(bigram1[i])
            except:
                continue

        return len(common) / max(len(bigram1), len(bigram2))

    # database of words to look to auto correct
    database = {"RSA", "USA", "ZIM", "country of birth",
                "names", "surname", "date of birth", "sex", "signature"}

    def AutoCorrect(word, database=database,
                    sim_threshold=0.7):
        max_sim = 0.0
        most_sim_word = word

        for data_word in database:
            curr_sim = get_similary_ratio(word, data_word)
            if curr_sim > max_sim:
                max_sim = curr_sim
                most_sim_word = data_word

        return most_sim_word if max_sim > sim_threshold else word


#################################### Extract the words out of the results and put it into a list ####################################
    result = []
    for words in text[0]:
        result.append(words[1][0])

    #################################### Remove "Signtaure" and other useless text ####################################

    for i in range(len(result)-1):
        if "signature" == AutoCorrect(result[i]):
            result.remove(f"{result[i]}")

    firstnames = "Error 18808"
    count = 0
    for i in range(len(result)-1):
        if "country of birth" == AutoCorrect(result[i]):
            break
        else:
            count += 1

    for p in range(count, len(result)-1):
        if len(result[p]) < 3:
            result.remove(f"{result[p]}")

    #################################### Surname ####################################
    surname = "Error 18808"
    count_surname = 0
    for i in range(len(result)):
        if "surname" in AutoCorrect(result[i]) and "names" in AutoCorrect(result[i+2]):
            surname = result[count_surname+1]
        else:
            count_surname += 1

    #################################### Get first names from ID ####################################

    firstnames = "Error 18808"
    count = 0
    for i in range(len(result)):
        if "name" in AutoCorrect(result[i]) and "sex" in result[i+2].lower():
            firstnames = result[i+1]
        else:
            count += 1

        #################################### Get Identification number ####################################

    text_and_acc = []
    for acc in text[0]:
        text_and_acc.append(acc[1])

    id_list = "0,1,2,3,4,5,6,7,8,9"
    identification_number = "Error 18808"
    for p in range(len(text_and_acc)):
        if id_list.split(",")[0] in text_and_acc[p] or id_list.split(",")[1] in text_and_acc[p][0]:
            if len(text_and_acc[p][0]) == 13:
                identification_number = text_and_acc[p][0]

        # Check accuracy score
        if text_and_acc[p][1]*100 < 88 == True:
            identification_number = "Error 24453"

    #################################### Get date of birth ####################################

    date_of_birth = "Error 18808"
    list1 = ["jan", "feb", "mar", "apr", "may", "jun",
             "jul", "aug", "sep", "oct", "nov", "dec"]
    for i in list1:
        for idx in range(len(result)):
            if i.lower().upper() in result[idx] and identification_number[0] in result[idx]:
                date_of_birth = result[idx]

    if len(date_of_birth.split()) != 1:

        date_of_birth = date_of_birth.split()
        date_of_birth = "".join(date_of_birth)

    day = date_of_birth[:2]
    month = date_of_birth[2:5]
    year = date_of_birth[5:10]

    # give dob spaces
    fix_dob_word_format = day + " " + month + " " + year

    # put the dates into numbers

    months_to_dates = {
        "jan": '01',
        "feb": '02',
        "mar": '03',
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12"
    }

    fix_dob_number_format = year + "-" + \
        months_to_dates[f"{month.lower()}"] + "-" + day

    ########### add ID number to a list as an integer ###########

    new_qid_list = []
    for i in identification_number:
        new_qid_list.append(i)
    for i in range(0, len(new_qid_list)):
        new_qid_list[i] = int(new_qid_list[i])

    #################################### Check citizenship via ID number ####################################

    citizen_id = new_qid_list[10]

    if citizen_id == 0:
        status = ("Citizen")
    else:
        status = ("Permianent resident")

    #################################### Extract sex from id number ####################################

    gender_id = new_qid_list[6:10]
    gender_id

    for i in range(0, len(gender_id)):
        gender_id[i] = int(gender_id[i])

    g_id = "".join(str(num) for num in gender_id)
    g_id = int(g_id)

    if g_id <= 4999:
        sex = ("F")
    else:
        sex = ("M")

    #################################### Coutry of birth ####################################

    country_of_birth = "Error 18808"
    # Use Re so auto correct the output of the country.

    for i in range(len(result)):
        if "country of birth" in AutoCorrect(result[i]):
            country_of_birth = AutoCorrect(result[i+1])

    #################################### Nationality ####################################

    nationality = country_of_birth

    national_count = 0
    for i in range(len(result)):
        if "nat" in AutoCorrect(result[i]) and "id" in AutoCorrect(result[i+2]):
            nationality = AutoCorrect(result[i+1])
        else:
            national_count += 1

    #################################### check if ID is valid using Luhn Algorithm ####################################

    def checkLuhn(id_number):

        nDigits = len(id_number)
        nSum = 0
        isSecond = False

        for i in range(nDigits - 1, -1, -1):
            d = ord(id_number[i]) - ord('0')

            if (isSecond == True):
                d = d * 2

            # We add two digits to handle
            # cases that make two digits after
            # doubling
            nSum += d // 10
            nSum += d % 10

            isSecond = not isSecond

        if (nSum % 10 == 0):
            return True
        else:
            return False

    result_dict = {
        "Personal_details": {
            "Firstname": firstnames,
            "Lastname": surname,
            "Sex": sex,
            "Nationality": nationality,
            "ID Number": identification_number,
            "Date of birth": fix_dob_word_format,
            "Date of birth (numbers)": fix_dob_number_format,
            "Country of birth": country_of_birth,
            "Status": status},

        "valid_id": {"ID valid?": checkLuhn(identification_number)}

    }

    return result_dict


pd.DataFrame(test_ocr_new_id(result))
