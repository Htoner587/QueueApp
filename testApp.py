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

"""
class MyTestCase_waitTimeCalculator(unittest.TestCase):

    calc=waitTimeCalculator.waitTimeCalculator()

    calc.database=pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="test_queue", port=3306)

    calc.numInStore=3

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


"""

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


if __name__ == '__main__':
    unittest.main()
