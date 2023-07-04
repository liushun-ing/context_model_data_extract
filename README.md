# 2023 Code Context Model

## 2023代码上下文模型数据收集项目

实验共考虑五个项目:PDE,Mylyn,Platform,ECF,MDT

其中MDT项目经过爬虫后，没有采集到数据，后面的数据处理不再考虑，实际只有四个项目，即
`PDE`,`Mylyn`,`Platform`,`ECF`

- /2023_dataset: 用来保存2023收集到的bug的数据，包含`mylyn_zip`和`patch_txt`两个文件夹，分别保存bug interactionHistory的xml文件和附加的代码说明

- /bugzilla_data: 用来记录四个项目爬虫的地址，和网页bug数目和实际采集数目等信息

- /data_extract: 使用bugzilla采集数据，保存xml文件

- /data_count: 用来进行数据的统计等，比如01解压zip文件，得到xml文件，02统计开始时间和event个数等、03过滤event,04统计有效event数目

- /model_formation: Code Context Model Formation，根据时间间隔分割working
  periods，得到分割后的时间片数据，保存在xls文件中，其中02指的是对resource事件也进行数据的收集工作，可能存在访问代码元素事件