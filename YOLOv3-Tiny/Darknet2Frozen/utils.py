# -*- coding: utf-8 -*-
import numpy as np
#import tensorflow.compat.v1 as tf
import tensorflow as tf
import cv2
from math import exp, sqrt

def freeze_graph(sess, output_graph):

    output_node_names = [
        "output_boxes",
        "inputs",
    ]
    output_node_names = ",".join(output_node_names)

    output_graph_def = tf.graph_util.convert_variables_to_constants(
        sess,
        tf.get_default_graph().as_graph_def(),
        output_node_names.split(",")
    )

    with tf.gfile.GFile(output_graph, "wb") as f:
        f.write(output_graph_def.SerializeToString())

    print("{} ops written to {}.".format(len(output_graph_def.node), output_graph))

def load_weights(var_list, weights_file):
    """
    Loads and converts pre-trained weights.
    :param var_list: list of network variables.
    :param weights_file: name of the binary file.
    :return: list of assign ops
    """
    with open(weights_file, "rb") as fp:
        _ = np.fromfile(fp, dtype=np.int32, count=5)

        weights = np.fromfile(fp, dtype=np.float32)

    ptr = 0
    i = 0
    assign_ops = []
    while i < len(var_list) - 1:
        var1 = var_list[i]
        var2 = var_list[i + 1]
        # do something only if we process conv layer
        if 'Conv' in var1.name.split('/')[-2]:
            # check type of next layer
            if 'BatchNorm' in var2.name.split('/')[-2]:
                # load batch norm params
                gamma, beta, mean, var = var_list[i + 1:i + 5]
                batch_norm_vars = [beta, gamma, mean, var]
                for var in batch_norm_vars:
                    shape = var.shape.as_list()
                    num_params = np.prod(shape)
                    var_weights = weights[ptr:ptr + num_params].reshape(shape)
                    ptr += num_params
                    assign_ops.append(
                        tf.assign(var, var_weights, validate_shape=True))

                # we move the pointer by 4, because we loaded 4 variables
                i += 4
            elif 'Conv' in var2.name.split('/')[-2]:
                # load biases
                bias = var2
                bias_shape = bias.shape.as_list()
                bias_params = np.prod(bias_shape)
                bias_weights = weights[ptr:ptr +
                                       bias_params].reshape(bias_shape)
                ptr += bias_params
                assign_ops.append(
                    tf.assign(bias, bias_weights, validate_shape=True))

                # we loaded 1 variable
                i += 1
            # we can load weights of conv layer
            shape = var1.shape.as_list()
            num_params = np.prod(shape)

            var_weights = weights[ptr:ptr + num_params].reshape(
                (shape[3], shape[2], shape[0], shape[1]))
            # remember to transpose to column-major
            var_weights = np.transpose(var_weights, (2, 3, 1, 0))
            ptr += num_params
            assign_ops.append(
                tf.assign(var1, var_weights, validate_shape=True))
            i += 1

    return assign_ops

def detections_boxes(detections):
    """
    Converts center x, center y, width and height values to coordinates of top left and bottom right points.
    :param detections: outputs of YOLO v3 detector of shape (?, 10647, (num_classes + 5))
    :return: converted detections of same shape as input
    """
    center_x, center_y, width, height, attrs = tf.split(
        detections, [1, 1, 1, 1, -1], axis=-1)
    w2 = width / 2
    h2 = height / 2
    x0 = center_x - w2
    y0 = center_y - h2
    x1 = center_x + w2
    y1 = center_y + h2

    boxes = tf.concat([x0, y0, x1, y1], axis=-1)
    detections = tf.concat([boxes, attrs], axis=-1, name="output_boxes")
    return detections

def get_boxes_and_inputs_pb(frozen_graph):

    with frozen_graph.as_default():
        boxes = [tf.get_default_graph().get_tensor_by_name("detector/yolo-v3-tiny/Conv_9/BiasAdd:0"),
                 tf.get_default_graph().get_tensor_by_name("detector/yolo-v3-tiny/Conv_12/BiasAdd:0")]
        inputs = tf.get_default_graph().get_tensor_by_name("inputs:0")
        
    return boxes, inputs

def load_graph(frozen_graph_filename):

    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")

    return graph

def scale_bbox(x, y, h, w, class_id, confidence):
    xmin = int((x - w / 2))
    ymin = int((y - h / 2))
    xmax = int(xmin + w)
    ymax = int(ymin + h)
    return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id, confidence=confidence)

def intersection_over_union(box_1, box_2):
    
    width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
    height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
    box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union
    
def sigmoid(x):
  return 1 / (1 + np.exp(-x))

def non_max_suppression(predictions_with_boxes, params, confidence_threshold=0.5, iou_threshold=0.5):

    result = {}
    objects = list()
    input_w = params["input_w"]
    input_h = params["input_h"]
    num_anchors = int(len(params["anchors"])/4)
    num_classes = params["classes"]
    num_coords = params["coords"]
    num_bbox_attrs = num_classes+num_coords+1
    anchors = params["anchors"]
    
    sides = [p.shape[1] for p in predictions_with_boxes]
    grid = [(out_blob, side, anchor_offset, n) for out_blob, side, anchor_offset in zip(predictions_with_boxes, sides, (6, 0)) for n in range(num_anchors)]
    for out_blob, side, anchor_offset, n in grid:
        index = np.argwhere(sigmoid(out_blob[0,:,:,n*num_bbox_attrs+num_coords]) >= confidence_threshold)
        for row, col in index:
            for j in range(num_classes):
                confidence = sigmoid(out_blob[0,row,col,n*num_bbox_attrs+num_coords+j+1])
                if confidence < confidence_threshold:
                    continue
                x = (col + sigmoid(out_blob[0,row,col,n*num_bbox_attrs+0])) / side * input_w
                y = (row + sigmoid(out_blob[0,row,col,n*num_bbox_attrs+1])) / side * input_h
                w = np.exp(out_blob[0,row,col,n*num_bbox_attrs+2]) * anchors[anchor_offset + 2 * n]
                h = np.exp(out_blob[0,row,col,n*num_bbox_attrs+3]) * anchors[anchor_offset + 2 * n + 1]
                objects.append(scale_bbox(x,y,h,w,j,confidence))
    
    for i in range(len(objects)):
        if objects[i]['confidence'] == 0:
            continue
        for j in range(i + 1, len(objects)):
            if intersection_over_union(objects[i], objects[j]) > iou_threshold:
                objects[j]['confidence'] = 0

    objects = [obj for obj in objects if obj['confidence'] >= confidence_threshold]
    
    for object in objects:
        box = [object["xmin"], object["ymin"], object["xmax"], object["ymax"]]
        score = object["confidence"]
        cls = object["class_id"]
        if cls not in result:
            result[cls] = []
        result[cls].append((box, score))
    return result

def load_coco_names(file_name):
    names = {}
    with open(file_name) as f:
        for id, name in enumerate(f):
            names[id] = name
    return names

def draw_boxes(boxes, img, cls_names, size, colors, is_letter_box_image):
    iw, ih = img.shape[0:2][::-1]
    w, h = size
    w_scale, h_scale = iw/w, ih/h
    for cls, bboxs in boxes.items():
        color = colors[cls]
        for box, score_ in bboxs:
            x1, y1, x2, y2 = box
            cv2.rectangle(img, (int(x1*w_scale), int(y1*h_scale)), (int(x2*w_scale), int(y2*h_scale)), color, 2)
            cv2.putText(img, "{} {:.2f}%".format(cls_names[cls], score_ * 100),
                        (int(x1*w_scale), int(y1*h_scale)), cv2.FONT_HERSHEY_DUPLEX, 0.5, color, 1, cv2.LINE_AA)
            
def letter_box_image(image, size, fill=128):
    iw, ih = image.shape[0:2][::-1]
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = cv2.resize(image, (nw,nh), interpolation=cv2.INTER_CUBIC)
    new_image = np.zeros((size[1], size[0], 3), np.uint8)
    new_image.fill(fill)
    dx = (w-nw)//2
    dy = (h-nh)//2
    new_image[dy:dy+nh, dx:dx+nw,:] = image
    return new_image