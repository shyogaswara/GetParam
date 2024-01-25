#!/usr/bin/env python

'''This code is used to get parameters of earthquake from short messages
that used by BMKG, Indonesia. Those parameters are origin time,
magnitude, latitude, longitude, depth, and location remarks.
The code written by shyogaswara, for further information please mail me 
at sh.yogaswara@gmail.com

[PYTHON VERSION]
3.10

[LIBRARIES]
datetime
re

[MOIDULES]
day_translator (github/shyogaswara)


[CHANGELOG 1/2024]
- rewrite all function from previous release into GetParam class
- remove the function to split text that depend on their origin
'''

import re
import pandas as pd
from datetime import datetime

from day_translator import dayTranslate, monthTranslate

__author__ = 'Shandy Yogaswara'
__version_info__ = (2024, 1, 'aN (Alpha Release)')
__version__ = ".".join(map(str, __version_info__))


class GetParam:
    ''' Class used to get parameters which is origin time, magnitudes
    latitude, longitude, depth, and location remarks

    [Attributes]
    recognized_str : str
        example of string format that can be used in this code
    
    [Arguments]
    text_str : str
        short messages of earthquake information contain all necessary 
        parameter in one sentence
        
    [Methods]
    get_param(self)
        get result from all function
    param_split(self)
        Split parameters from short messages with coma, depends on 
        circumstances it will be splitted into 4 or 5, if 5, combine the
        3rd and 4th into one parameters
    get_mag(self)
        Get magnitude
    get_ot(self)
        Get origin time and the day name in Indonesian
    get_depth(self)
        Get depth
    get_loc(self)
        Get latitude, longitude, and location string
    '''
    recognized_str1 = 'Info Gempa. Mag:2.9, 21-mei-24 18:29:27 WIB, Lok:0.30 LS,100.28 BT (9 km Tenggara Bukittinggi), Kedlmn: 10 Km ::BMKG-PGR VI'
    recognized_str2 = 'Info Gempa Mag:3.0, 21-Jan-24 18:29:27 WIB,Lok: 2.52 LS - 102.26 BT (49 km Tenggara MERANGIN-JAMBI), Kedlmn: 5 Km ::BMKG-KSI'
    def __init__(self, text_str):
        '''
        [Arguments]
        text_str : str
            short messages of earthquake information contain all
            necessary parameter in one sentence        
        '''
        self.text_str = text_str
        self.param_split()
        
    
    def get_param(self):
        '''
        get result from all function
        '''
        self.get_mag()
        self.get_ot()
        self.get_depth()
        self.get_loc()

    def param_split(self):
        '''
        [Variables]
        text_split : str
            short messages of eartrhquake that splitted by coma
        param_text : str
            list of splitted string
        index : int
            index number for iterating text_split to param_text

        [Raises]
        SyntaxError
            if the short messages either didnt had 3 or 4 commas or 
            unrecognized format
        '''
        self.param_text = []

        index = [0,1,-1]
        text_split = self.text_str.split(',')

        for i in index:
            self.param_text.append(text_split[i].strip())
        
        if len(text_split) == 5:
            ''' According to BMKG earthquake information in short
            messages format, the message string can only splited into
            4 or 5 segment by using comma as separator, however there
            may be another case. please check the error message for
            more information.
            '''
            s = f'{text_split[2]} - {text_split[3]}'
            self.param_text.append(s.strip())
        elif len(text_split) == 4:
            self.param_text.append(text_split[2].strip())
        else:
            raise SyntaxError(f'Short Messages format unrecognized, please use recognized format such as {GetParam.recognized_str1} or {GetParam.recognized_str2}.')
    
    def get_mag(self):
        '''
        [Variables]
        mag : float
            earthquake magnitude

        [Raises]
        ValueError
            if the magnitude resulted from string didnt result in float 
            or too many float number found in the string
        '''
        self.mag = [float(i) for i in (re.findall(r"[-+]?(?:\d*\.*\d+)", self.param_text[0]))]
        
        if len(self.mag) < 1:
            raise ValueError(f'Magnitude number cant be found in {self.param_text[0]}, please check the messages, the magnitude shall be inside Info gempa Mag:X.Y')
        elif len(self.mag) > 1:
            raise ValueError(f'too many float number, cant found real magnitude from {self.mag}')
    
    def get_ot(self):
        '''
        [Variables]
        text_split : str, list
            list of string
        dates : str, list
            list of string for date only, to translate few month name 
            that not already in english
        dates : datetime
            combination from prevoius split string in datetime format 
            %d %b %y
        dname, mname : datetime
            name of day and month in datetime format
        dayname : str
            translated day name 
        origintime : str
            combination of date, translated month, and year
        timestring : str
            hour minute second in string format

        [Raises]
        TypeError
            if the date resulted from string cant be converted to 
            datetime format
        IndexError
            if timestring cannot properly splitted because of
            different format
        '''

        try:
            text_split = self.param_text[1].split()
            dates = text_split[0].split('-')

            if dates[1] in ['Mei','mei']:
                dates[1] = 'May'
            elif dates[1] in ['Agu','agu']:
                dates[1] = 'Aug'
            elif dates[1] in ['Okt','okt']:
                dates[1] = 'Oct'
            elif dates[1] in ['Des','des']:
                dates[1] = 'Dec'

            dates = datetime.strptime(' '.join(dates), '%d %b %y').date()
            dname, mname = dates.strftime('%A'), dates.strftime('%b')
        
        except:
            raise TypeError('cannot determine datetime format, should be dd-mmm-yy')

        if len(text_split) != 3:
            raise IndexError(f'timestring in {self.param_text[1]} not properly splitted, please refer to [{GetParam.recognized_str1}] or [{GetParam.recognized_str2}] format as example')

        self.dayname = dayTranslate(dname)[1]
        self.origintime = f'{dates.day} {monthTranslate(mname)[1]} {dates.year}'
        self.timestring = f'{text_split[1]} {text_split[2]}'


    def get_depth(self):
        '''
        [Variables]
        depth : int
            earthquake depth

        [Raises]
        ValueError
            if the depth resulted from string didnt result in int or too
            many int number found in the string
        '''
        # find numbers in string that match [-+]?(?:\d*\.*\d+)
        # where \d is digit
        self.depth = [int(i) for i in (re.findall(r"[-+]?(?:\d*\.*\d+)", self.param_text[2]))]
        if len(self.depth) < 1:
            raise ValueError(f'depth number cant be found in {self.param_text[2]}, please check the messages, the depth shall be inside Kedlmn:X Km')
        elif len(self.depth) > 1:
            raise ValueError(f'too many int number, cant found real depth from {self.depth}')

    def get_loc(self):
        '''
        [Parameters]
        latlocator : str, list
            list of locator data for latitude
        lonlocator : str, list
            list of locator data for longitude
        locstring : str
            string of earthquake location information
        latlon : float, list
            latitude and longitude number
        latitude : float
            latitude value, negative if latlocator = LS
        longitude : float
            longitude value, negative if lonlocator = BB

        [Raises]
        ValueError
            if the either latitude and/or longitude is not found, get
            too many number, or outside Indonesian boundary
        '''

        latlocator = ['LS','LU']
        lonlocator = ['BT','BB']

        # find location string located between () brackets
        self.locstring = re.search(r"\(([^)]+)", self.param_text[3]).group(1)
        self.location = self.locstring.split()[-1].replace('-',', ')

        # find numbers in string with pattern \d+\.\d+
        # where \d means digit characters and + is more than one
        # \d+\.\d+ equal to float numbers
        latlon = [float(i) for i in (re.findall("\d+\.\d+", self.param_text[3]))]
        if len(latlon) < 2:
            raise ValueError(f'either latitude or longitude not found in {latlon}')
        elif len(latlon) > 2:
            raise ValueError(f'too many number found, cant determine latitude and longitude from {latlon}')

        if -11.0 <= latlon[0] <= 6:
            self.latitude, self.longitude = latlon[0], latlon[1]
        elif -11.0 <= latlon[1] <= 6:
            self.latitude, self.longitude = latlon[1], latlon[0]
        else:
            raise ValueError(f'latitude value of {latlon} are outside of Indonesian latitude')

        for el in latlocator:
            if el in self.param_text[3]:
                self.latlocator = f'{self.latitude}° {el}'
                if el == 'LS':
                    self.latitude = -self.latitude

        for el in lonlocator:
            if el in self.param_text[3]:
                self.lonlocator = f'{self.longitude}° {el}'
                if el == 'BB':
                    self.longitude = -self.longitude



if __name__ == '__main__':
    ppi = 'Info Gempa. Mag:2.9, 21-mei-24 18:29:27 WIB, Lok:0.30 LS,100.28 BT (9 km Tenggara Bukittinggi), Kedlmn: 10 Km ::BMKG-PGR VI'
    gsi = 'Info Gempa Mag:3.1, 20-Jan-24 20:43:28 WIB,Lok: 0.27 LS - 99.56 BT (51 km BaratDaya PASAMANBARAT-SUMBAR), Kedlmn: 3 Km ::BMKG-GSI'
    ksi = 'Info Gempa Mag:3.0, 21-Jan-24 18:29:27 WIB,Lok: 2.52 LS - 102.26 BT (49 km Tenggara MERANGIN-JAMBI), Kedlmn:, 5 Km ::BMKG-KSI'
    
    for i in [ppi, ksi, gsi]:
        getparam = GetParam(i)
        getparam.get_param()

        print(getparam.param_text)

        title_str = f'*GEMPABUMI TEKTONIK M{getparam.mag[0]} DI {getparam.location.upper()}, TIDAK BERPOTENSI TSUNAMI*'
        str_1st = f'''*Kejadian dan Parameter Gempabumi:*
Hari {getparam.dayname}, {getparam.origintime} pukul {getparam.timestring} wilayah {getparam.location.title()} diguncang gempa tektonik. Hasil analisis BMKG menunjukkan gempabumi ini memiliki parameter dengan magnitudo M{getparam.mag[0]}. Episenter gempabumi terletak pada koordinat {getparam.latlocator} ; {getparam.lonlocator}, atau tepatnya berlokasi di [land_or_sea] pada jarak {getparam.locstring} pada kedalaman {getparam.depth[0]} km.
        '''
        print(f'{title_str}\n{str_1st}')