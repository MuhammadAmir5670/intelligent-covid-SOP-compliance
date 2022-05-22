import cv2
import numpy as np

import os
from pathlib import Path

from detection.detector import Detector

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


class MaskDetector(Detector):
    COLORS = {
        '': (0,0,255),
        'mask': (0,128,0),
        'no_mask': (0,0,255),
        'mask_not_in_position': (255, 105, 180)
    }

    def __init__(self, path="weights/yolov5s-mask.pt"):
        super(self.__class__, self).__init__(path)

    def inference(self, coors, conf, cls):
        return self.names[int(cls)], coors

    def mark(self, label_n_locations, image):
        for label, location in label_n_locations:
            x1, y1, x2, y2 = location
    
            # Draw a box around the face
            cv2.rectangle(image, (x1, y1), (x2, y2), self.COLORS[label], 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, label, (x1, y2), font, 1, self.COLORS[label], 2)
        
        return image


if __name__ == '__main__':
    test_folder = BASE_PATH / 'tests'
    save_dir =  BASE_PATH / 'results'
    model = MaskDetector()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            cv2.imwrite(os.path.join('results', file), image)
