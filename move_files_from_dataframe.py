# @Author: Benjamin R. Everett <beneverett>
# @Date:   01-22-2018
# @Email:  benjamin.r.everett@gmail.com
# @Filename: move_files_from_dataframe.py
# @Last modified by:   beneverett
# @Last modified time: 01-22-2018

"""
Author: Benjamin R Everett
Last Updated: 12/06/2017
"""

import pandas as pd
import shutil
import os
import random
import math
import json
import cv2

"""
TO DO: Comment out code
"""

"""
-- This class moves files in a folder to train, validate, test folders
    based upon labels in a database
"""


class CreateFolders(object):

    def __init__(self,
                 filepath_labels,
                 filepath_codes,
                 filepath_images,
                 filepath_sorted_images,
                 df_column_for_filename,
                 df_column_for_classes,
                 adjust_splits=False):

        """
        -- Initializes class --

            PARAMETERS
            ----------
                filepath_labels: str
                    e.g. -> '../data/nov_22_5_classes_only_file_and_class.pkl'
                    filepath of pickled data frame containing
                      filenames and labels for filenames

                 filepath_codes: str
                    e.g. -> '../data/house_rest_retail_office_other.txt'
                    filepath of text file containing dict of folder names
                      and classes -> {'00_other': 0, '01_house': 1, etc ...}

                 filepath_images: str
                    e.g. -> '../images'
                    filepath of folder containing all fetched images

                 filepath_sorted_images: str
                    e.g. -> '../house_rest_retail_office_other'
                    filepath of folder to create for new images
                    NOTE: this folder should be uncreated. Script will create
                 df_column_for_filename='file',
                 df_column_for_classes='classes')

        """
        self.t_v_t = ['train', 'validate', 'test']
        self.filepath_labels = filepath_labels
        self.filepath_codes = filepath_codes
        self.filepath_images = filepath_images
        self.filepath_sorted_images = filepath_sorted_images
        self.codes = self._get_codes_dicty(filepath=filepath_codes)
        self.df = pd.read_pickle(filepath_labels)
        self.classes = list(self.codes.keys())
        self.df_column_for_classes = df_column_for_classes
        self.df_column_for_filename = df_column_for_filename
        self.filenames_dct = self._get_list_of_filenames_for_each_class()
        self.bad_files = []
        self.balanced_classes_dct = None
        self.filepath_balanced_images = None

    def copy_files(self):
        self._check_dataframe_against_images()
        self.results_dct = {}
        # ['00_other', etc ...]
        for folder in self.classes:
            self.results_dct[folder] = {}
            # [file1, file2, etc ...]
            files = self.filenames_dct[folder]['files']
            # return integers divisible by 5 in order:
            # train, validate, test
            nums = self._return_t_v_t_numbers_for_file(folder=folder)
            # [(train, 45), (validate, 65), (test, 40)]
            set_of_values = list(zip(self.t_v_t, nums))
            # (train, 45)
            for value in set_of_values:
                print("Now moving {}/{}".format(folder, value[0]))
                folder_count = 0
                v = value[1]
                while folder_count < v:
                    # get random file -> 'file2'
                    filey = files.pop(files.index(random.choice(files)))
                    print("Moving file: ", filey)
                    dest_folder = "{}/{}/{}" \
                        .format(self.filepath_sorted_images,
                                value[0],
                                folder)
                    src = "{}/{}".format(self.filepath_images, filey)
                    dst = "{}/{}".format(dest_folder, filey)
                    # check if the image is good
                    if self._check_if_image_good(image=src):
                        shutil.copyfile(src, dst)
                        folder_count += 1
                    else:
                        self.bad_files.append(src)
                        folder_count += 1
                        v -= 1
                # check to make sure files in folder are
                # multiple of 5
                while len(os.listdir(dest_folder)) % 5 != 0:
                    files = os.listdir(dst)
                    file_to_remove = files \
                        .pop(files.index(random.choice(files)))
                    print("Removing file: ", file_to_remove)
                    os.remove("{}/{}".format(dest_folder, file_to_remove))
                self.results_dct[folder][value[0]] = \
                    len(os.listdir(dest_folder))

        with open("{}/file_counts.json".format(self.filepath_sorted_images),
                  'w') as f:
            json.dump(self.results_dct, f)

        return self.results_dct

    def balance_classes(self):
        self.balanced_classes_dct = self._get_balance_classes_dct()
        self.create_folders(balancing=True)
        # ['train', 'test'....]
        for i in self.t_v_t:
            file_num = self.balanced_classes_dct[i]
            # ['00_other', '01_office.....']
            for val in self.classes:
                # train/00_other
                folder = '{}/{}'.format(i, val)

                list_of_files = [pic for pic in os.listdir('{}/{}'
                                 .format(self.filepath_sorted_images, folder))]
                total_files = len(list_of_files)
                move_to = '{}/{}'.format(self.filepath_balanced_images, folder)

                while len(os.listdir(move_to)) < file_num:
                    print("Moving pics in directory: ",
                          folder)
                    print("Total files in this directory: ", total_files)
                    print("Moving picture {} of {}"
                          .format(len(os.listdir(move_to)), file_num))

                    filey = list_of_files.pop(list_of_files.index(
                                              random.choice(list_of_files)))
                    src = '{}/{}/{}'.format(self.filepath_sorted_images,
                                            folder,
                                            filey)
                    dst = '{}/{}/{}'.format(self.filepath_balanced_images,
                                            folder,
                                            filey)

                    print("Copying file: {}".format(filey))
                    shutil.copyfile(src, dst)

        new_dct = {}
        for c in self.classes:
            new_dct[c] = {}
            for i in self.t_v_t:
                new_dct[c][i] = self.balanced_classes_dct[i]

        with open("{}/file_counts.json".format(self.filepath_balanced_images),
                  'w') as f:
            json.dump(new_dct, f)

        return new_dct

    def create_folders(self, balancing=False):
        if balancing is False:
            os.mkdir(self.filepath_sorted_images)
            for i in ['train', 'test', 'validate']:
                os.mkdir('{}/{}'.format(self.filepath_sorted_images, i))
            # self._get_codes_dicty(filepath=folder_codes)
            for i in ['train', 'test', 'validate']:
                for classy in self.classes:
                    os.mkdir('{}/{}/{}'.format(self.filepath_sorted_images,
                                               i,
                                               classy))
            print("\n\nThe following directories were created in {}:"
                  .format(self.filepath_sorted_images))
            print(os.listdir('{}'.format(self.filepath_sorted_images)))
            print("\n\n")
        else:
            self.filepath_balanced_images = \
                self.filepath_sorted_images + '_balanced'
            os.mkdir(self.filepath_balanced_images)
            for i in ['train', 'test', 'validate']:
                os.mkdir('{}/{}'.format(self.filepath_balanced_images, i))
            # self._get_codes_dicty(filepath=folder_codes)
            for i in ['train', 'test', 'validate']:
                for classy in self.classes:
                    os.mkdir('{}/{}/{}'.format(self.filepath_balanced_images,
                                               i,
                                               classy))
            print("\n\nThe following directories were created in {}:"
                  .format(self.filepath_balanced_images))
            print(os.listdir('{}'.format(self.filepath_balanced_images)))
            print("\n\n")

    def _get_codes_dicty(self, filepath):
        new_dct = {}
        with open(filepath, 'r') as f:
            data = eval(f.read())
            for k, v in data.items():
                folder = data[k]['folder_name']
                class_code = data[k]['class']
                new_dct[folder] = class_code

        return new_dct

    def _check_dataframe_against_images(self):
        images = os.listdir(self.filepath_images)
        print("Checking data frame against images folder...")

        def check_dataframe(row):
            if row[0] in images:
                return row
            else:
                pass
        # drop duplicates
        self.df.drop_duplicates(subset=self.df_column_for_filename,
                                inplace=True)
        # check that filenames in df are actually images
        self.df = self.df.apply(check_dataframe, axis=1)
        # drop null values from above function
        self.df.dropna(axis=0, how='any', inplace=True)

    def _get_list_of_filenames_for_each_class(self):
        filename_dct = {}
        for c in self.classes:
            filename_dct[c] = {}
        # self.codes = {'00_other': 0, '01_office': 1} etc....
        # self.classes = ['00_other', '01_office'.....]
        for k, v in self.codes.items():
            # get list of filenames according to code
            # e.g. v = 1 -> [file1, file2, etc...]
            files = list(self.df[self.df_column_for_filename]
                         [self.df[self.df_column_for_classes] == v])
            filename_dct[k]['class'] = v
            filename_dct[k]['files'] = files
            # dct = {'01_other': {'class': 0, 'files': [list of files]}

        # add onto dict
        # dct = {'01_other': {'class': 0,
        #                     'files': [list of files],
        #                     'train': [], ...}
        for k in self.codes.keys():
            for t_v_t in self.t_v_t:
                filename_dct[k][t_v_t] = []

        return filename_dct

    def _return_divisible_by_5(self, num):
        while num % 5 != 0:
            num -= 1
        return num

    def _return_t_v_t_numbers_for_file(self, folder):
        all_files = list(self.filenames_dct[folder]['files'])
        num_all_files = len(all_files)
        test_num = self._return_divisible_by_5(math.floor(num_all_files * 0.2))
        train_num = self._return_divisible_by_5(
            math.floor((num_all_files - test_num) * 0.8))
        val_num = self._return_divisible_by_5(
            num_all_files - train_num - test_num)

        # return integers divisible by 5 for t, v, t
        return train_num, val_num, test_num

    def _check_if_image_good(self, image):
        img = cv2.imread(image)
        try:
            img.shape
        except AttributeError:
            print("---------- ERROR: File unreadable ---------")
            return False
        else:
            return True

    def _get_balance_classes_dct(self):
        with open("{}/file_counts.json"
                  .format(self.filepath_sorted_images)) as f:
            self.results_dct = json.load(f)
        least_nums_dct = {}
        # ['00_other', '01_office', ....]
        for i in self.t_v_t:
            num = 10000000
            for key in self.results_dct.keys():
                new_num = self.results_dct[key][i]
                if new_num < num:
                    num = new_num
            least_nums_dct[i] = num

        return least_nums_dct


if __name__ == '__main__':
    copyfiles = \
        CreateFolders(filepath_labels='../data/\
house_rest_office_retail.pkl',
                      filepath_codes='../data/\
codes_other_commercial.txt',
                      filepath_images='../images',
                      filepath_sorted_images='../\
images_other_commercial',
                      df_column_for_filename='FULL_ADDRESS',
                      df_column_for_classes='class')
    # copyfiles.create_folders()
    # copyfiles.copy_files()
