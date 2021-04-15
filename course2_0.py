import requests
from multiprocessing import Queue
from bs4 import BeautifulSoup
import json, re
import ctypes
import sys
link="https://querycourse.ntust.edu.tw/QueryCourse/api/courses"

def strB2Q(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 32:  # 全形空格直接轉換
                inside_code = 12288
            elif (inside_code >= 33 and inside_code <= 126):  # 全形字元（除空格）根據關係轉化
                inside_code += 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

class Course():
    def __init__(self):
        self.CourseNo = ""
        self.CourseName = ""
        self.Dimension = ""
        self.CourseTeacher = ""
        self.CreditPoint = ""
        self.Time = ""
        self.ClassRoomNo = ""
        self.choosed = 0
        self.restrict = 0
    def __str__(self):
        return self.CourseName
    
canChooseCourse = []

""" node=""
node+="M1,M2,M3,M4,M5,M6,M7,M8,M9,M=,MA,MB,MC,MD,"
node+="T1,T2,T3,T4,T5,T6,T7,T8,T9,T=,TA,TB,TC,TD,"
node+="W1,W2,W3,W4,W5,W6,W7,W8,W9,W=,WA,WB,WC,WD,"
node+="R1,R2,R3,R4,R5,R6,R7,R8,R9,R=,RA,RB,RC,RD,"
node+="F1,F2,F3,F4,F5,F6,F7,F8,F9,F=,FA,FB,FC,FD,"
node+="S1,S2,S3,S4,S5,S6,S7,S8,S9,S=,SA,SB,SC,SD,"
node+="U1,U2,U3,U4,U5,U6,U7,U8,U9,U=,UA,UB,UC,UD" """

header={ 'content-type': 'application/x-www-form-urlencoded' }
payload={
    "Semester":"1091",
    "CourseNo":"", #chinese: CC12, english: FE
    "CourseName":"",
    "CourseTeacher":"",
    #"nodes":node,
    "Language":"zh",
    "OnlyGeneral":"1", #general class
    "Dimension":"",
    "OnleyNTUST":"1",
    "CourseNotes":"",
     "ForeignLanguage":"0",
     "OnlyMaster":"0"
}

regex = re.compile(r'限[0-9]+人') #regexp rule

res=requests.post(link,data=payload,headers=header)
#res.text is json
if res.status_code!=200:
    print("Request Error!!")
else:
    content = json.loads(res.text) #convert
    
    print("Semester: "+content[0]["Semester"])
    for row in content:
        try:
            restrictStr = regex.search(row['Contents']).group(0) #max student
            restrict = int(restrictStr[1:-1])
        except AttributeError:
            restrict = 99999
        choosed = int(row['ChooseStudent']) #current choosed

        if choosed<restrict:
            currCourse = Course()
            currCourse.CourseNo = row["CourseNo"]
            currCourse.CourseName = row['CourseName']
            currCourse.Dimension = row['Dimension']
            currCourse.CourseTeacher = row['CourseTeacher']
            currCourse.CreditPoint = row['CreditPoint']
            currCourse.Time = row['Node']
            currCourse.ClassRoomNo = row['ClassRoomNo']
            currCourse.choosed = choosed
            currCourse.restrict = restrict
            canChooseCourse.append(currCourse)

#sort
for i in range(len(canChooseCourse)):
    for j in range(len(canChooseCourse) - 1 - i):
        weight1 = canChooseCourse[j].restrict - canChooseCourse[j].choosed
        weight2 = canChooseCourse[j+1].restrict - canChooseCourse[j+1].choosed
        restrict1 = canChooseCourse[j].restrict
        restrict2 = canChooseCourse[j+1].restrict
        if(weight1 > weight2 or (weight1 == weight2 and restrict1 > restrict2)):
            temp = Course()
            temp = canChooseCourse[j]
            canChooseCourse[j] = canChooseCourse[j+1]
            canChooseCourse[j+1] = temp

#print
for i in range(len(canChooseCourse)):
    courseNo = canChooseCourse[i].CourseNo
    courseFullName = strB2Q(canChooseCourse[i].CourseName+'('+canChooseCourse[i].Dimension+')')
    teacher = strB2Q(canChooseCourse[i].CourseTeacher)
    credit = canChooseCourse[i].CreditPoint+"pt"
    time = canChooseCourse[i].Time

    classroom = canChooseCourse[i].ClassRoomNo
    try:
        temp = strB2Q(canChooseCourse[i].ClassRoomNo)
    except TypeError:
        classroom =  strB2Q("-")
    
    people = "%3s"%str(canChooseCourse[i].choosed)+"/"+"%3s"%str(canChooseCourse[i].restrict)
    remain = canChooseCourse[i].restrict - canChooseCourse[i].choosed
    
    print(courseNo, end=" ")
    print("　"*(20-len(courseFullName))+courseFullName, end=" ") 
    print("　"*(10-len(teacher))+teacher, end=" ")
    print("%04s"%credit, end=" ")
    print("%20s"%time, end=" ")
    print("　"*(7-len(classroom))+classroom, end=" ")
    print(people, end=" ")
    print("%3s"%remain, end=" ")
    print(strB2Q("!"*(4-remain)), end=" ")
    print()
