#Analysis script for Verdiem data from CalPlug 2014 study
#Developed by M. Klopfer Aug 30, 2018 - V1.1

#Operation:  This script is a stand-alone processor that takes the Verdiem data and formats it into a style used as a .CSV input for post analysis - this scrip breaks data to categorize states and transitions
#Dependencies and setup considerations:  This program uses Miniconda/Eclipse in development and is within an Eclipse workshop - it shares identical dependencies as PLSim:  https://github.com/CalPlug/PlugLoadSimulator-PLSim
#Note, if the console is not large enough in Eclipse to display the return, consider the following:  https://stackoverflow.com/questions/2600653/adjusting-eclipse-console-size

import mysql.connector
import sys
from datetime import timedelta
from datetime import datetime
from datetime import date
from datetime import time

#Run Options for Output Formatting
elapsedminortime=True #Print headers as time (False) or minutes since 00:00 (True)
finaldeltalist =[] #holder for the total collected delta values across all days
periodlength=15  #assume a standard 15 min period length
totalperiods = 95  #total number of columns devoted to the periods
periodstartcolumn = 9 #column which the period info starts in
record_idrow = 0 #position original identifier is in
subjectrow = 1 #Row the subject info is in
desktop_typerow = 2 #position for the desktop type info
MPIDrow = 3 #row MPID info is placed in
devicerow = 4 #Identify row for the device (CPU or USER) that is being reported on 
stateposition = 5 #position of the state/status identifier column
int_recordrow = 6
daterow = 7 #row that date information is placedin
day_of_weekrow = 8 #Day of the Week identifier

# Open database connection
db = mysql.connector.connect(host="XXXXXXX.calit2.uci.edu",    # host
                     user="XXXXXXX",         # username
                     passwd="XXXXXXXXX",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

query = ("SELECT * FROM DATA "
         "WHERE subject_identifier = %(s_ID)s AND (date BETWEEN %(start_DATE)s AND %(end_DATE)s)") #base query

#Query for device states
query_modifications= {'s_ID': 2,'start_DATE': "2014-01-01",'end_DATE': "2014-12-31"} #query records updated by defined variables in dictionary, for device, start and end dates - alternatively use this style for datetime hire_start = datetime.date(1999, 1, 1), for date time printout: #for (first_name, last_name, hire_date) in cursor: print("{}, {} was hired on {:%d %b %Y}".format(last_name, first_name, hire_date))
    
cursor.execute(query, query_modifications) #Process query with variable modifications
queryreturn = cursor.fetchall() #Fetch all rows with defined query for first state

#Used to search for transitions in the dateset to identify timing:
# First, 

def transitionsearch(inputarray):
    results = []
    resultswithstartandstop= []
    option1start = [(0,0)]
    option2start =[(0,1)]     
    optionend = [(0,0)]

    
    deltaidle = []
    deltaactive = []
    deltacombined = []

    results=[(n+1, b) for (n, (a,b)) in enumerate(zip(inputarray,inputarray[1:])) if a!=b]  #Return the point of transition (to the new value) and the prior value to the transition as the function return  
    resultswithstartandstop.extend(results)
    
    
    if (inputarray[0]==inputarray[1]):  #take care of the 0 case and add it to the array "resultswithstart"
        if (inputarray[0]==0):
            resultswithstartandstop.insert(0, option1start)
        if (inputarray[0]==1):
            resultswithstartandstop.insert(0, option2start)
            
    if (inputarray[len(inputarray)-2]==inputarray[len(inputarray)-1]):  #take care of the 0 case 
        if (inputarray[len(inputarray)-1]==1):
            endval=0
            
        if (inputarray[len(inputarray)-1]==1):
            endval=0
            
        optionend[0]= ((len(inputarray)),(inputarray[len(inputarray)-1]))
        if (len(resultswithstartandstop)!=0):
            resultswithstartandstop.extend(optionend)
    #fixes the o case for the "results" array when calculating specific states
    if (results[0][1] == 0): #take care of case 0 for the inactive scenarios
        deltaidle.append(results[0][0])
        deltacombined.append(results[0][0])
        
    for x in range(0, len(results)-1):     
        deltacombined.append(results[x+1][0] - results[x][0])
        if (results[x][1] == 1): #count transition to idle and period until activity comes back
            deltaidle.append(results[x+1][0] - results[x][0])
        if (results[x][1] == 0) :
            deltaactive.append(results[x+1][0] - results[x][0])
    
   
    return [resultswithstartandstop, deltaidle, deltaactive, deltacombined, results]

#collect and display unique states in the query
subjecttallylist = [] #total list of states found
subjecttallylist_unique_list = []  # intitalize a null list
statetallylist = [] #total list of states found
statetallylist_unique_list = [] #total list of states found
datetallylist = []  #total list of dates found
datetallylist_unique_list = []  #total list of dates found
for rowindex, row in enumerate(queryreturn): #go thru query and generate a full list of states from the dataset
    statetallylist.append(row[stateposition])
    datetallylist.append(row[daterow])
    subjecttallylist.append(row[subjectrow])
    
for x in statetallylist:
    # check if exists in unique_list or not
    if x not in statetallylist_unique_list:
        statetallylist_unique_list.append(x) 
        
for x in subjecttallylist:
    # check if exists in unique_list or not
    if x not in subjecttallylist_unique_list:
        subjecttallylist_unique_list.append(x) 
        
for x in datetallylist:
    # check if exists in unique_list or not
    if x not in datetallylist_unique_list:
        datetallylist_unique_list.append(x) 
        
#Print out Headers for CSV
sys.stdout.write("Date,State/Info,")
for x in range(0, (96*15)): #96 sets of 15 minute periods for all minutes in a 24 hour period
    timeholder = datetime.today() #initialize datetimeobject
    timeholder = (datetime.combine(date.today(), time(0,0,0)) + timedelta(minutes=1*x))
    if(elapsedminortime==False):
        sys.stdout.write(datetime.strftime(timeholder, '%H:%M:%S'))   
    else:
        sys.stdout.write(str(x))
    if ((x<(96*15)-1)): #suppress final comma
        sys.stdout.write(",")
print () #print newline after the header row is finished
    

for listeddate in datetallylist_unique_list: # display entries for a single date
    ontimelist = []
    activetimelist = []
    xorlist = []
    
    
    for rowindex, row in enumerate(queryreturn): #page thru all returned rows from query, also return an index number related to the row
        if ((("Active") in row[stateposition]) or (("On") in row[stateposition])):
            if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):
                sys.stdout.write(str(subjecttallylist_unique_list[0]))
                sys.stdout.write(',')
                sys.stdout.write(row[daterow].strftime("%m/%d/%y")) # (INSERT "("%B %d, %Y")" after %d to have commas in name.  Print out the datetime for each record 
                sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                sys.stdout.write(str(row[stateposition]))
                sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
                    lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
                    lengthnotinstate = (periodlength-int(row[x])) #This is used to read the value at the index each period: assuming a known total, subtract to find the time not in the state - there would be multiple check under this for more defined states
                    if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):   #Identify Active/On state by string comparison - for CPU this is ON, for User this is Active
                                #need to identify this is an active state
                        for a in range(lengthinstate):
                            sys.stdout.write('1') #print out all rows for inspection
                            sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                            activetimelist.append(1)
                            
                        for b in range(lengthnotinstate):
                            sys.stdout.write('0') #print out all rows for inspection
                            sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                            activetimelist.append(0)
                
                if ((("Active") in row[stateposition]) and (row[daterow] == listeddate)):    
                    print (len(activetimelist))
                    print() #Newline between rows - makes it formatted properly when there is final readout   
    
    
            if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):
                sys.stdout.write(str(subjecttallylist_unique_list[0]))
                sys.stdout.write(',')
                sys.stdout.write(row[daterow].strftime("%m/%d/%y")) # (INSERT "("%B %d, %Y")" after %d to have commas in name.  Print out the datetime for each record 
                sys.stdout.write(",") #If record line date is not intended to be displayed, turn of this line also
                sys.stdout.write(str(row[stateposition]))
                sys.stdout.write("    ,") #If record line date is not intended to be displayed, turn of this line also - add space so text aligns up in console
    
                for x in range(periodstartcolumn, periodstartcolumn+totalperiods): #page thru each of the data columns per the defined start and total number of these
                    lengthinstate = int(row[x])  #This is used to read the value at the index each period: total the time active in the column
                    lengthnotinstate = (periodlength-int(row[x])) #This is used to read the value at the index each period: assuming a known total, subtract to find the time not in the state - there would be multiple check under this for more defined states
                    if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):   #Identify Active/On state by string comparison - for CPU this is ON, for User this is Active
                                #need to identify this is an active state
                        for a in range(lengthinstate):
                            sys.stdout.write('1') #print out all rows for inspection
                            sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                            ontimelist.append(1)
                   
                        for b in range(lengthnotinstate):
                            sys.stdout.write('0') #print out all rows for inspection
                            sys.stdout.write(',') #Used when formatting a non-compliant PLSim CSV file
                            ontimelist.append(0)
                
                if ((("On") in row[stateposition]) and (row[daterow] == listeddate)):    
                    print (len(ontimelist))
                    print() #Newline between rows - makes it formatted properly when there is final readout   

    if ((len(ontimelist) == len(activetimelist)) and (sum(activetimelist) !=0 or sum(ontimelist) !=0)): #check to see if there is a list for the same day for both active and ON states
        xorstate=[]
        xorwaste=[]
        xorinvalid =[]
        activeperiods=[]
        offperiods=[]
        print() #Newline between rows - makes it formatted properly when there is final readout   
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        #sys.stdout.write("XOR Both states (valid/invalid),")
        for positionindex in range(0, len(activetimelist)):  #this is calculated but not printed - it is granularly broken down elsewhere
                xorstate.append(int(ontimelist[positionindex] != activetimelist[positionindex]))  #Calculate Raw XOR State      
            #    sys.stdout.write(str(xorstate[positionindex]))
             #   sys.stdout.write(',') 
        sys.stdout.write("On Periods (Mask): ")
        sys.stdout.write(',')
        for positionindex in range(0, len(activetimelist)):
                activeperiods.append(int(ontimelist[positionindex] == 1 and activetimelist[positionindex] == 1))  #Calculate Raw XOR State      
                sys.stdout.write(str(activeperiods[positionindex]))
                sys.stdout.write(',') 
        print() 
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
                        
        sys.stdout.write("Off Periods (Mask):")
        sys.stdout.write(',')
        for positionindex in range(0, len(activetimelist)):
                offperiods.append(int(ontimelist[positionindex] == 0 and activetimelist[positionindex] == 0))  #Calculate Raw XOR State      
                sys.stdout.write(str(offperiods[positionindex]))
                sys.stdout.write(',') 
        print() 
         
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')      
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("XOR Active/Idle State (Mask):,")
        for positionindex in range(0, len(activetimelist)):
            xorwaste.append(int(xorstate[positionindex] == 1 and ontimelist[positionindex] == 1))
            sys.stdout.write((str(xorwaste[positionindex])))
            sys.stdout.write(',')      
        print()  
        
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')      
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("XOR Invalid State (Mask):    ,")
        for positionindex in range(0, len(activetimelist)):
            xorinvalid.append(int(xorstate[positionindex] == 1 and ontimelist[positionindex] == 0))
            sys.stdout.write((str(xorinvalid[positionindex])))
            sys.stdout.write(',')      
        print() 
        
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
        sys.stdout.write(',') 
        returnresultsXORWaste=[]
        returnresultsXORWaste = transitionsearch(xorwaste) #read back in transition points
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write("Transition Points [Date Summary]:,")
        print(returnresultsXORWaste[0], sep=", ")
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
        sys.stdout.write(',')
        sys.stdout.write("Transition Deltas (Idle)[Date Summary]:,")
        print(returnresultsXORWaste[1], sep=", ")
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
        sys.stdout.write(',')
        sys.stdout.write("Transition Deltas (Active)[Date Summary]:,")
        print(returnresultsXORWaste[2], sep=", ")
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))  
        sys.stdout.write(',')
        sys.stdout.write("Transition Deltas (Combined)[Date Summary]:,")
        print(returnresultsXORWaste[3], sep=", ")
        finaldeltalist.append(returnresultsXORWaste[1]) #append to final delta list
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("XOR Both states [Date Summary]: ")
        xorsum=0    
        for positionindex in range(0, len(xorstate)):
            xorsum = xorsum + int(xorstate[positionindex])
        sys.stdout.write(str(xorsum))
        print()  
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("XOR Active/Idle State sum [Date Summary]: ")
        xorwastesum=0    
        for positionindex in range(0, len(xorwaste)):
            xorwastesum = xorwastesum + int(xorwaste[positionindex])
        sys.stdout.write(str(xorwastesum))
        print() #Newline between rows - makes it formatted properly when there is final readout   
        print() #Newline between rows - makes it formatted properly when there is final readout   
        print() #Newline between rows - makes it formatted properly when there is final readout   
    
print("Delta (Idle) Summary across all days: ")
sys.stdout.write(str(subjecttallylist_unique_list[0]))
sys.stdout.write(',')
sys.stdout.write("All Days")
sys.stdout.write(',')
sys.stdout.write("Idle Delta Summary:")
sys.stdout.write(',')
sys.stdout.write(str(finaldeltalist))             
cursor.close()
db.close()  #close DB connection