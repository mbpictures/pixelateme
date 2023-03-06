from pixelateme.main import run
from gooey import Gooey, GooeyParser

@Gooey(progress_regex=r"^(\d+)/(\d+)$", progress_expr="x[0] / x[1] * 100")
def parse_args():
    args = GooeyParser(description="Pixelate all faces on a image or video")
    args.add_argument("path", nargs="*", help="File path(s) and folders containing images and/or videos to pixelate", widget="MultiFileChooser")
    out = args.add_argument_group("Output")
    out.add_argument("--suffix", default="", help="A suffix which is concatenated to processed files")
    out.add_argument("--output", "-o", default="./pixelated",
                      help="Output directory, where all pixelated files are saved at", widget="DirChooser")
    blur_group = args.add_argument_group("Anonymization", "Configure anonymization settings")
    blur_group.add_argument("--mode", "-m", default="pixelate", choices=["pixelate", "blur", "color"], help="Anonymization mode")
    blur_group.add_argument("--ellipse", action="store_true",
                      help="Use ellipses as form to pixelate face instead of a rectangle")
    blur_group.add_argument("--blur-strength", dest="blur_strength", type=float, default=3,
                      help="Strength of the blur effect. The higher the value, the stronger the blur. Only working when mode is blur")
    blur_group.add_argument("--pixelate-size", dest="pixelate_size", type=float, default=5,
                      help="Raster size of pixelated effect. The low the value, the more blocks are generated. Only working when mode is pixelate")
    blur_group.add_argument("--soft-mask", dest="soft_mask", action="store_true", help="Enables a soft transition between blurred and original image")
    blur_group.add_argument("--soft-mask-strength", dest="soft_mask_strength", default=7, type=float, help="Defines the feather strength of the mask edge")

    face_detection = args.add_argument_group("Face Detection")
    face_detection.add_argument("--threshold", "-t", default=0.5, type=float, help="Threshold for face recognition", widget="DecimalField")
    face_detection.add_argument("--backend", default="auto", choices=["auto", "onnxrt", "opencv"], help="Backend for face recognition")
    face_detection.add_argument("--face-recognition-size", dest="face_recognition_size", default=None,
                                help="Maximum size of image used for face recognition in the format WxH (e.g. 720x480). Larger images/videos will be downscaled. Has no affect on output resolution.")
    face_detection.add_argument("--maximum-face-recognition-size", dest="max_face_recognition_size", default=640,
                                type=int,
                                help="The maximum number of pixels of the longest side. Image/Video will be scaled down according longest side.")

    face_recognition = args.add_argument_group("Face Recognition")
    face_recognition.add_argument("--only-blur-this-faces", default=None, dest="only_this_images", help="Folder containing images with faces. Only faces matching with one in this folder are pixelated", widget="DirChooser")
    face_recognition.add_argument("--blur-except-this-faces", default=None, dest="all_except_images", help="Folder containing images with faces. Only faces, that don't match any face in the folder, are pixelated", widget="DirChooser")
    face_recognition.add_argument("--deepface-similarity", dest="deepface_similarity", type=float, default=0.4, help="Maximum cosinus similarity of two faces, that are considered as 'same face'. Only relevant with either only-blur-this-faces or blur-except-this-faces set.")
    args.add_argument("--preview", dest="preview", action="store_true", help="Open Window displaying preview of the pixelated image")

    multi_processing = args.add_argument_group("Multiprocessing")
    multi_processing.add_argument("--multiprocessing", dest="multiprocessing", action="store_true", help="Enable multi processing for faster CPU execution")
    multi_processing.add_argument("--parallel-processes", dest="parallel_processes", default=4, type=int, help="Number of parallel anonymization processes. One proccess is additional created for displaying preview (if enabled).")

    return args.parse_args()


def main():
    args = parse_args()

    run(**vars(args))


if __name__ == "__main__":
    main()
