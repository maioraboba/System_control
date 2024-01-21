import cv2


class Camera:
    trackers = {
        'mos': cv2.legacy.TrackerMOSSE_create,
        'csrt': cv2.TrackerCSRT_create,
        'kcf': cv2.TrackerKCF_create,
        # 'tld': cv2.TrackerTLD_create,
        'mil': cv2.TrackerMIL_create,
        'got': cv2.TrackerGOTURN_create,
        # 'boos': cv2.TrackerBoosting_create,
        # 'mflow': cv2.TrackerMedianFlow_create,
    }

    def __init__(self, path="video.mp4", shape=(1280, 720), tracker='mos'):
        self.cap = cv2.VideoCapture(0)
        self.shape = shape
        self.w, self.h = self.shape
        self.center_w_img, self.center_h_img = self.w // 2, self.h // 2
        self.wait = 20
        self.side_bbox = 30

        self.bbox = (
        self.center_w_img - self.side_bbox, self.center_h_img - self.side_bbox, self.side_bbox * 2, self.side_bbox * 2)

        self.center_w_bbox, self.center_h_bbox = self.center_w_img, self.center_h_img

        self.tracker = self.trackers[tracker]()

    def draw_tracking_box(self, img, bounding_box):
        x, y, w, h = int(bounding_box[0]), int(bounding_box[1]), int(bounding_box[2]), int(bounding_box[3])

        self.center_w_bbox, self.center_h_bbox = x + w // 2, y + h // 2  # center bounding box

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3, 1)  # tracking box

        cv2.line(img, (x + w // 2, 0), (x + w // 2, y),
                 (0, 255, 0), thickness=1)
        cv2.line(img, (x + w // 2, y + h), (x + w // 2, self.h),
                 (0, 255, 0), thickness=1)
        cv2.line(img, (0, y + h // 2), (x, y + h // 2),
                 (0, 255, 0), thickness=1)
        cv2.line(img, (x + w, y + h // 2), (self.w, y + h // 2),
                 (0, 255, 0), thickness=1)

        cv2.line(img, (self.center_w_img - 20, self.center_h_img), (self.center_w_img + 20, self.center_h_img),
                 (0, 0, 255), thickness=1)  # aim box
        cv2.line(img, (self.center_w_img, self.center_h_img - 20), (self.center_w_img, self.center_h_img + 20),
                 (0, 0, 255), thickness=1)  # aim box

        cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)  # info

    def draw_aim_box(self):
        cv2.rectangle(self.img, (self.center_w_img - self.side_bbox, self.center_h_img - self.side_bbox),
                      (self.center_w_img + self.side_bbox, self.center_h_img + self.side_bbox),
                      (0, 0, 255), thickness=2)
        cv2.circle(self.img, (self.center_w_img, self.center_h_img), 5, (0, 0, 255), thickness=2)


class Drone:
    def __init__(self):
        pass


class Target:
    def __init__(self):
        self.flag_tracking = False

    @staticmethod
    def take_cursor_point(event, x, y, flags, parm):
        if event == cv2.EVENT_LBUTTONDOWN and target.flag_tracking is False:
            target.flag_tracking = True
            camera.tracker = camera.trackers[tracker]()
            camera.tracker.init(camera.img, camera.bbox)
            camera.wait = 1
        elif event == cv2.EVENT_RBUTTONDOWN and target.flag_tracking is True:
            target.flag_tracking = False
            camera.wait = 20


if __name__ == "__main__":
    drone = Drone()
    target = Target()

    path = "video.mp4"  # путь к видео файлу
    shape = 1280, 720  # размер окна (по дефолту 1280x720)
    tracker = 'mos'  # название трекера
    camera = Camera(path, shape, tracker)

    cv2.namedWindow("Tracking")
    cv2.setMouseCallback("Tracking", target.take_cursor_point)

    while True:
        timer = cv2.getTickCount()
        camera.success, camera.img = camera.cap.read()
        camera.img = cv2.resize(camera.img, camera.shape)

        if target.flag_tracking:
            success, bbox = camera.tracker.update(camera.img)
            if success:
                camera.draw_tracking_box(camera.img, bbox)
            else:
                cv2.putText(camera.img, "Lost", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            camera.draw_aim_box()

        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        cv2.putText(camera.img, f"FPS: {str(int(fps))}", (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Tracking", camera.img)

        if cv2.waitKey(camera.wait) & 0xFF == ord("q"):
            break
