import os
import cv2

from pathlib import Path
from detector import Detector
from utils.utils import distancing, plot_dots_on_people

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

class SocialDistancing(Detector):

    def __init__(self, path="weights/yolov5s.pt"):
        super(self.__class__, self).__init__(path)

    def inference(self, coors, conf, cls):
        if self.names[int(cls)] == 'person':
            return self.names[int(cls)], coors

    def mark(self, results, image):
        for _, coors in results:
            # Draw Dots on the objects detected
            plot_dots_on_people(coors, image)
        
        # Plot lines connecting people
        distancing(list(map(lambda values: values[1], results)), image, dist_thres_lim=(200,250))

        return image


if __name__ == '__main__':
    test_folder = BASE_PATH / 'tests'
    save_dir =  BASE_PATH / 'results'

    model = SocialDistancing()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            cv2.imwrite(os.path.join('results', file), image)
