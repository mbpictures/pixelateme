import argparse

import main as main_runner


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

    return args.parse_args()


def main():
    args = parse_args()

    main_runner.run(**vars(args))

