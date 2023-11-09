    # CONSIDER THE TYPE OF ID THEY USE. 



from paddleocr import PaddleOCR # main OCR dependencies
from matplotlib import pyplot as plt # plot images
import pandas as pd 
import numpy as np 
import cv2 #opencv
import os 


#load model
ocr_model = PaddleOCR(lang = 'en')

#image path 
IMAGE_PATH = r"" # add path to id picture

#function to extract ocr from image 
def test_ocr(file): 
  return ocr_model.ocr(file) 

#run fucntion to perform ocr on image 
result = test_ocr(IMAGE_PATH)



def test_ocr_id(text): 


    ERROR_18808 = "ERROR_18808"


    #################################### Auto correct ####################################
    def create_bigrams(word): 
        return [word[i] + word[i+1] for i in range (len(word) -1)]

    def get_similary_ratio( word1 , word2 ): 
        word1 , word2 = word1.lower() , word2.lower()

        common=[]

        bigram1 , bigram2 = create_bigrams(word1) , create_bigrams(word2)

        for i in range(len(bigram1)): 
            #find commone elemnt 

            try: 
                cm_elt = bigram2.index(bigram1[i])
                common.append(bigram1[i])
            except: 
                continue
        
        return len(common) / max( len(bigram1) , len(bigram2))


    # database of words to look to auto correct 
    database =  { "South Africa" , "Zimbwabe" , "Botswana" , "Namibia" , "Mozambique" , "Kenya" , "Lesotho" ,"Swaziland" , "Egypt" , "country of birth" , "forenames" , "surname" , "date of birth" }
    def AutoCorrect (word , database = database, 
    sim_threshold = 0.7): 
        max_sim = 0.0 
        most_sim_word = word 

        for data_word in database: 
            curr_sim = get_similary_ratio( word , data_word )
            if curr_sim > max_sim: 
                max_sim = curr_sim 
                most_sim_word = data_word

        return most_sim_word if max_sim >  sim_threshold else word 

    
    #################################### Extract the words out of the results and put it into a list ###################################    

    result = [x[1][0] for x in text[0]]

################################################################### EXTRACTION BEGINS HERE ###############################################



    #################################### Get date of birth ####################################

    def get_dob_year(ocr_results , postion) : 

        """ 
        input: result from ocr and the index of the result(int)
        returns: int of the year of the dates found

        """
        str_dash = '-'
        new_dob_list =[]
        for p in range(0, len(ocr_results)): 
        
                if str_dash in ocr_results[p] : 
                    new_dob_list.append(ocr_results[p])

        

        first_date = new_dob_list[postion]

        dob_list_first_dob = []
        for i in first_date: 
            if i == "-": 
                break 
            else: 
                dob_list_first_dob.append(i)


        for i in range(0, len(dob_list_first_dob)): 
            dob_list_first_dob[i] = int(dob_list_first_dob[i])

        return dob_list_first_dob


    def get_dob():

        "Returns the dob year"

        date1 = get_dob_year(result , 0)
        date2 = get_dob_year(result , 1)
        
        

        res = np.array(date2) -  np.array(date1)

        if res[0] <  0: 
            date1 = "".join(str(letter) for letter in date1)
            for k in range( 0 , len(result)): 
                if date1 in result[k]: 
                    date_of_birth = result[k]

            

        elif res[0] > 0: 
            date2 = "".join(str(letter) for letter in date1)
            for k in range( 0 , len(result)): 
                if date2 in result[k]: 
                    date_of_birth = result[k]

        return date_of_birth          

    #################################### Get Identification number ####################################

    year = get_dob()[2:4]
    month = get_dob()[5:7]
    day = get_dob()[8:10]

    
    dob_6_digit = year + month + day
    for i in range( len(result)):
        if dob_6_digit in result[i]: 
            busi_id = result[i]

        liss = [i for i in busi_id]

        for number in range(0 , len(busi_id)): 
            try: 
                liss[number] = int(liss[number])
            except: 
                continue


    _id_integer_list = [integer for integer in liss if type(integer) == int ]

    if len(_id_integer_list) == 13: 
        identification_number = "".join((str(e)) for e in _id_integer_list)
    else: 
        identification_number = ERROR_18808  

    #################################### Surname ####################################
    surname = ERROR_18808
    count_surname = 0 
    for i in range (len(result)): 
        if "surname" in AutoCorrect(result[i]) and "forenames" in AutoCorrect(result[i+2]):
            surname = result[count_surname+1]
        else: 
            count_surname +=1 


    #################################### Get first names from ID ####################################
    firstnames = ERROR_18808
    count = 0 
    for i in range (len(result)): 
        if "forenames" in AutoCorrect(result[i])and "country of birth" in AutoCorrect(result[i+2]):
                firstnames = result[i+1]
                
        else: 
            count +=1 
        


    #################################### Extract sex from id number ####################################

    gender_id = _id_integer_list[6:10]
    
    for i in range (0 , len(gender_id)): 
        gender_id[i] = int(gender_id[i])
    

    g_id = int("".join(str(num) for num in gender_id))
    
    if g_id <= 4999: 
        sex = ("F")
    else: 
        sex = ("M") 
    

    #################################### Coutry of birth ####################################

    country_of_birth = ERROR_18808
    #Use Re so auto correct the output of the country. 

    for i in range(len(result)): 
        if "country of birth" in AutoCorrect(result[i]): 
            country_of_birth = AutoCorrect(result[i+1])



    #################################### Nationality ####################################

    nationality = country_of_birth
    
    national_count = 0 
    for i in range (len(result)): 
        if "nat" in AutoCorrect(result[i])  and "id" in AutoCorrect(result[i+2]):
            nationality = AutoCorrect(result[i+1])    
        else: 
            national_count +=1         
            


    #################################### Check citizenship via ID number ####################################

    citizen_id =_id_integer_list[10]

    if citizen_id == 0: 
        citizen = "Citizen"
    else: 
        citizen = "Permianent resident"


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

    #################################### Put results in a dictionary and retunr the dictionary ####################################

    result_dict ={
            'Personal_details': {
                                "Firstname": firstnames ,
                                "Lastname": surname , 
                                "Sex": sex ,
                                "Nationality": nationality ,
                                "ID Number": identification_number ,
                                "Date of birth": get_dob() ,
                                "Country of birth": country_of_birth , 
                                "Status": citizen},

            'valid_id_number': {"ID valid?": checkLuhn(identification_number)}
            
        }        
    
    return result_dict


df_results = test_ocr_id(result)
pd.DataFrame(df_results)
