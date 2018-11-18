from PIL import Image, ImageDraw
import face_recognition
import subprocess

UPLOAD_INPUT_DIR = 'upload_images/input/'
UPLOAD_STYLE_DIR = 'upload_images/style/'
RESCALED_INPUT_DIR = 'upload_images/input_rescaled/'
RESCALED_STYLE_DIR = 'upload_images/style_rescaled/'
INPUT_DIR = '/home/upload-http-server/images/input/'
STYLE_DIR = '/home/upload-http-server/images/style/'
SEGMENTATION_DIR = '/home/upload-http-server/images/segmentation/'
TMP_RESULTS_DIR = '/home/upload-http-server/images/tmp_results/'
FINAL_RESULTS_DIR = '/home/upload-http-server/images/final_results/'


def process_images(index):
    print('Start processing images with index {index}'.format(index=index))
    if not rescale_image(UPLOAD_INPUT_DIR + 'in' + str(index) + '.png', RESCALED_INPUT_DIR + 'in' + str(index) + '.png'):
        return 1
    if not rescale_image(UPLOAD_STYLE_DIR + 'tar' + str(index) + '.png', RESCALED_STYLE_DIR + 'tar' + str(index) + '.png'):
        return 1
    resize_images(RESCALED_INPUT_DIR + 'in' + str(index) + '.png', INPUT_DIR + 'in' + str(index) + '.png',
                  RESCALED_STYLE_DIR + 'tar' + str(index) + '.png', STYLE_DIR + 'tar' + str(index) + '.png')
    make_segmentation(INPUT_DIR + 'in' + str(index) + '.png', SEGMENTATION_DIR + 'in' + str(index) + '.png')
    make_segmentation(STYLE_DIR + 'tar' + str(index) + '.png', SEGMENTATION_DIR + 'tar' + str(index) + '.png')

    subprocess.call('cd /usr/local/app/styletransfer;\nth /usr/local/app/styletransfer/neuralstyle_seg.lua -content_image '+INPUT_DIR+'in' + str(index) + '.png'+' -style_image '+STYLE_DIR+'tar' + str(index) + '.png'+' -content_seg '+SEGMENTATION_DIR+'in' + str(index) + '.png'+' -style_seg '+SEGMENTATION_DIR+'tar' + str(index) + '.png'+' -index '+str(index)+' -num_iterations 1000 -save_iter 1000 -print_iter 100 -gpu 0 -serial '+TMP_RESULTS_DIR, shell=True)

    subprocess.call('cd /usr/local/app/styletransfer/gen_laplacian;\noctave gen_laplacian.m '+str(index), shell=True)
    subprocess.call('cd /usr/local/app/styletransfer;\nth /usr/local/app/styletransfer/deepmatting_seg.lua -content_image '+INPUT_DIR+'in' + str(index) + '.png'+' -style_image '+STYLE_DIR+'tar' + str(index) + '.png'+' -init_image '+TMP_RESULTS_DIR+'out'+str(index)+'_t_1000.png'+' -content_seg '+SEGMENTATION_DIR+'in' + str(index) + '.png'+' -style_seg '+SEGMENTATION_DIR+'tar' + str(index) + '.png'+' -index '+str(index)+' -num_iterations 1000 -save_iter 1000 -print_iter 100 -gpu 0 -serial '+FINAL_RESULTS_DIR + ' -f_radius 15 -f_edge 0.01', shell=True)
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


def make_segmentation(in_path, out_path):
    print('Start making segmentation mask for image ' + in_path)
    image = face_recognition.load_image_file(in_path)

    # Find all facial features in all the faces in the image
    face_landmarks_list = face_recognition.face_landmarks(image)

    # Create a PIL imagedraw object so we can draw on the picture
    pil_image = Image.fromarray(image)

    face_landmarks = face_landmarks_list[0]
    d = ImageDraw.Draw(pil_image)

    # uncomment if don't want to transfer background
    # make black or purple background
    # if args['background'] == '1':
    #     color = (0, 0, 0)
    # else:
    #     color = (255, 0, 255)

    color = (0, 0, 0)
    d.line([(0, 0), (0, 0 + pil_image.size[1]), pil_image.size], fill=color)
    ImageDraw.floodfill(pil_image, (int(pil_image.size[0] / 2), int(pil_image.size[1] / 2)), value=color, border=color)

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

    face_landmarks[facial_feature].append((xmax, ymin - (ymax - ymin) / 2))
    face_landmarks[facial_feature].append((xmin, ymin - (ymax - ymin) / 2))
    face_landmarks[facial_feature].append(face_landmarks[facial_feature][0])
    d.line(face_landmarks[facial_feature], fill=(0, 0, 255))
    ImageDraw.floodfill(pil_image, ((xmax + xmin) / 2, (ymax + ymin) / 2), value=(0, 0, 255), border=(0, 0, 255))

    facial_feature = 'right_eye'
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

    face_landmarks[facial_feature].append(face_landmarks[facial_feature][0])
    d.line(face_landmarks[facial_feature], fill=(255, 255, 255))
    ImageDraw.floodfill(pil_image, ((xmax + xmin) / 2, (ymax + ymin) / 2), value=(255, 255, 255),
                        border=(255, 255, 255))

    facial_feature = 'left_eye'
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
    face_landmarks[facial_feature].append(face_landmarks[facial_feature][0])
    d.line(face_landmarks[facial_feature], fill=(255, 255, 0))
    ImageDraw.floodfill(pil_image, ((xmax + xmin) / 2, (ymax + ymin) / 2), value=(255, 255, 0), border=(255, 255, 0))

    facial_feature = 'top_lip'
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

    face_landmarks[facial_feature].append(face_landmarks[facial_feature][0])
    d.line(face_landmarks[facial_feature], fill=(255, 0, 0))
    ImageDraw.floodfill(pil_image, (face_landmarks[facial_feature][2][0], face_landmarks[facial_feature][2][1] + 1),
                        value=(255, 0, 0), border=(255, 0, 0))

    facial_feature = 'bottom_lip'
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

    face_landmarks[facial_feature].append(face_landmarks[facial_feature][0])
    d.line(face_landmarks[facial_feature], fill=(255, 0, 0))
    ImageDraw.floodfill(pil_image, (face_landmarks[facial_feature][3][0], face_landmarks[facial_feature][3][1] - 1),
                        value=(255, 0, 0), border=(255, 0, 0))

    # Save the picture
    pil_image.save(out_path)
    print('Finish making segmentation mask, write mask to ' + out_path)
