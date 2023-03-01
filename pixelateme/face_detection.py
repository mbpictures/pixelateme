from deepface import DeepFace


class FaceDetection:
    def __init__(self, centerface, all_except_images_data=[], only_this_images_data=[], **kwargs):
        self.all_except_images = all_except_images_data
        self.only_this_images = only_this_images_data
        self.threshold = kwargs.get("threshold")
        self.deepface_similarity = kwargs.get("deepface_similarity")
        self.centerface = centerface

    def blur_face(self, face):
        for image in self.all_except_images:
            result = DeepFace.verify(face, image, enforce_detection=False)
            if result["distance"] <= self.deepface_similarity:
                return False

        blur = True
        for image in self.only_this_images:
            result = DeepFace.verify(face, image, enforce_detection=False)
            if result["distance"] <= self.deepface_similarity:
                return True
            blur = False

        return blur

    def filter_boxes(self, image, boxes):
        def condition(box):
            x1, y1, x2, y2 = box
            return self.blur_face(image[y1:y2, x1:x2])
        return list(filter(lambda x: condition(x), boxes))

    def get_boxes(self, frame):
        dets, _ = self.centerface(frame, threshold=self.threshold)
        boxes = list(map(lambda x: x[:4], dets))
        boxes = list(map(lambda x: list(map(lambda y: int(y), x)), boxes))

        return self.filter_boxes(frame, boxes)
