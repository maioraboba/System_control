import cv2
import face_recognition

from mfrc522 import SimpleMFRC522

import sqlite3 as sql


class RFID:
    def __init__(self):
        self.reader = SimpleMFRC522()
        print('Awaiting input...')
        self.name = None
        # self.flag_rfid = True

    def read(self):
        event = self.reader.read()
        self.name = event[1].strip()


class Camera:
    def __init__(self):
        self.face_names = []
        self.face_locations = []
        self.face_encodings = []

        self.photo, self.img, self.bboxs, self.face_encoding = None, None, None, None
        self.known_faces, self.rgb_frame, self.match = None, None, None
        self.name, self.photos = None, None

        self.detector = face_recognition.FaceDetector()

        self.cap = cv2.VideoCapture(0)
        self.success, self.frame = self.cap.read()
        self.windowHeight = self.frame.shape[1]
        self.windowWidth = self.frame.shape[0]

    def face_compare(self):
        self.photo = self.photos[0]
        self.img, self.bboxs = self.detector.findFaces(video.frame, draw=False)

        self.face_encoding = face_recognition.face_encodings(self.photo)[0]
        self.known_faces = [self.face_encoding]

        self.rgb_frame = video.frame[:, :, ::-1]

        self.face_locations = face_recognition.face_locations(self.rgb_frame, model="cnn")
        self.face_encodings = face_recognition.face_encodings(self.rgb_frame, self.face_locations)

        for face_encoding in self.face_encodings:
            # See if the face is a match for the known face(s)
            self.match = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.50)
            if self.match[0]:
                self.face_names.append(rfid.name)


class SqlData:
    def __init__(self):
        self.con = sql.connect("data.db")
        self.cur = self.con.cursor()

    def take_img_from_sql(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
        self.cur.execute('SELECT photo FROM photos WHERE name = ?', [rfid.name])
        camera.photos = self.cur.fetchall()


class Video:
    def __init__(self, shape):
        self.shape = shape
        self.w, self.h = self.shape
        self.center = (self.w / 2, self.h / 2)
        self.frame = None
        self.success, self.img = False, None
        self.font = cv2.FONT_HERSHEY_COMPLEX

    def success_check(self):
        for (top, right, bottom, left), name in zip(camera.face_locations, camera.face_names):
            cv2.rectangle(self.frame, (left, top), (right, bottom), (255, 255, 0), 2)
            cv2.rectangle(self.frame, (left, bottom - 25), (right, bottom), (255, 255, 0), cv2.FILLED)
            cv2.putText(self.frame, name, (left + 6, bottom - 6), self.font, 0.5, (255, 255, 255), 1)

            cv2.putText(self.frame, "Проход разрешён.", (int(camera.windowWidth * 0.4),
                                                         int(camera.windowHeight * 0.85)), self.font, 1,
                        (255, 255, 255), 2)

            cv2.putText(self.frame, "Лицо найдено", (int(camera.windowWidth * 0.4), int(camera.windowHeight * 0.92)),
                        self.font, 1, (255, 255, 255), 2)
            cv2.rectangle(self.frame, (0, int(camera.windowHeight * 0.7)), (camera.windowWidth, camera.windowHeight),
                          (0, 255, 0), cv2.FILLED)
            # rfid.flag_rfid = True

    def give_card(self):
        cv2.putText(self.frame, "Поднесите карту", (int(camera.windowWidth * 0.4), int(camera.windowHeight * 0.85)),
                    self.font, 1, (255, 255, 255), 2)
        cv2.rectangle(self.frame, (0, int(camera.windowHeight * 0.7)), (camera.windowWidth, camera.windowHeight),
                      (0, 0, 255), cv2.FILLED)
        # rfid.flag_rfid = True

    def no_card_in_base(self):
        cv2.putText(self.frame, "Проход запрещён.", (int(camera.windowWidth * 0.4), int(camera.windowHeight * 0.85)),
                    self.font, 1, (255, 255, 255), 2)

        cv2.putText(self.frame, "Вашей карты нет в базе школы.", (int(camera.windowWidth * 0.4),
                                                                  int(camera.windowHeight * 0.92)), self.font,
                    1, (255, 255, 255), 2)

        cv2.rectangle(self.frame, (0, int(camera.windowHeight * 0.7)), (camera.windowWidth, camera.windowHeight),
                      (0, 0, 255), cv2.FILLED)
        # rfid.flag_rfid = True

    def card_someone_else(self):
        cv2.putText(self.frame, "Проход запрещён.", (int(camera.windowWidth * 0.4), int(camera.windowHeight * 0.85)),
                    self.font, 1, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта не принадлежит вам", (int(camera.windowWidth * 0.4),
                                                             int(camera.windowHeight * 0.92)), self.font, 1,
                    (255, 255, 255), 2)
        cv2.rectangle(self.frame, (0, int(camera.windowHeight * 0.7)), (camera.windowWidth, camera.windowHeight),
                      (0, 0, 255), cv2.FILLED)
        rfid.flag_rfid = False

    def rotate_img(self):
        camera.success, camera.img = camera.cap.read()
        rotate_matrix = cv2.getRotationMatrix2D(center=video.center, angle=-90, scale=1.5)
        self.frame = cv2.warpAffine(src=camera.img, M=rotate_matrix, dsize=(video.w, video.h))


if __name__ == "__main__":
    camera = Camera()
    video = Video((camera.windowWidth, camera.windowHeight))
    sqlData = SqlData()

    while True:
        rfid = RFID()
        video.rotate_img()
        # if rfid.flag_rfid:
        rfid.read()
        if rfid.name:
            sqlData.take_img_from_sql()
            if camera.photos:
                camera.face_compare()
                if camera.face_names:
                    video.success_check()
                    for i in range(30):
                        video.rotate_img()
                        video.success_check()
                        cv2.imshow("Image", video.frame)
                else:
                    video.card_someone_else()
            else:
                video.no_card_in_base()
                for i in range(30):
                    video.rotate_img()
                    video.no_card_in_base()
                    cv2.imshow("Image", video.frame)
        else:
            for i in range(30):
                video.rotate_img()
                video.give_card()
                cv2.imshow("Image", video.frame)
        #
        # else:   # flag = false
        #     for _ in range(30):
        #         video.rotate_img()
        #         camera.face_compare()
        #         if camera.face_names:
        #             video.success_check()
        #             for _ in range(30):
        #                 video.rotate_img()
        #                 video.success_check()
        #                 cv2.imshow("Image", video.frame)
        #             break
        #         else:
        #             video.card_someone_else()
        #         cv2.imshow("Image", video.frame)

        cv2.imshow("Image", video.frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
