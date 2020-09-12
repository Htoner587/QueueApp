#IMPORTS
import datetime
import pymysql
from datetime import timedelta

class waitTimeCalculator():

    store=None
    numInStore=None

    @staticmethod
    def calculate_wait_time():

        if waitTimeCalculator.store!=None:

            print("Calculating average wait time ...")

            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()

            """
            NUMBER OF PEOPLE IN STORE
            """

            retrive5 = "Select WaitTime FROM q_Customers WHERE WaitTime IS NULL AND StoreID=%s ORDER BY CustomerID DESC;"

            cursor.execute(retrive5, waitTimeCalculator.store)

            rows = cursor.fetchall()

            inStore = len(rows)


            """
            CALCULATION
            """

            if(inStore<waitTimeCalculator.numInStore):
                waitTime=datetime.timedelta(minutes=0)
                print("Store not full")
                print("There are "+str(inStore)+"people in store")


            if(inStore==waitTimeCalculator.numInStore):
                waitTime=datetime.timedelta(minutes=5)
                print("Store full")


            if(inStore>waitTimeCalculator.numInStore):

                """
                            GET THE RATE OF EXIT
                            """
                total = timedelta(0, 0, 0, 0)

                retrive = "Select ExitTime FROM q_Customers WHERE ExitTime!='NULL' AND StoreID=%s ORDER BY CustomerID DESC LIMIT 10 ;"

                cursor.execute(retrive, waitTimeCalculator.store)

                rows = cursor.fetchall()

                for i in range(len(rows) - 1):
                    diff = rows[i][0] - rows[i + 1][0]
                    total += diff

                # convert to total seconds and take the average
                exitRate = total.seconds / (len(rows) - 1)

                #print("Exit Rate is " + str(exitRate))

                """
                GET THE TIME OF THE LAST ARRIVAL 
                """

                retrive4 = "Select Time FROM q_Length WHERE StoreID=%s AND Arrival=1 ORDER BY LengthID DESC LIMIT 1 ;"

                cursor.execute(retrive4, waitTimeCalculator.store)

                rows = cursor.fetchall()

                lastArrival = rows[0][0]

                #print("Last Arrival " + str(lastArrival))

                """
                LAST EXIT TIME
                """

                retrive2 = "Select ExitTime FROM q_Customers WHERE ExitTime!='NULL' AND StoreID=%s AND ExitTime<%s ORDER BY CustomerID DESC LIMIT 1 ;"

                data = (waitTimeCalculator.store, lastArrival)

                cursor.execute(retrive2, data)

                rows = cursor.fetchall()

                lastExit = rows[0][0]

                #print("Last Exit " + str(lastExit))

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
                #waitTime=datetime.datetime.fromtimestamp(waitTime)
                print("Queue outside")

            print("Wait Time = "+str(waitTime))

            #minutes = divmod(waitTime.total_seconds(), 60)
            #outputString = "The average wait time is " +str(waitTime)

            #self.root.ids.home_screen.ids.avg_wait.text=str(outputString)
            #self.root.ids.home_screen2.ids.avg_wait.text = str(outputString)

            cursor.close()

            return waitTime
