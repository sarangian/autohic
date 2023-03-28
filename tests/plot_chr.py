#!/usr/bin/env python3
# encoding: utf-8 

"""
@author: jzj
@contact: jzjlab@163.com
@file: plot_chr.py
@time: 12/12/22 10:05 AM
@function: visualize Whole genome chromosome
"""
import os
import numpy as np
import hicstraw
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import pyplot as plt
import matplotlib.lines as lines

from src.core.utils.logger import logger
from src.core.utils.get_cfg import get_max_hic_len


def plot_chr_inter(hic_file, out_path=None, color_percent=95, figure_size=(10, 10), dpi=300, fig_format="png"):
    # check input arguments
    if hic_file is None:
        raise ValueError("hic data path is None, please check your input \n")

    if out_path is None:
        logger.warning("Out path is None, use hic file path as out path \n")
        out_path = os.path.dirname(hic_file)

    hic = hicstraw.HiCFile(hic_file)

    hic_len = int
    for chrom in hic.getChromosomes():
        hic_len = chrom.length
    logger.info("hic file full length is %s \n" % hic_len)

    resolution = hic.getResolutions()[0]
    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)

    # resolution max length and width
    res_max_len = get_max_hic_len(resolution)

    # check if you need to cut matrix
    if res_max_len > hic_len:
        logger.info("Resolution max length bigger than hic length \n")
        for res in hic.getResolutions():
            if get_max_hic_len(res) > hic_len:
                resolution = res
                continue
        logger.info("Get contact matrix use resolution is %s\n" % resolution)
        # get new interaction matrix object
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", "NONE", "BP", resolution)
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
    else:
        logger.info("Resolution max length less than hic length, use max resolution")

        # cut matrix
        block_num = int(hic_len / res_max_len) + 1
        iter_len = np.linspace(0, hic_len, block_num + 1)
        incr_distance = iter_len[1]
        final_matrix = None
        for i in iter_len[1:]:
            temp_matrix = None
            for j in iter_len[1:]:

                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(int(i - incr_distance), int(i),
                                                                        int(j - incr_distance), int(j))
                if not np.any(temp_matrix):
                    temp_matrix = numpy_matrix_chr
                else:
                    temp_matrix = np.hstack((temp_matrix, numpy_matrix_chr))

            if not np.any(final_matrix):
                final_matrix = temp_matrix
            else:
                final_matrix = np.vstack((final_matrix, temp_matrix))

        # 去除全零行
        not_row = final_matrix[[not np.all(final_matrix[i] == 0) for i in range(final_matrix.shape[0])], :]
        # 去除全零列
        numpy_matrix_chr = not_row[:, [not np.all(not_row[:, i] == 0) for i in range(not_row.shape[1])]]

    maxcolor = (np.percentile(numpy_matrix_chr, color_percent))

    fig, ax = plt.subplots(figsize=figure_size)
    red_map = LinearSegmentedColormap.from_list("bright_red", [(1, 1, 1), (1, 0, 0)])

    ax.matshow(numpy_matrix_chr, cmap=red_map, vmin=0, vmax=maxcolor)
    plt.axis('off')  # remove axis

    # 将纵坐标刻度设置为空
    ax.set_yticks([])
    ax.set_xticks([])

    plt.savefig(os.path.join(out_path, "chromosome"), bbox_inches='tight', pad_inches=0, dpi=dpi,
                format=fig_format)
    plt.show()  # not show figure
    plt.close()


# plot whole genome chromosome interaction map in one figure
def plot_chr(hic_file, genome_name=None, chr_len_file=None, hic_len=None, color=None, resolution=None,
             out_path=None,
             nor_method="NONE", color_percent=95, figure_size=(10, 10), dpi=300, fig_format="png"):
    # check input arguments
    if hic_file is None:
        raise ValueError("hic data path is None, please check your input \n")

    if out_path is None:
        logger.warning("Out path is None, use hic file path as out path \n")
        out_path = os.path.dirname(hic_file)

    hic = hicstraw.HiCFile(hic_file)

    if hic_len is None:
        for chrom in hic.getChromosomes():
            hic_len = chrom.length
        logger.info("hic file full length is %s \n" % hic_len)

    if genome_name is None:
        logger.warning("Genome name is None, please check your genome input \n")
        genome_name = os.path.basename(hic_file)

    if color is None:
        color = [(1, 1, 1), (1, 0, 0)]

    if resolution is None:
        resolution = hic.getResolutions()[0]
        # fixme: 选择合适的分辨率
        logger.info("Resolution is None, use default resolution %s to plot \n" % resolution)

    chr_len_list = []
    with open(chr_len_file, 'r') as f:
        for line in f.readlines():
            line_split = line.strip().split("\t")
            if line_split[0] == "Chr":
                continue
            chr_len_list.append(int(line_split[2]))
        hic_len = chr_len_list[-1]

    # get interaction matrix object
    matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)

    # resolution max length and width
    res_max_len = get_max_hic_len(resolution)

    # check if you need to cut matrix
    if res_max_len > hic_len:
        logger.info("Resolution max length bigger than hic length \n")
        for res in hic.getResolutions():
            if get_max_hic_len(res) > hic_len:
                resolution = res
                continue
        logger.info("Get contact matrix use resolution is %s\n" % resolution)
        # get new interaction matrix object
        matrix_object_chr = hic.getMatrixZoomData('assembly', 'assembly', "observed", nor_method, "BP", resolution)
        numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(0, hic_len, 0, hic_len)
    else:
        logger.info("Resolution max length less than hic length, use max resolution")

        # cut matrix
        block_num = int(hic_len / res_max_len) + 1
        iter_len = np.linspace(0, hic_len, block_num + 1)
        incr_distance = iter_len[1]
        final_matrix = None
        for i in iter_len[1:]:
            temp_matrix = None
            for j in iter_len[1:]:

                numpy_matrix_chr = matrix_object_chr.getRecordsAsMatrix(int(i - incr_distance), int(i),
                                                                        int(j - incr_distance), int(j))
                if not np.any(temp_matrix):
                    temp_matrix = numpy_matrix_chr
                else:
                    temp_matrix = np.hstack((temp_matrix, numpy_matrix_chr))

            if not np.any(final_matrix):
                final_matrix = temp_matrix
            else:
                final_matrix = np.vstack((final_matrix, temp_matrix))

        # 去除全零行
        not_row = final_matrix[[not np.all(final_matrix[i] == 0) for i in range(final_matrix.shape[0])], :]
        # 去除全零列
        numpy_matrix_chr = not_row[:, [not np.all(not_row[:, i] == 0) for i in range(not_row.shape[1])]]

    # matrix flip
    dense_matrix = np.flipud(numpy_matrix_chr)

    maxcolor = (np.percentile(dense_matrix, color_percent))

    fig, ax = plt.subplots(figsize=figure_size)
    red_map = LinearSegmentedColormap.from_list("bright_red", color)

    im = ax.matshow(dense_matrix, cmap=red_map, vmin=0, vmax=maxcolor)

    # set genome title
    ax.set_title(genome_name, fontsize=25)

    # FIXME: 测试多个基因组增加染色体名字
    # label_scale = dense_matrix.shape[1] / chr_len_list[-1]
    # chr_len_list_mid = [0] + chr_len_list
    # midpoints = []
    # for i in range(len(chr_len_list_mid) - 1):
    #     midpoint = (chr_len_list_mid[i] + chr_len_list_mid[i + 1]) / 2
    #     midpoints.append(midpoint)

    # TODO: 增加染色体框线
    # add chr lines
    # chr_line_list = chr_len_list[:-1]
    # chr_line_list_scale = [x * label_scale for x in chr_line_list]
    # for line_x in chr_line_list_scale:
    #     fig.add_artist(lines.Line2D([line_x, line_x], [0, chr_line_list_scale[-1]], linestyle='--', color='w'))
    #     fig.add_artist(lines.Line2D([0, chr_line_list_scale[-1]], [line_x, line_x], linestyle='--', color='w'))

    # add x labels
    # chr_ticks = [x * label_scale for x in midpoints]
    # chr_labels = ["Chr" + str(i) for i in range(1, len(midpoints) + 1)]

    # 设置横坐标的位置和标签
    # ax.set_xticks(chr_ticks)
    # ax.set_xticklabels(chr_labels)
    # ax.xaxis.set_ticks_position("bottom")

    # 将纵坐标刻度设置为空
    ax.set_yticks([])
    ax.set_xticks([])  # need to adjust

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.savefig(os.path.join(out_path, genome_name) + "_chr", bbox_inches='tight', pad_inches=0.1, dpi=dpi,
                format=fig_format)
    plt.show()  # not show figure
    plt.close()


def main():
    hic_file = "/home/jzj/Jupyter-Docker/buffer/10_genomes/03_silkworm/silkworm.2.hic"
    out_path = "/home/jzj/buffer"
    chr_len_file = "/home/jzj/buffer/chr.txt"
    plot_chr(hic_file, chr_len_file=chr_len_file, out_path=out_path, fig_format="svg")
    # plot_chr_inter(hic_file, out_path)


if __name__ == "__main__":
    main()
