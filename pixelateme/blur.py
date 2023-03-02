import cv2
import numpy as np


class Blur:
    def __init__(self, mode="blur", ellipse=True, **kwargs):
        self.mode = mode
        self.ellipse = ellipse
        self.kwargs = kwargs

    @staticmethod
    def get_ellipse(box):
        x1, y1, x2, y2 = box
        center = x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2
        size = (x2 - x1) // 2, (y2 - y1) // 2
        return center, size

    @staticmethod
    def get_ellipse_masks(shape, boxes):
        mask = np.zeros(shape, dtype="uint8")
        for box in boxes:
            center, size = Blur.get_ellipse(box)
            cv2.ellipse(mask, center, size, 0, 0, 360, (255, 255, 255), -1)
        return mask

    @staticmethod
    def get_box_masks(shape, boxes):
        mask = np.zeros(shape, dtype="uint8")
        for box in boxes:
            x1, y1, x2, y2 = box
            cv2.rectangle(mask, (x1, y1), (x2, y2), (255, 255, 255), -1)
        return mask

    def get_mask(self, shape, boxes):
        if self.ellipse:
            return Blur.get_ellipse_masks(shape, boxes)
        return Blur.get_box_masks(shape, boxes)

    def solid(self, image, boxes):
        mask = self.get_mask(image.shape, boxes)
        zeros = np.zeros(image.shape, dtype="uint8")
        return np.where(mask > 0, zeros, image)

    def blur(self, image, boxes):
        kernel_size = int(self.kwargs.get("blur_strength") / 100 * image.shape[1]), int(
            self.kwargs.get("blur_strength") / 100 * image.shape[1])
        kernel_size = tuple(map(lambda x: x if x % 2 == 1 else x + 1, kernel_size))
        blurred = cv2.GaussianBlur(image, kernel_size, 0)
        mask = self.get_mask(image.shape, boxes)
        return np.where(mask > 0, blurred, image)

    def pixelate(self, image, boxes):
        mask = self.get_mask(image.shape, boxes)
        w, h = (self.kwargs.get("pixelate-size"), self.kwargs.get("pixelate_size"))
        height, width = image.shape[:2]
        temp = cv2.resize(image, (int(width / w), int(height / h)), interpolation=cv2.INTER_LINEAR)
        pixelate = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

        return np.where(mask > 0, pixelate, image)

    def blur_faces(self, image, boxes):
        if self.mode == "color":
            return self.solid(image, boxes)
        if self.mode == "blur":
            return self.blur(image, boxes)
        if self.mode == "pixelate":
            return self.pixelate(image, boxes)

        raise Exception("Unsupported mode. Supported modes are color, blur and pixelate!")
