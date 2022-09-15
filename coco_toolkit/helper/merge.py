import datetime
import os
import shutil

from tqdm import tqdm

from coco_toolkit.helper.preprocess import PreProcess
from coco_toolkit.helper.report import AnalyzeCategories


def merge_multiple_cocos(*args: list, merge_path: str, first_id: int, visualizer: bool):
    """
    This function merge all given datasets and save to a new folder with annotation and images.
        @param args:  This parameter contains lists which has two indexes.These lists contain json path
        information in index 0 and images path information in index 1. For example;
        args = [json_path_1, image path_1], [json_path_2, image path_2] ...
        And call it as *args(merge_multiple_cocos(*args,..).
        @param merge_path: Path of output folder directory
        @param first_id: Value of first id
        @param visualizer: If it's True visualize categories with pie chart
        @return:  Merge data and save to given directory
    """
    merged = {
        "licenses": [],
        "info": {},
        "categories": [],
        "images": [],
        "annotations": [],
    }
    categories: list = []
    class_names: list = []
    list_dir: list = []

    time = str(datetime.datetime.now()).split(".")[0].split()
    time = "-".join(time).replace(":", "-")

    merged_path_ann = merge_path + f"/merge_folder_{time}/annotations"
    merged_path_img = merge_path + f"/merge_folder_{time}/images"
    os.makedirs(merged_path_ann), os.makedirs(merged_path_img)

    for index, path in enumerate(tqdm(args)):
        json_path = path[0]
        image_path = path[1]
        coco = PreProcess.reader(json_path)
        preprocess = PreProcess(coco)
        preprocess.check_id_unique()
        preprocess.set_unique_image_id(first_id=first_id * (index + 1))
        preprocess.set_unique_annotation_id(first_id=first_id * (index + 1))

        list_dir.append(os.listdir(image_path))

        merged["images"] += preprocess.coco["images"]
        merged["annotations"] += preprocess.coco["annotations"]

        if index == 0:
            merged["categories"] += preprocess.coco["categories"]
            if "licenses" in preprocess.coco:
                merged["licenses"] = preprocess.coco["licenses"]
            if "info" in preprocess.coco:
                merged["info"] = preprocess.coco["info"]

            class_names = [cat["name"] for cat in preprocess.coco["categories"]]

        else:
            for cat in preprocess.coco["categories"]:
                if cat["name"] not in class_names:
                    class_names.append(cat["name"])
                    categories.append(cat)

        if categories:
            merged["categories"] += categories
            categories = []

        for image in list_dir[0]:
            shutil.copy(image_path + f"/{image}", merged_path_img + f"/{image}")
        list_dir = []

    preprocess = PreProcess(merged)
    preprocess.set_unique_class_id(first_id=0, back_grounds=True)
    preprocess.save_coco_file(directory=merged_path_ann, file_name="merge")
    a = AnalyzeCategories(preprocess.coco)
    a.total_class_count()
    a.plot_class_pie_chart(visualizer)
    return preprocess.coco
