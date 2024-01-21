import cv2
import face_recognition

from mfrc522 import SimpleMFRC522

import sqlite3 as sql


class Video:
    def __init__(self, shape):
        self.cap = cv2.VideoCapture(0)
        self.shape = shape
        self.w, self.h = self.shape
        self.center = (self.w / 2, self.h / 2)
        self.flag_rfid = True
        self.name, self.photos, self.frame = None, None, None
        self.photo, self.img, self.bboxs, self.face_encoding = None, None, None, None
        self.known_faces, self.rgb_frame, self.match = None, None, None

        self.face_names = []
        self.face_locations = []
        self.face_encodings = []

    def success_check(self):
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            cv2.rectangle(self.frame, (left, top), (right, bottom), (255, 255, 0), 2)
            cv2.rectangle(self.frame, (left, bottom - 25), (right, bottom), (255, 255, 0), cv2.FILLED)
            cv2.putText(self.frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            cv2.putText(self.frame, "Проход разрешён.", (int(windowWidth * 0.4), int(windowHeight * 0.85)),
                        font, 1, (255, 255, 255), 2)
            cv2.putText(self.frame, "Лицо найдено", (int(windowWidth * 0.4), int(windowHeight * 0.92)),
                        font, 1, (255, 255, 255), 2)
            cv2.rectangle(self.frame, (0, int(windowHeight * 0.7)), (windowWidth, windowHeight),
                          (0, 255, 0), cv2.FILLED)
            self.flag_rfid = True

    def give_card(self):
        cv2.putText(self.frame, "Поднесите карту", (int(windowWidth * 0.4), int(windowHeight * 0.85)),
                    font, 1, (255, 255, 255), 2)
        cv2.rectangle(self.frame, (0, int(windowHeight * 0.7)), (windowWidth, windowHeight), (0, 0, 255), cv2.FILLED)
        video.flag_rfid = True

    def no_card_in_base(self):
        cv2.putText(self.frame, "Проход запрещён.", (int(windowWidth * 0.4), int(windowHeight * 0.85)),
                    font, 1, (255, 255, 255), 2)
        cv2.putText(self.frame, "Вашей карты нет в базе школы.", (int(windowWidth * 0.4), int(windowHeight * 0.92)),
                    font, 1, (255, 255, 255), 2)
        cv2.rectangle(self.frame, (0, int(windowHeight * 0.7)), (windowWidth, windowHeight), (0, 0, 255), cv2.FILLED)
        self.frame = True

    def card_someone_else(self):
        cv2.putText(self.frame, "Проход запрещён.", (int(windowWidth * 0.4), int(windowHeight * 0.85)),
                    font, 1, (255, 255, 255), 2)
        cv2.putText(self.frame, "Карта не принадлежит вам", (int(windowWidth * 0.4), int(windowHeight * 0.92)),
                    font, 1, (255, 255, 255), 2)
        cv2.rectangle(self.frame, (0, int(windowHeight * 0.7)), (windowWidth, windowHeight), (0, 0, 255), cv2.FILLED)
        video.flag_rfid = False

    def take_img_from_sql(self):
        cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
        self.name = event[1].strip()
        cur.execute('SELECT photo FROM photos WHERE name = ?', [self.name])
        self.photos = cur.fetchall()

    def face_compare(self):
        self.photo = self.photos[0]
        self.img, self.bboxs = detector.findFaces(self.frame, draw=False)

        self.face_encoding = face_recognition.face_encodings(self.photo)[0]
        self.known_faces = [self.face_encoding]

        self.rgb_frame = self.frame[:, :, ::-1]

        self.face_locations = face_recognition.face_locations(self.rgb_frame, model="cnn")
        self.face_encodings = face_recognition.face_encodings(self.rgb_frame, self.face_locations)

        for face_encoding in self.face_encodings:
            # See if the face is a match for the known face(s)
            self.match = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.50)
            if self.match[0]:
                self.face_names.append(self.name)


def cicle_take_fps():
    video.success, video.img = video.cap.read()
    rotate_matrix = cv2.getRotationMatrix2D(center=video.center, angle=-90, scale=1.5)
    video.frame = cv2.warpAffine(src=video.img, M=rotate_matrix, dsize=(video.w, video.h))


if __name__ == "__main__":
    con = sql.connect("data.db")
    cur = con.cursor()

    font = cv2.FONT_HERSHEY_COMPLEX
    detector = face_recognition.FaceDetector()

    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    windowHeight = frame.shape[1]
    windowWidth = frame.shape[0]

    video = Video((windowWidth, windowHeight))

    reader = SimpleMFRC522()
    print('Awaiting input...')

    while True:
        cicle_take_fps()
        if video.flag_rfid:   # flag = True
            event = reader.read()
            if event:
                video.take_img_from_sql()
                if video.photos:
                    video.face_compare()
                    if not video.face_names:
                        video.card_someone_else()
                    else:
                        video.success_check()
                        for i in range(30):
                            cicle_take_fps()
                            video.success_check()
                            cv2.imshow("Image", video.frame)
                else:
                    video.no_card_in_base()
                    for i in range(30):
                        cicle_take_fps()
                        video.no_card_in_base()
                        cv2.imshow("Image", video.frame)
            else:
                for i in range(30):
                    cicle_take_fps()
                    video.give_card()
                    cv2.imshow("Image", video.frame)

        else:   # flag = false
            for _ in range(30):
                cicle_take_fps()
                video.face_compare()
                if video.face_names:
                    video.success_check()
                    for _ in range(30):
                        cicle_take_fps()
                        video.success_check()
                        cv2.imshow("Image", video.frame)
                    break
                else:
                    video.card_someone_else()
                cv2.imshow("Image", video.frame)

        cv2.imshow("Image", video.frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
