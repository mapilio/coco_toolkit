import os
import unittest
from coco_toolkit.convertors.voc2coco import voc_to_coco
from coco_toolkit.convertors.coco2yolo import coco_to_yolo
from coco_toolkit.helper.merge import merge_multiple_cocos
from coco_toolkit.helper.preprocess import PreProcess
from coco_toolkit.helper.report import AnalyzeCategories


class TestCocoMergeTool(unittest.TestCase):
    def test_set_unique_image_id(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        start_id = 10
        p.set_unique_image_id(first_id=start_id)
        result = p.coco["images"][0]["id"]
        result_1 = p.coco["images"][2]["id"]
        result_2 = p.coco["images"][4]["id"]
        self.assertEqual(result, start_id)
        self.assertEqual(result_1, start_id + 2)
        self.assertEqual(result_2, start_id + 4)

    def test_set_unique_class_id(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        start_id = 0
        p.set_unique_class_id(first_id=start_id, back_grounds=True)
        result = p.coco["categories"][0]["id"]
        result_1 = p.coco["categories"][1]["id"]
        self.assertEqual(result, start_id)
        self.assertEqual(result_1, start_id + 1)

    def test_set_unique_annotation_id(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        start_id = 6
        p.set_unique_annotation_id(first_id=start_id)
        result = p.coco["annotations"][0]["id"]
        result_1 = p.coco["annotations"][2]["id"]
        result_2 = p.coco["annotations"][4]["id"]
        self.assertEqual(result, start_id)
        self.assertEqual(result_1, start_id + 2)
        self.assertEqual(result_2, start_id + 4)

    def test_check_id_unique(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        result = p.check_id_unique()
        self.assertTrue(result)

    def test_extrack_data_by_class_name(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        img_path = "tests/coco_dataset/images"
        out_path = os.getcwd()
        p = PreProcess(coco)
        export_list = ["crosswalk"]
        p.extrack_data_by_class_name(categories=export_list, image_path=img_path, out_path=out_path)
        result = AnalyzeCategories(p.coco).class_have_ann_list()
        self.assertEqual(result, export_list)

    def test_filter_data_by_class_name(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        img_path = "tests/coco_dataset/images"
        out_path = os.getcwd()
        p = PreProcess(coco)
        filter_list = ["crosswalk"]
        p.filter_data_by_class_name(categories=filter_list, image_path=img_path, out_path=out_path)
        result = AnalyzeCategories(p.coco).class_have_ann_list()
        self.assertEqual(result, ["stop", "trafficlight"])

    def test_remove_segmentation(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        p.remove_segmentation()
        result = p.coco["annotations"][0]["segmentation"]
        result_1 = p.coco["annotations"][7]["segmentation"]
        self.assertEqual(result, {})
        self.assertEqual(result_1, {})

    def test_box2segmentation(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        p.remove_segmentation()
        p.box2segmentation()
        result = p.coco["annotations"][0]["segmentation"]
        self.assertEqual(result, [[147, 70, 147, 173, 288, 173, 288, 70]])

    def test_change_image_file_names(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        img_path = "tests/coco_dataset/images"
        image_list = os.listdir(img_path)
        name = coco["images"][0]["file_name"]
        p.change_image_file_names(image_path=img_path, inplace=True)
        if name in image_list:
            result = True
        else:
            result = False
        self.assertTrue(result)

    def test_remove_duplicate_image_names(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        p.remove_duplicate_image_name()
        len_image = 10
        result = len(p.coco["images"])
        self.assertEqual(result, len_image)

    def test_given_category_count(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        result = AnalyzeCategories(coco).given_category_count("crosswalk")
        self.assertEqual(result, 4)

    def test_class_names(self):
        path = "tests/coco_dataset/annotations/coco.json"
        class_names = ["Background", "stop", "trafficlight", "crosswalk"]
        coco = PreProcess.reader(path)
        result = AnalyzeCategories(coco).class_names()
        self.assertEqual(result, class_names)

    def test_total_class(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        result = AnalyzeCategories(coco).total_class_count()
        total_class = 4
        self.assertEqual(result, total_class)

    def test_classes_have_annotations_tuple(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        have_anno_class = ("stop", "trafficlight", "crosswalk")
        result = AnalyzeCategories(coco).classes_have_annotations_tuple()
        self.assertEqual(result, have_anno_class)

    def test_aspect_ratio(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        aspect_ratio_dict = {
            "100:67": 1,
            "16:9": 1,
            "200:133": 1,
            "3:4": 2,
            "400:267": 1,
            "400:301": 2,
            "40:27": 1,
            "4:3": 1,
        }
        result = AnalyzeCategories(coco).images_aspect_ratio()
        self.assertEqual(result, aspect_ratio_dict)

    def test_merge_multiple_cocos(self):
        path_1 = "tests/coco_dataset_1/annotations/coco.json"
        img_1 = "tests/coco_dataset_1/images"
        path_2 = "tests/coco_dataset/annotations/coco.json"
        img_2 = "tests/coco_dataset/images"
        merge_path = "test_merge"
        len_annotations = 51
        len_images = 20
        len_categories = 7
        args = [path_1, img_1], [path_2, img_2]
        merge = merge_multiple_cocos(*args, merge_path=merge_path, first_id=100000, visualizer=False)
        result = len(merge["annotations"])
        result_1 = len(merge["images"])
        result_2 = len(merge["categories"])

        self.assertEqual(result, len_annotations)
        self.assertEqual(result_1, len_images)
        self.assertEqual(result_2, len_categories)

    def test_remove_distorted_bbox(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        p.remove_distorted_bbox()
        count = []
        for ann in coco["annotations"]:
            if ann["bbox"] != {}:
                count.append(0)
        result = len(count)
        len_anno = 13
        self.assertEqual(result, len_anno)

    def test_unite_classes(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        class_name_list = ["stop", "trafficlight", "crosswalk"]
        new_class_name = "Road Sign"
        p.unite_classes(class_names=class_name_list, new_class_name=new_class_name)

        result = True
        for cat in p.coco["categories"]:
            if cat["name"] in class_name_list:
                result = False

        self.assertTrue(result)

    def test_save_coco_file(self):
        path = "tests/coco_dataset/annotations/coco.json"
        coco = PreProcess.reader(path)
        p = PreProcess(coco)
        dir_ = os.getcwd()
        f_name = "test_save"
        p.save_coco_file(directory=dir_, file_name=f_name)

        result = False
        if os.path.exists(os.path.join(dir_, f_name + ".json")):
            result = True

        self.assertTrue(result)


class TestCocoConvertorsTool(unittest.TestCase):
    # TODO
    def test_coco2yolo(self):
        pass


if __name__ == "__main__":
    unittest.main()
