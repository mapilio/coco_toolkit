import datetime
import logging
import os
import shutil
from pathlib import Path

from coco_toolkit.helper.preprocess import PreProcess, reader
from coco_toolkit.modules.voc2coco import main


def voc2coco(data_xml_folder_path: str, output_path: str, image_path: str):
    """
    :param data_xml_folder_path: directory of folder that obtain datas in format xml
    :param output_path: directory of folder that created coco json
    :param image_path: Data set's images path
    :return: Coco json file as dictionary and saves coco data set in given output path
    """
    time = str(datetime.datetime.now()).split(".")[0].split()
    time = "-".join(time).replace(":", "-")

    main(data_xml_folder_path, output_path, time)
    json_path = output_path + f"/converted_coco_{time}/annotations/coco.json"
    coco = reader(json_path)
    p = PreProcess(coco)
    p.set_unique_image_id(first_id=1)
    p.set_unique_annotation_id(first_id=1)
    p.set_unique_class_id(first_id=0, back_grounds=True)
    list_dir_img = os.listdir(image_path)
    for image in list_dir_img:
        shutil.copy(
            image_path + f"/{image}",
            output_path + f"/converted_coco_{time}/images/{image}",
        )
    path = Path(json_path)
    p.save_coco_file(directory=str(path.parent.absolute()), file_name="coco")
    logging.getLogger().setLevel(logging.INFO)
    logging.info("coco dataset is ready!")
    logging.info(f"It's saved to {output_path}/converted_coco_{time}")
    return p.coco
