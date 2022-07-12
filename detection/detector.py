import os
import cv2
import copy
import torch
import numpy as np

from pathlib import Path
from utils.torch_utils import select_device
from models.experimental import attempt_load

from utils.general import check_img_size, scale_coords, non_max_suppression
from utils.datasets import letterbox

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

class Detector:

    image_size = 640
    conf_threshold = 0.3
    iou_threshold = 0.5
    
    def __init__(self, path, threshold=0.3):
        self.threshold = threshold
        self.device = 'cpu'
        self.model = attempt_load(BASE_PATH / path, map_location=self.device)
        self.names = self.model.names if hasattr(self.model, 'names') else self.model.modules.names

    
    def __call__(self, image):
        inference = []
        # orig height and width of the image
        height, width = image.shape[:2]

        # Copy of the original image
        image_ = copy.deepcopy(image)
        
        # resize image to self.image_size
        resized = self.image_size / max(height, width)

        # always resize down, only resize up if training with augmentation
        if resized != 1:
            interp = cv2.INTER_AREA if resized < 1  else cv2.INTER_LINEAR
            image_ = cv2.resize(image_, (int(width * resized), int(height * resized)), interpolation=interp)

        # check image is of size => self.image_size
        image_size = check_img_size(self.image_size)
        image_ = letterbox(image, new_shape=image_size)[0]
        
        # Convert BGR to RGB, to 3x416x416
        image_ = image_[:, :, ::-1].transpose(2, 0, 1).copy()

        image_ = torch.from_numpy(image_).to(self.device)
        image_ = image_.float()  # uint8 to fp16/32
        image_ /= 255.0  # 0 - 255 to 0.0 - 1.0
        if image_.ndimension() == 3:
            image_ = image_.unsqueeze(0)

        # Inference
        predictions = self.model(image_, augment=True)[0]

        # Apply NMS
        predictions = non_max_suppression(predictions, self.conf_threshold, self.iou_threshold, agnostic=True)

        # detections in the image
        for _, detections in enumerate(predictions):
            if detections is not None and len(detections):

                # Rescale boxes from self.image_size to original image size
                detections[:, :4] = scale_coords(image_.shape[2:], detections[:, :4], image.shape).round()

                for *coors, conf, cls in detections:
                    result = self.inference(np.array(coors, dtype=int).tolist(), conf, cls)

                    if result:
                        inference.append(result)

        return inference

    def inference(self, coors, conf, cls):
        """"processes the inference"""
        if conf > self.threshold:
            return cls, coors

    def mark(self, *args, **kwargs):
        """Function that draws the inference on the image"""
        raise RuntimeError('Must be implemented by subclasses.')