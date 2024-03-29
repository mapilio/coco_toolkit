import logging
import math
import os

import matplotlib.pyplot as plt

from coco_toolkit.modules.coco_viewer.cocoviewer import cocoviewer


class AnalyzeCategories:
    def __init__(self, coco: any):
        """
        :param coco: Coco json file
        """
        self.coco = coco.copy()

    def plot_category_destinations(self):

        categories = {category["id"]: category["name"] for category in self.coco["categories"]}
        category_destinations = {category_id: [] for category_id in categories}
        for annotation in self.coco["annotations"]:
            category_id = annotation["category_id"]
            image_id = annotation["image_id"]
            image_info = next((image for image in self.coco["images"] if image["id"] == image_id), None)
            if image_info:
                category_destinations[category_id].append((image_info["file_name"], annotation["bbox"]))
        for category_id, destination in category_destinations.items():
            category_name = categories[category_id]
            fig, ax = plt.subplots()
            for image_filename, bbox in destination:
                ax.text(bbox[0], bbox[1], image_filename, fontsize=8, color="white",
                        bbox=dict(facecolor='red', alpha=0.5))
            ax.set_xlim([0, 1000])
            ax.set_ylim([0, 1000])
            ax.set_title(f"Category: {category_name}")
            plt.savefig(f"tests/output/{category_name}")
            plt.close()

    def get_class_info(self):
        class_id = {}
        info_class = {}
        info_class_not_zero = {}
        for cat in self.coco["categories"]:
            if cat["name"] not in class_id:
                class_id[cat["name"]] = cat["id"]
        for key, value in class_id.items():
            count = 0
            for ann in self.coco["annotations"]:
                if ann["category_id"] == value:
                    count += 1
                else:
                    continue
            info_class[key] = int(count)

        for key, value in info_class.items():
            if value != 0:
                info_class_not_zero[key] = value

        return info_class, info_class_not_zero, class_id

    def given_category_count(self, category):
        """
        :param category: Category name
        :return: Return count of given category.
        """
        category_info, _, _ = AnalyzeCategories.get_class_info(self)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("{} count =%s".format(category), category_info[category])
        return category_info[category]

    def class_names(self):
        """
        :return: List of class names
        """
        _, _, unique = AnalyzeCategories.get_class_info(self)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("class names =%s", list(unique.keys()))
        return list(unique.keys())

    def total_class_count(self):
        """
        :return: Total class count
        """
        _, _, unique = AnalyzeCategories.get_class_info(self)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("total class =%s", len(unique))
        return len(unique)

    def classes_have_annotations_tuple(self):
        """
        :return: Return class names that has annotation info
        """
        _, not_zero, _ = AnalyzeCategories.get_class_info(self)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("class names =%s", tuple(not_zero.keys()))
        return tuple(not_zero.keys())

    def plot_class_pie_chart(self, visualize: bool):
        _, data, total = AnalyzeCategories.get_class_info(self)
        plt.figure(figsize=(15, 15))
        plt.pie(
            list(data.values()),
            labels=list(data.keys()),
            autopct="%1.1f%%",
            rotatelabels=90,
        )
        plt.legend(loc="lower right")
        plt.title("Pie Chart Categories", fontsize=40)
        plt.text(
            1.1,
            1.1,
            f" Class names that has annotations : {len(data)}",
            fontsize=25,
            color="r",
            horizontalalignment="right",
        )
        plt.savefig("Class_Report.png")
        if visualize:
            plt.show()

    def images_aspect_ratio(self):
        """
        :return: Return dictionary of  images aspect ratio information
        """
        aspect_ratio_dict = {}
        list_ratios = []
        for img in self.coco["images"]:
            w = img["width"]
            h = img["height"]
            gcd = math.gcd(w, h)
            w = int(w / gcd)
            h = int(h / gcd)
            aspect_r = "{}:{}".format(w, h)
            if aspect_r in list_ratios:
                aspect_ratio_dict[aspect_r] = aspect_ratio_dict[aspect_r] + 1
            else:
                aspect_ratio_dict[aspect_r] = 1
                list_ratios.append(aspect_r)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("image aspect ratio = %s", aspect_ratio_dict)
        return aspect_ratio_dict

    def bbox_aspect_ratio(self):
        """
        :return: Return dictionary of  bbox aspect ratio information of aspect ratio that three aspect
         ratio has max count

        """
        aspect_ratio_dict = {}
        list_ratios = []

        for ann in self.coco["annotations"]:
            x1, y1, x2, y2 = (
                ann["bbox"][0],
                ann["bbox"][1],
                ann["bbox"][2],
                ann["bbox"][3],
            )
            w = int(x1 - x2)
            h = int(y1 - y2)
            ratio = round(w / h, 1)
            if ratio >= 1:
                w = ratio
                h = 1
            else:
                w = 10
                h = ratio * 10
            aspect_r = "{}:{}".format(w, h)
            if aspect_r in list_ratios:
                aspect_ratio_dict[aspect_r] = aspect_ratio_dict[aspect_r] + 1
            else:
                aspect_ratio_dict[aspect_r] = 1
                list_ratios.append(aspect_r)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("bbox aspect ratio = %s", list(sorted(aspect_ratio_dict.items(), key=lambda item: item[1]))[-3::])
        return list(sorted(aspect_ratio_dict.items(), key=lambda item: item[1]))[-3::]

    @staticmethod
    def coco_viewer(image_path, json_path):
        return cocoviewer(image_path, json_path)

    def class_have_ann_list(self):
        """
        :return: Return class names that has annotation info
        """
        _, not_zero, _ = AnalyzeCategories.get_class_info(self)
        logging.getLogger().setLevel(logging.INFO)
        logging.info("class names = %s", list(not_zero.keys()))
        return list(not_zero.keys())
