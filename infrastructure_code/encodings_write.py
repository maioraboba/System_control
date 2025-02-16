import face_recognition
import pickle
import os

image_folder = 'C:/Users/ASUS/yandexProject/System_control/photos_from_db'
encodings_file = 'C:/Users/ASUS/yandexProject/System_control/encodings_photos/face_encodings.pkl'

face_encodings = dict()

for filename in os.listdir(image_folder):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(image_folder, filename)
        image = face_recognition.load_image_file(image_path)

        encodings = face_recognition.face_encodings(image)

        if encodings:
            face_encodings[filename.split(".")[0]] = encodings[0]

with open(encodings_file, 'wb') as f:
    pickle.dump(face_encodings, f)
print(face_encodings)
print(f'Кодировки лиц сохранены в {encodings_file}')
