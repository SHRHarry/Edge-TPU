# Edge-TPU-YOLOv3-Tiny Convert & Run
## Introduction
This repository is the model conversion process of Edge-TPU Mini PCIe Accelerator.
In order to run the model on Edge-TPU, it must be converted to full quantized TensorFlow-Lite model.
The following are the model conversion steps, including:
1. Convert Darknet model(`.weights`) to Tensorflow frozen graph(`.pb`).
2. Convert Tensorflow frozen graph(`.pb`) to TF-lite model(`.tflite`).
3. Compile a TF-Lite model(`.tflite`) into a file that's compatible with the Edge TPU(`_edgetpu.tflite`).

## Reference
1. [Convert YOLOv3-Tiny to tensorflow model](https://github.com/mystic123/tensorflow-yolo-v3)
2. [Compile and deploy YOLOv3-Tiny models for CoralDevBoard/TinkerEdgeT](https://github.com/SHRHarry/EdgeTPU-YOLOv3-Tiny)
3. [Run Tiny YOLO-v3 on Google's Edge TPU USB Accelerator.](https://github.com/guichristmann/edge-tpu-tiny-yolo)
4. [Get started with the M.2 or Mini PCIe Accelerator](https://coral.ai/docs/m2/get-started/)
