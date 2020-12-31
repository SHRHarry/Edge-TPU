python convert_frozen_model_to_tflite.py -m InputData\coco-tiny-v3-relu_1225.pb ^
                                         -o OutputData\coco-tiny-v3-relu_1225.tflite ^
                                         --params InputData\coco-tiny-v3-relu.json

python demo_tiny_yolo_tflite.py -m OutputData\coco-tiny-v3-relu_1225.tflite ^
                                -I iamge212.png ^
                                --params InputData\coco-tiny-v3-relu.json ^
                                -l InputData\coco.labels ^
                                -pt 0.5 ^
                                -iout 0.5 ^
                                -O iamge212_out.png

python yolov3_tiny_tflite_demo.py --model OutputData\coco-tiny-v3-relu_1225.tflite ^
                                  --anchors InputData\tiny_yolo_anchors.txt ^
                                  --classes InputData\coco.names ^
                                  -t 0.5 ^
                                  --quant ^
                                  --image iamge212.png