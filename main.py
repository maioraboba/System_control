import cv2
import face_recognition
import numpy
import threading
from picamera.array import PiRGBArray
from picamera import PiCamera

from mfrc522 import SimpleMFRC522

import sqlite3 as sql


class RFID:
    def __init__(self):
        self.reader = SimpleMFRC522()
        self.name = None
        self.flag_rfid = False

    def read(self):
        print(threading.get_ident())
        event = self.reader.read()
        self.name = event[1].strip()
        print("readed")


class Camera:
    def __init__(self):
        self.face_names = []
        self.face_locations = []
        self.face_encodings = []
        self.photo, self.img, self.bboxs, self.face_encoding = None, None, None, None
        self.known_faces, self.rgb_frame, self.match = None, None, None
        self.name, self.photos = None, None

        self.windowHeight = 480
        self.windowWidth = 800
        self.cam = PiCamera()
        self.cam.resolution = (self.windowWidth, self.windowHeight)
        self.cam.framerate = 30
        self.rawCapture = PiRGBArray(self.cam, size=(self.windowWidth, self.windowHeight))

    def face_compare(self):
        small_frame = cv2.resize(video.frame, (0, 0), fx=0.25, fy=0.25)
        self.rgb_frame = numpy.ascontiguousarray(small_frame[:, :, ::-1])

        self.face_locations = face_recognition.face_locations(self.rgb_frame)
        self.face_encodings = face_recognition.face_encodings(self.rgb_frame, self.face_locations)

        self.face_names = []
        for face_encoding in self.face_encodings:
            # See if the face is a match for the known face(s)
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

        person_image = face_recognition.load_image_file(f"{rfid.name}.jpg")
        print(rfid.name)
        camera.face_encoding = face_recognition.face_encodings(person_image)[0]
        camera.known_faces = [camera.face_encoding]


class Video:
    def __init__(self, shape):
        self.shape = shape
        self.w, self.h = self.shape
        self.center = (self.w / 2, self.h / 2)
        self.frame = None
        self.success, self.img = False, None
        self.font = cv2.FONT_HERSHEY_COMPLEX

    def success_check(self):
        name = rfid.name
        cv2.rectangle(self.frame, (0, 0), (camera.windowWidth, camera.windowHeight),
                      (0, 255, 0), cv2.FILLED)

        cv2.putText(self.frame, f"{name}, проходите.", (int(camera.windowWidth * 0.3),
                                                        int(camera.windowHeight * 0.50)), self.font,
                    1, (255, 255, 255), 2)
        cv2.imshow('Image', self.frame)
        rfid.flag_rfid = False
        cv2.waitKey(5000)

    def no_card_in_base(self):
        cv2.putText(self.frame, "Проход запрещён.", (int(camera.windowWidth * 0.4), int(camera.windowHeight * 0.85)),
                    self.font, 1, (255, 255, 255), 2)

        cv2.putText(self.frame, f"{rfid.name}, вашей карты нет в базе школы.", (int(camera.windowWidth * 0.4),
                                                                                int(camera.windowHeight * 0.92)),
                    self.font, 1, (255, 255, 255), 2)

        cv2.rectangle(self.frame, (0, int(camera.windowHeight * 0.7)), (camera.windowWidth, camera.windowHeight),
                      (0, 0, 255), cv2.FILLED)
        rfid.flag_rfid = False
        cv2.imshow('Image', self.frame)
        cv2.waitKey(5000)

    def card_someone_else(self):
        cv2.rectangle(self.frame, (0, 0), (camera.windowWidth, camera.windowHeight),
                      (0, 0, 255), cv2.FILLED)
        cv2.putText(self.frame, "Проход запрещен.", (int(camera.windowWidth * 0.3), int(camera.windowHeight * 0.5)),
                    self.font, 1, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта принадлежит не вам", (int(camera.windowWidth * 0.2),
                                                             int(camera.windowHeight * 0.6)), self.font, 1,
                    (255, 255, 255), 2)
        rfid.flag_rfid = False
        cv2.imshow('Image', self.frame)
        cv2.waitKey(5000)

    def show_banan(self):
        global stop
        self.frame = camera.img
        cv2.rectangle(self.frame, (0, 0), (camera.windowWidth, camera.windowHeight),
                      (255, 0, 0), cv2.FILLED)
        cv2.putText(self.frame, "Поднесите карту.", (int(camera.windowWidth * 0.3), int(camera.windowHeight * 0.5)),
                    self.font, 1, (255, 255, 255), 2)
        cv2.imshow("Image", self.frame)
        print("show")
        cv2.waitKey(0)
        if stop:
            print(34543)
            return


def rotate_img():
    rotate_matrix = cv2.getRotationMatrix2D(center=video.center, angle=90, scale=1)
    camera.img = cv2.warpAffine(src=camera.img, M=rotate_matrix, dsize=(video.w, video.h))


def main():
    global stop, running
    while running:
        if not rfid.flag_rfid:
            stop = False
            thr1 = threading.Thread(target=rfid.read)
            camera.img = cv2.imread("proz.png")
            thr2 = threading.Thread(target=video.show_banan)
            thr2.start()
            thr1.start()
            thr1.join()
            stop = True
            cv2.waitKey(100)
            if rfid.name:
                rfid.flag_rfid = True
                sqlData.take_img_from_sql()
                print("niggg...")
        else:
            print("cum")
            for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):

                camera.img = frame.array
                video.frame = camera.img
                rotate_img()
                camera.face_compare()
                print(camera.face_names)
                if rfid.name in camera.face_names:
                    print("a")
                    video.success_check()
                    print("b")
                elif camera.face_names:
                    print("c")
                    video.card_someone_else()
                    print("d")
                print(2)
                cv2.imshow("Image", video.frame)
                camera.rawCapture.truncate(0)
                if not rfid.flag_rfid:
                    break
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break


if __name__ == "__main__":
    camera = Camera()
    video = Video((camera.windowWidth, camera.windowHeight))
    sqlData = SqlData()
    running = True
    stop = False

    # obama_image = face_recognition.load_image_file("obama.jpg")
    # camera.face_encoding = face_recognition.face_encodings(obama_image)[0]
    # camera.known_faces = [camera.face_encoding]

    rfid = RFID()
    thrm = threading.Thread(target=main)
    thrm.start()