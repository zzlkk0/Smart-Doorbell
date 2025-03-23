import cv2
import numpy as np
import os

# 设置数据路径和模型保存路径
data_path = 'data'            # 存放人脸数据集的文件夹
trainer_path = 'trainer'       # 存放训练模型的文件夹
model_file = 'trainer.yml'     # 保存的模型文件名

# 确保训练目录存在
if not os.path.exists(trainer_path):
    os.makedirs(trainer_path)

# 加载人脸检测器
faceCascade = cv2.CascadeClassifier('/home/link/facedetect/haarcascade_frontalface_default.xml')
# 创建LBPH识别器
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 获取数据集中的人脸图像和标签
def get_images_and_labels(path):
    face_samples = []
    ids = []

    # 遍历每个子文件夹作为不同的ID
    for person_id, person_name in enumerate(os.listdir(path)):
        person_path = os.path.join(path, person_name)
        print(person_id,person_name)
        if not os.path.isdir(person_path):
            continue
        
        # 遍历该子文件夹中的所有图像
        for image_name in os.listdir(person_path):
            image_path = os.path.join(person_path, image_name)
            gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if gray_image is None:
                print(f"[WARN] 无法读取图像文件：{image_path}")
                continue
            
            # 检测人脸
            faces = faceCascade.detectMultiScale(gray_image)
            for (x, y, w, h) in faces:
                face_samples.append(gray_image[y:y + h, x:x + w])
                ids.append(person_id)

    return face_samples, ids

# 训练模型
print("\n[INFO] 开始训练模型...")
faces, ids = get_images_and_labels(data_path)
if len(faces) == 0:
    print("[ERROR] 没有找到任何有效的人脸数据！")
else:
    recognizer.train(faces, np.array(ids))

    # 保存模型
    model_save_path = os.path.join(trainer_path, model_file)
    recognizer.write(model_save_path)
    print(f"\n[INFO] 模型已成功保存到: {model_save_path}")
