
import cv2
import torch

from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh
from utils.datasets import letterbox
import copy

from pathlib import Path
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 640
CONF_TRESHOLD = 0.3
IOU_THESHOLD = 0.5
BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

def get_coors(xywh, w, h):
    x1 = int(xywh[0] * w - 0.5 * xywh[2] * w)
    y1 = int(xywh[1] * h - 0.5 * xywh[3] * h)
    x2 = int(xywh[0] * w + 0.5 * xywh[2] * w)
    y2 = int(xywh[1] * h + 0.5 * xywh[3] * h)
    return [x1, y1, x2, y2]


class FaceDetector:

    def __init__(self, path='weights/yolov5n-face.pt') -> None:
        self.model = attempt_load(BASE_PATH / path, map_location=device)

    def __call__(self, image):
        h,w,_  = image.shape
        image_ = copy.deepcopy(image)

        height_0, width_0 = image.shape[:2]  # orig hw
        resized = IMAGE_SIZE / max(height_0, width_0)  # resize image to img_size

        if resized != 1:  # always resize down, only resize up if training with augmentation
            interp = cv2.INTER_AREA if resized < 1  else cv2.INTER_LINEAR
            image_ = cv2.resize(image_, (int(width_0 * resized), int(height_0 * resized)), interpolation=interp)

        image_size = check_img_size(IMAGE_SIZE, s=self.model.stride.max())  # check img_size

        image_ = letterbox(image_, new_shape=image_size)[0]
        
        # Convert
        image_ = image_[:, :, ::-1].transpose(2, 0, 1).copy()  # BGR to RGB, to 3x416x416

        image_ = torch.from_numpy(image_).to(device)
        image_ = image_.float()  # uint8 to fp16/32
        image_ /= 255.0  # 0 - 255 to 0.0 - 1.0
        if image_.ndimension() == 3:
            image_ = image_.unsqueeze(0)

        # Inference
        predictions = self.model(image_)[0]

        # Apply NMS
        predictions = non_max_suppression(predictions, CONF_TRESHOLD, IOU_THESHOLD)

        locations = []
        # Process detections
        for _, detections in enumerate(predictions): 
            gn = torch.tensor(image.shape)[[1, 0, 1, 0]].to(device) 
            if len(detections):
                detections[:, :4] = scale_coords(image_.shape[2:], detections[:, :4], image.shape).round()
                for index in range(detections.size()[0]):
                    xywh = (xyxy2xywh(detections[index, :4].view(1, 4)) / gn).view(-1).tolist()
                    coors = get_coors(xywh, w, h)
                    locations.append(coors)

        return locations


import os

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