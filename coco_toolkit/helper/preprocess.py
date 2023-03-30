import datetime
import glob
import hashlib
import json
import logging
import os
import random
import shutil
from pathlib import Path

import numpy as np
from addict import Dict
from tqdm import tqdm


class PreProcess:
    """
    Preprocess class for preparing coco json dataset for Training.
    """

    def __init__(self, coco: dict):
        """
        @param coco: Coco json file to be processed
        """
        self.coco = coco.copy()

    @staticmethod
    def reader(path: str) -> Dict:
        """
        This function read coco json file as a dictionary.

            @param path: Coco json file path to be read
            @return: Return coco json file as a dictionary
        """
        log = logging.getLogger()
        assert os.path.isfile(path), log.error(" Invalid json file path.Please check your directory")

        with open(path) as f:
            cfg = json.load(f)
            return Dict(cfg)

    def set_unique_image_id(self, first_id: int):
        """
        This function changes all images id.

            @param first_id: First image id value
        """

        old_dic: dict = {}

        for img in self.coco["images"]:
            old_dic[first_id] = img["id"]
            first_id += 1

        new_dict = dict([(value, key) for key, value in old_dic.items()])

        for img in self.coco["images"]:
            img["id"] = new_dict[img["id"]]
        for ann in self.coco["annotations"]:
            ann["image_id"] = new_dict[ann["image_id"]]

    def set_unique_class_id(self, first_id: int, back_grounds: bool):
        """
        This function changes all class' id.

            @param first_id: First class id value
            @param back_grounds: Boolean variable. İf it's True add background to class
        """
        old_dic = {}
        check_bg: list = []

        backgrounds = {"id": 0, "name": "Background", "supercategory": ""}

        if back_grounds:
            for cat in self.coco["categories"]:
                if cat["name"] == "Background" or cat["name"] == "background":
                    check_bg.append(1)
            if not check_bg:
                self.coco["categories"].insert(0, backgrounds)

        for cat in self.coco["categories"]:
            old_dic[first_id] = cat["id"]
            first_id += 1

        new_dict = dict([(value, key) for key, value in old_dic.items()])

        for cat in self.coco["categories"]:
            cat["id"] = new_dict[cat["id"]]

        for ann in self.coco["annotations"]:
            ann["category_id"] = new_dict[ann["category_id"]]

    def set_unique_annotation_id(self, first_id: int):
        """
        This function changes all annotations' id.

            @param first_id: First annotation id value
        """

        for ann in self.coco["annotations"]:
            ann["id"] = first_id
            first_id += 1

    def check_id_unique(self):
        """
        This function check all ids are unique or not if not unique return False else return True.
        """
        log = logging.getLogger()
        anno, image, category = [], [], []

        for ann in self.coco["annotations"]:
            anno.append(ann["id"])
        for img in self.coco["images"]:
            image.append(img["id"])
        for cat in self.coco["categories"]:
            category.append(cat["id"])

        a = True if np.unique(anno).size == len(anno) else False

        b = True if np.unique(image).size == len(image) else False

        c = True if np.unique(category).size == len(category) else False

        if a and b and c:
            return True
        else:
            for key, value in {"annotation": a, "image": b, "category": c}.items():
                if not value:
                    log.error(f"{key} id not unique")
            return False

    def extract_data_by_class_name(self, categories: list, image_path: str, out_path: str):
        """
        This function export coco json file and images, then save image
         and json file to new folder in given path directory
            @param categories: List of chosen categories names
            @param image_path: Image path of data set
            @param out_path: Output directory
        """
        items, ann_items, cat_items, img_id, move_list_dir, image_list = [], [], [], [], [], []

        for cat in self.coco["categories"]:
            if cat["name"] in categories:
                items.append(cat["id"])
                cat_items.append(cat)

        for ann in self.coco["annotations"]:
            if ann["category_id"] in items:
                ann_items.append(ann)
                img_id.append(ann["image_id"])

        img_id = set(img_id)
        for img in self.coco["images"]:
            if img["id"] in img_id:
                move_list_dir.append(img["file_name"])
                image_list.append(img)

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        img_path = out_path + f"/extracted_dataset_{time}/images"
        ann_path = out_path + f"/extracted_dataset_{time}/annotations"

        os.makedirs(img_path)
        os.makedirs(ann_path)

        for image in move_list_dir:
            shutil.copy(
                image_path + f"/{image}",
                img_path + f"/{image}",
            )

        self.coco["images"] = image_list
        self.coco["annotations"] = ann_items
        self.coco["categories"] = cat_items

        p = PreProcess(self.coco)
        p.set_unique_annotation_id(first_id=1)
        p.set_unique_annotation_id(first_id=1)
        p.set_unique_class_id(first_id=0, back_grounds=True)
        p.save_coco_file(directory=ann_path, file_name="extracted_dataset")
        logging.getLogger().setLevel(logging.INFO)
        logging.info(f"Extracted dataset created to {out_path}/extracted_dataset_{time}")

    def separate_json_by_categories(self):

        categories = self.coco['categories']
        category_images = {}
        for category in categories:
            category_images[category['name']] = []
        images = self.coco['images']
        for image in images:
            image_id = image['id']
            file_name = image['file_name']
            for annotation in self.coco['annotations']:
                if annotation['image_id'] == image_id:
                    category_id = annotation['category_id']
                    category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), None)
                    if category_name is not None:
                        category_images[category_name].append({'id': image_id, 'file_name': file_name})

        for category_name, image_data in category_images.items():
            with open(f"tests/output/{category_name}.json", "w") as outfile:
                json.dump(image_data, outfile)

    def change_category_name_and_id(self, object_id: int, new_id: int, new_name: str):
        """
        :param path: json path
        :param object_id: old category id
        :param new_id: new category id
        :param new_name: new category name
        """
        for category in self.coco['categories']:
            if category['id'] == object_id:
                category['id'] = new_id
                category['name'] = new_name
                break

        with open("tests/output/coco_dataset_new.json", 'w') as f:
            json.dump(self.coco, f)

    def filter_data_by_class_name(self, categories: list, image_path: str, out_path: str):
        """
        This function filter coco json file and images,
         then save image and json file to new folder in given path directory
            @param categories: List of chosen categories names
            @param image_path: Image path of data set
            @param out_path: Output directory
        """
        items, ann_items, cat_items, img_id, move_list_dir, image_list = [], [], [], [], [], []

        for cat in self.coco["categories"]:
            if cat["name"] not in categories:
                items.append(cat["id"])
                cat_items.append(cat)

        for ann in self.coco["annotations"]:
            if ann["category_id"] in items:
                ann_items.append(ann)
                img_id.append(ann["image_id"])
        img_id = set(img_id)
        for img in self.coco["images"]:
            if img["id"] in img_id:
                move_list_dir.append(img["file_name"])
                image_list.append(img)

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        img_path = out_path + f"/filtered_dataset_{time}/images"
        ann_path = out_path + f"/filtered_dataset_{time}/annotations"

        os.makedirs(img_path)
        os.makedirs(ann_path)

        for image in move_list_dir:
            shutil.copy(
                image_path + f"/{image}",
                img_path + f"/{image}",
            )

        self.coco["images"] = image_list
        self.coco["annotations"] = ann_items
        self.coco["categories"] = cat_items

        p = PreProcess(self.coco)
        p.set_unique_annotation_id(first_id=1)
        p.set_unique_annotation_id(first_id=1)
        p.set_unique_class_id(first_id=0, back_grounds=True)
        p.save_coco_file(directory=ann_path, file_name="filtered_dataset")
        logging.getLogger().setLevel(logging.INFO)
        logging.info(f"Filtered dataset created to {out_path}/filtered_dataset_{time}")

    def box2segmentation(self):
        """
        if boundary box array has a negative value change to positive,
        if annotations has no segmentation info create segmentation array
        """
        for ann in self.coco["annotations"]:
            x1, y1, x2, y2 = (
                ann["bbox"][0],
                ann["bbox"][1],
                ann["bbox"][2],
                ann["bbox"][3],
            )
            if not ann["segmentation"] or ann["segmentation"] == []:
                ann["segmentation"] = [[x1, y1, x1, (y1 + y2), (x1 + x2), (y1 + y2), (x1 + x2), y1]]

    def save_coco_file(self, directory: str, file_name: str):
        """
        This function saves coco json file to given directory named as given file name.

            @param directory: The directory of coco json file to be saved
            @param file_name: The file name of coco json file to be saved
        """
        with open(os.path.join(directory, f"{file_name}.json"), "w") as fp:
            json.dump(self.coco, fp)

    def compare_two_annotations(self, path1: str, path2: str):
        """

        :param path1: first path
        :param path2: second path
        """
        coco_file = [path1, path2]

        for i in range(2):
            with open(coco_file[i], "r") as f:
                coco_data = json.load(f)

            num_annotations = len(coco_data["annotations"])
            logging.getLogger().setLevel(logging.INFO)
            logging.info(f"The COCO dataset has {num_annotations} annotations.")

    def remove_duplicate_image_name(self):
        """
        This function removes duplicate image names from coco json file
        """
        id_image, filename, remove_list, images, anno = [], [], [], [], []

        for img in self.coco["images"]:
            id_image.append(img["id"])
            filename.append(img["file_name"])

        seen = set()
        dupes = [x for x in filename if x in seen or seen.add(x)]

        for img in self.coco["images"]:
            if img["file_name"] in dupes:
                remove_list.append(img["id"])
                dupes.remove(img["file_name"])

        for img in self.coco["images"]:
            if not img["id"] in remove_list:
                images.append(img)
        for ann in self.coco["annotations"]:
            if ann["image_id"] not in remove_list:
                anno.append(ann)

        self.coco["annotations"] = anno
        self.coco["images"] = images

        logging.getLogger().setLevel(logging.INFO)
        logging.info("Deleted duplicate image count = " + str(len(remove_list)))

        if not remove_list:
            logging.info("There is no duplicate image name so coco json file did not change")
        else:
            logging.info("Duplicate names has removed")

    @staticmethod
    def create_random_image_name(image_base_name, path):
        code = f"{path}--{image_base_name}"
        hash_object = hashlib.md5(code.encode())
        photo_uuid = hash_object.hexdigest()
        return photo_uuid + ".jpeg"

    def change_image_file_names(self, image_path: str, inplace: bool):
        """
        This function change images' file name and copy them to a new folder.
            @param image_path: Image folder path
            @param inplace: If inplace True save coco json file to another coco json file
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        path = Path(image_path)
        abs_path = path.parent.absolute()

        os.makedirs(f"{abs_path}/image_name_change_{time}/images")

        hashname_dict = {}
        for index, img_path in enumerate(glob.glob(os.path.join(image_path, "*"))):
            basename = os.path.basename(img_path)
            uuid = PreProcess.create_random_image_name(basename, image_path)
            hashname_dict[basename] = uuid
            shutil.copy(
                img_path,
                f"{abs_path}/image_name_change_{time}/images/{basename}",
            )
            os.rename(
                f"{abs_path}/image_name_change_{time}/images/{basename}",
                os.path.join(f"{abs_path}/image_name_change_{time}/images", uuid),
            )

        for image in self.coco["images"]:
            for key, values in hashname_dict.items():
                if image["file_name"] == str(key):
                    image["file_name"] = values
        if inplace:
            os.makedirs(f"{abs_path}/image_name_change_{time}/annotations")

            PreProcess(self.coco).save_coco_file(
                directory=f"{abs_path}/image_name_change_{time}/annotations", file_name="image_name_change"
            )
            logging.getLogger().setLevel(logging.INFO)
        logging.info(f"New dataset folder created to {abs_path}/image_name_change_{time}")

    def remove_segmentation(self):
        """
        This function removes segmentations information
        """
        for ann in self.coco["annotations"]:
            del ann["segmentation"]

    def remove_distorted_bbox(self):
        """
        This function remove distorted bbox information if there is any
        """
        ann_list: list = []
        count = 0
        for ann in self.coco["annotations"]:
            if not (
                len(ann["bbox"]) != 4
                or False in [False for p in ann["bbox"] if type(p) != float and type(p) != int]
                or False in [False for p in ann["bbox"] if p < 0]
            ):
                ann_list.append(ann)
            else:
                count += 1
        self.coco["annotations"] = ann_list
        if count != 0:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("Annotations that has distorted bbox information has removed")
        else:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("There is no distorted bbox so coco json file did not change")

    def train_test_validation_split(
        self,
        image_path: str,
        test_percent: int,
        validation_percent: int,
        out_path: str,
    ):
        """
        This function split dataset according to test, validation percent and save them to given output path.

            @param image_path: Path of folder that contains dataset images
            @param test_percent: Test split percent
            @param validation_percent: Validation split percent
            @param out_path: Output path
            @return: Return spoiled train test validation datasets as tuple
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        exit_path = out_path + f"/data-{time}"

        train = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }
        test = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }
        validation = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }

        (
            random_list,
            img_id_test,
            img_id_train,
            img_id_val,
            list_dir_train,
            list_dir_test,
            list_dir_validation,
            id_train,
        ) = ([], [], [], [], [], [], [], [])
        list_split = [train, test, validation]

        p = PreProcess(self.coco)
        if not p.check_id_unique():
            assert False, "Id not unique"

        len_images = len(self.coco["images"])
        len_test = int(len_images * test_percent / 100)
        len_validation = int(len_images * validation_percent / 100)
        len_train = len_images - (len_test + len_validation)

        logging.getLogger().setLevel(logging.INFO)
        logging.info("Train image count :" + str(len_train))
        logging.info("Test image count :" + str(len_test))
        logging.info("Validation image count :" + str(len_validation))

        answer = input("Do you want to split datasets?  [yes/ no]: ")
        if any(answer.lower() == f for f in ["no", "n", "0"]):
            test_p = input("Please choose test percent : %")
            val_p = input("Please choose val percent : %")
            return PreProcess.train_test_validation_split(self, image_path, int(test_p), int(val_p), out_path)

        for elem in list_split:
            elem["categories"] = self.coco["categories"]
            elem["licenses"] = self.coco["licenses"]
            elem["info"] = self.coco["info"]

        for i in tqdm(range(len_test + len_validation)):
            x = random.randint(0, (len_test + len_validation))
            while x in random_list:
                x = random.randint(0, len(self.coco["images"]) - 1)
            random_list.append(x)

            if i < len_validation:
                validation["images"] += [self.coco["images"][x]]
                img_id_val.append(self.coco["images"][x]["id"])
                list_dir_validation.append(self.coco["images"][x]["file_name"])
                id_train.append(self.coco["images"][x]["id"])
            else:
                test["images"] += [self.coco["images"][x]]
                img_id_test.append(self.coco["images"][x]["id"])
                list_dir_test.append(self.coco["images"][x]["file_name"])
                id_train.append(self.coco["images"][x]["id"])

        for img in tqdm(self.coco["images"]):
            if img["id"] not in id_train:
                train["images"] += [img]
                list_dir_train.append(img["file_name"])
                img_id_train.append(img["id"])

        for ann in tqdm(self.coco["annotations"]):
            if ann["image_id"] in img_id_train:
                train["annotations"] += [ann]
            if ann["image_id"] in img_id_test:
                test["annotations"] += [ann]
            if ann["image_id"] in img_id_val:
                validation["annotations"] += [ann]

        os.makedirs(exit_path + "/train/annotations"), os.makedirs(exit_path + "/train/images")
        p = PreProcess(test)
        if len_test != 0:
            os.makedirs(exit_path + "/test/images"), os.makedirs(exit_path + "/test/annotations")

            for image in list_dir_test:
                shutil.copy(
                    image_path + f"/{image}",
                    exit_path + "/test/images" + f"/{image}",
                )
            p.set_unique_annotation_id(first_id=1)
            p.set_unique_image_id(first_id=1)
            p.save_coco_file(directory=exit_path + "/test/annotations/", file_name="test")

        for image in list_dir_train:
            shutil.copy(
                image_path + f"/{image}",
                exit_path + "/train/images" + f"/{image}",
            )
        p = PreProcess(train)
        p.set_unique_annotation_id(first_id=1)
        p.set_unique_image_id(first_id=1)
        p.save_coco_file(directory=exit_path + "/train/annotations/", file_name="train")

        if len_validation != 0:
            os.makedirs(exit_path + "/validation/images"), os.makedirs(exit_path + "/validation/annotations")

            for image in list_dir_validation:
                shutil.copy(
                    image_path + f"/{image}",
                    exit_path + "/validation/images" + f"/{image}",
                )
            p = PreProcess(validation)
            p.set_unique_annotation_id(first_id=1)
            p.set_unique_image_id(first_id=1)
            p.save_coco_file(directory=exit_path + "/validation/annotations/", file_name="validation")
        logging.info("Data split Done!")
        logging.info(f" Data saved to {exit_path}")

        return train, test, validation

    def unite_classes(self, class_names: list, new_class_name: str):
        """
        This function unite given classes in a class. And return new coco json file

            @param class_names: List of class names
            @param new_class_name: Name of class name to be created
            @return:
        """
        classes: list = []
        class_id: list = []

        for cat in self.coco["categories"]:
            if cat["name"] not in class_names:
                classes.append(cat)
            else:
                class_id.append(cat["id"])

        max_id = self.coco["categories"][-1]["id"]

        # get unique id
        class_id = list(set(class_id))

        # unite classes in one class
        classes += [{"id": f"{max_id + 1}", "name": f"{new_class_name}", "supercategory": ""}]

        # set new class id
        for ann in self.coco["annotations"]:
            if ann["category_id"] in class_id:
                ann["category_id"] = f"{max_id + 1}"

        # change categories
        self.coco["categories"] = classes

        # set unique id
        p = PreProcess(self.coco)
        p.set_unique_class_id(first_id=0, back_grounds=True)

    @staticmethod
    def image_split(image_path: str, test_percent: int, val_percent: int):
        """
        This function split images according to test validation percent into a new folder
            @param image_path: Path of folder that obtain images
            @param test_percent: Image split test percent
            @param val_percent: Image split val percent
        """

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        random_list: list = []

        parent_path = os.path.abspath(os.path.join(image_path, os.pardir))
        list_images = os.listdir(image_path)

        len_images = len(list_images)
        len_test = int(len_images * test_percent / 100)
        len_validation = int(len_images * val_percent / 100)

        os.makedirs(parent_path + f"/train-{time}"), os.makedirs(parent_path + f"/test-{time}")
        os.makedirs(parent_path + f"/val-{time}")
        train_path, test_path, val_path = (
            parent_path + f"/train-{time}",
            parent_path + f"/test-{time}",
            parent_path + f"/val-{time}",
        )

        for i in tqdm(range(len_test + len_validation)):
            x = random.randint(0, (len_test + len_validation))
            while x in random_list:
                x = random.randint(0, len(list_images) - 1)
            random_list.append(x)

            if i < len_validation:
                shutil.copy(image_path + f"/{list_images[x]}", val_path + f"/{list_images[x]}")
                list_images.remove(list_images[x])
            else:
                shutil.copy(image_path + f"/{list_images[x]}", test_path + f"/{list_images[x]}")
                list_images.remove(list_images[x])

        for image in list_images:
            shutil.copy(image_path + f"/{image}", train_path + f"/{image}")

    def reduce_class(self, img_count: int):
        """
        This function reduce image count according to given integer parameter.
        It sorts image by annotation size and pick first "img_count" images.
            @param img_count: Max image count
        """

        ann_info: dict = {}
        image_id: list = []
        image_list: list = []
        ann_list: list = []

        for ann in self.coco["annotations"]:
            if ann["category_id"] not in list(ann_info.keys()):
                ann_info[ann["category_id"]] = {}

        for ann in self.coco["annotations"]:
            for elem in ann_info:
                if elem == ann["category_id"]:
                    if ann["image_id"] not in ann_info[elem]:
                        ann_info[elem][ann["image_id"]] = 1
                    else:
                        ann_info[elem][ann["image_id"]] += 1

        for key, _ in ann_info.items():
            sort_list = sorted(ann_info[key].items(), key=lambda item: item[1])
            sort_list.reverse()
            for x in range(0, img_count, 1):
                image_id.append(sort_list[x][0])

        set(image_id)

        for image in self.coco["images"]:
            if image["id"] in image_id:
                image_list.append(image)

        for ann in self.coco["annotations"]:
            if ann["image_id"] in image_id:
                ann_list.append(ann)

        self.coco["images"] = image_list
        self.coco["annotations"] = ann_list
