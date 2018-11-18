import time
from PIL import Image
import face_recognition

UPLOAD_INPUT_DIR = 'upload_images/input/'
UPLOAD_STYLE_DIR = 'upload_images/style/'
RESCALED_INPUT_DIR = 'upload_images/input_rescaled/'
RESCALED_STYLE_DIR = 'upload_images/style_rescaled/'
INPUT_DIR = 'images/input/'
STYLE_DIR = 'images/style/'


def process_images(index):
    print('Start processing images with index {index}'.format(index=index))
    if not rescale_image(UPLOAD_INPUT_DIR + 'in' + str(index) + '.png', RESCALED_INPUT_DIR + 'in' + str(index) + '.png'):
        return 1
    if not rescale_image(UPLOAD_STYLE_DIR + 'tar' + str(index) + '.png', RESCALED_STYLE_DIR + 'tar' + str(index) + '.png'):
        return 1
    resize_images(RESCALED_INPUT_DIR + 'in' + str(index) + '.png', INPUT_DIR + 'in' + str(index) + '.png',
                  RESCALED_STYLE_DIR + 'tar' + str(index) + '.png', STYLE_DIR + 'tar' + str(index) + '.png')
    print('Finish processing images with index {index}'.format(index=index))


def rescale_image(in_path, out_path):
    print('Start rescaling image ' + in_path)
    image = face_recognition.load_image_file(in_path)
    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)

    # Create a PIL imagedraw object so we can draw on the picture
    pil_image = Image.fromarray(image)

    if len(face_landmarks_list) != 1:  # no face or too many faces detected
        print('No faces or too many faces found, exit')
        return False

    face_landmarks = face_landmarks_list[0]

    facial_feature = 'chin'
    xmin = xmax = face_landmarks[facial_feature][0][0]
    ymin = ymax = face_landmarks[facial_feature][0][1]
    for landmark in face_landmarks[facial_feature]:
        if landmark[0] < xmin:
            xmin = landmark[0]
        if landmark[0] > xmax:
            xmax = landmark[0]
        if landmark[1] < ymin:
            ymin = landmark[1]
        if landmark[1] > ymax:
            ymax = landmark[1]

    w = xmax - xmin
    h = ymax - ymin

    cropped_pil_image = pil_image.crop((xmin - int(w / 5), ymin - int(h), xmax + int(w / 5), ymax + int(h / 5)))
    cropped_pil_image.save(out_path)
    print('Finish rescaling image, write to ' + out_path)
    return True


def resize_images(in_path1, out_path1, in_path2, out_path2):
    print('Start resizing images')
    image1 = Image.open(in_path1)
    image2 = Image.open(in_path2)

    x1, y1 = image1.size
    x2, y2 = image2.size

    xmin = x1 if x1 < x2 else x2
    ymin = y1 if y1 < y2 else y2

    image1.resize((xmin, ymin)).save(out_path1)
    image2.resize((xmin, ymin)).save(out_path2)
    print('Finish resizing images, write results to {path1} and {path2}'.format(path1=out_path2, path2=out_path2))
