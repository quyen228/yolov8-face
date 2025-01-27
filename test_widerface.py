import os
import argparse
from glob import glob 
from tqdm import tqdm 
from ultralytics import YOLO

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', type=str, default='runs/pose/yolov8n-face/weights/best.pt', help='model.pt path(s)')
    parser.add_argument('--img-size', nargs= '+', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.01, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', type=str, default='cpu', help='augmented inference')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--save_folder', default='./widerface_evaluate/widerface_txt/', type=str, help='Dir to save txt results')
    parser.add_argument('--dataset_folder', default='./data/widerface/val/images/', type=str, help='dataset path')
    opt = parser.parse_args()
    print(opt)

    model = YOLO(opt.weights)

    # testing dataset    
    test_dataset = glob(opt.dataset_folder)

    for image_path in test_dataset:        
        results = model.predict(source=image_path, imgsz=opt.img_size, conf=opt.conf_thres, iou=opt.iou_thres, augment=opt.augment, device=opt.device)
        img_name = image_path.split("/")[-2] + "/" + os.path.basename(image_path)
        save_name = opt.save_folder + img_name[:-4] + ".txt"
        dirname = os.path.dirname(save_name)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(save_name, "w") as fd:
            result = results[0].cpu().numpy()
            file_name = os.path.basename(save_name)[:-4] + "\n"
            bboxs_num = str(result.boxes.shape[0]) + '\n'
            fd.write(file_name)
            fd.write(bboxs_num)
            for box in result.boxes:
                conf = box.conf[0]
                cls  = box.cls[0]
                xyxy = box.xyxy[0]
                x1 = int(xyxy[0] + 0.5)
                y1 = int(xyxy[1] + 0.5)
                x2 = int(xyxy[2] + 0.5)
                y2 = int(xyxy[3] + 0.5)
                fd.write('%d %d %d %d %.03f' % (x1, y1, x2-x1, y2-y1, conf if conf <= 1 else 1) + '\n')
        
