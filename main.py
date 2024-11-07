import cv2
import face_recognition
import numpy
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import pickle

from mfrc522 import SimpleMFRC522

import sqlite3 as sql


class RFID:
    def __init__(self):
        self.reader = SimpleMFRC522()
        self.name = None
        self.flag_rfid = False

    def read(self):
        try:
            event = self.reader.read()
            self.name = event[1].strip()
        finally:
            GPIO.cleanup()


class Camera:
    def __init__(self):
        self.face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.photo, self.img, self.bboxs, self.face_encoding = None, None, None, None
        self.known_faces, self.rgb_frame, self.match = None, None, None
        self.name, self.photos = None, None
        self.printed = None

        self.windowHeight = 480
        self.windowWidth = 800
        self.cam = PiCamera()
        self.cam.resolution = (self.windowWidth, self.windowHeight)
        self.cam.framerate = 30
        self.rawCapture = PiRGBArray(self.cam, size=(self.windowWidth, self.windowHeight))

    def face_compare(self):
        small_frame = cv2.resize(camera.img, (0, 0), fx=0.25, fy=0.25)
        self.rgb_frame = numpy.ascontiguousarray(small_frame[:, :, ::-1])

        self.face_locations = face_recognition.face_locations(self.rgb_frame)
        self.face_encodings = face_recognition.face_encodings(self.rgb_frame, self.face_locations)

        self.face_names = []
        for face_encoding in self.face_encodings:
            self.match = face_recognition.compare_faces([self.known_faces[rfid.name]], face_encoding)
            name = "Unknown"
            if self.match[0]:
                name = rfid.name
            self.face_names.append(name)


class SqlData:
    def __init__(self):
        self.con = sql.connect("/home/admin/sys_new/db/data.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def take_img_from_sql(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
        self.cur.execute('SELECT photo FROM photos WHERE name = ?', (rfid.name,))
        camera.photos = self.cur.fetchall()

        if camera.photos:
            for photo in camera.photos:
                with open(f"/home/admin/sys_new/photos_from_db/{rfid.name}.jpg", "wb") as file:
                    file.write(photo[0])
        else:
            video.no_card_in_base()


class Video:
    def __init__(self, shape):
        self.shape = shape
        self.w, self.h = self.shape
        self.center = (self.w / 2, self.h / 2)
        self.frame = None
        self.success, self.img = False, None
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.time_show = 3000
        self.result = None

    def success_check(self):
        name = rfid.name
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (0, 255, 0), cv2.FILLED)
        cv2.putText(self.frame, f"{' '.join(name.split()[:2])},", (int(camera.windowHeight * 0.25),
                                                        int(camera.windowWidth * 0.4)), self.font,
                    0.8, (255, 255, 255), 2)
        cv2.putText(self.frame, "Проходите", (int(camera.windowHeight * 0.3),
                                                int(camera.windowWidth * 0.5)), self.font,
            0.8, (255, 255, 255), 2)
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('Image', self.frame)
        rfid.flag_rfid = False
        cv2.waitKey(self.time_show)
        camera.rawCapture.truncate(0)
        return 0

    def no_card_in_base(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (0, 0, 255), cv2.FILLED)
        cv2.putText(self.frame, "Проход запрещен.",
                    (int(camera.windowHeight * 0.05), int(camera.windowWidth * 0.4)),
                    self.font, 0.95, (255, 255, 255), 2)
        cv2.putText(self.frame, f"{rfid.name},", (int(camera.windowHeight * 0.05),
                                                  int(camera.windowWidth * 0.45)),
                    self.font, 0.9, (255, 255, 255), 2)
        cv2.putText(self.frame, "Вашей карты нет в базе школы.", (int(camera.windowHeight * 0.05),
                                                                  int(camera.windowWidth * 0.5)),
                    self.font, 0.7, (255, 255, 255), 2)
        rfid.flag_rfid = False
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('Image', self.frame)
        cv2.waitKey(self.time_show)
        camera.rawCapture.truncate(0)
        return 0

    def card_someone_else(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (0, 0, 255), cv2.FILLED)
        cv2.putText(self.frame, "Проход запрещен.", (int(camera.windowHeight * 0.2), int(camera.windowWidth * 0.5)),
                    self.font, 0.95, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта принадлежит не вам.", (int(camera.windowHeight * 0.05),
                                                              int(camera.windowWidth * 0.6)), self.font, 0.85,
                    (255, 255, 255), 2)
        rfid.flag_rfid = False
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('Image', self.frame)
        cv2.waitKey(self.time_show)
        camera.rawCapture.truncate(0)
        return 0

    def give_card(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (255, 0, 0), cv2.FILLED)
        cv2.putText(self.frame, "Поднесите карту.", (int(camera.windowHeight * 0.2), int(camera.windowWidth * 0.5)),
                    self.font, 0.95, (255, 255, 255), 2)
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        print("showed_give_card")
        cv2.imshow("Image", self.frame)
        cv2.waitKey(0)
        camera.rawCapture.truncate(0)
        return 0

    def card_taken(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (0, 255, 0), cv2.FILLED)
        cv2.putText(self.frame, f"{' '.join(rfid.name.split()[:3])},",
                    (int(camera.windowHeight * 0.05), int(camera.windowWidth * 0.45)),
                    self.font, 0.8, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта успешно считана.",
                    (int(camera.windowHeight * 0.05), int(camera.windowWidth * 0.5)),
                    self.font, 0.8, (255, 255, 255), 2)
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow("Image", self.frame)
        rfid.flag_rfid = False
        cv2.waitKey(self.time_show)
        camera.rawCapture.truncate(0)
        return 0


if __name__ == "__main__":
    cv2.namedWindow('Image', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    camera = Camera()
    video = Video((camera.windowWidth, camera.windowHeight))
    sqlData = SqlData()
    with open("/home/admin/sys_new/encodings_photos/face_encodings.pkl", 'rb') as f:
        loaded_face_encodings = pickle.load(f)
    camera.known_faces = loaded_face_encodings
    running = True
    camera.printed = cv2.imread("/home/admin/sys_new/img/proz.jpg")
    rfid = RFID()
    while running:
        if not rfid.flag_rfid:
            camera.printed = cv2.imread("/home/admin/sys_new/img/proz.jpg")
            thr1 = threading.Thread(target=rfid.read)
            thr2 = threading.Thread(target=video.give_card)
            print("give_card")
            thr2.start()
            thr1.start()
            thr1.join()
            if rfid.name:
                rfid.flag_rfid = True
                sqlData.take_img_from_sql()
        else:
            video.card_taken()
            camera.printed = cv2.imread("/home/admin/sys_new/img/proz.jpg")
            for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
                camera.img = frame.array
                video.frame = frame.array
                camera.img = cv2.rotate(camera.img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                camera.face_compare()
                print("checked")

                if rfid.name in camera.face_names:
                    video.success_check()
                    break
                elif camera.face_names:
                    video.card_someone_else()
                    break
                print("show")

                cv2.imshow("Image", video.frame)
                camera.rawCapture.truncate(0)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            print("babax")

    cv2.destroyAllWindows()