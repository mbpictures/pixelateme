import os

import numpy as np
import cv2

# ORIGINAL: https://github.com/ORB-HD/deface/blob/master/deface/centerface.py


class CenterFace:
    default_onnx_path = f'{os.path.dirname(__file__)}/centerface.onnx'

    def __init__(self, onnx_path=None, in_shape=None, backend='auto', max_size=640):
        self.in_shape = in_shape
        self.max_size = max_size
        self.onnx_input_name = 'input.1'
        self.onnx_output_names = ['537', '538', '539', '540']

        if onnx_path is None:
            onnx_path = self.default_onnx_path

        if backend == 'auto':
            try:
                import onnx
                import onnxruntime
                backend = 'onnxrt'
            except:
                backend = 'opencv'
        self.backend = backend

        if self.backend == 'opencv':
            self.net = cv2.dnn.readNetFromONNX(onnx_path)
        elif self.backend == 'onnxrt':

            # Silence warnings about unnecessary bn initializers
            onnxruntime.set_default_logger_severity(3)

            static_model = onnx.load(onnx_path)
            dyn_model = self.dynamicize_shapes(static_model)
            self.sess = onnxruntime.InferenceSession(dyn_model.SerializeToString(), providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

    @staticmethod
    def ensure_rgb(img: np.ndarray) -> np.ndarray:
        """Convert input image to RGB if it is in RGBA or L format"""
        if img.ndim == 2:  # 1-channel grayscale -> RGB
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[2] == 4:  # 4-channel RGBA -> RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        return img

    @staticmethod
    def dynamicize_shapes(static_model):
        from onnx.tools.update_model_dims import update_inputs_outputs_dims

        input_dims, output_dims = {}, {}
        for node in static_model.graph.input:
            dims = [d.dim_value for d in node.type.tensor_type.shape.dim]
            input_dims[node.name] = dims
        for node in static_model.graph.output:
            dims = [d.dim_value for d in node.type.tensor_type.shape.dim]
            output_dims[node.name] = dims
        input_dims.update({
            'input.1': ['B', 3, 'H', 'W']  # RGB input image
        })
        output_dims.update({
            '537': ['B', 1, 'h', 'w'],  # heatmap
            '538': ['B', 2, 'h', 'w'],  # scale
            '539': ['B', 2, 'h', 'w'],  # offset
            '540': ['B', 10, 'h', 'w']  # landmarks
        })
        dyn_model = update_inputs_outputs_dims(static_model, input_dims, output_dims)
        return dyn_model

    def __call__(self, img, threshold=0.5):
        img = CenterFace.ensure_rgb(img)
        orig_shape = img.shape[:2]
        in_shape = self.in_shape
        if in_shape is None:
            in_shape = orig_shape[::-1]
        w_new, h_new, scale_w, scale_h = self.transform(in_shape, orig_shape)

        blob = cv2.dnn.blobFromImage(
            img, scalefactor=1.0, size=(w_new, h_new),
            mean=(0, 0, 0), swapRB=False, crop=False
        )
        if self.backend == 'opencv':
            self.net.setInput(blob)
            heatmap, scale, offset, lms = self.net.forward(self.onnx_output_names)
        elif self.backend == 'onnxrt':
            heatmap, scale, offset, lms = self.sess.run(self.onnx_output_names, {self.onnx_input_name: blob})
        else:
            raise RuntimeError(f'Unknown backend {self.backend}')
        dets, lms = self.decode(heatmap, scale, offset, lms, (h_new, w_new), threshold=threshold)
        if len(dets) > 0:
            dets[:, 0:4:2], dets[:, 1:4:2] = dets[:, 0:4:2] / scale_w, dets[:, 1:4:2] / scale_h
            lms[:, 0:10:2], lms[:, 1:10:2] = lms[:, 0:10:2] / scale_w, lms[:, 1:10:2] / scale_h
        else:
            dets = np.empty(shape=[0, 5], dtype=np.float32)
            lms = np.empty(shape=[0, 10], dtype=np.float32)

        return dets, lms

    def transform(self, in_shape, orig_shape):
        h_orig, w_orig = orig_shape
        w_new, h_new = in_shape
        if w_new > self.max_size or h_new > self.max_size:
            if w_new > h_new:
                h_new = h_new * (self.max_size / w_new)
                w_new = self.max_size
            else:
                w_new = w_new * (self.max_size / h_new)
                h_new = self.max_size
        # Make spatial dims divisible by 32
        w_new, h_new = int(np.ceil(w_new / 32) * 32), int(np.ceil(h_new / 32) * 32)
        scale_w, scale_h = w_new / w_orig, h_new / h_orig
        return w_new, h_new, scale_w, scale_h

    def decode(self, heatmap, scale, offset, landmark, size, threshold=0.1):
        heatmap = np.squeeze(heatmap)
        scale0, scale1 = scale[0, 0, :, :], scale[0, 1, :, :]
        offset0, offset1 = offset[0, 0, :, :], offset[0, 1, :, :]
        c0, c1 = np.where(heatmap > threshold)
        boxes, lms = [], []
        if len(c0) > 0:
            for i in range(len(c0)):
                s0, s1 = np.exp(scale0[c0[i], c1[i]]) * 4, np.exp(scale1[c0[i], c1[i]]) * 4
                o0, o1 = offset0[c0[i], c1[i]], offset1[c0[i], c1[i]]
                s = heatmap[c0[i], c1[i]]
                x1, y1 = max(0, (c1[i] + o1 + 0.5) * 4 - s1 / 2), max(0, (c0[i] + o0 + 0.5) * 4 - s0 / 2)
                x1, y1 = min(x1, size[1]), min(y1, size[0])
                boxes.append([x1, y1, min(x1 + s1, size[1]), min(y1 + s0, size[0]), s])
                lm = []
                for j in range(5):
                    lm.append(landmark[0, j * 2 + 1, c0[i], c1[i]] * s1 + x1)
                    lm.append(landmark[0, j * 2, c0[i], c1[i]] * s0 + y1)
                lms.append(lm)
            boxes = np.asarray(boxes, dtype=np.float32)
            lms = np.asarray(lms, dtype=np.float32)
            keep = self.nms(boxes[:, :4], boxes[:, 4], 0.3)
            boxes = boxes[keep, :]
            lms = lms[keep, :]
        return boxes, lms

    @staticmethod
    def nms(boxes, scores, nms_thresh):
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)
        order = np.argsort(scores)[::-1]
        num_detections = boxes.shape[0]
        suppressed = np.zeros((num_detections,), dtype=np.uint8)
        for _i in range(num_detections):
            i = order[_i]
            if suppressed[i]:
                continue
            ix1 = x1[i]
            iy1 = y1[i]
            ix2 = x2[i]
            iy2 = y2[i]
            iarea = areas[i]

            for _j in range(_i + 1, num_detections):
                j = order[_j]
                if suppressed[j]:
                    continue

                xx1 = max(ix1, x1[j])
                yy1 = max(iy1, y1[j])
                xx2 = min(ix2, x2[j])
                yy2 = min(iy2, y2[j])
                w = max(0, xx2 - xx1)
                h = max(0, yy2 - yy1)

                inter = w * h
                ovr = inter / (iarea + areas[j] - inter)
                if ovr >= nms_thresh:
                    suppressed[j] = True
        keep = np.nonzero(suppressed == 0)[0]
        return keep