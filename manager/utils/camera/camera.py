import cv2
from .base import BaseCamera

from manager.utils.combined import merge

class Camera(BaseCamera):
    streaming = False

    def __init__(self, source=-1):
        Camera.set_video_source(source)
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        if BaseCamera.video_source != source:
            if source == 0:
                BaseCamera.camera = cv2.VideoCapture(source, cv2.CAP_DSHOW)
            else:
                BaseCamera.camera = cv2.VideoCapture(source)
            
            Camera.streaming = True
            BaseCamera.video_source = source

    @staticmethod
    def validate_source(source):
        if source != 0 and source != -1:
            camera = cv2.VideoCapture(source)
            if not camera.isOpened():
                print(f'Could not start camera. invalid source given: {source}')
                return False
            camera.release()
        return True

    @staticmethod
    def stop_stream():
        Camera.streaming = False
        BaseCamera.video_source = None
        BaseCamera.camera.release()

    @staticmethod
    def frames():
        if not BaseCamera.camera.isOpened():
            ValueError(f'Could not start camera. invalid source given: {BaseCamera.video_source}')

        while True:
            # read current frame
            _, img = BaseCamera.camera.read()
            if img is None:
                Camera.stop_stream()
                return

            # encode as a jpeg image and return it
            # yield cv2.imencode('.jpg', img)[1].tobytes()
            yield img

    def stream(self, models=[]):
        """Video streaming generator function."""
        yield b'--frame\r\n'

        while Camera.streaming:
            frame = self.get_frame()
            for model in models:
                # get inference results
                results = model(frame)
                # plot inference results on frame
                frame = model.mark(results, frame)

            # Encode the frames to jpg format
            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'
    
    def combined(self, models=[]):
        """Video streaming generator function."""
        yield b'--frame\r\n'
        while Camera.streaming:
            frame = self.get_frame()
            if frame is None:
                continue
            frame = merge(frame, *models)
            
            # Encode the frames to jpg format
            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'