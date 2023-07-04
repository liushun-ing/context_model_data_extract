# 根据时间间隔对history进行分割，得到working periods
import os
from datetime import datetime
from os.path import isdir, join
import xml.etree.ElementTree as ET

import xlwt

from data_count.time_util import get_common_time

model_id = 1
write_excel = None
sheet1 = None
line_index = None
row0 = ["bug report", "id", "Kind", "StructureKind", "StructureHandle", "StartDate"]


def make_dir(directory):
    """
    创建一个目录

    :param directory: 目录地址
    :return: 无返回值，创建目录
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def init_xsl():
    global write_excel
    global sheet1
    global line_index
    global row0
    line_index = 0
    write_excel = xlwt.Workbook()  # 创建工作表
    sheet1 = write_excel.add_sheet(u"Sheet1", cell_overwrite_ok=True)  # 创建sheet
    # 生成第一行
    for i in range(0, len(row0)):
        sheet1.write(line_index, i, row0[i])


def save_xsl(project_name: str, bug_id: str):
    global write_excel
    file_path = os.path.dirname(os.path.realpath(__file__))
    make_dir("04/" + project_name)
    file_name = os.path.join(file_path, "04/" + project_name + "/" + bug_id + ".xls")
    if os.path.exists(file_name):
        os.remove(file_name)
    # 保存文件
    write_excel.save(file_name)


def write_xsl(row: list):
    global line_index
    global sheet1
    global row0
    line_index += 1
    # 生成第一行
    for i in range(0, len(row0)):
        sheet1.write(line_index, i, row[i])


def duration_is_over(date1: str, date2: str):
    time1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
    duration = time2 - time1
    return (duration.seconds + duration.days * 86400) >= 120 * 60


def break_interaction_history(events_nodes: list[ET.Element], bug_id, project_name, p_sheet, p_line_index):
    global model_id
    model_id = 1  # 初始化
    transfer_nodes: list(map) = []
    for node in events_nodes:
        transfer_nodes.append({
            "id": 0,
            "event_kind": node.attrib.get('Kind'),
            "event_structure_kind": node.attrib.get('StructureKind'),
            "event_start_date": get_common_time(node.attrib.get('StartDate')),
            "event_structure_handle": node.attrib.get('StructureHandle')
        })
    transfer_nodes.sort(key=lambda x: x.get('event_start_date'))  # 按照时间升序排列
    c_i, n_i = 0, 1  # current_index next_index
    c_n = transfer_nodes[c_i]  # current_node
    c_n.update({"id": model_id})
    # 然后一个一个的判断
    while n_i < len(transfer_nodes):
        # 之前与前一个node的时间差达到时间间隔，就递增model_id
        if duration_is_over(transfer_nodes[c_i].get('event_start_date'), transfer_nodes[n_i].get('event_start_date')):
            model_id += 1
        n_n = transfer_nodes[n_i]
        n_n.update({"id": model_id})  # 更新当前的node
        c_i = n_i
        n_i += 1  # 进入下一个node
    # 分完组之后，进行过滤event
    fi = 0
    while fi < len(transfer_nodes):
        te = transfer_nodes[fi]
        e_kind = te.get('event_kind')
        e_structure_king = te.get('event_structure_kind')
        if (e_kind == 'selection' or e_kind == 'edit') and e_structure_king == 'java':
            fi += 1
            continue
        else:
            transfer_nodes.pop(fi)
            fi -= 1
        fi += 1
    # 过滤之后，可能存在某些model_id对应的period中一个event也没有了，这是就会多占用一个id，需要进一步调整id
    true_id, fore_id = 0, 0
    for e in transfer_nodes:
        curr_id = e.get("id")
        # 如果当前id不等于上一个id，就需要进入下一个id
        if not curr_id == fore_id:
            fore_id = curr_id
            true_id += 1
        e.update({"id": true_id})
    # 调整好之后，就可以写入文件了
    if len(transfer_nodes) <= 0:
        return -1
    else:
        for en in transfer_nodes:
            write_xsl([bug_id, en.get("id"), en.get("event_kind"), en.get("event_structure_kind"),
                       en.get("event_structure_handle"),
                       en.get("event_start_date")])
        save_xsl(project_name, bug_id)
        last_node = transfer_nodes[len(transfer_nodes) - 1]
        p_sheet.write(p_line_index, 0, bug_id)
        p_sheet.write(p_line_index, 1, last_node.get("id"))
        print("{}'s {} bug has {} working periods".format(project_name, bug_id, last_node.get("id")))
        return 1


path = '../2023_dataset/mylyn_zip'
project_dir_list = os.listdir(path)

total_data_work_excel = xlwt.Workbook()  # 创建工作表
for project in project_dir_list:
    project_path = join(path, project)
    if not isdir(project_path):
        continue
    print('目录:', project, project_path)
    project_sheet = total_data_work_excel.add_sheet(project, cell_overwrite_ok=True)  # 创建sheet
    project_line_index = 0
    project_sheet.write(project_line_index, 0, "bug")
    project_sheet.write(project_line_index, 1, "working periods")
    bug_dir_list = os.listdir(project_path)
    # 进入bug目录
    for bug in sorted(bug_dir_list, key=len):
        xml_counts = 0  # 当前bug的xml文件个数，也就是Interaction Traces个数
        bug_path = join(project_path, bug)
        if not isdir(bug_path):
            continue
        zip_dir_list = os.listdir(bug_path)
        project_line_index += 1
        # 读取到bug_zip
        for bug_zip in zip_dir_list:
            bug_zip_path = join(bug_path, bug_zip)
            if not isdir(bug_zip_path):
                continue
            xml_dir_list = os.listdir(bug_zip_path)
            bug_start_time_list = []
            # 开始读取xml文件
            for xml_file in xml_dir_list:
                if not xml_file.endswith('.xml'):
                    continue
                xml_counts += 1  # 增加traces个数
                if not xml_counts == len(zip_dir_list) / 2:  # 只要最后一个，如果不是直接跳过
                    continue
                init_xsl()
                xml_file_path = join(bug_zip_path, xml_file)
                tree = ET.parse(xml_file_path)
                # 拿到InteractionHistory节点
                root = tree.getroot()
                # 拿到所有的InteractionEvent
                all_events_nodes = root.findall('InteractionEvent')
                result = break_interaction_history(all_events_nodes, bug, project, project_sheet, project_line_index)
                if result == -1:
                    project_line_index -= 1
file_path = os.path.dirname(os.path.realpath(__file__))
file_name = os.path.join(file_path, "04/total_working_data.xls")
if os.path.exists(file_name):
    os.remove(file_name)
# 保存文件
total_data_work_excel.save(file_name)
