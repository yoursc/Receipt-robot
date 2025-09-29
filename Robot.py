import re

from rich.console import Console
from pathlib import Path

# 工作空间路径
CONF_WORK_SPACE = "D:\\WorkSpace\\单据扫描\\作业单"
# 编号白名单，不在名单上的文件将被忽略
CONF_CAR_LIST_IN = ['0000',
                    '1010',
                    '1001', '1008',
                    '1003', '1005',
                    '1015',
                    '2001', '2002', '2003', '2005'
                    ]
CONF_CAR_LIST_OUT = ['刘永杰', '李新伟', '康菊会']

# 全局变量
# 临时文件路径
WORK_TMP = ""
CAR_LIST = CONF_CAR_LIST_IN + CONF_CAR_LIST_OUT
ERR_FLAG = 0

console = Console()


def check_base_dir_path():
    """
    检查并验证工作目录及其子目录结构是否符合要求。

    该函数会检查以下目录是否存在：
    1. 主工作目录（CONF_WORK_SPACE）
    2. "待整理"子目录
    3. 配置中指定的车辆子目录（CONF_CAR_LIST_IN 和 CONF_CAR_LIST_OUT）

    Raises:
        ValueError: 如果主工作目录不存在或检查过程中发现任何缺失目录（ERR_FLAG > 0）
    """

    global CONF_WORK_SPACE, CAR_LIST, ERR_FLAG
    console.log("[green]检查工作目录")
    # 检查工作目录是否存在
    if not Path(CONF_WORK_SPACE).exists():
        raise ValueError("工作目录不存在")
    # 检查导入目录是否存在
    check_dir = Path(CONF_WORK_SPACE, "待整理")
    if not check_dir.exists():
        console.log(f"[red]输入目录{check_dir}不存在")
        ERR_FLAG += 1
    # 检查车辆子目录是否存在
    for item in CONF_CAR_LIST_IN:
        out_dir = Path(CONF_WORK_SPACE, item)
        if not out_dir.exists():
            console.log(f"[red]输出目录{out_dir}不存在")
            ERR_FLAG += 1
    for item in CONF_CAR_LIST_OUT:
        out_dir = Path(CONF_WORK_SPACE, '0000', item)
        if not out_dir.exists():
            console.log(f"[red]输出目录{out_dir}不存在")
            ERR_FLAG += 1
    console.log("检查工作目录:完成")
    if ERR_FLAG > 0:
        raise ValueError("有未解决的错误，程序停止运行")


def check_file_duplication():
    global ERR_FLAG
    console.log("[green]检查文件重复")
    # e.g. 20231231-1001-1234567
    reg = r'\d{8}-\d{4}-\d{7}'
    for f in Path(CONF_WORK_SPACE, "待整理").iterdir():
        # 跳过目录文件
        if Path(f).is_dir():
            continue
        # 检测文件命名是否合规
        if len(f.name) <= 0:
            continue
        if re.match(reg, f.name) is None:
            continue
        # 车辆编号核查
        car_no = f.name.split("-")[1]
        if car_no not in CAR_LIST:
            console.log(f"[yellow]车辆编号不在白名单中: {f.name}")
            continue
        # 本地文件是否重复
        target_file_path = Path(CONF_WORK_SPACE, car_no, f.name)
        if target_file_path.exists():
            # todo 文件对比，若相同，则删除未分类文件
            console.log(f"[red]目标路径文件已存在: {f.name}")
            ERR_FLAG += 1
    console.log("检查文件重复:完成")
    if ERR_FLAG > 0:
        raise ValueError("有未解决的错误，程序停止运行")


# TODO AI识图，检查内容错误

def move_file():
    global ERR_FLAG
    console.log("[green]移动文件")
    # e.g. 20231231-1001-1234567
    reg = r'\d{8}-\d{4}-\d{7}'
    for f in Path(CONF_WORK_SPACE, "待整理").iterdir():
        # 跳过目录文件
        if Path(f).is_dir():
            continue
        # 检测文件命名是否合规
        if len(f.name) <= 0:
            continue
        if re.match(reg, f.name) is None:
            continue
        # 车辆编号核查
        car_no = f.name.split("-")[1]
        if car_no not in CAR_LIST:
            continue
        # 本地文件是否重复
        target_file_path = Path(CONF_WORK_SPACE, car_no, f.name)
        Path(f).rename(target_file_path)
        console.log(f"[green]    移动: {f.name}")
    console.log("移动文件:完成")


if __name__ == "__main__":
    check_base_dir_path()
    check_file_duplication()
    move_file()
