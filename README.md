COCO-TOOLKIT
=================
<!--ts-->
- [Introduction](#introduction)
   - [Preprocessing](#preprocessing)
   - [Converter](#converter)
   - [Merge](#merge)
   - [Report](#report)

- [Installation](#installation)
- [Usage](#usage)
    - [Import](#import)
    	- [Preprocess](#preprocess)
        - [Merge](#merge)
        - [Report](#report)
        - [Converter](#converter)
    - [ClassPreProcess](#classpreprocess)
		- [reader](#reader)
		- [set_unique_image_id](#set_unique_image_id)
		- [set_unique_class_id](#set_unique_class_id)
		- [set_unique_annotation_id](#set_unique_annotation_id)
		- [check_id_unique](#check_id_unique)
		- [extrack_data_by_class_name](#extrack_data_by_class_name)
		- [filter_data_by_class_name](#filter_data_by_class_name)
		- [remove_segmentation](#remove_segmentation)
		- [remove_distorted_bbox](#remove_distorted_bbox)
		- [box2segmentation](#box2segmentation)
		- [save_coco_file](#save_coco_file)
		- [remove_duplicate_image_name](#remove_duplicate_image_name)
		- [change_image_file_names](#change_image_file_names)
		- [train_test_validation_split](#train_test_validation_split)
		- [unite_classes](#unite_classes)
		- [image_split](#image_split)
    - [FunctionMerge](#functionmerge)
		- [merge_multiple_cocos](#merge_multiple_cocos)
    - [ClassAnalyzeCategories](#classanalyzecategories)
		- [given_category_count](#given_category_count)	
		- [class_names](#class_names)
		- [total_class_count](#total_class_count)
		- [classes_have_annotations_tuple](#classes_have_annotations_tuple)
		- [plot_class_pie_chart](#plot_class_pie_chart)
		- [images_aspect_ratio](#images_aspect_ratio)
		- [bbox_aspect_ratio](#bbox_aspect_ratio)
		- [class_have_ann_list](#class_have_ann_list)
		- [coco_viewer](#coco_viewer)
	 - [FunctionConverter](#functionconverter)
		- [voc2coco](#voc2coco)	
- [References](#references)

<!--te-->


Introduction
============
Coco-toolkit is a tool for preparing and analyzing object detection data which is coco json format in Python. Tool countains merge, preprocessing, report and converter modules.

### Preprocessing
This class obtain preprocess functions for preparing coco json dataset.

### Converter
This module has converter function which is Pascal voc to coco json.

### Merge
Merge module has multiple coco merge function.
It merges all given coco json file and return all in one output folder.

### Report
Report module has analyze dataset functions. These functions are; return information of data set, plots data set information as pie chart, and integrates data set with coco viewer.

Installation
============
In terminal code run;
```bash

pip install coco-toolkit
```
Usage
============

###  Import
---
#### Preprocess
```bash

from coco_toolkit.helper.preprocess import PreProcess
```

#### Merge
```bash

from coco_toolkit.helper.merge import merge_multiple_cocos
```

#### Report
```bash

from coco_toolkit.helper.report import AnalyzeCategories
```
#### Converter
```bash

from coco_toolkit.convertors.converter import voc2coco
```

### ClassPreProcess
---
##### reader

This function read given coco json file path . It returns coco json file as a dictionary.

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)

```
##### set_unique_image_id
This function set unique image id all images. 

parameter first_id: First image id value

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.set_unique_image_id(first_id=1)
p.coco # Processed coco json file 
```
##### set_unique_class_id
This function set unique category id all categories.

parameter first_id: First image id value
parameter b_grounds: If it's True add backgrounds to categories if there is no background category

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.set_unique_class_id(first_id=1-0, back_grounds=True)
p.coco # Processed coco json file 
```
##### set_unique_annotation_id
This function set unique annotation id all annotations. 

parameter first_id: First image id value

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.set_unique_annotation_id(first_id=0-1)
p.coco # Processed coco json file 
```
##### check_id_unique
This function check annotations, image and category id. If all id are unique return True,
if id not unique return False

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
result = p.check_id_unique() # Return False or True
```

##### extrack_data_by_class_name
This function extrack coco json file according to given list of categories. Saves new coco json data(annotations and images) to given out_path.

parameter categories: List of chosen categories names
parameter image_path: Image path of dataset
parameter out_path: Output directory

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
img_path = "coco_dataset/images"
out_path = os.getcwd()
p = PreProcess(coco)
export_list = ["crosswalk"]
extrack_list = ["crosswalk"] # Category to be extracted from coco data
p.extrack_data_by_class_name(
            categories=export_list, image_path=img_path,
            out_path=out_path
        )
p.coco # Processed coco json file 
```

##### filter_data_by_class_name
This function remove categories by given list of category names. Saves new coco json data(annotations and images) to given out_path.

parameter categories: List of chosen categories names
parameter image_path: Image path of dataset
parameter out_path: Output directory

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
img_path = "coco_dataset/images"
out_path = os.getcwd()
p = PreProcess(coco)
filter_list = ["crosswalk"]
p.filter_data_by_class_name(
            categories=filter_list, image_path=img_path,
            out_path=out_path
        )
p.coco # Processed coco json file 

```
##### remove_segmentation
This function remove segmentations from annotations. Return updated coco json file. If parameter inplace True save updated coco json file to given path.


For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.remove_segmentation()
p.coco # Processed coco json file 

```
##### remove_distorted_bbox
This function remove distorted bbox from annotations. 


For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.remove_distorted_bbox()
p.coco # Processed coco json file 
```
##### box2segmentation
This function create segmentation list from bbox to annotations if there is no segmentation list . 

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.box2segmentation()
p.coco # Processed coco json file 
```
##### save_coco_file
This function save coco json file to given directory + file name.

parameter directory: The directory of coco json file to be saved
parameter file_name: The file name of coco json file to be saved(without extencion)

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
dir_ = os.getcwd()
f_name = "test_save"
p.save_coco_file(directory=dir_, file_name=f_name)
```
##### remove_duplicate_image_name
This function if there is a duplicate image name in coco json file remove duplicate name.

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
p.remove_duplicate_image_name()
p.coco # Processed coco json file 
```
##### change_image_file_names
This function change images' file name and copy them to a new folder. If inplace True save coco json file to new
folder.

parameter image_path: Path of folder that contains dataset images
parameter inplace: If it's True create new coco json file to given directory

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
img_path = "coco_dataset/images"
p.change_image_file_names(image_path=img_path, inplace=True)
p.coco # Processed coco json file 
```
##### train_test_validation_split
This function split data set to train, test and validation according to given split percent. Return train,test and validation coco json file.

parameter image_path: Path of folder that contains dataset images
parameter test_percent: Test split percent
parameter validation_percent: Validation split percent
parameter out_path: Output path

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
img_path = "coco_dataset/images"
output_path = "/home/documents"

train,test,validation = p.train_test_validation_split(image_path=img_path, test_percent=20, validation_percent=15, out_path=output_path)
```
##### unite_classes
This function unite given classes in a class. 

 parameter class_names: List of class names
 parameter new_class_name: Name of class name to be created

For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
p = PreProcess(coco)
class_name_list = ["stop", "trafficlight", "crosswalk"]
new_class_name = "Road Sign"
p.unite_classes(class_names=class_name_list, new_class_name=new_class_name)
p.coco # Processed coco json file 
```
##### image_split
This functon split image dataand  create train test validation image folders.

 parameter image_path: Path of folder that obtain images
 parameter test_percent: Image split test percent
 parameter val_percent: Image split val percent
 
 For example:
```bash
img_path = "coco_dataset/images"
PreProcess.image_split(image_path=img_path, test_percent=15, val_percent=25)
```
### FunctionMerge
---
##### merge_multiple_cocos
This function merge all given coco datasets and save given directory.

parameter args: It contains lists in index 0 json path and index 1 images path. For example
[json_path_1, image path_1], [json_path_2, image path_2] 
parameter merge_path: Path of output folder directory
parameter first_id: Value of first id
parameter visualizer: if it's True visualize categories with pie chart

 For example:
```bash
path_1 = "coco_dataset_1/annotations/coco.json"
img_1 = "coco_dataset_1/images"
path_2 = "coco_dataset/annotations/coco.json"
img_2 = "coco_dataset/images"
merge_path = "test_merge"
args = [path_1, img_1], [path_2, img_2]
merge = merge_multiple_cocos(*args, merge_path=merge_path, first_id=100000, visualizer=True)
```
### ClassAnalyzeCategories
---
##### given_category_count
This function return count of given category annotations.

parameter category: Category name

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
count = AnalyzeCategories(coco).given_category_count("crosswalk")
```
##### class_names
This function return list of class names .

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
class_name_list = AnalyzeCategories(coco).class_names()
```
##### total_class_count
This function return class count.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
count = AnalyzeCategories(coco).total_class_count()
```

##### classes_have_annotations_tuple
This function return class names as  tuple that has annotation.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
tuple = AnalyzeCategories(coco).classes_have_annotations_tuple()
```
##### plot_class_pie_chart
This function save class information  pie chart as png and if parameter visualize True visualize pie chart

parameter visualize: If it's True visualize pie chart.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
AnalyzeCategories(coco).plot_class_pie_chart(visualize=True)
```
##### images_aspect_ratio
This function return image dataset aspect ratio as dictionary.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
info_dictionary = AnalyzeCategories(coco).images_aspect_ratio()
```

##### bbox_aspect_ratio
This function return dictionary of  bbox aspect ratio information. It returns  three aspect
ratio which is has max count.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
info_dictionary = AnalyzeCategories(coco).bbox_aspect_ratio()
```

##### class_have_ann_list
This function return list of  class names that has annotation.

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
coco = reader(path)
list_class_names = AnalyzeCategories(coco).class_have_ann_list()
```

##### coco_viewer
This function open coco viewer .

 For example:
```bash
path = "coco_dataset/annotations/coco.json"
img_path = "coco_dataset/images"
AnalyzeCategories.coco_viewer(image_path=img_path, json_path=path)
```

### FunctionConverter
---
##### voc2coco
This fuction convert poscal voc format to coco json format. And return coco  json file as dictionary and saves coco data set in given output path.

parameter data_xml_folder_path: directory of folder that obtain datas in format xml
parameter output_path: directory of folder that created coco json
parameter image_path: Data set's images path

```bash
path_xml = "coco_dataset/annotations_xml"
img_path = "xml_dataset/images"
output_path = "/home/documents"
voc2coco(data_xml_folder_path=path_xml, output_path=output_path, image_path=img_path)
```
References
============
https://github.com/trsvchn/coco-viewer

https://github.com/yukkyo/voc2coco

`

## Check before PR 

```bash
black . --config pyproject.toml
isort .
pre-commit run --all-files


```