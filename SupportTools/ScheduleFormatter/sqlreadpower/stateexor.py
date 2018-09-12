#Analysis script for Verdiem data from CalPlug 2014 study - Idle Time Reporter using XOR
#Developed by M. Klopfer Sept 11, 2018 - V1.5
#Operation:  This script is a stand-alone processor that takes the Verdiem data and formats it into a style used as a .CSV input into the PLSin program.  This script will not actually output a .CSV file its current state, just format the text in a way that can be quickly formatted into the specific PLSim format.   
            #The script reads from a database/table with the following entries:  record_id    subject_identifier    desktop_type    MPID    device    status    int_record    date    day_of_week P1  P2...[There are 96 entries that correspond to 15 minute periods across the day]

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

#define global variables
resultsreviewcount=0
idleaverage= 0

# Open database connection
db = mysql.connector.connect(host="XXXXXXX.calit2.uci.edu",    # host
                     user="XXXXXXXX",         # username
                     passwd="XXXXXXXXX",  # password
                     db="VerdiemStudy")        # DBName

cursor = db.cursor() # Cursor object for database query

query = ("SELECT * FROM DATA "
         "WHERE subject_identifier = %(s_ID)s AND (date BETWEEN %(start_DATE)s AND %(end_DATE)s)") #base query

#Query for device states
query_modifications= {'s_ID': 1,'start_DATE': "2014-01-01",'end_DATE': "2014-12-31"} #query records updated by defined variables in dictionary, for device, start and end dates - alternatively use this style for datetime hire_start = datetime.date(1999, 1, 1), for date time printout: #for (first_name, last_name, hire_date) in cursor: print("{}, {} was hired on {:%d %b %Y}".format(last_name, first_name, hire_date))
    
cursor.execute(query, query_modifications) #Process query with variable modifications
queryreturn = cursor.fetchall() #Fetch all rows with defined query for first state




#Used to search for transitions in the dateset to identify timing:
# First, 

def transitionsearch(inputarray, mask):  #input array used for comparison and a mask of always
    results = []
    resultswithstart= []
    resultswithstartandstop = []
    option1start = ((0,0))
    option2start = ((0,1))   
    updatedoptionend = []  #needs to be a list, converted to tuple later upon insert

    
    deltaidle = []
    deltaactive = []
    deltaactiveOn = []
    deltaactiveOff = []
    deltacombined = []

    results=[(n+1, b) for (n, (a,b)) in enumerate(zip(inputarray,inputarray[1:])) if a!=b]  #Return the point of transition (to the new value) and the prior value to the transition as the function return  
    resultswithstart.extend(results)
    
    if (inputarray[0]==inputarray[1]):  #take care of the 0 case and add it to the array "resultswithstart"
        if (inputarray[0]==0):
            resultswithstart.insert(0, tuple(option1start))
        if (inputarray[0]==1):
            resultswithstart.insert(0, tuple(option2start))
            
    resultswithstartandstop.extend(resultswithstart)
    
    if (inputarray[len(inputarray)-2]==inputarray[len(inputarray)-1]):  #take care of the 0 case 
        if (inputarray[len(inputarray)-1]==1):
            endval=0
            
        if (inputarray[len(inputarray)-1]==0):
            endval=1
            
        updatedoptionend.append(len(inputarray)) #rem-1
        updatedoptionend.append(endval)
        if (len(results)!= 0):
            t= tuple(updatedoptionend)
            resultswithstartandstop.insert((len(inputarray)), t)   #rem-1
           
    for x in range(0, len(resultswithstartandstop)-1):     
        deltacombined.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 1): #count transition to idle and period until activity comes back
            deltaidle.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0 and mask[resultswithstartandstop[x][0]] == 0):
            deltaactiveOff.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0):    
            deltaactive.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
        if (resultswithstartandstop[x][1] == 0 and mask[resultswithstartandstop[x][0]] == 1):    
            deltaactiveOn.append(resultswithstartandstop[x+1][0] - resultswithstartandstop[x][0])
            
    
   
    return [resultswithstartandstop, deltaidle, deltaactive, deltacombined, deltaactiveOff, deltaactiveOn, results, resultswithstart]

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
sys.stdout.write("Subject,Date,State/Info,")
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
                    #print (len(activetimelist))  #print number of actions, helpful for debug
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
                    #sprint (len(ontimelist))  #print number of actions, helpful for debug
                    print() #Newline between rows - makes it formatted properly when there is final readout   



    
    if ((len(ontimelist) == len(activetimelist)) and (sum(activetimelist) !=0 or sum(ontimelist) !=0)): #check to see if there is a list for the same day for both active and ON states
        
        xorstate=[]
        xorwaste=[]
        xorinvalid =[]
        activeperiods=[]
        offperiods=[]
        logicalstate = []
        print() #Newline between rows - makes it formatted properly when there is final readout   
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        #sys.stdout.write("XOR Both states (valid/invalid),") #calculate XOR value Raw before doing validity check
        for positionindex in range(0, len(activetimelist)):  #this is calculated but not printed - it is granularly broken down elsewhere
                xorstate.append(int(ontimelist[positionindex] != activetimelist[positionindex]))  #Calculate Raw XOR State      
            #    sys.stdout.write(str(xorstate[positionindex])) #Print raw XOR value
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
        returnresultsXORWaste = transitionsearch(xorwaste, activetimelist) #read back in transition points
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
        sys.stdout.write("Transition Deltas (On-Active/Off)[Date Summary]:,")
        print(returnresultsXORWaste[2], sep=", ")
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("Transition Deltas (Off)[Date Summary]:,")
        print(returnresultsXORWaste[4], sep=", ")
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("Transition Deltas (On-Active)[Date Summary]:,")
        print(returnresultsXORWaste[5], sep=", ")
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
        xorsum=0    
        for positionindex in range(0, len(xorstate)):
            xorsum = xorsum + int(xorstate[positionindex])
        sys.stdout.write("XOR Active-Idle State sum [Date Summary](total -- day %):, ")
        xorwastesum=0    
        for positionindex in range(0, len(xorwaste)):
            xorwastesum = xorwastesum + int(xorwaste[positionindex])
        sys.stdout.write(str(xorwastesum))
        sys.stdout.write(', ')
        sys.stdout.write(str(xorwastesum/1440))
        idleaverage += (xorwastesum/1440)
        print()  
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("Active-On State sum [Date Summary](total -- day %):, ")
        activeonstate=0    
        for positionindex in range(0, len(returnresultsXORWaste[5])):
            activeonstate = activeonstate + int(returnresultsXORWaste[5][positionindex])
        sys.stdout.write(str(activeonstate))
        sys.stdout.write(', ')
        sys.stdout.write(str(activeonstate/1440))
        print()  
        sys.stdout.write(str(subjecttallylist_unique_list[0]))
        sys.stdout.write(',')
        sys.stdout.write(listeddate.strftime("%m/%d/%y"))
        sys.stdout.write(',')
        sys.stdout.write("Off State sum [Date Summary](total -- day %):, ")
        activeoffstate=0    
        for positionindex in range(0, len(returnresultsXORWaste[4])):
            activeoffstate = activeoffstate + int(returnresultsXORWaste[4][positionindex])
        sys.stdout.write(str(activeoffstate))
        sys.stdout.write(', ')
        sys.stdout.write(str(activeoffstate/1440))
        print() #Newline between rows - makes it formatted properly when there is final readout   
        print() #Newline between rows - makes it formatted properly when there is final readout   
        print() #Newline between rows - makes it formatted properly when there is final readout   
        resultsreviewcount+=1 #increment total results returned
       
        #Logical State Determination - generic template (must be run per day)
        #temp1 = []
        #logicalstatelist = []
        #for positionindex in range(0, len(activetimelist)):
        
        #    if (xorwwaste[positionindex] == 1):
        #        state=0 #Idle
        #    if (activetimelist[positionindex] == 1 and xorwwaste[positionindex] == 0):
        #        state=1 #Active
        #    if (activetimelist[positionindex] == 0 and xorwwaste[positionindex] == 0):
        #        state=2 #Off
        #    else:
        #        state=-1
            
                
        #        temp1.append(positionindex)
        #        temp1.append(endval)
        #        if (len(results)!= 0):
        #            t= tuple(temp1)
        #            logicalstatelist.insert((positionindex), t)                          
        #print(logicalstatelist)  #Per day state list - need to build list of list for all days   
        

print(",,Subject Summary Analysis:")                
print(",,Delta (Idle) Summary across all days: ")
sys.stdout.write(str(subjecttallylist_unique_list[0]))
sys.stdout.write(',')
sys.stdout.write("All Days")
sys.stdout.write(',')
sys.stdout.write("Idle Delta Summary:")
sys.stdout.write(',')
sys.stdout.write(str(finaldeltalist))
print()
sys.stdout.write(",,Idle time average across all days: ")
sys.stdout.write('{:.2%}'.format((idleaverage/resultsreviewcount)))
print()

def savingsevaluation(inputarray, timersetting):
    savingsarray=[]

    newlist=[int(x) for xs in inputarray for x in xs]
    #print(newlist)
    for index in range(0, (len(newlist))):
        if (newlist[index] < timersetting):  #no negative savings
            savingsval=0
            savingsarray.append(int(savingsval))
            
        else:
            savingsval = (newlist[index] - timersetting)
            savingsarray.append(int(savingsval))

    return [savingsarray]
            

def savingsreporting(analysisvalues, averagebase, deltawatt, energyreport):
    print()
    print(",,++++++++++++++++++++++++++++++++++++++++++++++++++++")
    for x in analysisvalues:
        savingsarrayreturn = savingsevaluation (finaldeltalist, x)     
        sys.stdout.write(",,Applied savings for ")
        sys.stdout.write(str(x))
        sys.stdout.write(" minutes, ")
        sys.stdout.write(str(savingsarrayreturn))
        print()
        savingssum = 0 #Initialize the sum counter
        for index in range(0, len(savingsarrayreturn)):
            savingssum = savingssum + int(savingsarrayreturn[0][index])
        print()
        sys.stdout.write(",,Total (min) Runtime Saved:, ")
        print(str(sum(savingsarrayreturn[0])))
        perday= (sum(savingsarrayreturn[0])/averagebase)
        print()
        sys.stdout.write(",,Per day (min) Runtime Saved:, ")
        print(str(perday))
        sys.stdout.write(",,Per day (Hr) Runtime Saved:, ")
        print(str(perday/60))
        if (energyreport == True):
            runtimehr= perday/60
            sys.stdout.write(",,Projected per day Energy Saved considering a delta of ")
            sys.stdout.write(str(deltawatt))
            sys.stdout.write(" W -- presented in (kWh/day):, ")
            sys.stdout.write(str((deltawatt/1000)*runtimehr))
            print()
            sys.stdout.write(",,Simple Schedule Projected per Year Energy Saved (same W) -- presented in (kWh/year):, ")
            sys.stdout.write(str(((deltawatt/1000)*runtimehr)*365))
            print()
        print (",,______________________________________________")
        
savingsreporting([5,10,15,20,25,30,35,40,45,60],resultsreviewcount,45,True) 
           
           
cursor.close()
db.close()  #close DB connection