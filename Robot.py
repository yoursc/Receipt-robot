import re
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table, Column

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
table = Table(show_header=True, header_style="bold magenta")
table.add_column("文件名", style="dim")
table.add_column("文件大小")
table.add_column("MD5", justify="center")
table.add_column("修改时间", justify="center")
table.add_column("处理结果", justify="center")


def convert_size(size_bytes: int) -> str:
    """将字节转换为更友好的格式"""
    import math
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_file_md5(path: Path) -> str:
    import hashlib
    md5_hash = hashlib.md5()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


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
    ERR_FLAG = 0
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
    """
    检查待整理目录下的文件是否重复。

    该函数会遍历待整理目录下的所有文件，并检查文件名、大小、MD5值和修改时间是否与已存在的文件重复。
    完全相同的文件会删除；
    文件名重复但内容不同的文件会被表姐，并记录在ERR_FLAG中。

    Raises:
        ValueError: 如果有未解决的错误，程序停止运行
    """
    global ERR_FLAG
    ERR_FLAG = 0
    console.log("[green]检查文件重复")
    # e.g. 20231231-1001-1234567
    reg = r'\d{8}-\d{4}-\d{7}'
    for source_file_path in Path(CONF_WORK_SPACE, "待整理").iterdir():
        # 跳过目录文件
        if Path(source_file_path).is_dir():
            continue
        # 检测文件命名是否合规
        if len(source_file_path.name) <= 0:
            continue
        if re.match(reg, source_file_path.name) is None:
            continue
        # 车辆编号核查
        car_no = source_file_path.name.split("-")[1]
        if car_no not in CAR_LIST:
            console.log(f"[yellow]车辆编号不在白名单中: {source_file_path.name}")
            continue
        # 本地文件是否重复
        target_file_path = Path(CONF_WORK_SPACE, car_no, source_file_path.name)
        if target_file_path.exists():
            s_size = source_file_path.stat().st_size
            t_size = target_file_path.stat().st_size
            if s_size == t_size:
                size_str = "[green]" + convert_size(s_size)
            else:
                size_str = "[red]" + convert_size(s_size) + " -> " + convert_size(t_size)
            s_md5 = get_file_md5(source_file_path)
            t_md5 = get_file_md5(target_file_path)
            if s_md5 == t_md5:
                md5_str = "[green]" + s_md5
            else:
                md5_str = "[red]" + s_md5 + " -> " + t_md5
            s_mtime = source_file_path.stat().st_mtime
            t_mtime = target_file_path.stat().st_mtime
            if s_mtime == t_mtime:
                mtime_str = "[green]" + datetime.fromtimestamp(s_mtime).strftime("%Y-%m-%d %H:%M:%S")
            else:
                mtime_str = "[red]" + datetime.fromtimestamp(s_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S") + " -> " + datetime.fromtimestamp(t_mtime).strftime("%Y-%m-%d %H:%M:%S")
            if s_size == t_size and s_md5 == t_md5 and s_mtime == t_mtime:
                result_str = "[green]源文件已删除"
                source_file_path.unlink()
            else:
                result_str = "[red]文件名冲突，请检查"
                ERR_FLAG += 1
            table.add_row(
                source_file_path.name,
                size_str,
                md5_str,
                mtime_str,
                result_str
            )
    console.print(table)

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
