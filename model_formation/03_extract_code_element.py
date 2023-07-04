# 提取code element和最早最晚的startDate
import os
from os.path import isdir, join
import numpy as np
import xlrd
import xlwt
from collections import Counter

write_excel = None
new_sheet = None
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
    write_excel = xlwt.Workbook()  # 创建工作表
    global new_sheet
    global line_index
    global row0
    line_index = 0
    new_sheet = write_excel.add_sheet('sheet1', cell_overwrite_ok=True)  # 创建sheet
    # 生成第一行
    for i in range(0, len(row0)):
        new_sheet.write(line_index, i, row0[i])


def save_xsl(xls_file_path):
    global write_excel
    if os.path.exists(xls_file_path):
        os.remove(xls_file_path)
    # 保存文件
    write_excel.save(xls_file_path)


def write_xsl(row: list):
    global line_index
    global new_sheet
    global row0
    line_index += 1
    # 生成第一行
    for i in range(0, len(row0)):
        new_sheet.write(line_index, i, row[i])


def read_xls_excel(url, index=1):
    """
    读取xls格式文件
    参数：
        url:文件路径
        index：工作表序号（第几个工作表，传入参数从1开始数）
    返回：
        data:表格中的数据
    """
    # 打开指定的工作簿
    workbook = xlrd.open_workbook(url)
    # 获取工作簿中的所有表格
    sheets = workbook.sheet_names()
    # 获取工作簿中所有表格中的的第 index 个表格
    worksheet = workbook.sheet_by_name(sheets[index - 1])
    # 定义列表存储表格数据
    data = []
    # 遍历每一行数据
    for i in range(1, worksheet.nrows):
        # 定义表格存储每一行数据
        da = []
        # 遍历每一列数据
        for j in range(0, worksheet.ncols):
            # 将行数据存储到da列表
            da.append(int(float(worksheet.cell_value(i, j))) if j == 1 else worksheet.cell_value(i, j))
        # 存储每一行数据
        data.append(da)
    # 返回数据
    return data


file_path = os.path.dirname(os.path.realpath(__file__))
file_dir_list = os.listdir(file_path)
for index_dir in file_dir_list:
    # 进入01，02，03，04文件夹
    if index_dir not in ['01', '02', '03', '04']:
        continue
    index_path = join(file_path, index_dir)
    print("current project:" + index_dir)
    project_list = os.listdir(index_path)
    total_data_work_excel = xlwt.Workbook()  # 创建工作表
    total_data_work_excel_1 = xlwt.Workbook()  # 创建工作表
    # 进入项目目录
    for project_dir in project_list:
        if project_dir not in ['PDE', 'Mylyn', 'Platform', 'ECF']:
            continue
        make_dir("code_elements/" + index_dir + '/' + project_dir)
        project_path = join(index_path, project_dir)
        xls_list = os.listdir(project_path)
        # 用来统计bug的working period信息
        project_sheet = total_data_work_excel.add_sheet(project_dir, cell_overwrite_ok=True)  # 创建sheet
        project_line_index = 0
        project_sheet.write(project_line_index, 0, "bug")
        project_sheet.write(project_line_index, 1, "working periods")
        # 用来统计每个working period的event个数信息
        project_sheet_1 = total_data_work_excel_1.add_sheet(project_dir, cell_overwrite_ok=True)  # 创建sheet
        project_line_index_1 = 0
        project_sheet_1.write(project_line_index_1, 0, "bug")
        project_sheet_1.write(project_line_index_1, 1, "working period id")
        project_sheet_1.write(project_line_index_1, 2, "contain events")

        for xls_file in sorted(xls_list, key=len):
            init_xsl()  # 初始化xls写文件
            xls_path = join(project_path, xls_file)
            xls_data = read_xls_excel(xls_path)  # 拿到所有的data
            # 过滤所有重复，无效的event,并记录最早和最晚的startDate
            a = np.array(xls_data)
            # 提取第一个和最后一个event的startDate
            all_start_date = a[:, -1]
            first_date, last_date = min(all_start_date), max(all_start_date)
            con = []
            handles = []  # 用来保存handles
            for line in xls_data:
                # 有效且不重复才返回True,留下来
                if line[4].endswith('.java') or line[4].find('.java[') > -1:
                    if line[4] in handles:
                        con.append(False)
                    else:
                        handles.append(line[4])
                        con.append(True)
                else:
                    con.append(False)
            effective_data = a[con]  # 得到有效的event
            # 写入新的文件
            # 过滤之后，可能存在某些model_id对应的period中一个event也没有了，这是就会多占用一个id，需要进一步调整id
            true_id, fore_id = 0, 0
            for e in effective_data:
                curr_id = e[1]
                # 如果当前id不等于上一个id，就需要进入下一个id
                if not curr_id == fore_id:
                    fore_id = curr_id
                    true_id += 1
                e[1] = true_id
            # 调整好之后，就可以写入文件了
            if len(effective_data) <= 0:
                continue
            else:
                for en in effective_data:
                    write_xsl(en)
                write_xsl(['', '', '', '', '', first_date])  # 最后写入两个时间
                write_xsl(['', '', '', '', '', last_date])
                xls_file_name = os.path.join(file_path,
                                             "code_elements/" + index_dir + '/' + project_dir + "/" + xls_file + ".xls")
                save_xsl(xls_file_name)
                # 统计work period所有数据
                project_line_index += 1
                last_node = effective_data[len(effective_data) - 1]
                project_sheet.write(project_line_index, 0, xls_file)
                project_sheet.write(project_line_index, 1, last_node[1])
                print("{}'s {} bug has {} working periods".format(project_dir, xls_file, last_node[1]))
                # 统计每个working period的event个数信息
                all_ids = effective_data[:, 1]
                id_groups = Counter(all_ids)
                for key_id in id_groups.keys():
                    project_line_index_1 += 1
                    project_sheet_1.write(project_line_index_1, 0, xls_file)
                    project_sheet_1.write(project_line_index_1, 1, key_id)
                    project_sheet_1.write(project_line_index_1, 2, id_groups.get(key_id))
    # 保存文件
    total_file_name = os.path.join(file_path, "code_elements/" + index_dir + "/total_working_data.xls")
    if os.path.exists(total_file_name):
        os.remove(total_file_name)
    total_data_work_excel.save(total_file_name)
    # 保存event统计文件
    total_file_name_1 = os.path.join(file_path, "code_elements/" + index_dir + "/working_periods_event_count.xls")
    if os.path.exists(total_file_name_1):
        os.remove(total_file_name_1)
    total_data_work_excel_1.save(total_file_name_1)
