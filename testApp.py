import unittest
import queueAnalysisSQL
import main
import datetime
from datetime import timedelta
import pymysql
import waitTimeCalculator
from main import UserType
import cv2


class MyTestCase_App(unittest.TestCase):

    app=main.QueueBusterApp()


    def test_setUser(self):

        self.app.setUser(UserType.HigherLevelAdmin,2)

        self.assertEqual(self.app.user.userNumber, 2)

        self.assertEqual(self.app.user.userType, UserType.HigherLevelAdmin )


    def test_setStore(self):

        self.app.setStore(1)

        self.assertEqual(self.app.selectedStore.storeNumber, 1)

        self.assertEqual(self.app.selectedStore.entrance_videos[0],"videos/video-7a.mov")

        self.assertEqual(self.app.selectedStore.exit_videos[0], "videos/video-7b.mov")



    def test_selectStore(self):

        self.app.selectStore("Asda Westwood")

        self.assertEqual(self.app.selectedStore.storeNumber, 1)


class MyTestCase_waitTimeCalculator(unittest.TestCase):

    calc=waitTimeCalculator.waitTimeCalculator()

    calc.database=pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="test_queue", port=3306)

    calc.maxInStore=3

    mydatabase = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                    database="test_queue", port=3306)

    mycursor=mydatabase.cursor()

    def setUp(self):

        insert="INSERT INTO `q_customers` (`CustomerID`, `StoreID`, `Date`, `EntranceTime`, `ExitTime`, `WaitTime`, `AgeID`, `GenderID`) VALUES (NULL, '1', %s, '16:00:00.000000', NULL, NULL, NULL, '0'), (NULL, '2', %s, '16:00:00.000000', NULL, NULL, NULL, '1'), (NULL, '2', %s, '16:18:00.000000', NULL, NULL, NULL, '0'), (NULL, '2', %s, '16:22:00.000000', NULL, NULL, NULL, '0'),(NULL, '3', %s, '16:00:00.000000', '16:05:00.000000', NULL, NULL, '1'),(NULL, '3', %s, '16:02:00.000000', '16:07:00.000000', NULL, NULL, '1'),(NULL, '3', %s, '15:59:00.000000', '16:03:00.000000', NULL, NULL, '0'),(NULL, '3', %s, '16:05:00.000000', NULL, NULL, NULL, '1'),(NULL, '3', %s, '16:06:00.000000', NULL, NULL, NULL, '1'),(NULL, '3', %s, '16:08:00.000000', NULL, NULL, NULL, '0');"

        date=datetime.date.today()

        data=(date,date,date,date,date,date,date,date,date,date,)

        self.mycursor.execute(insert,data)

        #self.mydatabase.commit()

        insert2= "INSERT INTO `q_length` (`LengthID`, `StoreID`, `Date`, `Time`, `QueueLength`, `Arrival`) VALUES ('NULL', '3', %s, '16:00:00', '0', '0x01'),('NULL', '3', %s, '16:02:00', '0', '0x01'),(NULL, 3, %s, '16:05:00', 0, 0x01),(NULL, 3, %s, '16:06:00', 0, 0x01),(NULL, 3, %s, '16:08:00', 1, 0x01),(NULL, 3, %s, '16:08:30', 1, 0x01);"

        data2=(date,date,date,date,date,date)

        self.mycursor.execute(insert2, data2)

        self.mydatabase.commit()

    def test_wait_time_1(self):

        #Store 1 - Store not full, no wait time

        self.calc.store=1

        predicted=datetime.timedelta(minutes=0)

        actual=self.calc.calculate_wait_time()

        self.assertEqual(predicted,actual)

    def test_wait_time_2(self):
        #Store 2 - Store Full but no queue. Set wait time of 5 mins

        self.calc.store=2

        predicted=datetime.timedelta(minutes=5)

        actual=self.calc.calculate_wait_time()

        self.assertEqual(predicted,actual)

    def test_wait_time_3(self):

        #Store 3 - store full queue outside. Wait time calculated with algorithm

        self.calc.store=3

        predicted=datetime.timedelta(minutes=2, seconds=30)

        actual=self.calc.calculate_wait_time()

        self.assertEqual(predicted,actual)

    def tidyUp(self):

        date=datetime.date.today()

        delete="DELETE FROM `q_customers` WHERE Date=%s"

        self.mycursor.execute(delete,date)

        self.mydatabase.commit()

        delete2="DELETE FROM `q_length` WHERE Date=%s"

        self.mycursor.execute(delete2, date)

        self.mydatabase.commit()

        self.mycursor.close()



class MyTestCase_AdvertisingScreen(unittest.TestCase):

    app=main.QueueBusterApp()

    advertScreen=main.AdvertisingScreen()

    def test_calculate_ages(self):

        self.advertScreen.store=3

        self.advertScreen.database=pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="test_queue", port=3306)

        self.advertScreen.calculate_age()

        self.assertEqual(self.advertScreen.avg_age, 24)

        self.assertEqual(self.advertScreen.avg_gender, 2/3)


"""
class MyTestCase_queueAnalysisSQL(unittest.TestCase):

    qa=queueAnalysisSQL.queueAnalysis()


    def test_threadedProcessing(self):
        #using the videos from store 1

        self.qa.store=1

        testdatabase = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                       database="queue_buster", port=3306)

        testcursor = testdatabase.cursor()

        retrive= "SELECT * FROM q_customers where StoreID=1"

        testcursor.execute(retrive)

        rows = testcursor.fetchall()

        startCustomers=len(rows)

        testcursor.close()

        entranceVideos=["videos/video-7a.mov"]

        exitVideos=["videos/video-7b.mov"]

        self.qa.threadedProcessing(entranceVideos, exitVideos, "videos/example_01.mp4")

        testdatabase = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                       database="queue_buster", port=3306)

        testcursor = testdatabase.cursor()

        testcursor.execute(retrive)

        rows=testcursor.fetchall()

        endCustomers =len(rows)

        self.assertGreater(endCustomers, startCustomers)

        testcursor.close()
"""

if __name__ == '__main__':
    unittest.main()
