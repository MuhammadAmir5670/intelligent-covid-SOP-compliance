
import os
import cv2

from pathlib import Path
from detector import Detector

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

class FaceDetector(Detector):

    def __init__(self, path="weights/yolov5n-face.pt"):
        super(self.__class__, self).__init__(path)

    def inference(self, coors, *args, **kwargs):
        return coors

    def mark(self, results, image):
        for coors in results:
            cv2.rectangle(image, (coors[0], coors[1]), (coors[2], coors[3]), [0,0,255], 2)
        return image

if __name__ == "__main__":
    
    test_folder = BASE_PATH / 'tests'
    save_dir = BASE_PATH / 'results'
    model = FaceDetector()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            locations = model(image)
            for coors in locations:
                cv2.rectangle(image, (coors[0], coors[1]), (coors[2], coors[3]), [0,0,255], 2)

            cv2.imwrite(str(BASE_PATH / 'results' / file), image)