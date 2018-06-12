import os
import xml.etree.ElementTree as ET

import cv2
import numpy as np


def argsProcessor():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--dataPath", help="DataPath")
    parser.add_argument("-o", "--outputFiles", help="outputFiles", default="bar")
    return parser.parse_args()


if __name__ == '__main__':
    args = argsProcessor()
    dir = args.dataPath
    output_dir = args.outputFiles
    if (not os.path.isdir(output_dir)):
        os.mkdir(output_dir)
    import csv

    with open(args.outputFiles + "/gt.csv", 'a') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for folder in os.listdir(dir):
            a = 0
            print(str(folder))
            if (os.path.isdir(dir + "/" + folder)):
                for file in os.listdir(dir + "/" + folder):
                    images_dir = dir + "/" + folder + "/" + file
                    if (os.path.isdir(images_dir)):
                        list_gt = []
                        tree = ET.parse(images_dir + "/" + file + ".gt")
                        root = tree.getroot()
                        for a in root.iter("frame"):
                            if a.attrib["rejected"] != "false":
                                print("Some frames are not valid")
                                0 / 0
                            list_gt.append(a)

                        # print list_gt
                        for image in os.listdir(images_dir):
                            if image.endswith(".jpg"):
                                try:
                                    # Now we have opened the file and GT. Write code to create multiple files and scale gt
                                    list_of_points = {}
                                    img = cv2.imread(images_dir + "/" + image)
                                    for point in list_gt[int(float(image[0:-4])) - 1].iter("point"):
                                        myDict = point.attrib

                                        list_of_points[myDict["name"]] = (
                                            int(float(myDict['x'])), int(float(myDict['y'])))

                                    ptr1 = (
                                        min(list_of_points["tl"][0], list_of_points["bl"][0], list_of_points["tr"][0],
                                            list_of_points["br"][0]),
                                        min(list_of_points["tr"][1], list_of_points["tl"][1], list_of_points["br"][1],
                                            list_of_points["bl"][1]))

                                    ptr2 = (
                                        max(list_of_points["tl"][0], list_of_points["bl"][0], list_of_points["tr"][0],
                                            list_of_points["br"][0]),
                                        max(list_of_points["tr"][1], list_of_points["tl"][1], list_of_points["br"][1],
                                            list_of_points["bl"][1]))

                                    start_x = np.random.randint(0, ptr1[0] - 2)
                                    start_y = np.random.randint(0, ptr1[1] - 2)

                                    end_x = np.random.randint(ptr2[0] + 2, img.shape[1])
                                    end_y = np.random.randint(ptr2[1] + 2, img.shape[0])

                                    myGt = np.asarray((list_of_points["tl"], list_of_points["tr"], list_of_points["br"],
                                                       list_of_points["bl"]))
                                    myGt = myGt - (start_x, start_y)

                                    img = img[start_y:end_y, start_x:end_x]

                                    myGt = myGt * (1.0 / img.shape[1], 1.0 / img.shape[0])
                                    myGtTemp = myGt * myGt
                                    sum_array = myGtTemp.sum(axis=1)
                                    tl_index = np.argmin(sum_array)
                                    tl = myGt[tl_index]
                                    tr = myGt[(tl_index + 1) % 4]
                                    br = myGt[(tl_index + 2) % 4]
                                    bl = myGt[(tl_index + 3) % 4]

                                    tl = [round(a, 4) for a in tl]
                                    tr = [round(a, 4) for a in tr]
                                    br = [round(a, 4) for a in br]
                                    bl = [round(a, 4) for a in bl]

                                    img = cv2.resize(img, (64, 64))
                                    no = 0
                                    gt_crop = np.array([tl, tr, br, bl])

                                    cv2.imwrite(output_dir + "/" + folder + file + image, img)
                                    spamwriter.writerow((folder + file + image, (tl, tr, br, bl)))


                                except KeyboardInterrupt:
                                    raise