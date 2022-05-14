import os
import cv2
import dlib
import json

import numpy as np
from pathlib import Path
from align import AlignDlib
from collections import defaultdict
from inception_blocks import faceRecoModel

from keras import backend as K

from detection.face_detector import FaceDetector
K.set_image_data_format('channels_first')


BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))


class FaceRecognizer:
    
    def __init__(self, path='vitals/database.json') -> None:
        self.database = path
        self.model = faceRecoModel(input_shape=(3, 96, 96))
        self.detector = FaceDetector()
        self.model.load_weights(BASE_PATH / 'vitals/nn4.small2.v1.h5')
        self.alignment = AlignDlib(str(BASE_PATH / 'vitals/landmarks.dat'))

    @property
    def database(self):
        return self.__database

    @database.setter
    def database(self, path):
        self.__database = defaultdict(list)
        if path:
            database = FaceRecognizer.from_json_file(BASE_PATH / path)
            for data in database:
                encodings = list(map(lambda array: np.array(array), data['encodings']))
                self.__database['encodings'].extend(encodings)
                self.__database['names'].extend([data['label']] * len(encodings))
                self.__database[data['label']] = data['email']
    
    @staticmethod
    def from_json_file(path):
        with open(path) as file:
            data = json.load(file)
        return data

    def align_face(self, image, bb=None):
        return self.alignment.align(96, image, bb=bb,
                            landmarkIndices=AlignDlib.OUTER_EYES_AND_NOSE)

    def encode_face(self, image, bbox):
        resized_image = self.align_face(image, bb=bbox)
        image = np.around(np.transpose(resized_image, (2, 0, 1)) / 255.0, decimals=12)
        train = np.array([image])
        embedding = self.model.predict_on_batch(train)
        return embedding

    def get_locations(self, image):
        locations = self.detector(image)
        coors = []
        for loc in locations:
            coors.append((loc[-1], loc[0], loc[1], loc[2]))
        return coors

    def get_faces(self, image):
        results = []
        locations = self.detector(image)

        for locs in locations:
            dlibRect = dlib.rectangle(locs[0], locs[1], locs[2], locs[3])
            face_encoding = self.encode_face(image, dlibRect)
            results.append((locs, face_encoding))

        return results

    def compare_faces(self, encoding):
        return np.linalg.norm(self.database['encodings'] - encoding, axis=1)

    def face_distance(self, face_to_compare):
        distances = []
        for encoding in self.database['encodings']:
            distances.append(np.linalg.norm(encoding - face_to_compare))
        return np.array(distances)

    def __call__(self, image, tolerance=0.5):
        results = []

        for loc, encoding in self.get_faces(image):
            name = 'unknown'
            # find the euclidean distance between known faces and new face
            distances = self.face_distance(encoding)
            # index of matched face encoding with minimum euclidean distance
            index = np.argmin(distances)
            # Check if the face is enough accurate to be recognized
            if distances[index] <= tolerance:
                name = self.database['names'][index]
                
            results.append((name, loc))
        
        return results

    def mark(self, results, image):
        for label, coors in results:
            cv2.rectangle(image, (coors[0], coors[1]), (coors[2], coors[3]), [0,0,255], 2)
            cv2.rectangle(image, (coors[0], coors[3]), (coors[2], coors[3] + 50), (0, 0, 255), cv2.FILLED)
            cv2.putText(image, label, (coors[0]+10,coors[3]+40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, [255,255,255], 2, cv2.LINE_AA)

        return image


if __name__ == "__main__":
    test_folder = BASE_PATH / 'test'
    save_dir = BASE_PATH / 'results'
    model = FaceRecognizer()

    for (root,dir,files) in os.walk(test_folder, topdown=True):
        for file in files:
            image_path = os.path.join(root,file)
            save_path = os.path.join(save_dir, file)
            image = cv2.imread(image_path)
            results = model(image)
            image = model.mark(results, image)
            print(str(BASE_PATH / 'results' / file))
            cv2.imwrite(str(BASE_PATH / 'results' / file), image)