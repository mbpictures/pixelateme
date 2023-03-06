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
        mask = Blur.get_ellipse_masks(shape, boxes) if self.ellipse else Blur.get_box_masks(shape, boxes)
        if self.kwargs.get("soft_mask"):
            mask = cv2.GaussianBlur(mask, self.get_blur_kernel(self.kwargs.get("soft_mask_strength"), mask.shape), 0)
        return mask

    @staticmethod
    def get_blur_kernel(blur_strength, image_shape):
        kernel_size = int(blur_strength / 100 * image_shape[1]), int(blur_strength / 100 * image_shape[1])
        return tuple(map(lambda x: x if x % 2 == 1 else x + 1, kernel_size))

    def mix_images(self, source: np.array, blurred: np.array, mask: np.array):
        if not self.kwargs.get("soft_mask"):
            return np.where(mask > 0, blurred, source)
        mask = mask / 255
        result = blurred * mask + source * (1 - mask)
        return result.astype(np.uint8)

    def solid(self, image, boxes):
        mask = self.get_mask(image.shape, boxes)
        zeros = np.zeros(image.shape, dtype="uint8")
        return self.mix_images(image, zeros, mask)

    def blur(self, image, boxes):
        kernel_size = self.get_blur_kernel(self.kwargs.get("blur_strength"), image.shape)
        blurred = cv2.GaussianBlur(image, kernel_size, 0)
        mask = self.get_mask(image.shape, boxes)
        return self.mix_images(image, blurred, mask)

    def pixelate(self, image, boxes):
        mask = self.get_mask(image.shape, boxes)
        height, width = image.shape[:2]
        w, h = (self.kwargs.get("pixelate_size") / 100 * width, self.kwargs.get("pixelate_size") / 100 * height)
        temp = cv2.resize(image, (int(width / w), int(height / h)), interpolation=cv2.INTER_LINEAR)
        pixelate = cv2.resize(temp, (width, height), interpolation=cv2.INTER_NEAREST)

        return self.mix_images(image, pixelate, mask)

    def blur_faces(self, image, boxes):
        if self.mode == "color":
            return self.solid(image, boxes)
        if self.mode == "blur":
            return self.blur(image, boxes)
        if self.mode == "pixelate":
            return self.pixelate(image, boxes)

        raise Exception("Unsupported mode. Supported modes are color, blur and pixelate!")
