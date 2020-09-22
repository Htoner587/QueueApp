#IMPORTS
import datetime
import pymysql
from datetime import timedelta

class waitTimeCalculator():

    store=None
    maxInStore=None

    database= pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

    #@staticmethod
    def calculate_wait_time(self):


        if self.store!=None:

            print("Calculating average wait time ...")

            cursor = self.database.cursor()



            """
            FINDS THE NUMBER OF PEOPLE IN STORE
            """

            retrive5 = "Select InStore FROM q_Customers WHERE InStore IS NULL AND StoreID=%s AND Date=%s ORDER BY CustomerID DESC;"

            data=(self.store,datetime.date.today())

            cursor.execute(retrive5, data)

            rows = cursor.fetchall()

            inStore = len(rows)



            """
            CHECKS IF ANYONE HAS EXITED THE STORE YET
            """

            retrive2 = "Select ExitTime FROM q_Customers WHERE ExitTime!='NULL' AND StoreID=%s ORDER BY ExitTime DESC;"

            data = (self.store, lastArrival)

            cursor.execute(retrive2, data)

            rows = cursor.fetchall()

            if len(rows)<2:
                numExits=0




            """
            CALCULATION
            """

            if(inStore<self.maxInStore):
                waitTime=datetime.timedelta(minutes=0)


            if(inStore>=self.maxInStore):

                if (numExits == 0):
                    waitTime = datetime.timedelta(minutes=5)


                else:

                    """
                    GETs THE RATE OF EXIT
                    """
                    total = timedelta(0, 0, 0, 0)

                    retrive = "Select ExitTime FROM q_Customers WHERE ExitTime!='NULL' AND StoreID=%s AND Date=%sORDER BY ExitTime DESC LIMIT 10 ;"

                    cursor.execute(retrive, data)

                    rows = cursor.fetchall()

                    for i in range(len(rows) - 1):
                        diff = rows[i][0] - rows[i + 1][0]
                        total += diff

                    exitRate = total.seconds / (len(rows) - 1)




                    """
                    GET THE TIME OF THE LAST ARRIVAL 
                    """

                    retrive4 = "Select Time FROM q_Length WHERE StoreID=%s AND Arrival=0x01 AND Date=%s ORDER BY LengthID DESC LIMIT 1 ;"

                    cursor.execute(retrive4, data)

                    rows = cursor.fetchall()

                    if len(rows)>0:
                        lastArrival = rows[0][0]

                    else:
                        waitTime=datetime.timedelta(minutes=0)



                    """
                    LAST EXIT TIME
                    """

                    retrive2 = "Select ExitTime FROM q_Customers WHERE ExitTime!='NULL' AND StoreID=%s AND ExitTime<%s ORDER BY ExitTime DESC LIMIT 1 ;"

                    data = (self.store, lastArrival)

                    cursor.execute(retrive2, data)

                    rows = cursor.fetchall()

                    if len(rows)>0:
                        lastExit = rows[0][0]
                    else:
                        waitTime=datetime.timedelta(minutes=5)


                    """
                    GET MOST RECENT QUEUE LENGTH
                    """

                    retrive3 = "SELECT QueueLength FROM `q_length` WHERE Date=%s ORDER BY Time DESC LIMIT 1"

                    cursor.execute(retrive3, datetime.date.today())

                    rows = cursor.fetchall()

                    q_length = rows[0][0] + 1

                    #print("Q Length " + str(q_length))



                    var1=(exitRate * q_length)
                    # convert back to Date Time

                    var1=datetime.datetime.fromtimestamp(var1)

                    zero=datetime.datetime.fromtimestamp(0)

                    var1=var1-zero

                    var2=(lastArrival-lastExit)

                    waitTime=var1-var2

                cursor.close()

            return waitTime

