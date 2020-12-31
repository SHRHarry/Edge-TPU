docker build --no-cache -t edge_tpu_compiler:build -f DockerfileBUILD .

docker build --no-cache -t edge_tpu_compiler:run -f DockerfileRUN .

docker rmi edge_tpu_compiler:build

docker run -i -t -d --name converter1 edge_tpu_compiler:run

mkdir OutputModels\DeepLab\PASCAL\MultiTPU
mkdir OutputModels\EffNet\ImageNet\MultiTPU
mkdir OutputModels\YOLO\COCO\MultiTPU

docker cp converter1:/EdgeTPUConverter/InputModels/DeepLab/PASCAL/demo_edgetpu.tflite OutputModels\DeepLab\PASCAL\
docker cp converter1:/EdgeTPUConverter/InputModels/EffNet/ImageNet/efficientnet-edgetpu-S_quant_edgetpu.tflite OutputModels\EffNet\ImageNet\
docker cp converter1:/EdgeTPUConverter/InputModels/YOLO/COCO/coco-tiny-v3-relu_1225_edgetpu.tflite OutputModels\YOLO\COCO\

docker cp converter1:/EdgeTPUConverter/InputModels/DeepLab/PASCAL/MultiTPU OutputModels\DeepLab\PASCAL\
docker cp converter1:/EdgeTPUConverter/InputModels/EffNet/ImageNet/MultiTPU OutputModels\EffNet\ImageNet\
docker cp converter1:/EdgeTPUConverter/InputModels/YOLO/COCO/MultiTPU OutputModels\YOLO\COCO\

docker stop converter1
docker rm converter1
docker images && docker ps -a