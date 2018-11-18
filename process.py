import time
from PIL import Image
# import face_recognition

UPLOAD_INPUT_DIR = 'upload_images/input/'
UPLOAD_STYLE_DIR = 'upload_images/style/'
RESCALED_INPUT_DIR = 'upload_images/input_rescaled/'
RESCALED_STYLE_DIR = 'upload_images/style_rescaled/'


def process_images(index):
    print('Start processing images with index {index}'.format(index=index))
    time.sleep(2)
    print('Finish processing images with index {index}'.format(index=index))


# def rescale_image(in_path, out_path):
#     image = face_recognition.load_image_file(in_path)
#     # Find all facial features in all the faces in the image
#     face_landmarks_list = face_recognition.face_landmarks(image)
#
#     # Create a PIL imagedraw object so we can draw on the picture
#     pil_image = Image.fromarray(image)
#
#     if len(face_landmarks_list) != 1:  # no face or too many faces detected
#         return 1
#
#     face_landmarks = face_landmarks_list[0]
#
#     facial_feature = 'chin'
#     xmin = xmax = face_landmarks[facial_feature][0][0]
#     ymin = ymax = face_landmarks[facial_feature][0][1]
#     for landmark in face_landmarks[facial_feature]:
#         if landmark[0] < xmin:
#             xmin = landmark[0]
#         if landmark[0] > xmax:
#             xmax = landmark[0]
#         if landmark[1] < ymin:
#             ymin = landmark[1]
#         if landmark[1] > ymax:
#             ymax = landmark[1]
#
#     w = xmax - xmin
#     h = ymax - ymin
#
#     cropped_pil_image = pil_image.crop((xmin - int(w / 5), ymin - int(h), xmax + int(w / 5), ymax + int(h / 5)))
#     cropped_pil_image.save(out_path)
#     return 0
