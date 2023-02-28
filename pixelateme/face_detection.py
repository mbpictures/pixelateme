from deepface import DeepFace


class FaceDetection:
    def __init__(self, centerface, threshold=0.5, all_except_images=[], only_this_images=[]):
        self.all_except_images = all_except_images
        self.only_this_images = only_this_images
        self.threshold = threshold
        self.centerface = centerface

    def blur_face(self, face):
        for image in self.all_except_images:
            result = DeepFace.verify(face, image)
            if result["verified"]:
                return False

        blur = True
        for image in self.only_this_images:
            result = DeepFace.verify(face, image)
            if result["verified"]:
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

        return self.filter_boxes(frame, boxes)
