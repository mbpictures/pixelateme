import os.path
import mimetypes
from tqdm import tqdm

import cv2

from pixelateme.face_detection import FaceDetection
from pixelateme.centerface import CenterFace
from pixelateme.blur import Blur


kill_preview = False

def get_files(paths):
    result = []
    for path in paths:
        if os.path.isfile(path):
            result.append(path)
        else:
            for file in os.listdir(path):
                result.append(os.path.join(path, file))

    return result


def get_type(path):
    if not os.path.exists(path):
        return None

    mime = mimetypes.guess_type(path)
    if mime[0].startswith("video"):
        return "video"
    if mime[0].startswith("image"):
        return "image"
    return None


def get_blurred_frame(face_detection: FaceDetection, blur: Blur, frame, preview):
    global kill_preview
    boxes = face_detection.get_boxes(frame)
    blurred = blur.blur_faces(image=frame, boxes=boxes)
    if preview and not kill_preview:
        cv2.imshow("Preview (press q to exit preview, blurring will continue)", cv2.resize(blurred, (720, 480)))
        a = cv2.waitKey(1)
        if a == ord('q'):
            kill_preview = True
            cv2.destroyAllWindows()
    return blurred


def get_output_file_name(path, kwargs):
    basename = os.path.splitext(path)
    folder = os.path.join(os.path.abspath(kwargs.get("output")), basename[0] + kwargs.get("suffix") + basename[1])
    os.makedirs(os.path.dirname(folder), exist_ok=True)
    return folder


def process_image(path, face_detection: FaceDetection, blur: Blur, kwargs):
    frame = cv2.imread(path)
    blurred = get_blurred_frame(face_detection, blur, frame, kwargs.get("preview"))
    cv2.imwrite(get_output_file_name(path, kwargs), blurred)


def process_video(path, face_detection: FaceDetection, blur: Blur, kwargs):
    cap = cv2.VideoCapture(path)
    ret, img = cap.read()
    out = cv2.VideoWriter(get_output_file_name(path, kwargs), -1, 20, (img.shape[1], img.shape[0]))
    while ret:
        blurred = get_blurred_frame(face_detection, blur, img, kwargs.get("preview"))
        out.write(blurred)

        ret, img = cap.read()

    cap.release()
    out.release()


def run(**kwargs):
    in_shape = None
    if kwargs.get("face_recognition_size") is not None:
        splitted = kwargs.get("face_recognition_size").split("x")
        in_shape = int(splitted[0]), int(splitted[1])
    centerface = CenterFace(backend=kwargs.get("backend"), in_shape=in_shape)
    all_except_images, only_this_images = [], []
    if kwargs.get("all_except_images") is not None:
        all_except_image_files = get_files([kwargs.get("all_except_images")])
        for path in all_except_image_files:
            all_except_images.append(cv2.imread(path))

    if kwargs.get("only_this_images") is not None:
        only_this_images_files = get_files([kwargs.get("only_this_images")])
        for path in only_this_images_files:
            all_except_images.append(cv2.imread(path))

    face_detection = FaceDetection(centerface, all_except_images_data=all_except_images, only_this_images_data=only_this_images, **kwargs)
    blur = Blur(**kwargs)

    paths = get_files(kwargs.get("path"))
    if len(paths) > 1:
        paths = tqdm(paths, desc="Processing files...")

    for path in paths:
        file_type = get_type(path)

        if file_type is None:
            print(f"Warning: File {path} is not a video and not an image, skipping...")

        if file_type == "video":
            process_video(path, face_detection, blur, kwargs)
        else:
            process_image(path, face_detection, blur, kwargs)

    if kwargs.get("preview"):
        cv2.destroyAllWindows()
