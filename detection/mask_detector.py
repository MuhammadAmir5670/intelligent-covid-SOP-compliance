# -*- coding: UTF-8 -*-
import cv2
import torch
import copy
from utils.datasets import letterbox
from utils.general import xyxy2xywh
from utils.general import check_img_size, non_max_suppression, scale_coords
import os
from pathlib import Path

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


# Constants 
IMAGE_SIZE = 640
CONF_TRESHOLD = 0.3
IOU_THESHOLD = 0.5
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def get_coors(xywh, w, h):
    x1 = int(xywh[0] * w - 0.5 * xywh[2] * w)
    y1 = int(xywh[1] * h - 0.5 * xywh[3] * h)
    x2 = int(xywh[0] * w + 0.5 * xywh[2] * w)
    y2 = int(xywh[1] * h + 0.5 * xywh[3] * h)
    return [x1, y1, x2, y2]

class MaskDetector:
    COLORS = {
        '': (0,0,255),
        'mask': (0,128,0),
        'no_mask': (0,0,255),
        'mask_not_in_position': (255, 105, 180)
    }

    def __init__(self, path='weights/yolov5s-mask.pt') -> None:
        self.model = torch.load(BASE_PATH / path, map_location=device)['model'].float().fuse().eval()
        self.names = self.model.names

    def __call__(self, image) -> list:
        results = []

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

        # Process detections
        for _, detections in enumerate(predictions): 
            gn = torch.tensor(image.shape)[[1, 0, 1, 0]].to(device) 
            if len(detections):
                detections[:, :4] = scale_coords(image_.shape[2:], detections[:, :4], image.shape).round()
                for index in range(detections.size()[0]):
                    xywh = (xyxy2xywh(detections[index, :4].view(1, 4)) / gn).view(-1).tolist()
                    coors = get_coors(xywh, w, h)
                    *locs, conf, cls = detections[index]
                    results.append((self.names[int(cls)], coors))
        return results

    def mark(self, label_n_locations, image):
        for label, location in label_n_locations:

            top, left, bottom, right = location
            # x1, y1, x2, y2 = location
            # x1 distance from left
            # x2 distance from left
            # y2 distance from top
            
            # Draw a box around the face
            cv2.rectangle(image, (top, left), (bottom, right), self.COLORS[label], 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(image, label, (top + 5, left - 10), font, 1, self.COLORS[label], 2)
        
        return image


if __name__ == '__main__':
    test_folder = 'tests'
    save_dir = 'results'
    model = MaskDetector()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            cv2.imwrite(os.path.join('results', file), image)
