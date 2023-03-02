from setuptools import setup, find_packages
import versioneer

with open('README.md', 'r', encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='PixelateMe',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Marius Butz',
    description='A Python CLI-Tool and package to pixelate or blur faces in images and videos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mbpictures/pixelateme',
    packages=find_packages(include=["pixelateme"]),
    entry_points={'console_scripts': [
        'pixelateme = pixelateme.cli:main',
    ]},
    package_data={'pixelateme': ['centerface.onnx']},
    include_package_data=True,
    install_requires=[
        'deepface',
        'tqdm',
        'opencv-python',
        'onnx',
        'onnxruntime'
    ],
    extras_require={
        'gpu':  ['onnxruntime-gpu'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
