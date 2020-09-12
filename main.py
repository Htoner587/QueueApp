from datetime import timedelta
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition, CardTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from queueAnalysisSQL import queueAnalysis
from waitTimeCalculator import waitTimeCalculator
import kivy.utils
import pymysql
from kivy.clock import Clock, mainthread
import threading
import ageRecognition
from kivy.uix.popup import Popup
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import ffpyplayer
import datetime

"""

SCREEN AND POPUP CLASSES

"""


class LoginScreen(Screen):

    def signIn(self):

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)

        cursor = connection.cursor()

        retrive = "SELECT RoleID, StaffID, StoreID FROM `q_Staff` WHERE UserName= %s AND Password=%s "

        data = (app.root.ids.login_screen.ids.login.text, app.root.ids.login_screen.ids.passw.text)

        cursor.execute(retrive, data)

        rows = cursor.fetchall()

        if len(rows) == 1:
            app.setUser(rows[0][0], rows[0][1])
            print("The user is " + str(rows[0][1]) + " their user type is " + str(rows[0][0]))
            if rows[0][0] == 0:
                app.change_screen("admin_home", direction='right', mode='push')

            if rows[0][0] == 1:
                app.setStore(rows[0][2])
                app.change_screen("home_screen", direction='right', mode='push')
            if rows[0][0] == 2:
                app.setStore(rows[0][2])
                app.change_screen("home_screen2", direction='right', mode='push')


        else:
            app.root.ids.login_screen.ids.login_msg.text = "Incorrect Username and Password combination please try again!"

        cursor.close()

    pass


class HomeScreen(Screen):
    videoPopup = Popup()

    def open_popup_entrance(self):
        videoPopup = MyVideoPopup()
        videoPopup.title = "Entrance Video"

        videoPopup.ids.video_player_1.source = app.selectedStore.entrance_videos[0]
        if len(app.selectedStore.entrance_videos) > 1:
            videoPopup.ids.video_player_2.source = app.selectedStore.entrance_videos[1]
            if len(app.selectedStore.entrance_videos) > 2:
                videoPopup.ids.video_player_3.source = app.selectedStore.entrance_videos[3]

        videoPopup.open()


    def open_popup_exit(self):
        videoPopup = MyVideoPopup()
        videoPopup.title = "Entrance Video"

        app.videoPopup.ids.video_player_1.source = app.selectedStore.exit_videos[0]
        if len(app.selectedStore.exit_videos) > 1:
            app.videoPopup.ids.video_player_2.source = app.selectedStore.exit_videos[1]
            if len(app.selectedStore.exit_videos) > 2:
                app.videoPopup.ids.video_player_3.source = app.selectedStore.exit_videos[3]

        videoPopup.open()

    pass


class HomeScreen2(HomeScreen):
    """
    videoPopup = None

    def open_popup_entrance(self):
        app.videoPopup = MyVideoPopup()
        app.videoPopup.title = "Entrance Video"

        app.videoPopup.ids.video_player_1.source = app.entrance_videos[0]
        if len(app.entrance_videos) > 1:
            app.videoPopup.ids.video_player_2.source = app.entrance_videos[1]
            if len(app.entrance_videos) > 2:
                app.videoPopup.ids.video_player_3.source = app.entrance_videos[3]

        app.videoPopup.open()

    def open_popup_exit(self):
        app.videoPopup = MyVideoPopup()
        app.videoPopup.title = "Entrance Video"

        app.videoPopup.ids.video_player_1.source = app.exit_videos[0]
        if len(app.entrance_videos) > 1:
            app.videoPopup.ids.video_player_2.source = app.exit_videos[1]
            if len(app.entrance_videos) > 2:
                app.videoPopup.ids.video_player_3.source = app.exit_videos[3]

        app.videoPopup.open()

    """
    pass


class AdminHome(Screen):

    def getChains(self):
        chains = []

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)
        cursor = connection.cursor()

        retrive = "SELECT * FROM `q_chain` "

        cursor.execute(retrive)

        rows = cursor.fetchall()

        for i in range(len(rows)):
            chains.append(str(rows[i][0]) + "- " + str(rows[i][1]))

        app.root.ids.add_store_screen.ids.chain.values = chains

    pass


class SelectStore(Screen):
    pass


class AddStoreScreen(Screen):

    def addStore(self):
        chain = app.root.ids.add_store_screen.ids.chain.text

        chainvect = chain.split('-')

        chainNum = chainvect[0]

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)
        cursor = connection.cursor()

        retrive = "INSERT INTO `q_Stores` ( `StoreID`,`StoreName`, `HouseNumber`, `StreetName`, `City`, `Postcode`, `Country`, `ChainID`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)"

        data = (app.root.ids.add_store_screen.ids.store_name.text, app.root.ids.add_store_screen.ids.house_number.text,
                app.root.ids.add_store_screen.ids.street_name.text, app.root.ids.add_store_screen.ids.city.text,
                app.root.ids.add_store_screen.ids.postcode.text, app.root.ids.add_store_screen.ids.country.text,
                chainNum)

        print("ADDING STORE")

        cursor.execute(retrive, data)

        connection.commit()

        app.change_screen("admin_home", direction='right', mode='push')

        cursor.close()

    pass


class AddStaffScreen(Screen):

    def addStaff(self):

        RoleID = None

        roleName = app.root.ids.add_staff_screen.ids.role.text

        if roleName == "Higher Level Admin":
            RoleID = 0
        if roleName == "Admin Staff":
            RoleID = 1
        if roleName == "Viewer":
            RoleID = 2

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)
        cursor = connection.cursor()

        retrive = "INSERT INTO `q_Staff` ( `StaffID`, `StoreID`,`FirstName`, `LastName`, `RoleID`, `UserName`, `Password`) VALUES (NULL, %s, %s, %s, %s, %s,%s)"

        data = (app.selectedStore, app.root.ids.add_staff_screen.ids.first_name.text,
                app.root.ids.add_staff_screen.ids.last_name.text,
                str(RoleID), app.root.ids.add_staff_screen.ids.user_name.text,
                app.root.ids.add_staff_screen.ids.password.text)

        print("ADDING STAFF")

        cursor.execute(retrive, data)

        connection.commit()

        app.change_screen("home_screen", direction='right', mode='push')

        cursor.close()

    pass


class SettingsScreen(Screen):
    fileSelector = None

    def open_popup(self):
        fileSelector = MySettingsPopup()
        fileSelector.title = "Please select a video"
        fileSelector.open(self)

    def update_conf(self, new_val):
        app.my_queue_analysis.confidence_val = new_val
        self.root.ids.settings_screen.ids.confidence.text = "Confidence % for Facial Detection is " + str(
            self.my_queue_analysis.confidence_val)

    def update_length(self, new_val):
        app.tol_length = new_val

    def update_wait(self, new_val):
        app.tol_wait = new_val

    pass


class AdvertisingScreen(Screen):
    avg_gender = None

    avg_age = 0

    age_src = ["adv_imgs/child1.10.jpg", "adv_imgs/girl10.18.jpg", "adv_imgs/boy10.18.jpg", "adv_imgs/adults18.50.jpg",
               "adv_imgs/adults50+.jpg"]

    advert_image = age_src[2]

    def calculate_age(self, *args):

        if app.selectedStore != None:
            print("Calculating the ages from database")

            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()

            retrive = "Select MedianValue, GenderID FROM (q_Customers JOIN q_age ON q_customers.AgeID=q_age.AgeID) WHERE WaitTime IS NULL AND StoreID=%s;"

            store = (app.selectedStore)

            cursor.execute(retrive, store)

            rows = cursor.fetchall()

            totalAge = 0
            totalGender = 0

            for row in rows:
                totalAge += row[0]
                totalGender += row[1]

            cursor.close()

            if len(rows) > 0:
                avg_age = totalAge / len(rows)

                avg_gender = totalGender / len(rows)

                app.root.ids.advertising_screen.ids.avg_age.text = "The average age in the queue is " + str(
                    round(avg_age, 2))
                app.root.ids.advertising_screen.ids.avg_gen.text = "The average gender in the queue is " + str(
                    round(avg_gender, 2))

                if avg_age < 10:
                    self.root.ids.advertising_screen.ids.age_src.source = str(AdvertisingScreen.age_src[0])

                if avg_age >= 10:
                    if avg_age < 18:
                        if avg_gender < 0.5:
                            app.root.ids.advertising_screen.ids.age_src.source = str(AdvertisingScreen.age_src[1])
                        else:
                            app.root.ids.advertising_screen.ids.age_src.source = str(AdvertisingScreen.age_src[2])

                if avg_age >= 18:
                    if avg_age <= 50:
                        app.root.ids.advertising_screen.ids.age_src.source = str(AdvertisingScreen.age_src[3])
                    else:
                        app.root.ids.advertising_screen.ids.age_src.source = str(AdvertisingScreen.age_src[4])

    pass


class WaitAlertPopup(Popup):
    pass


class LengthAlertPopup(Popup):
    pass


class MyVideoPopup(Popup):
    # Popup to view video footage
    pass


class VideoPlayer():

    def build(self):
        video = Video()
        video.state = 'play'
        video.options = {'eos': 'loop'}

        video.allow_stretch = True

        return video


class MySettingsPopup(Popup):

    def selected(self, filename):
        try:
            print(filename[0])
            print(app.root.ids.settings_screen.ids.video_path.text)
            app.root.ids.settings_screen.ids.video_path.source = filename[0]
            print(app.root.ids.settings_screen.ids.video_path.text)
            SettingsScreen.fileSelector.dismiss()


        except:
            pass


class FileChooserWindow(App):
    def build(self):
        return MySettingsPopup()


"""
STORE
"""


class Store():
    selectedStore=None
    tol_length = 15
    tol_wait = datetime.timedelta(minutes=30)
    entrance_videos = []
    exit_videos = []
    queue_video = None


"""
APP - MAIN FUNCTIONALITY
"""

GUI = Builder.load_file("main.kv")


class QueueBusterApp(App):
    my_queue_analysis = None
    my_wait_time_calculator = None
    selectedStore = Store()
    user = None
    userType = None
    tol_length_popup = LengthAlertPopup()
    tol_wait_popup = WaitAlertPopup()

    def build(self):
        return GUI

    @mainthread
    def on_start(self):
        Clock.schedule_interval(self.num_in_queue, 60)
        Clock.schedule_interval(AdvertisingScreen.calculate_age, 60)
        Clock.schedule_interval(self.update_ages, 150)
        Clock.schedule_interval(self.calculate_wait_time, 60)

    def start_second_thread(self, video_entrance, video_exit, video_queue):
        self.my_queue_analysis = queueAnalysis()
        self.my_queue_analysis.store = app.selectedStore.selectedStore
        self.root.ids.settings_screen.ids.confidence.text = "Confidence % for Facial Detection is " + str(
            self.my_queue_analysis.confidence_val)
        t2 = threading.Thread(target=self.my_queue_analysis.threadedProcessing,
                              args=(video_entrance, video_exit, video_queue))
        t2.start()

    def setUser(self, userType, user):
        self.user = user
        self.userType = userType

    def setStore(self, store):

        #self.selectedStore = Store()

        self.selectedStore.selectedStore=store

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)

        cursor = connection.cursor()

        retrive = "SELECT source, videoType FROM `q_videos` WHERE StoreID= %s "

        data = (store)

        cursor.execute(retrive, data)

        rows = cursor.fetchall()

        for row in rows:
            if row[1] == 0:
                self.selectedStore.entrance_videos.append(row[0])
            if row[1] == 1:
                self.selectedStore.exit_videos.append(row[0])
            if row[1] == 2:
                self.selectedStore.queue_video = row[0]

        cursor.close()

    def selectStore(self, store):
        # retrive store number from string store name and then setStore

        connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                     database="queue_buster", port=3306)

        cursor = connection.cursor()
        retrive = "Select StoreID FROM q_Stores WHERE StoreName=%s ;"

        cursor.execute(retrive, store)
        rows = cursor.fetchall()
        # self.selectedStore= Store(rows[0][0])
        self.setStore(rows[0][0])
        cursor.close()

    # METHODS

    def update_ages(self, *args):

        if app.selectedStore != None:
            print("Adding ages to database")

            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()

            retrive = "Select CustomerID FROM q_Customers WHERE AgeID IS NULL AND StoreID=%s;"

            store = (app.selectedStore)

            cursor.execute(retrive, store)

            rows = cursor.fetchall()

            for i in range(len(rows)):
                ageRecognition.mainAgeFunction(rows[i][0])

            cursor.close()

    def calculate_wait_time(self, *args):
        if app.selectedStore != None:
            app.my_wait_time_calculator = waitTimeCalculator()
            waitTimeCalculator.store = app.selectedStore
            waitTimeCalculator.numInStore = app.tol_length

            waitTime = app.my_wait_time_calculator.calculate_wait_time()
            outputString = "The average wait time is " + str(waitTime)
            self.root.ids.home_screen.ids.avg_wait.text = str(outputString)
            self.root.ids.home_screen2.ids.avg_wait.text = str(outputString)

            if waitTime > app.tol_wait:
                app.tol_wait_popup.open()
                app.tol_wait_popup.title = "WARNING"

    def num_in_queue(self, *args):
        ## Number of people in the store!!!
        if app.selectedStore != None:
            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()
            retrive = "Select WaitTime FROM q_Customers WHERE WaitTime IS NULL AND StoreID=%s ORDER BY CustomerID DESC;"

            store = (app.selectedStore)

            print("Calculating queue length ... ")
            # executing the quires
            cursor.execute(retrive, store)
            rows = cursor.fetchall()
            queueLength = len(rows)
            outputString = "There are " + str(queueLength) + " people in the queue"
            self.root.ids.home_screen.ids.q_len.text = str(outputString)
            self.root.ids.home_screen.ids.q_len.text = str(outputString)

            if queueLength > app.tol_length:
                app.tol_length_popup.open()
                app.tol_length_popup.title = "WARNING"
            cursor.close()

    def change_screen(self, screen_name, direction='forward', mode=""):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['screen_manager']
        # print(direction, mode)
        # If going backward, change the transition. Else make it the default
        # Forward/backward between pages made more sense to me than left/right
        if direction == 'forward':
            mode = "push"
            direction = 'left'
        elif direction == 'backwards':
            direction = 'right'
            mode = 'pop'
        elif direction == "None":
            screen_manager.transition = NoTransition()
            screen_manager.current = screen_name
            return
        if screen_name == "admin_home":
            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()
            retriveStores = "SELECT StoreName FROM `q_Stores`"

            cursor.execute(retriveStores)

            rowsStores = cursor.fetchall()

            store = []

            for i in range(len(rowsStores)):
                store.append(rowsStores[i][0])

            app.root.ids.select_store_screen.ids.dropdown.values = store

            cursor.close()

        if screen_name == "add_staff_screen":
            connection = pymysql.connect(host="localhost", user="admin", passwd="TueyW8ObgPTK0Qmb",
                                         database="queue_buster", port=3306)

            cursor = connection.cursor()

            retriveRoles = "SELECT RoleName FROM `q_roleid` "

            cursor.execute(retriveRoles)

            rowsRoles = cursor.fetchall()

            roles = []

            for i in range(len(rowsRoles)):
                roles.append(rowsRoles[i][0])

            app.root.ids.add_staff_screen.ids.role.values = roles

            cursor.close()

        screen_manager.transition = CardTransition(direction=direction, mode=mode)

        screen_manager.current = screen_name


"""

MAIN

"""

if __name__ == '__main__':
    app = QueueBusterApp()
    app.run()
