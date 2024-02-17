import cv2
import face_recognition
import numpy
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO

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
            self.match = face_recognition.compare_faces(self.known_faces, face_encoding)
            name = "Unknown"
            if self.match[0]:
                name = rfid.name
            self.face_names.append(name)


class SqlData:
    def __init__(self):
        self.con = sql.connect("data.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def take_img_from_sql(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
        self.cur.execute('SELECT photo FROM photos WHERE name = ?', (rfid.name,))
        camera.photos = self.cur.fetchall()

        if camera.photos:
            for photo in camera.photos:
                with open(f"{rfid.name}.jpg", "wb") as file:
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
        cv2.putText(self.frame, f"{name}, проходите.", (int(camera.windowHeight * 0.1),
                                                        int(camera.windowWidth * 0.4)), self.font,
                    0.8, (255, 255, 255), 2)
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('Image', self.frame)
        rfid.flag_rfid = False
        cv2.waitKey(self.time_show)

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

    def card_someone_else(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (0, 0, 255), cv2.FILLED)
        cv2.putText(self.frame, "Проход запрещен.", (int(camera.windowHeight * 0.2), int(camera.windowWidth * 0.5)),
                    self.font, 0.95, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта принадлежит не вам.", (int(camera.windowHeight * 0.08),
                                                              int(camera.windowWidth * 0.6)), self.font, 0.85,
                    (255, 255, 255), 2)
        rfid.flag_rfid = False
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow('Image', self.frame)
        cv2.waitKey(self.time_show)

    def give_card(self):
        self.frame = camera.printed
        cv2.rectangle(self.frame, (0, 0), (camera.windowHeight, camera.windowWidth),
                      (255, 0, 0), cv2.FILLED)
        cv2.putText(self.frame, "Поднесите карту.", (int(camera.windowHeight * 0.2), int(camera.windowWidth * 0.5)),
                    self.font, 0.95, (255, 255, 255), 2)
        self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow("Image", self.frame)
        cv2.waitKey(0)

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


def main():
    global running
    while running:
        if not rfid.flag_rfid:
            thr1 = threading.Thread(target=rfid.read)
            thr2 = threading.Thread(target=video.give_card)
            camera.printed = cv2.imread("proz.jpg")
            thr1.start()
            thr2.start()
            thr1.join()
            if rfid.name:
                rfid.flag_rfid = True
                sqlData.take_img_from_sql()
        else:
            video.card_taken()
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    camera = Camera()
    video = Video((camera.windowWidth, camera.windowHeight))
    sqlData = SqlData()
    running = True

    rfid = RFID()
    thrm = threading.Thread(target=main)
    thrm.start()
