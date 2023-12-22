#!/opt/conda/envs/autohic/bin/python
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: deb_adjust_v3.py
@time: 3/29/23 3:49 PM
@function: 
"""

import json
from collections import OrderedDict

from src.assembly.asy_operate import AssemblyOperate
from src.utils.get_cfg import get_ratio
from src.utils.logger import logger


def adjust_debris(errors_queue, hic_file, modified_assembly_file):
    """
    Debris adjust
    Args:
        errors_queue:
        hic_file:
        modified_assembly_file:

    Returns:
        debris error information queue
    """

    logger.info("Start adjust debris errors:\n")

    # get ratio between chromosome length and hic file length
    ratio = get_ratio(hic_file, modified_assembly_file)

    # initialize AssemblyOperate class
    asy_operate = AssemblyOperate(modified_assembly_file, ratio)

    error_deb_info = OrderedDict()  # debris info

    # iterate error queue
    for error in errors_queue:
        logger.info(f"Re-search {error} debris location ctg information:\n")
        new_error_contain_ctg = asy_operate.find_site_ctg_s(modified_assembly_file, errors_queue[error]["start"],
                                                            errors_queue[error]["end"])

        new_error_contain_ctg = json.loads(new_error_contain_ctg)  # convert str to dict

        logger.info(f"Needs to be moved ctg: {new_error_contain_ctg}\n")

        error_deb_info[error] = {
            "deb_ctg": list(new_error_contain_ctg.keys())
        }

    return error_deb_info


def main():
    pass


if __name__ == "__main__":
    main()
