import datetime
import logging
import os
import shutil
from pathlib import Path

from coco_toolkit.helper.preprocess import PreProcess
from coco_toolkit.convertors.voc2coco import main


def voc2coco(data_xml_folder_path: str, output_path: str, image_path: str):
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
