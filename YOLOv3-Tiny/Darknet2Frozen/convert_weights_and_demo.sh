set -e
CONDA_PATH="E:/ForInstallAnaconda/Scripts/anaconda.exe"
CONDA_SETTING_SCRIPT="${CONDA_PATH}/../../etc/profile.d/conda.sh"
source "${CONDA_SETTING_SCRIPT}"
conda activate deeplab

CFG=./InputData/coco-tiny-v3-relu.cfg
CLASS_NAME=./InputData/coco.names
PARAMS=./InputData/coco-tiny-v3-relu.json
LABELS=./InputData/coco.labels
WEIGHTS_FILE=./InputData/coco-tiny-v3-relu.weights
OUTPUT_GRAPH=./OutputData/coco-tiny-v3-relu_1225.pb
SIZE=416
INPUT_IMAGE=very_new_image_aug_4_191.jpg
OUTPUT_IMAGE=very_new_image_aug_4_191_out.jpg

python generate_model_params.py -i $CFG \
                                -l $CLASS_NAME \
                                -o InputData/

python convert_weights_pb.py --class_names $CLASS_NAME \
                             --weights_file $WEIGHTS_FILE \
                             --data_format NHWC \
                             --output_graph $OUTPUT_GRAPH \
                             --size $SIZE \
                             --tiny \
                             --model_config $CFG

python demo_tiny_yolo_tf.py -m $OUTPUT_GRAPH \
                            -I $INPUT_IMAGE \
                            -O $OUTPUT_IMAGE \
                            --params $PARAMS \
                            -l $LABELS \
                            -pt 0.5 \
                            -iout 0.5 \