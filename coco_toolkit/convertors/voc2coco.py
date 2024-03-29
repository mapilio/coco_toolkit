import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List
import datetime
import logging
import shutil
from pathlib import Path
from coco_toolkit.helper.preprocess import PreProcess
from tqdm import tqdm


def save_image_id(path_xml: str, out_txt_path: str):
    list_image = os.listdir(path_xml)
    image_names = []
    for img in list_image:
        name = img
        name = name.split(".")[0]
        image_names.append(name)
    with open(f"{out_txt_path}/id.txt", "w") as f:
        for string in image_names:
            f.write(string + "\n")
    return out_txt_path + "/id.txt"


def save_label_txt(path_xml: str, out_txt_path: str):
    list_xml = os.listdir(path_xml)
    class_names: list = []
    for xml in list_xml:
        root = ET.parse(os.path.join(path_xml, xml)).getroot()
        for elem in root:
            if elem.tag == "object":
                for sub_elem in elem:
                    if sub_elem.tag == "name":
                        if sub_elem.text not in class_names:
                            class_names.append(sub_elem.text)
    with open(f"{out_txt_path}/labels.txt", "w") as f:
        for string in class_names:
            f.write(string + "\n")
    with open(f"{out_txt_path}/list.txt", "w") as f:
        for xml in list_xml:
            f.write(path_xml + "/" + xml + "\n")
    return out_txt_path + "/labels.txt", out_txt_path + "/list.txt"


def get_label2id(labels_path: str) -> Dict[str, int]:
    """id is 1 start"""
    with open(labels_path, "r") as f:
        labels_str = f.read().split()
    labels_ids = list(range(1, len(labels_str) + 1))
    return dict(zip(labels_str, labels_ids))


def get_annpaths(
    ann_dir_path: str = None,
    ann_ids_path: str = None,
    ext: str = "",
    annpaths_list_path: str = None,
) -> List[str]:
    # If use annotation paths list
    if annpaths_list_path is not None:
        with open(annpaths_list_path, "r") as f:
            ann_paths = f.read().split()
        return ann_paths

    # If use annotaion ids list
    ext_with_dot = "." + ext if ext != "" else ""
    with open(ann_ids_path, "r") as f:
        ann_ids = f.read().split()
    ann_paths = [os.path.join(ann_dir_path, aid + ext_with_dot) for aid in ann_ids]
    return ann_paths


def get_image_info(annotation_root, extract_num_from_imgid=True):

    path = annotation_root.findtext("path")
    if path is None:
        filename = annotation_root.findtext("filename")
    else:
        filename = os.path.basename(path)
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]

    if extract_num_from_imgid and isinstance(img_id, str):
        img_id = int(re.findall(r"\d+", img_id)[0])

    size = annotation_root.find("size")
    width = int(size.findtext("width"))
    height = int(size.findtext("height"))

    image_info = {
        "file_name": filename,
        "height": height,
        "width": width,
        "id": img_id,
    }
    return image_info


def get_coco_annotation_from_obj(obj, label2id):
    label = obj.findtext("name")
    assert label in label2id, f"Error: {label} is not in label2id !"
    category_id = label2id[label]
    bndbox = obj.find("bndbox")
    xmin = int(float(bndbox.findtext("xmin"))) - 1
    ymin = int(float(bndbox.findtext("ymin"))) - 1
    xmax = int(float(bndbox.findtext("xmax")))
    ymax = int(float(bndbox.findtext("ymax")))
    assert xmax > xmin and ymax > ymin, f"Box size error !: (xmin, ymin, xmax, ymax): {xmin, ymin, xmax, ymax}"
    o_width = xmax - xmin
    o_height = ymax - ymin
    ann = {
        "area": o_width * o_height,
        "iscrowd": 0,
        "bbox": [xmin, ymin, o_width, o_height],
        "category_id": category_id,
        "ignore": 0,
        "segmentation": [],  # This script is not for segmentation
    }
    return ann


def convert_xmls_to_cocojson(
    annotation_paths: List[str],
    label2id: Dict[str, int],
    output_jsonpath: str,
    extract_num_from_imgid: bool = True,
):
    output_json_dict = {
        "images": [],
        "type": "instances",
        "annotations": [],
        "categories": [],
    }
    bnd_id = 1  # START_BOUNDING_BOX_ID, TODO input as args ?
    print("Start converting !")
    for a_path in tqdm(annotation_paths):
        # Read annotation xml
        ann_tree = ET.parse(a_path)
        ann_root = ann_tree.getroot()

        img_info = get_image_info(
            annotation_root=ann_root,
            extract_num_from_imgid=extract_num_from_imgid,
        )
        img_id = img_info["id"]
        output_json_dict["images"].append(img_info)
        count = 1
        for obj in ann_root.findall("object"):
            ann = get_coco_annotation_from_obj(obj=obj, label2id=label2id)
            ann.update({"image_id": img_id, "id": bnd_id})
            output_json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1
            count += 1

    for label, label_id in label2id.items():
        category_info = {
            "supercategory": "none",
            "id": label_id,
            "name": label,
        }
        output_json_dict["categories"].append(category_info)

    with open(output_jsonpath, "w") as f:
        output_json = json.dumps(output_json_dict)
        f.write(output_json)


def main(xml_path, output_path, time):
    parser = argparse.ArgumentParser(description="This script support converting voc format xmls to coco format json")
    parser.add_argument(
        "--ann_dir",
        type=str,
        default=None,
        help="path to annotation files directory. It is not need when use --ann_paths_list",
    )
    parser.add_argument(
        "--ann_ids",
        type=str,
        default=None,
        help="path to annotation files ids list. It is not need when use --ann_paths_list",
    )
    parser.add_argument(
        "--ann_paths_list",
        type=str,
        default=None,
        help="path of annotation paths list. It is not need when use --ann_dir and --ann_ids",
    )
    parser.add_argument("--labels", type=str, default=None, help="path to label list.")
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="path to output json file",
    )
    parser.add_argument(
        "--ext",
        type=str,
        default="",
        help="additional extension of annotation file",
    )
    parser.add_argument(
        "--extract_num_from_imgid",
        action="store_true",
        help="Extract image number from the image filename",
    )
    args = parser.parse_args()
    labes, ann_path_l = save_label_txt(xml_path, output_path)
    label2id = get_label2id(labels_path=labes)
    ann_paths = get_annpaths(
        ann_dir_path=args.ann_dir,
        ann_ids_path=args.ann_ids,
        ext="xml",
        annpaths_list_path=ann_path_l,
    )
    os.makedirs(output_path + f"/converted_coco_{time}/annotations")
    os.makedirs(output_path + f"/converted_coco_{time}/images")

    convert_xmls_to_cocojson(
        annotation_paths=ann_paths,
        label2id=label2id,
        output_jsonpath=output_path + f"/converted_coco_{time}/annotations/coco.json",
        extract_num_from_imgid=args.extract_num_from_imgid,
    )


def voc_to_coco(data_xml_folder_path: str, output_path: str, image_path: str):
    """
    This function return converted coco json file and saves coco data set in given output path
        @param data_xml_folder_path: Directory of folder that obtain datas in format xml
        @param output_path: Directory of folder that created coco json
        @param image_path: Data set's images path
        @return: Converted coco json file as dictionary and saves coco data set in given output path
    """

    time = str(datetime.datetime.now()).split(".")[0].split()
    time = "-".join(time).replace(":", "-")

    main(data_xml_folder_path, output_path, time)
    json_path = output_path + f"/converted_coco_{time}/annotations/coco.json"
    coco = PreProcess.reader(json_path)
    preprocess = PreProcess(coco)
    preprocess.set_unique_image_id(first_id=1)
    preprocess.set_unique_annotation_id(first_id=1)
    preprocess.set_unique_class_id(first_id=0, back_grounds=True)
    list_dir_img = os.listdir(image_path)
    for image in list_dir_img:
        shutil.copy(
            image_path + f"/{image}",
            output_path + f"/converted_coco_{time}/images/{image}",
        )
    path = Path(json_path)
    preprocess.save_coco_file(directory=str(path.parent.absolute()), file_name="coco")
    logging.getLogger().setLevel(logging.INFO)
    logging.info("coco dataset is ready!")
    logging.info(f"It's saved to {output_path}/converted_coco_{time}")
    return preprocess.coco
