# @Author: Benjamin R. Everett <beneverett>
# @Date:   01-22-2018
# @Email:  benjamin.r.everett@gmail.com
# @Filename: label_pics.py
# @Last modified by:   beneverett
# @Last modified time: 01-22-2018
"""
This class will label pics via pointing to a directory of pics
and pointing to a text file of labels

Very helpful for binary classification of pictures
"""

import os
import cv2
import random
import shutil

"""
-- --

    PARAMETERS
    ----------

    RETURNS
    -------
"""

"""
To Do: Comment out code
"""


class Labeler(object):

    def __init__(self,
                 text_file,
                 number_of_images_to_label,
                 images_folder
                 ):

        """
        -- Initialize Function --

            NOTE
            ----
            "Backspace":
                Pressing the 'backspace' key signifies to the
                labeler that you mislabled the previous image.
                It will redisplay the current image and the
                previous image at a later point in the current labeling
                session for proper labeling.

            PARAMETERS
            ----------

            text_file: str -> "single_multi_other.txt"
                txt file should be placed in main images folder
                txt file should contain a dictionary with the name of the label
                the corresponding number you'll hit to label the photo
                File should be in the following format:
                    {'house': 0, 'not_house': 1, 'dog_house': 2, etc...}

            number_of_images_to_label: int -> 10
                number of images to label this session
                e.g. Will display 10 images to label before closing the session

            images_folder: str -> "/Users/beneverett/Desktop/house"
                filepath for folder containing unlabeled images

            RETURNS
            -------

            self.images_folder: str -> "/Users/beneverett/Desktop/house"
                filepath of images folder

            self.txt_dct: dict -> {'house': 0, 'not_house': 1, 'dog_house': 2,
                                  etc...}
                dictionary of label names and label value

            self.num_to_keystroke: dict -> {0: 48, 1: 49, 2: 50, 3: 51,
                                            etc ...}
                dictionary containing keystroke to key code
                https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes

            self.keystroke_to_num: dict -> {48: 0, 49: 1, 50: 2, 51: 3,
                                            etc ...}
                dictionary containing keycode to keystroke
                https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes

            self.number_of_images_to_label: int -> 10
                number of images to be labeled before closing
        """

        self.images_folder = images_folder
        self.txt_dct = self._load_text_file(text_file)
        self.num_to_keystroke, self.keystroke_to_num = \
            self._key_mappings()
        self.number_of_images_to_label = number_of_images_to_label
        self._make_folders(filepath=images_folder)
        self.set_all_images, self.number_of_images_to_label = \
            self._get_folder_info(self.number_of_images_to_label)
        self.images_to_label = self._get_list_images_to_label(
                               num_to_label=self.number_of_images_to_label,
                               all_images=self.set_all_images)
        print("\n\nWe're going to label these images:\n{}\n"
              .format(self.images_to_label))

    def _get_list_images_to_label(self, num_to_label, all_images):
        images_to_label = set()
        # create list of images to label
        while len(images_to_label) < num_to_label:
            # random sample returns list, get first element from list
            image = random.sample(all_images, 1)[0]
            # if we have not already labeled the image
            # add it to the list to label
            images_to_label.add(image)
        # return the list of images to label
        return images_to_label

    def _make_folders(self, filepath):
        folders = self.txt_dct.keys()
        files = os.listdir(filepath)
        for folder in folders:
            if folder not in files:
                os.mkdir('{}/{}'.format(self.images_folder, folder))

    def label_images(self):
        counter = 1
        acceptable_keys = self._get_acceptable_keys()
        last_image = None
        while len(self.images_to_label) > 0:
            image = self.images_to_label.pop()
            key_stroke = self._display_image(image=image, counter=counter)
            if key_stroke != 'error':
                print("Recorded key stroke: {}".format(key_stroke))
                if key_stroke in acceptable_keys:
                    cv2.destroyAllWindows()
                    self._move_pic(image=image, key_stroke=key_stroke)
                    counter += 1
                    last_image = image
                elif key_stroke == 8:
                    print("You made a mistake. It happens")
                    print("Adding both images back to list...\n\n")
                    self.images_to_label.add(last_image)
                    self.images_to_label.add(image)
                else:
                    print("That was not an acceptable keystroke")
                    print("Adding image back to list...")
                    self.images_to_label.add(image)
            else:
                print("Bad image. Moving onto the next")
                counter += 1

    def _switch_key_values_in_dict(self, dictionary):
        keys = dictionary.keys()
        values = dictionary.values()
        keys_and_values = zip(values, keys)
        new_dct = {}
        for value in keys_and_values:
            new_dct[value[0]] = value[1]
        return new_dct

    def _get_acceptable_keys(self):
        values = self.txt_dct.values()
        txt_keystrokes = set()
        for value in values:
            txt_keystrokes.add(self.num_to_keystroke[value])
        return txt_keystrokes

    def _move_pic(self, image, key_stroke):
        txt_dct_reversed = self._switch_key_values_in_dict(
                                    dictionary=self.txt_dct)
        print("Dictionary: {}".format(txt_dct_reversed))
        print("Assigned label based upon keystroke: {}"
              .format(self.keystroke_to_num[key_stroke]))
        folder = txt_dct_reversed[self.keystroke_to_num[key_stroke]]
        print("Picture moved to folder titled: {}".format(folder))
        print('\n')
        src = '{}/{}'.format(self.images_folder, image)
        dst = '{}/{}/{}'.format(self.images_folder, folder, image)
        shutil.move(src, dst)

    def _display_image(self, image, counter):
        print("Loading: {}".format(image))
        img = cv2.imread("{}/{}".format(self.images_folder, image))

        try:
            img.shape

        except AttributeError:
            return 'error'

        else:
            pretty_txt_dct = "{}".format(self.txt_dct).strip("{").strip("}")
            pic_title = "{}/{} ~ {}" \
                        .format(counter, self.number_of_images_to_label,
                                pretty_txt_dct)
            # load image as NumPy array
            cv2.imshow(pic_title, img)
            # move the picture to the relative center of my screen
            cv2.moveWindow(pic_title, 420, 50)

            # openCV2 specification to set a wait key
            k = cv2.waitKey()
            return k

    def _load_text_file(self, filepath):
        filepath = "{}/{}".format(self.images_folder, filepath)
        with open(filepath, 'r') as f:
            return eval(f.read())

    def _key_mappings(self):
        # make file based
        num_to_keystroke = {0: 48, 1: 49, 2: 50, 3: 51,
                            4: 52, 5: 53, 6: 54, 7: 55, 8: 56, 9: 57}
        keystroke_to_num = {48: 0, 49: 1, 50: 2, 51: 3, 52:
                            4, 53: 5, 54: 6, 55: 7, 56: 8, 57: 9}

        return num_to_keystroke, keystroke_to_num

    def _get_folder_info(self, number_of_images_to_label):
        # only get images with jpg
        set_all_images = {x for x in os.listdir(self.images_folder)
                          if x.split('.')[-1] in ["jpg", "png", "jpeg"]}
        self.total_num_images = len(set_all_images)

        # check that requested number of images to label is not too many

        if number_of_images_to_label > self.total_num_images:
            print("\n\n")
            print("You can't label {} images"
                  .format(number_of_images_to_label))
            print("There are only {} left to label."
                  .format(self.total_num_images))
            print("Instead you'll label the last {} images.\n"
                  .format(self.total_num_images))
            number_of_images_to_label = self.total_num_images

        return set_all_images, number_of_images_to_label


if __name__ == '__main__':

    label = Labeler(images_folder="/\
Users/beneverett/Desktop/suite",
                    number_of_images_to_label=2500,
                    text_file="suite_text.txt")
    label.label_images()
