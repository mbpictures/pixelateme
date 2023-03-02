import argparse

from pixelateme.main import run


def parse_args():
    args = argparse.ArgumentParser(prog="PixelateMe", description="Pixelate all faces on a image or video")
    args.add_argument("path", nargs="*", help="File path(s) and folders containing images and/or videos to pixelate")
    args.add_argument("--suffix", default="", help="A suffix which is concatenated to processed files")
    args.add_argument("--output", "-o", default="./pixelated", help="Output directory, where all pixelated files are saved at")
    args.add_argument("--mode", "-m", default="pixelate", choices=["pixelate", "blur", "color"], help="Anonymization mode")
    args.add_argument("--threshold", "-t", default=0.5, help="Threshold for face recognition")
    args.add_argument("--backend", default="auto", choices=["auto, onnxrt", "opencv"], help="Backend for face recognition")
    args.add_argument("--only-blur-this-faces", default=None, dest="only_this_images", help="Folder containing images with faces. Only faces matching with one in this folder are pixelated")
    args.add_argument("--blur-except-this-faces", default=None, dest="all_except_images", help="Folder containing images with faces. Only faces, that don't match any face in the folder, are pixelated")
    args.add_argument("--ellipse", action="store_true", help="Use ellipses as form to pixelate face instead of a rectangle")
    args.add_argument("--blur-strength", dest="blur_strength", type=float, default=3, help="Strength of the blur effect. The higher the value, the stronger the blur. Only working when mode is blur")
    args.add_argument("--pixelate-size", dest="pixelate_size", type=int, default=16, help="Raster size of pixelated effect. The low the value, the more blocks are generated. Only working when mode is pixelate")
    args.add_argument("--deepface-similarity", dest="deepface_similarity", type=float, default=0.4, help="Maximum cosinus similarity of two faces, that are considered as 'same face'. Only relevant with either only-blur-this-faces or blur-except-this-faces set.")
    args.add_argument("--preview", dest="preview", action="store_true", help="Open Window displaying preview of the pixelated image")
    args.add_argument("--face-recognition-size", dest="face_recognition_size", default=None, help="Maximum size of image used for face recognition in the format WxH (e.g. 720x480). Larger images/videos will be downscaled. Has no affect on output resolution.")
    args.add_argument("--maximum-face-recognition-size", dest="max_face_recognition_size", default=640, type=int, help="The maximum number of pixels of the longest side. Image/Video will be scaled down according longest side.")

    return args.parse_args()


def main():
    args = parse_args()

    run(**vars(args))

