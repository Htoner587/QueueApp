import unittest
from queueAnalysisSQL import queueAnalysis
import main

class MyTestCase_App(unittest.TestCase):

    app=main.QueueBusterApp()


    def test_setUser(self):

        self.app.run()

        self.app.setUser(1,2)

        self.assertEqual(self.app.userNumber, 2)

        self.assertEqual(self.app.userType, 1)


    def test_setStore(self):

        self.app.setStore(1)

        self.assertEqual(self.app.selectedStore, 1)

        self.assertEqual(self.app.entrance_videos[0],"videos/video-3a.mov")

        self.assertEqual(self.app.entrance_videos[1], "videos/video-5a.mov")

        self.assertEqual(self.app.exit_videos[0], "videos/video-2c.mov")

        self.assertEqual(self.app.exit_videos[1], "videos/video-5b.mov")


    def test_selectStore(self):

        self.app.selectStore("Asda Westwood")

        self.assertEqual(self.app.selectedStore, 1)


if __name__ == '__main__':
    unittest.main()
