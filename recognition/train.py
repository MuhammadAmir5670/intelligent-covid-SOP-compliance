import os
import cv2
from recognition.inference import FaceRecognizer
from pathlib import Path
import random
from skimage import transform, exposure
import numpy as np
import json


BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


def random_rotate(image):
    random_degree = random.uniform(-10, 10)
    new_img = 255 * transform.rotate(image, random_degree)
    new_img = new_img.astype(np.uint8)
    return new_img

def random_shear(image):
    random_degree = random.uniform(-0.1, 0.1)
    afine_tf = transform.AffineTransform(shear=random_degree)
    new_img = 255 * transform.warp(image, inverse_map=afine_tf)
    new_img = new_img.astype(np.uint8)
    return new_img


def change_contrast(image, percent_change=(0, 15)):
    percent_change = random.uniform(percent_change[0], percent_change[1])
    v_min, v_max = np.percentile(image, (0. + percent_change, 100. - percent_change))
    new_img = exposure.rescale_intensity(image, in_range=(v_min, v_max))
    new_img = new_img.astype(np.uint8)
    return new_img


def gamma_correction(image, gamma_range=(0.7, 1.0)):
    gamma = random.uniform(gamma_range[0], gamma_range[1])
    new_img = exposure.adjust_gamma(image, gamma=gamma, gain=random.uniform(0.8, 1.0))
    new_img = new_img.astype(np.uint8)
    return new_img

avail_transforms = {'rotate': random_rotate,
                    'shear': random_shear,
                    'contrast': change_contrast,
                    'gamma': gamma_correction}


def apply_transform(image, num_transform=2):
    choices = random.sample(range(0, len(avail_transforms)), num_transform)
    img_out = image
    for choice in choices:
        operation = list(avail_transforms)[choice]
        img_out = avail_transforms[operation](img_out)
    return img_out


class Prepare:
    def __init__(self, dir_path='faces_database', save_dir='vitals') -> None:
        self.model = FaceRecognizer(path=False)
        self.dir_path = BASE_PATH / dir_path
        self.save_dir = BASE_PATH / save_dir

    def get_face(self, image):
        results = self.model.get_faces(image)
        if len(results):
            return results[0]
        return None, None

    def to_json_file(self, data, name):
        with open(self.save_dir / name, 'w') as file:
            json.dump(data, file, indent=4)

    def generate_database(self, augmentations=2, output_name='database.json'):
        encoded_database = []

        # For each person director in facesdatabase directory
        for root, _, files in os.walk(self.dir_path):
            print('\n\n--------------------------------------------\n')

            database = {'encodings': []}
            # for each image file in person directory
            for file_name in files:
                # Name of the person based on the directory name
                database['label'], database['email'] = list(map(lambda value: value.strip(), os.path.basename(root).split('-')))

                print(f"Prerprocessing data for {database['label']}")

                # complete absolute path to image file  
                file_path = Path(root) / file_name
                
                # Read the image from the disk
                image = cv2.imread(str(file_path))

                # Number of Augmentations to perform for each image
                operations = augmentations + 1
                for ops in range(operations):
                    print('Augmentations # ', ops + 1)

                    if ops > 0:
                        image = apply_transform(image, num_transform=2)
                        
                    location, encoding = self.get_face(image)
                    if location != None:
                        database['encodings'].append(encoding.tolist())

                    print(f'Face of {file_name} {files.index(file_name)+1}-{ops} folder added to Encoded Database')

            if len(files):
                encoded_database.append(database)
        
        self.to_json_file(encoded_database, output_name)



if __name__ == "__main__":
    prepare = Prepare()
    prepare.generate_database()
