from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO


if __name__ == "__main__":
    reader = SimpleMFRC522()
    try:
            text = input('Новый ученик:')
            print("Поднесите карту к устройству ввода")
            reader.write(text)
            print("Записано")
    finally:
        GPIO.cleanup()
