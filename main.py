import cv2
import face_recognition
import numpy as np
import threading
import pickle
import sqlite3 as sql
import RPi.GPIO as GPIO
from picamera.array import PiRGBArray
from picamera import PiCamera
from mfrc522 import SimpleMFRC522


class RFID:
    def __init__(self):
        self.reader = SimpleMFRC522()
        self.name = None
        self.flag_rfid = False

    def read(self):
        try:
            _, self.name = self.reader.read()
            self.name = self.name.strip()
            self.flag_rfid = True  # Устанавливаем флаг сразу после считывания
        finally:
            GPIO.cleanup()


class Camera:
    def __init__(self):
        self.windowHeight, self.windowWidth = 480, 800
        self.cam = PiCamera()
        self.cam.resolution = (self.windowWidth, self.windowHeight)
        self.cam.framerate = 30
        self.rawCapture = PiRGBArray(self.cam, size=(self.windowWidth, self.windowHeight))
        self.known_faces = self.load_encodings()
        self.default_img = cv2.imread("/home/admin/sys_new/img/proz.jpg")

    @staticmethod
    def load_encodings():
        with open("/home/admin/sys_new/encodings_photos/face_encodings.pkl", 'rb') as f:
            return pickle.load(f)

    def face_compare(self, img):
        """Сравнение лица с базой"""
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for fe in face_encodings:
            match = face_recognition.compare_faces([self.known_faces.get(rfid.name, np.zeros(128))], fe)
            face_names.append(rfid.name if match[0] else "Unknown")

        return face_names


class SqlData:
    def __init__(self):
        self.con = sql.connect("/home/admin/sys_new/db/data.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def take_img_from_sql(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
        self.cur.execute('SELECT photo FROM photos WHERE name = ?', (rfid.name,))
        photos = self.cur.fetchall()

        if photos:
            with open(f"/home/admin/sys_new/photos_from_db/{rfid.name}.jpg", "wb") as file:
                file.write(photos[0][0])
        else:
            video.display_message(f"Проход запрещен {rfid.name}, вашей карты нет в базе школы.", (0, 0, 255))
            rfid.flag_rfid = False


class Video:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.time_show = 2000  # Уменьшил время ожидания

    @staticmethod
    def split_messages(message):
        line = message.split()
        sc, res_message, mes = 0, list(), list()
        for k in line:
            if len(k) + sc <= 18:
                mes.append(k)
                sc += len(k)
            else:
                res_message.append(mes)
                sc = 0
                mes = [k]
        res_message.append(mes)
        return res_message

    def display_message(self, message, color):
        frame = camera.default_img.copy()
        cv2.rectangle(frame, (0, 0), (camera.windowHeight, camera.windowWidth), color, cv2.FILLED)
        heigh = 150
        for line in self.split_messages(message):
            cv2.putText(frame, " ".join(line).strip(), (50, heigh), self.font, 0.8, (255, 255, 255), 2)
            heigh += 50
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imshow("Image", frame)
        cv2.waitKey(self.time_show)
        camera.rawCapture.truncate(0)


if __name__ == "__main__":
    cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('Image', cv2.WND_PROP_FULLSCREEN, 1)

    camera = Camera()
    video = Video()
    sqlData = SqlData()
    rfid = RFID()

    while True:
        if not rfid.flag_rfid:
            thr = threading.Thread(target=rfid.read)
            thr.start()
            video.display_message("Поднесите карту.", (255, 0, 0))
            thr.join()  # Ждем, пока RFID считает карту
            if rfid.name:
                sqlData.take_img_from_sql()
        else:
            video.display_message(f"Карта успешно считана, {rfid.name}.", (0, 255, 0))
            rfid.flag_rfid = False
            for frame in camera.cam.capture_continuous(camera.rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                face_names = camera.face_compare(cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE))

                if rfid.name in face_names:
                    video.display_message(f"Проходите, {rfid.name}.", (0, 255, 0))
                    break
                elif face_names:
                    video.display_message("Проход запрещен. Карта принадлежит не вам.", (0, 0, 255))
                    break

                cv2.imshow("Image", img)
                camera.rawCapture.truncate(0)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break