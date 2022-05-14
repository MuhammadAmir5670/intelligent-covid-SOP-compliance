import argparse

from utils.datasets import *
from utils.utils import *

import os
from pathlib import Path
import copy


BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
IMAGE_SIZE = 640
CONF_TRESHOLD = 0.3
IOU_THESHOLD = 0.5

class SocialDistancing:
    
    def __init__(self, path='weights/yolov5s.pt') -> None:
        self.device = torch_utils.select_device()
        self.model = torch.load(BASE_PATH / path, map_location=self.device)['model'].float().fuse().eval()
        self.names = self.model.names if hasattr(self.model, 'names') else self.model.modules.names

    def __call__(self, image):
        results = []

        h,w,_  = image.shape
        image_ = copy.deepcopy(image)

        height_0, width_0 = image.shape[:2]  # orig hw
        resized = IMAGE_SIZE / max(height_0, width_0)  # resize image to img_size

        if resized != 1:  # always resize down, only resize up if training with augmentation
            interp = cv2.INTER_AREA if resized < 1  else cv2.INTER_LINEAR
            image_ = cv2.resize(image_, (int(width_0 * resized), int(height_0 * resized)), interpolation=interp)

        image_size = check_img_size(IMAGE_SIZE)  # check img_size

        image_ = letterbox(image, new_shape=image_size)[0]
        
        # Convert
        image_ = image_[:, :, ::-1].transpose(2, 0, 1).copy()  # BGR to RGB, to 3x416x416

        image_ = torch.from_numpy(image_).to(self.device)
        image_ = image_.float()  # uint8 to fp16/32
        image_ /= 255.0  # 0 - 255 to 0.0 - 1.0
        if image_.ndimension() == 3:
            image_ = image_.unsqueeze(0)

        # Inference
        predictions = self.model(image_, augment=True)[0]

        # Apply NMS
        predictions = non_max_suppression(predictions, CONF_TRESHOLD, IOU_THESHOLD, fast=True, agnostic=True)

        for _, detections in enumerate(predictions):  # detections per image
            if detections is not None and len(detections):
                # Rescale boxes from img_size to im0 size
                detections[:, :4] = scale_coords(image_.shape[2:], detections[:, :4], image.shape).round()

                for *coors, conf, cls in detections:
                    label = self.names[int(cls)]
                    if label == 'person':
                        results.append((label, coors))

        return results

                

    def mark(self, results, image):
        for _, coors in results:
            plot_dots_on_people(coors, image)
        
        # Plot lines connecting people
        distancing(list(map(lambda values: values[1], results)), image, dist_thres_lim=(200,250))

        return image


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--weights', type=str, default='weights/yolov5s.pt', help='model.pt path')
    # parser.add_argument('--source', type=str, default='tests', help='source')  # file/folder, 0 for webcam
    # parser.add_argument('--output', type=str, default='results', help='output folder')  # output folder
    # parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    # parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
    # parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    # parser.add_argument('--fourcc', type=str, default='mp4v', help='output video codec (verify ffmpeg support)')
    # parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    # parser.add_argument('--view-img', action='store_true', help='display results')
    # parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    # parser.add_argument('--classes', nargs='+', type=int, help='filter by class')
    # parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    # parser.add_argument('--augment', action='store_true', help='augmented inference')
    # opt = parser.parse_args()
    # opt.img_size = check_img_size(opt.img_size)
    # print(opt)

    # with torch.no_grad():
    #     detect()

    test_folder = 'tests'
    save_dir = 'results'
    model = SocialDistancing()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            cv2.imwrite(os.path.join('results', file), image)
