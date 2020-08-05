# -*- coding: utf-8 -*-

#                  ToulligQC development code
#
# This code may be freely distributed and modified under the
# terms of the GNU General Public License version 3 or later
# and CeCILL. This should be distributed with the code. If you
# do not have a copy, see:
#
#      http://www.gnu.org/licenses/gpl-3.0-standalone.html
#      http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#
# Copyright for this code is held jointly by the Genomic platform
# of the Institut de Biologie de l'École Normale Supérieure and
# the individual authors.
#
# First author: Lionel Ferrato-Berberian
# Maintainer: Karine Dias
# Since version 0.1

# Class for generating Plotly and MPL graphs and statistics tables in HTML format, they use the result_dict or dataframe_dict dictionnaries.

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from matplotlib.pyplot import table

from plotly.subplots import make_subplots
from scipy.interpolate import interp1d
import plotly.graph_objs as go
import plotly.offline as py 
from collections import defaultdict
from scipy.ndimage.filters import gaussian_filter1d
import plotly.express.colors as pxc

figure_image_width = 1000
figure_image_height = 600


def _is_in_result_dict(dict, dict_key, default_value):
    """
    Global function to check for the presence of an entry in a dictionary
    and give it a default value.
    :param result_dict: result_dict dictionary
    :param dict_key: entry (string)
    :param default_value:
    :return:
    """
    if dict_key not in dict or not dict[dict_key]:
        dict[dict_key] = default_value
    return dict[dict_key]

#Stats d'un DF, count = str, autres valeurs avec 2 décimales & renommer 50->median
def _make_desribe_dataframe(value):
    """
    Creation of a statistics table printed with the graph in report.html
    :param value: information measured (series)
    """

    desc = value.describe()
    desc.loc['count'] = desc.loc['count'].astype(int).astype(str)
    desc.iloc[1:] = desc.iloc[1:].applymap(lambda x: '%.2f' % x) #tout sauf 1ere ligne (count) et 2 décimales
    desc.rename({'50%': 'median'}, axis='index', inplace=True)

    return desc


def _safe_log(x):
    """
    Verification that we haven't a null value
    :param x: tested value
    :return: log2 value or 0
    """
    if x <= 0:
        return 0
    return np.log2(x)

#
#  1D plots
#


def read_count_histogram(result_dict, dataframe_dict, main, my_dpi, result_directory, desc):
    """
    Plots the histogram of count of the different types of reads:
    FastQ return by MinKNOW
    1D read return by Guppy
    1D pass read return by Guppy (Qscore >= 7)
    1D fail read return by Guppy (Qscore < 7)
    """

    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    # Histogram with barcoded read counts
    if 'read.pass.barcoded.count' in dataframe_dict:

        data = {
            'Read Count': result_dict['basecaller.sequencing.summary.1d.extractor.read.count'],
            'Read Pass Count': result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.count"],
            'Read Pass Barcoded Count': dataframe_dict["read.pass.barcoded.count"],
            'Read Fail Count': result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.count"],
            'Read Fail Barcoded Count': dataframe_dict["read.fail.barcoded.count"]
        }
        colors = ["#54A8FC", "salmon", '#ffa931', "#50c878", "SlateBlue"]

        trace = go.Bar(x=[*data], y=list(data.values()),
                                hovertext=["<b>Total number of reads</b>",
                                           "<b>Reads of qscore > 7</b>",
                                           "<b>Barcoded reads with qscore > 7</b>",
                                           "<b>Reads of qscore < 7</b>",
                                           "<b>Barcoded reads with qscore < 7</b>"],
                                #hoverinfo="x",
                                name="Barcoded graph",
                                marker_color=colors,
                                marker_line_color="black",
                                marker_line_width=1.5, opacity=0.9)

        # Array of data for HTML table with barcode reads
        array = np.array(
            #count
            [[result_dict["basecaller.sequencing.summary.1d.extractor.read.count"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.count"],
              dataframe_dict["read.pass.barcoded.count"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.count"],
              dataframe_dict["read.fail.barcoded.count"]],
             #frequencies
             [result_dict["basecaller.sequencing.summary.1d.extractor.read.count.frequency"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.frequency"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.barcoded.frequency"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.frequency"],
              result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.barcoded.frequency"]]])

        dataframe = pd.DataFrame(array, index=['count', 'frequency'],
                                 columns=["Read count", "1D pass", "1D pass barcoded", "1D fail", "1D fail barcoded"])

    # Histogram without barcodes
    else:

        data = {
            'Read Count': result_dict['basecaller.sequencing.summary.1d.extractor.read.count'],
            'Read Pass Count': result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.count"],
            'Read Fail Count': result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.count"]
        }

        colors = ["#54A8FC", "salmon", "#50c878"]

        trace = go.Bar(x=[*data], y=list(data.values()),
                       hovertext=["<b>Total number of reads</b>",
                                  "<b>Reads of qscore > 7</b>",
                                  "<b>Barcoded reads with qscore > 7</b>",
                                  "<b>Reads of qscore < 7</b>",
                                  "<b>Barcoded reads with qscore < 7</b>"],
                       #hoverinfo="x",
                       name="Barcoded graph",
                       marker_color=colors,
                       marker_line_color="black",
                       marker_line_width=1.5, opacity=0.9)

        # Array of data for HTML table without barcode reads
        array = np.array([[result_dict["basecaller.sequencing.summary.1d.extractor.read.count"],
                           result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.count"],
                           result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.count"]],
                          # frequencies
                          [result_dict["basecaller.sequencing.summary.1d.extractor.read.count.frequency"],
                          result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.frequency"],
                          result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.frequency"]]])

        # Create dataframe with array data
        dataframe = pd.DataFrame(array, index=['count', 'frequency'],
                                 columns=["Read count", "1D pass", "1D fail"])

    layout = go.Layout(
        hovermode="x",
        title={
            'text': "<b>Read count histogram</b>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(
                family="Calibri, sans",
                size=25,
                color="black")
        },
        xaxis=dict(title="<b>Read type</b>",
                   linecolor="black",
                   titlefont=dict(
                       family="Calibri",
                       size=18,
                       color="black"
                   )
                   ),
        yaxis=dict(title="<b>Counts</b>",
                   linecolor="black",
                   titlefont=dict(
                       family="Calibri",
                       size=18,
                       color="black"
                   )),
        autosize=True,  # à voir
        width=800,
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig = go.Figure(data=trace, layout=layout)
    div = py.plot(fig,
                  filename=output_file,
                  include_plotlyjs=True,
                  output_type='div',
                  auto_open=False,
                  show_link=False)

    # HTML table
    dataframe.iloc[0] = dataframe.iloc[0].astype(int).astype(str)
    dataframe.iloc[1:] = dataframe.iloc[1:].applymap('{:.2f}'.format)
    table_html = pd.DataFrame.to_html(dataframe)

    return main, output_file, table_html, desc, div


def read_length_multihistogram(result_dict, dataframe_dict, main, my_dpi, result_directory, desc):
    """
    Plots an histogram of the read length for the different types of read:
    1D, 1Dpass, 1D fail
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    minimum, maximum = \
        min(dataframe_dict["sequence.length"]), \
        max(dataframe_dict["sequence.length"])
    read_type = ['1D', '1D pass', '1D fail']

    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    ax = plt.subplot()

    data = [dataframe_dict["sequence.length"],
            result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.length"],
            result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.length"]]
    ls = 2 ** np.linspace(_safe_log(minimum), _safe_log(maximum), 30)
    n, bins, patches = ax.hist(data, color=["salmon", "yellowgreen", "orangered"],
                               edgecolor='black', label=read_type,
                               bins=ls)
    plt.legend()

    ax.set_xscale('log', basex=2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax.set_xticks(bins)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_rotation('vertical')
    ax.set_xlabel('Read length(bp)')
    ax.set_ylabel('Read number')

    dataframe = \
        pd.DataFrame({"1D": dataframe_dict["sequence.length"],
                      "1D pass": result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.length"],
                      "1D fail": result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.length"]})
    dataframe = dataframe[["1D", "1D pass", "1D fail"]]

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    table_html = pd.DataFrame.to_html(_make_desribe_dataframe(dataframe))

    return main, output_file, table_html, desc


def allread_number_run(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the different reads (1D, 1D pass, 1D fail) produced along the run against the time(in hour)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)

    plt.plot(result_dict["basecaller.sequencing.summary.1d.extractor.start.time.sorted"],
             np.arange(len(result_dict["basecaller.sequencing.summary.1d.extractor.start.time.sorted"])),
             color='salmon', linewidth=1, label="1D")

    plt.plot(result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.sorted"],
             np.arange(len(result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.sorted"])),
             color='yellowgreen', linewidth=1, label="1D pass")

    plt.plot(result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.sorted"],
             np.arange(len(result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.sorted"])),
             color='orangered', linewidth=1, label="1D fail")

    plt.xticks(np.arange(0, max(result_dict["basecaller.sequencing.summary.1d.extractor.start.time.sorted"]), 8))

    plt.ylabel("Read number")
    plt.xlabel("Time (Hour)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc


def read_quality_multiboxplot(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots a boxplot of reads quality per read type (1D, 1D pass, 1D fail)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi, facecolor='white', edgecolor='black')
    gs = gridspec.GridSpec(nrows=1, ncols=2)

    my_pal = {"1D": "salmon", "1D pass": "yellowgreen", "1D fail": "orangered"}
    order = ["1D", "1D pass", "1D fail"]
    dataframe = \
        pd.DataFrame({"1D": result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"],
                      "1D pass": result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'],
                      "1D fail": result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore']})
    ax = plt.subplot(gs[0])
    sns.boxplot(data=dataframe, ax=ax, palette=my_pal, order=order, linewidth=1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    plt.ylabel('Mean Phred score')

    ax2 = plt.subplot(gs[1])
    sns.violinplot(data=dataframe, ax=ax2, palette=my_pal, inner=None, cut=0, order=order, linewidth=1)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    plt.ylabel('Mean Phred score')

    dataframe = dataframe[["1D", "1D pass", "1D fail"]]
    table_html = pd.DataFrame.to_html(_make_desribe_dataframe(dataframe))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return main, output_file, table_html, desc


def phred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    """
    Plot the distribution of the phred score (not use anymore)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    plt.subplot()

    sns.distplot(result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"], bins=15, color='salmon',
                 hist_kws=dict(edgecolor="k", linewidth=1), hist=True, label="1D")

    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")

    dataframe = pd.DataFrame({"1D": result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"]})
    rd = dataframe.describe().drop('count').round(2).reset_index()

    plt.axvline(x=result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"].describe()['50%'], color='salmon')

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    table_html = pd.DataFrame.to_html(rd)

    return main, output_file, table_html, desc


def allphred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    """
    Plot the distribution of the phred score per read type (1D , 1D pass, 1D fail)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=1, ncols=2)
    ax = plt.subplot(gs[0])

    sns.distplot(result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"], bins=15, ax=ax, color='salmon',
                 hist_kws=dict(edgecolor="k", linewidth=1), hist=True, label="1D")
    plt.axvline(x=result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"].describe()['50%'], color='salmon')

    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.2f}'))

    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")

    ax2 = plt.subplot(gs[1])

    max_frequency_pass = max(result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'].value_counts(normalize=True))

    max_frequency_fail = max(result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore'].value_counts(normalize=True))

    if max_frequency_pass > max_frequency_fail:
        sns.distplot(result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'],
                     ax=ax2, bins=15, hist_kws=dict(edgecolor="k", linewidth=1),
                     color='yellowgreen', hist=True, label='1D pass')

        sns.distplot(result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore'],
                     ax=ax2, bins=15, hist_kws=dict(edgecolor="k", linewidth=1),
                     color='orangered', label='1D fail', hist=True)

    else:
        sns.distplot(result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore'],
                     ax=ax2, bins=15, hist_kws=dict(edgecolor="k", linewidth=1),
                     color='orangered', label='1D fail', hist=True)

        sns.distplot(result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'],
                     ax=ax2, bins=15, hist_kws=dict(edgecolor="k", linewidth=1),
                     color='yellowgreen', hist=True, label='1D pass')

    ax2.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
    ax2.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.2f}'))

    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")
    plt.axvline(x=result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'].describe()['50%'], color='yellowgreen')
    plt.axvline(x=result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore'].describe()['50%'], color='orangered')

    dataframe = \
        pd.DataFrame({"1D": result_dict["basecaller.sequencing.summary.1d.extractor.mean.qscore"],
                      "1D pass": result_dict['basecaller.sequencing.summary.1d.extractor.read.pass.qscore'],
                      "1D fail": result_dict['basecaller.sequencing.summary.1d.extractor.read.fail.qscore']})

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    dataframe = _make_desribe_dataframe(dataframe).drop('count')

    table_html = pd.DataFrame.to_html(dataframe)

    return main, output_file, table_html, desc


def all_scatterplot(result_dict, dataframe_dict, main, my_dpi, result_directory, desc):
    """
    Plot the scatter plot representing the relation between the phred score and the sequence length in log
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    ax = plt.gca()

    read_pass = plt.scatter(x=result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.length"],
                            y=result_dict["basecaller.sequencing.summary.1d.extractor.read.pass.qscore"],
                            color="yellowgreen")

    read_fail = plt.scatter(x=result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.length"],
                            y=result_dict["basecaller.sequencing.summary.1d.extractor.read.fail.qscore"],
                            color="orangered")

    plt.legend((read_pass, read_fail), ("1D pass", "1D fail"))
    plt.xlim(np.min(dataframe_dict["sequence.length"]
                    .loc[dataframe_dict["sequence.length"] > 0]),
             np.max(dataframe_dict["sequence.length"]))

    plt.yticks()
    plt.xscale('log')
    plt.xlabel("Sequence length")
    plt.ylabel("Mean Phred score")
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc


def channel_count_histogram(Guppy_log, main, my_dpi, result_directory, desc):
    """
    Plots an histogram of the channel count according to the channel number (not use anymore)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    ax.hist(Guppy_log['channel'], edgecolor='black',
            bins=range(min(Guppy_log['channel']), max(Guppy_log['channel']) + 64, 64))
    ax.set_xlabel("Channel number")
    ax.set_ylabel("Count")

    channel_count = Guppy_log['channel']
    total_number_reads_per_channel = pd.value_counts(channel_count)
    plt.subplot(gs[1])

    dataframe = table(ax, np.round(total_number_reads_per_channel
                                   .describe().drop(['mean', 'std', '50%', '75%', '25%']), 2), loc='center')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axis('off')

    dataframe.set_fontsize(12)
    dataframe.scale(1, 1.2)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    table_html = pd.DataFrame.to_html(total_number_reads_per_channel.describe())

    return main, output_file, table_html, desc


def _minion_flowcell_layout():
    """
    Represents the layout of a minion flowcell (not use anymore)
    """
    seeds = [125, 121, 117, 113, 109, 105, 101, 97,
             93, 89, 85, 81, 77, 73, 69, 65,
             61, 57, 53, 49, 45, 41, 37, 33,
             29, 25, 21, 17, 13, 9, 5, 1]

    flowcell_layout = []
    for s in seeds:
        for block in range(4):
            for row in range(4):
                flowcell_layout.append(s + 128 * block + row)
    return flowcell_layout


def plot_performance(pore_measure, main, my_dpi, result_directory, desc):
    """
    Plots the channels occupancy by the reads
    @:param pore_measure: reads number per pore
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    flowcell_layout = _minion_flowcell_layout()

    pore_values = []
    for pore in flowcell_layout:
        if pore in pore_measure:
            pore_values.append(pore_measure[pore])
        else:
            pore_values.append(0)

    d = {'Row number': list(range(1, 17)) * 32,
         'Column number': sorted(list(range(1, 33)) * 16),
         'tot_reads': pore_values,
         'labels': flowcell_layout}

    df = pd.DataFrame(d)

    d = df.pivot("Row number", "Column number", "tot_reads")
    df.pivot("Row number", "Column number", "labels")
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    sns.heatmap(d, fmt="", linewidths=.5, cmap="YlGnBu", annot_kws={"size": 7},
                cbar_kws={'label': 'Read number per pore channel', "orientation": "horizontal"})

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

#
# For each barcode 1D
#


def barcode_percentage_pie_chart_pass(result_dict, dataframe_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of 1D read pass percentage per barcode of a run.
    Needs the samplesheet file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(dataframe_dict['barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    count_sorted = dataframe_dict["read.pass.barcoded"]
    barcodes = count_sorted.index.values.tolist()

    cs = plt.get_cmap('Spectral')(np.arange(len(barcodes)) / len(barcodes))

    sizes = [(100 * chiffre) / sum(count_sorted) for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        ax1 = plt.subplot()
        ax1.pie(sizes, labels=None, startangle=90, colors=cs, wedgeprops={'linewidth': 1, 'edgecolor': 'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcodes, sizes)],
                   loc="upper right", edgecolor="black")

    else:
        ax1 = plt.subplot()
        length = np.arange(0, len(count_sorted))
        ax1.bar(length, count_sorted, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcodes)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    barcode_table = pd.DataFrame({"barcode arrangement": count_sorted/sum(count_sorted)*100,
                                 "read count": count_sorted})
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format
    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc


def barcode_percentage_pie_chart_fail(result_dict, dataframe_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of 1D read fail percentage per barcode of a run.
    Needs the samplesheet file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(dataframe_dict['barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    count_sorted = dataframe_dict["read.fail.barcoded"]
    barcodes = count_sorted.index.values.tolist()

    cs = plt.get_cmap('Spectral')(np.arange(len(barcodes)) / len(barcodes))

    sizes = [(100 * chiffre) / sum(count_sorted) for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        ax1 = plt.subplot()
        ax1.pie(sizes, labels=None, startangle=90, colors=cs, wedgeprops={'linewidth': 1, 'edgecolor': 'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcodes, sizes)],
                   loc="upper right", edgecolor='black')

    else:
        ax1 = plt.subplot()
        length = np.arange(0, len(count_sorted))
        ax1.bar(length, count_sorted, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcodes)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    barcode_table = pd.DataFrame({"barcode arrangement": count_sorted/sum(count_sorted)*100,
                                  "read count": count_sorted})
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format

    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc


def barcode_length_boxplot(result_dict, datafame_dict, main, my_dpi, result_directory, desc):
    """
    Plot boxplot of the 1D pass and fail read length for each barcode indicated in the sample sheet
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    plt.subplot()

    ax = sns.boxplot(data=datafame_dict['barcode_selection_sequence_length_melted_dataframe'],
                     x='barcodes', y='length', hue='passes_filtering',
                     showfliers=False, palette={True: "yellowgreen", False: "orangered"},
                     hue_order=[True, False])

    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.905, 0.98), loc=2, borderaxespad=0., labels=["Pass", "Fail"], handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Read length(bp)')

    df = datafame_dict['barcode_selection_sequence_length_dataframe']
    all_read = df.describe().T
    read_pass = df.loc[df['passes_filtering'] == bool(True)].describe().T
    read_fail = df.loc[df['passes_filtering'] == bool(False)].describe().T
    concat = pd.concat([all_read, read_pass, read_fail], keys=['1D', '1D pass', '1D fail'])
    dataframe = concat.T

    dataframe.loc['count'] = dataframe.loc['count'].astype(int).astype(str)
    dataframe.iloc[1:] = dataframe.iloc[1:].applymap('{:.2f}'.format)
    table_html = pd.DataFrame.to_html(dataframe)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc


def barcoded_phred_score_frequency(result_dict, dataframe_dict, main, my_dpi, result_directory, desc):
    """
    Plot boxplot of the 1D pass and fail read qscore for each barcode indicated in the sample sheet
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    plt.figure(figsize=(figure_image_width / my_dpi, figure_image_height / my_dpi), dpi=my_dpi)
    plt.subplot()

    ax = sns.boxplot(data=dataframe_dict['barcode_selection_sequence_phred_melted_dataframe'],
                     x='barcodes', y='qscore', hue='passes_filtering', showfliers=False,
                     palette={True: "yellowgreen", False: "orangered"}, hue_order=[True, False])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.905, 0.98), loc=2, borderaxespad=0., labels=["Pass", "Fail"], handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Mean Phred score')

    df = dataframe_dict['barcode_selection_sequence_phred_dataframe']
    all_read = df.describe().T
    read_pass = df.loc[df['passes_filtering'] == bool(True)].describe().T
    read_fail = df.loc[df['passes_filtering'] == bool(False)].describe().T
    concat = pd.concat([all_read, read_pass, read_fail], keys=['1D', '1D pass', '1D fail'])
    dataframe = concat.T
    dataframe.loc['count'] = dataframe.loc['count'].astype(int).astype(str)
    dataframe.iloc[1:] = dataframe.iloc[1:].applymap('{:.2f}'.format)
    table_html = pd.DataFrame.to_html(dataframe)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc


def sequence_length_over_time(time_df, dataframe_dict, main, my_dpi, result_directory, desc):
        
        output_file = result_directory + '/' + '_'.join(main.split())
        
        # x_data = result_dict.get("basecaller.sequencing.summary.1d.extractor.start.time.sorted")
        # arr = np.array(x_data)
        
        time = [t/3600 for t in time_df.dropna()]
        time = np.array(sorted(time))

        # 10 minutes interval
        interval = int(max(time) / 0.6)
        
        low_bin = np.min(time) - np.fmod(np.min(time)- np.floor(np.min(time)), interval/3600)
        high_bin = np.max(time)  - np.fmod(np.max(time)- np.ceil(np.max(time)), interval/3600)
        bins = np.arange(low_bin, high_bin, interval/3600)
        
        digitized = np.digitize(time, bins, right=True) 
        
        bin_means = [time[digitized == i].mean() for i in range(1, len(bins))]
        
        # Interpolation
        length = dataframe_dict.get('sequence.length')
        f = interp1d(time, length, kind="linear")
        x_int = np.linspace(time[0],time[-1], 150)
        y_int = f(x_int)
        
        # Plot of mean values Y axis
        length_filt = length.loc[length >= 0].dropna()
        
        fig = make_subplots(rows=2, cols=1,
                            subplot_titles=("<b>Interpolation plot</b>", "<b>10 minutes interval plot</b>"),
                            vertical_spacing=0.15)
        
        fig.append_trace(go.Scatter(
        x=x_int,
        y=y_int,
        mode='lines',
        name='interpolation curve',
        line=dict(color='#205b47', width=3, shape="spline", smoothing=0.5)),
        row=1, col=1
        )
        
        #TODO: test pycoqc func
        x_pyc = _binned_data_pycoqc(length, 100)
        
        #items = 2
        #value = 5
        #         print(items[0]) #x
        # print(items[1][0]) #1st array de x
        
        # for key, value in x_pyc.items():
        #     print(value[0]) #array
        #     print(key[0]) #x
        #     fig.append_trace(go.Scatter(
        #         x=value[0],
        #         y=time,
        #         mode='lines',
        #         name=key[0],
        #         line=dict(color="#e76f51", width=3, shape="linear")),
        #         row=2, col=1
        #     )
        
        fig.update_layout(    
                title={
                'text': "<b>Read length over experiment time</b>",
                'y':1.0,
                'x':0.45,
                'xanchor': 'center',
                'yanchor': 'top',
                'font' : dict(
                family="Calibri, sans",
                size=26,
                color="black")},
            xaxis=dict(
                title="<b>Experiment time (hours)</b>",
                titlefont_size=16
                ),
            yaxis=dict(
                title='<b>Read length (bp)</b>',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.02,
                y=1.0,
                title_text="<b>Legend</b>",
                title=dict(font=dict(size=16)),
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)',
                font=dict(size=15)
            ),
            hovermode=False,
            height=800, width=1400
        )
        
        div = py.plot(fig,
                            filename=output_file,
                            include_plotlyjs=True,
                            output_type='div',
                            auto_open=False,
                            show_link=False)
            
        # py.plot(fig, filename=output_file, include_plotlyjs=True, output_type='file',
        #          auto_open=False, image_height=1000, image_width=800)

        table_html = None

        return main, output_file, table_html, desc, div
    
#TODO: delete method
def _binned_data_pycoqc(data, bins, smooth_sigma=1.5):

    # Bin data in categories
    t = data.dropna().values
    x = np.linspace (t.min(), t.max(), num=bins)
    t = np.digitize (t, bins=x, right=True)

    # List quality value per categories
    bin_dict = defaultdict (list)
    for bin_idx, val in zip (t, data) :
        bin = x[bin_idx]
        bin_dict[bin].append(val)

    # Aggregate values per category
    val_name = ["Min", "Max", "25%", "75%", "Median"]
    stat_dict = defaultdict(list)
    for bin in x:
        if bin in bin_dict:
            p = np.percentile (bin_dict[bin], [0, 100, 25, 75, 50])
        else:
            p = [np.nan,np.nan,np.nan,np.nan,np.nan]
        for val, stat in zip (val_name, p):
            stat_dict[val].append(stat)

    # Values smoothing
    if smooth_sigma:
        for val in val_name:
            stat_dict [val] = gaussian_filter1d (stat_dict [val], sigma=smooth_sigma)

    # make data dict
    data_dict = dict(
        x = [x,x,x,x,x],
        y = [stat_dict["Min"], stat_dict["Max"], stat_dict["25%"], stat_dict["75%"], stat_dict["Median"]],
        name = val_name)

    return data_dict


   
def phred_score_over_time(qscore_df, time_df, main, my_dpi, result_directory, desc):
        
        output_file = result_directory + '/' + '_'.join(main.split())

        # Time data
        time = [t/3600 for t in time_df.dropna()]
        time = np.array(sorted(time))

        # 10 minutes interval
        interval = int(max(time) / 0.6)
        
        low_bin = np.min(time) - np.fmod(np.min(time)- np.floor(np.min(time)), interval/3600)
        high_bin = np.max(time)  - np.fmod(np.max(time)- np.ceil(np.max(time)), interval/3600)
        bins = np.arange(low_bin, high_bin, interval/3600)
        
        digitized = np.digitize(time, bins, right=True) 
        
        bin_means = [time[digitized == i].mean() for i in range(1, len(bins))]
        
        # Qscore data
        qscore = qscore_df.dropna()

        # Interpolation
        f = interp1d(time, qscore, kind="linear")
        x_int = np.linspace(time[0],time[-1], 100)
        y_int = f(x_int)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_int,
            y=y_int,
            mode='markers',
            marker=dict(
        size=10,
        color=qscore,
        colorbar=dict(
            title="PHRED score"
        ),
        colorscale="Temps")))
        
        fig.update_layout(    
                title={
                'text': "<b>PHRED score over experiment time</b>",
                'y':1.0,
                'x':0.45,
                'xanchor': 'center',
                'yanchor': 'top',
                'font' : dict(
                family="Calibri, sans",
                size=26,
                color="black")},
            xaxis=dict(
                title="<b>Experiment time (hours)</b>",
                titlefont_size=16
                ),
            yaxis=dict(
                title='<b>PHRED quality score</b>',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.02,
                y=1.0,
                title_text="<b>Legend</b>",
                title=dict(font=dict(size=16)),
                bgcolor='white',
                bordercolor="white",
                font=dict(size=15)
            ),
            height=850, width=1500,
            paper_bgcolor="#F8F8FF",
            plot_bgcolor="#F8F8FF"
        )

        div = py.plot(fig,
                            filename=output_file,
                            include_plotlyjs=True,
                            output_type='div',
                            auto_open=False,
                            show_link=False)
        table_html = None

        return main, output_file, table_html, desc, div


def length_over_time_slider(time_df, dataframe_dict, main, my_dpi, result_directory, desc):
        
        output_file = result_directory + '/' + '_'.join(main.split())

        time = [t/3600 for t in time_df.dropna()]
        time = np.array(sorted(time))
        
        fig = go.Figure()
        
        # Interpolation
        length = dataframe_dict.get('sequence.length')
        f = interp1d(time, length, kind="nearest")
        # Add traces, one for each slider step
        for step in range(5, 505, 5):
            x_int = np.linspace(time[0],time[-1], step)
            y_int = f(x_int)
        
            fig.add_trace(go.Scatter(
                visible=False,
                x=x_int,
                y=y_int,
                mode='lines',
                line=dict(color='#2D85E2', width=2.5, shape="spline", smoothing=0.5))
            )
        
        # Make 60th trace visible
        fig.data[60].visible = True
        
        fig.update_layout(    
                title={
                'text': "<b>Interpolated read length over experiment time</b>",
                'y':1.0,
                'x':0.45,
                'xanchor': 'center',
                'yanchor': 'top',
                'font' : dict(
                family="Calibri, sans",
                size=26,
                color="black")},
            xaxis=dict(
                title="<b>Experiment time (hours)</b>",
                titlefont_size=16
                ),
            yaxis=dict(
                title='<b>Read length (bp)</b>',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.02,
                y=1.0,
                title_text="<b>Legend</b>",
                title=dict(font=dict(size=16)),
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)',
                font=dict(size=15)
            ),
            height=800, width=1400
        )
        
        # Create and add slider
        npoints = []
        for i in range(len(fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}],  # layout attribute
            )
            step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
            npoints.append(step)

        sliders = [dict(
            active=50,
            currentvalue={"prefix": "Number of points: "},
            pad={"t": 100},
            steps=npoints
        )]

        fig.update_layout(
            sliders=sliders
        )
        
        # Edit slider labels
        fig['layout']['sliders'][0]['currentvalue']['prefix']='Number of values : '
        for i, points in enumerate(range(5, 505, 5), start = 0):
            fig['layout']['sliders'][0]['steps'][i]['label']=points
        
        div = py.plot(fig,
                            filename=output_file,
                            include_plotlyjs=True,
                            output_type='div',
                            auto_open=False,
                            show_link=False)

        table_html = None

        return main, output_file, table_html, desc, div

    
def speed_over_time(duration_df, sequence_length_df, time_df, main, my_dpi, result_directory, desc):
        
        output_file = result_directory + '/' + '_'.join(main.split())
    
        speed = pd.Series(sequence_length_df / duration_df)
        
        time = [t/3600 for t in time_df]
        time = np.array(sorted(time))

        f = interp1d(time, speed, kind="linear")
        x_int = np.linspace(time[0],time[-1], 100)
        y_int = f(x_int)
    
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
        x=x_int,
        y=y_int,
        fill='tozeroy',
        mode='lines',
        line=dict(color='#AE3F7B', width=3, shape="linear"))
        )

        fig.update_layout(    
                title={
                'text': "<b>Speed over experiment time</b>",
                'y':1.0,
                'x':0.45,
                'xanchor': 'center',
                'yanchor': 'top',
                'font' : dict(
                family="Calibri, sans",
                size=26,
                color="black")},
            xaxis=dict(
                title="<b>Experiment time (hours)</b>",
                titlefont_size=16
                ),
            yaxis=dict(
                title='<b>Speed (bases per second)</b>',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.02,
                y=1.0,
                title_text="<b>Legend</b>",
                title=dict(font=dict(size=16)),
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)',
                font=dict(size=15)
            ),
            hovermode='x',
            height=800, width=1400
        )
        fig.update_yaxes(type="log")
        
        div = py.plot(fig,
                            filename=output_file,
                            include_plotlyjs=True,
                            output_type='div',
                            auto_open=False,
                            show_link=False)

        table_html = None

        return main, output_file, table_html, desc, div
    
    
def nseq_over_time(time_df, main, my_dpi, result_directory, desc):
        
        output_file = result_directory + '/' + '_'.join(main.split())

        time = [t/3600 for t in time_df]
        time = pd.Series(time)
        # create custom xaxis points to reduce graph size
        time_points = np.linspace(min(time), max(time), 20)
        n_seq = time.groupby(pd.cut(time, time_points, right=True)).count()

        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=list(n_seq.values), mode='lines',
            
            line=dict(color='#5199FF', width=3, shape="spline", smoothing=0.5)
        ))

        fig.update_layout(    
                title={
                'text': "<b>Number of sequences through experiment time</b>",
                'y':1.0,
                'x':0.45,
                'xanchor': 'center',
                'yanchor': 'top',
                'font' : dict(
                family="Calibri, sans",
                size=26,
                color="black")},
            xaxis=dict(
                title="<b>Experiment time (hours)</b>",
                titlefont_size=16
                ),
            yaxis=dict(
                title='<b>Number of sequences</b>',
                titlefont_size=16,
                tickfont_size=14,
            ),
            legend=dict(
                x=1.02,
                y=1.0,
                title_text="<b>Legend</b>",
                title=dict(font=dict(size=16)),
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)',
                font=dict(size=15)
            ),
            hovermode='x',
            height=800, width=1400
        )
        fig.update_yaxes(type="log")
        
        div = py.plot(fig,
                            filename=output_file,
                            include_plotlyjs=True,
                            output_type='div',
                            auto_open=False,
                            show_link=False)
        
        table_html = None

        return main, output_file, table_html, desc, div
    

