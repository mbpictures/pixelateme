<h1 align="center">
Welcome to PixelateMe 👋<br />
</h1>
<h2 align="center">
Your Python package for anonymising faces in images and videos
</h2>
<p align="center">
    <a href="LICENSE" target="_blank">
        <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" />
    </a>
    <img src="https://img.shields.io/github/actions/workflow/status/mbpictures/pixelateme/python-publish.yml?color=%2397CA00&style=for-the-badge" />
    <a href="https://pypi.org/project/PixelateMe/" target="_blank">
        <img src="https://img.shields.io/pypi/v/pixelateme?style=for-the-badge" />
    </a>
</p>

> This CLI tool lets you pixelate, blur or remove faces from videos and images. GPU acceleration supported

<p align="center">
    <img src="https://raw.githubusercontent.com/mbpictures/pixelateme/master/demos/image.png" /><br />
    <em>Original image from <a href="https://unsplash.com/de/fotos/wdVwF3Ese4o" target="_blank">unsplash.com</a> by Susan G. Komen 3-Day</em><br />
    <img src="https://raw.githubusercontent.com/mbpictures/pixelateme/master/demos/video.gif" /><br />
    <em>Original video from <a href="https://www.pexels.com/video/close-up-video-of-man-wearing-red-hoodie-3249935/" target="_blank">pexels.com</a> by fauxels</em>
</p>

## ⚡️ Quickstart
### 📥 Install
```shell
pip install pixelateme
```
With GPU support (additionally installs ```onnxruntime-gpu```:
```shell
pip install pixelateme[gpu]
```

### ▶️ Run
After installation, pip registers a shortcut binary which can be called like this:
```shell
pixelateme --mode blur FOLDER_OR_FILES
```
This will create a new ```pixelated``` folder to hold all the pixelated files.

### 📝 Custom code
To use this package in your own code, you can import the main module. This module exports a run method that accepts all CLI arguments as parameters.
```python
from pixelateme.main import run

run(path=["FILE_PATHS"])
```

## 🎯 Features
- Different anonymisation modes: pixelate, blur and color
- GPU acceleration
- Preview of currently processed files
- Face Recognition to blur only certain faces or all faces except certain ones
- ONNXRT and OpenCV run-time backend
- Process multiple files in parallel

## 💻 CLI Arguments
* ```--suffix```: Filename suffix of processed files. Default: 
* ```--output``` (-o): Output directory for processed files. Default: ./pixelated
* ```--mode``` (-m): Mode of anonymization. Default: pixelate
* ```--threshold``` (-t): Threshold for detected faces (higher means more confidence). Default: 0.5
* ```--backend```: Desired backend (e.g. opencv or onnxrt). Auto prefers onnxrt and falls back to opencv. Default: auto
* ```--only-blur-this-faces```: Folder containing images of faces (one face per image) that should be considered for anonymisation. All other faces will not be anonymised. Default: None
* ```--blur-except-this-faces```: Folder containing images of faces (one face per image), which should be ignored for anonymization. Default: None
* ```--ellipse```: Uses ellipses as form for anonymization. Default is rectangle
* ```--blur-strength```: Defines how "blurry" a face will be. Only working with ```--mode``` "blur". Default: 3
* ```--pixelate-size```: Amount of pixelation effect. The lower the value, the harder it is to recognise the face. Default: 16
* ```--deepface-similarity```: The maximum similarity between two faces. A higher value means that more faces are considered equal. Only working in combination with ```--blur-except-this-faces``` or ```--only-blur-this-faces```. Default: 0.4
* ```--preview```: Enable preview of the currently processed image. No preview is default
* ```--face-recognition-size```: Image size to use for face detection. Format: WxH (e.g. 720x480). Default: None
* ```--maximum-face-recognition-size```: Maximum number of pixels of the longest side for face detection. Images larger than this will be downscaled for face recognition. This doesn't affect output resolution. Default: 640
* ```--multiprocessing```: Enable multiprocessing to process files in videos. Useful when anonymizing multiple large videos. Disabled by default
* ```--parallel-processes```: Number of parallel processes. Only works with ```--multiprocessing``` enabled. Default: 4

## 👏 Acknowledgements
* [**deface**](https://github.com/ORB-HD/deface): Deface was one of my inspirations for this package and the implementation of CenterFace.
* [**CenterFace**](https://github.com/Star-Clouds/CenterFace): Used for face detection
* [**DeepFace**](https://github.com/serengil/deepface): Used for face recognition
* [**ONNX**](https://github.com/onnx/onnx): Face detection backend
* [**OpenCV**](https://opencv.org/): Face detection backend, used for I/O and face anonymisation (blur, pixelation and color)

## 👥 Author

👤 **Marius Butz**

* Website: http://marius-butz.de

## ⭐️ Show your support

- Give a [⭐️ star](https://github.com/mbpictures/tessera) if this project helped you!
- Create a [🍴 fork](https://github.com/mbpictures/tessera) and contribute by fixing bugs or adding features
