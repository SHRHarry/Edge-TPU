# Edge-TPU YOLOv3-Tiny Convert & Run
## Introduction
This repository is the model conversion process of Edge-TPU M.2 or Mini PCIe Accelerator.
In order to run the model on Edge-TPU, it must be converted to full quantized TensorFlow-Lite model.
The following are the model conversion steps, including:
1. Convert Darknet model `.weights` to TensorFlow frozen graph `.pb`.
2. Convert Tensorflow frozen graph `.pb` to TF-lite model `.tflite`.
3. Compile a TF-Lite model `.tflite` into a file that's compatible with the Edge TPU `_edgetpu.tflite`.

P.S.Since different versions of tensotflow will be used, it is recommended to use anaconda to create environments of different versions.

## Step1 Darknet2Frozen
### Setup
Assuming a fresh [Anaconda](https://www.anaconda.com/download/) distribution with Python 3.6.12, you can install the dependencies with:
```
pip install tensorflow==1.12.0 opencv-python==4.1.2.30 numpy pillow 
```
### 

## Step2 Frozen2tflite

## Step3 EdgeTPUCompiler

## Reference
1. [Convert YOLOv3-Tiny to tensorflow model](https://github.com/mystic123/tensorflow-yolo-v3)
2. [Compile and deploy YOLOv3-Tiny models for CoralDevBoard/TinkerEdgeT](https://github.com/SHRHarry/EdgeTPU-YOLOv3-Tiny)
3. [Run Tiny YOLO-v3 on Google's Edge TPU USB Accelerator.](https://github.com/guichristmann/edge-tpu-tiny-yolo)
4. [Get started with the M.2 or Mini PCIe Accelerator](https://coral.ai/docs/m2/get-started/)
