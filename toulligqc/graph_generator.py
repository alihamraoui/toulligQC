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


# Graph generation

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
from pandas.tools.plotting import table
import re

pd.options.display.float_format = '{x:.2f}'.format


def _is_in_result_dict(dict, dict_key, default_value):
    if dict_key not in dict or not dict[dict_key]:
        dict[dict_key] = default_value
    return dict[dict_key]

def _make_table(value, ax, metric_suppression=''):
    '''
    Creation of a statistics table printed with the graph
    :param value: information measured
    :param ax: axes used
    :param metric_suppression: suppression of a metric when we use the describe pandas function
    '''

    if metric_suppression:
        the_table = table(ax, np.round(value.describe().drop(metric_suppression), 2), loc='center')
    else:
        the_table = table(ax, np.round(value.describe(), 2), loc='center')

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.axis('off')

    the_table.set_fontsize(12)
    the_table.scale(1, 1.2)

def _make_table_html(value):
    '''
    Creation of a statistics table printed with the graph in report.html
    :param value: information measured
    :param metric_suppression: suppression of a metric when we use the describe pandas function
    '''

    table=np.round(value.describe(),2)
    pd.options.display.float_format = '{:.0f}'.format
    table_html = pd.DataFrame.to_html(table)
    return table_html

def _safe_log(x):
    '''
    Verification that we haven't a null value
    :param x: tested value
    :return: log2 value or 0
    '''
    if x <= 0:
        return 0
    return np.log2(x)

#  1D plots

def read_count_histogram(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the count histograms of count  of the different types of reads eventually available in a Minion run: template, complement, full_2D.
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.mec = 'black'
    plt.mfc = 'white'
    plt.subplots_adjust(bottom=0.015, top=1.0)

    result_dict['albacore.log.extractor.fast5.files.submitted'] = _is_in_result_dict(result_dict, 'albacore.log.extractor.fast5.files.submitted', -1)

    if result_dict['albacore.log.extractor.fast5.files.submitted'] == -1:
        read_type = [result_dict['albacore.stats.1d.extractor.fastq.entries'],
                     result_dict['albacore.stats.1d.extractor.read.count'],
                     result_dict["albacore.stats.1d.extractor.read.pass.count"],
                     result_dict["albacore.stats.1d.extractor.read.fail.count"]]
        label = ("FastQ entries", "1D", "1D pass", "1D fail")
        nd = np.arange(len(read_type))
        bars = ax.bar(nd, read_type, align='center',color=["lightblue", "salmon", "yellowgreen", "orangered"],edgecolor="black",linewidth=1)

        array = np.array([[result_dict["albacore.stats.1d.extractor.fastq.entries"],result_dict["albacore.stats.1d.extractor.read.count"],result_dict["albacore.stats.1d.extractor.read.pass.count"], result_dict["albacore.stats.1d.extractor.read.fail.count"]],
                          [result_dict['albacore.stats.1d.extractor.fastq.entries.percent'],result_dict["albacore.stats.1d.extractor.read.count.percent"],result_dict["albacore.stats.1d.extractor.read.pass.percent"],result_dict["albacore.stats.1d.extractor.read.fail.percent"]]])
        dataframe = pd.DataFrame(array, index = ['count', 'frequency'],columns=["FastQ_entries","1D","1D pass","1D fail"])

    else:
        read_type = [result_dict['albacore.log.extractor.fast5.files.submitted'],
                     result_dict['albacore.log.extractor.fast5.files.basecalled.error.count'],
                     result_dict['albacore.stats.1d.extractor.fastq.entries'],
                     result_dict['albacore.stats.1d.extractor.read.count'],
                     result_dict["albacore.stats.1d.extractor.read.pass.count"],
                     result_dict["albacore.stats.1d.extractor.read.fail.count"]]
        label = ("Raw Fast5", "Raw Fast5 with error", "FastQ entries", "1D", "1D pass", "1D fail")
        nd = np.arange(len(read_type))
        bars = ax.bar(nd, read_type, align='center',color=["Green", "yellow", "lightblue", "salmon", "yellowgreen", "orangered"],edgecolor="black",linewidth=1)

        array = np.array([[result_dict['albacore.log.extractor.fast5.files.submitted'], result_dict['albacore.log.extractor.fast5.files.basecalled.error.count'],result_dict["albacore.stats.1d.extractor.fastq.entries"], result_dict["albacore.stats.1d.extractor.read.count"],
                           result_dict["albacore.stats.1d.extractor.read.pass.count"], result_dict["albacore.stats.1d.extractor.read.fail.count"]],
                          [result_dict['albacore.log.extractor.fast5.files.percent'], result_dict['albacore.log.extractor.fast5.files.basecalled.error.percent'],result_dict['albacore.stats.1d.extractor.fastq.entries.percent'],result_dict["albacore.stats.1d.extractor.read.count.percent"],
                           result_dict["albacore.stats.1d.extractor.read.pass.percent"],result_dict["albacore.stats.1d.extractor.read.fail.percent"]]])
        dataframe = pd.DataFrame(array, index = ['count', 'frequency'],columns=["Raw Fast5","Raw Fast5 with error","FastQ_entries","1D","1D pass","1D fail"])

    plt.xticks(nd, label)
    plt.xlabel("Read type")
    plt.ylabel("Counts")
    plt.title(main)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., 1 * height, '%d' % int(height), ha='center', va='bottom')

    plt.savefig(output_file)
    plt.close()

    pd.options.display.float_format = '{:.2f}'.format
    table_html = pd.DataFrame.to_html(dataframe)

    return main, output_file, table_html, desc

def read_length_multihistogram(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots an histogram of the reads length by bins of 100 for each of the barcodes described in the design file or without barcode
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    minimum, maximum = min(result_dict["albacore.stats.1d.extractor.sequence.length.template"]), max(result_dict["albacore.stats.1d.extractor.sequence.length.template"])
    read_type=['1D','1D pass','1D fail']

    fig = plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.subplots_adjust(bottom=0.015, top=1.0)

    n, bins, patches = ax.hist([result_dict["albacore.stats.1d.extractor.sequence.length.template"],
                                result_dict["albacore.stats.1d.extractor.read.pass"],
                                result_dict["albacore.stats.1d.extractor.read.fail"]],
                               color=["salmon", "yellowgreen", "orangered"],
                               edgecolor='black', label=read_type,
                               bins=2 ** np.linspace(_safe_log(minimum), _safe_log(maximum), 30))
    plt.legend()

    ax.set_xscale('log', basex=2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.1f}'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xticks(bins)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_rotation('vertical')
    ax.set_xlabel('Read length(bp)')
    ax.set_ylabel('Read number')
    ax.set_title(main)

    dataframe = pd.DataFrame({"1D": result_dict["albacore.stats.1d.extractor.sequence.length.template"], "1D pass": result_dict["albacore.stats.1d.extractor.read.pass"], "1D fail": result_dict["albacore.stats.1d.extractor.read.fail"]})
    dataframe = dataframe[["1D","1D pass","1D fail"]]

    plt.savefig(output_file)
    plt.close()

    table_html = _make_table_html(dataframe)

    return main, output_file, table_html, desc

def allread_number_run(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the reads produced along the run against the time(in hour)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    plt_read_1d = plt.plot(result_dict["albacore.stats.1d.extractor.start.time.sorted"],np.arange(len(result_dict["albacore.stats.1d.extractor.start.time.sorted"])),color='salmon',linewidth=1,label="1D")
    plt_read_pass = plt.plot(result_dict["albacore.stats.1d.extractor.read.pass.sorted"],np.arange(len(result_dict["albacore.stats.1d.extractor.read.pass.sorted"])),color='yellowgreen',linewidth=1,label="1D pass")
    plt_read_fail = plt.plot(result_dict["albacore.stats.1d.extractor.read.fail.sorted"],np.arange(len(result_dict["albacore.stats.1d.extractor.read.fail.sorted"])),color='orangered',linewidth=1,label="1D fail")

    plt.xticks(np.arange(0,max(result_dict["albacore.stats.1d.extractor.start.time.sorted"]),8))

    plt.ylabel("Read number")
    plt.xlabel("Time (Hour)")
    plt.legend()

    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc


def speed_during_the_run(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the reads produced along the run against the time(in hour)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    bins = result_dict["run_time"]*10
    bin_count = _define_bins_count(result_dict["read_pass_sorted"],result_dict["read_pass_speed"],result_dict["read_fail_sorted"],result_dict["read_fail_speed"],bins,methode='count')
    bin_median_1d,bin_centers_1d = _make_median_fitted_model(result_dict["start_time_sorted"],result_dict["read_speed"],bins,'median')

    plt_read_1d = plt.plot(bin_centers_1d[0:bin_count],bin_median_1d[0:bin_count],color='salmon',linewidth=1,label="1D")

    bin_median_pass,bin_centers_pass = _make_median_fitted_model(result_dict["read_pass_sorted"], result_dict["read_pass_speed"],bins,'median')
    plt_read_pass = plt.plot(bin_centers_pass[0:bin_count],bin_median_pass[0:bin_count],color='yellowgreen',linewidth=1,label="1D pass")

    bin_median_fail,bin_centers_fail = _make_median_fitted_model(result_dict["read_fail_sorted"], result_dict["read_fail_speed"],bins,'median')
    plt_read_fail = plt.plot(bin_centers_fail[0:bin_count],bin_median_fail[0:bin_count],color='orangered',linewidth=1,label="1D fail")

    plt.ylabel("Speed (base per seconde)")
    plt.xlabel("Time (Hour)")
    plt.xticks(np.arange(0, max(result_dict["start_time_sorted"]), 8))
    plt.legend()
    plt.title(main)

    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

def read_quality_during_the_run(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the reads produced along the run against the time(in hour)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    bins = int(max(result_dict["start_time_sorted"])*10)
    bin_count = _define_bins_count(result_dict["read_pass_sorted"], result_dict["read_pass_speed"],result_dict["read_fail_sorted"], result_dict["read_fail_speed"], bins,methode='count')

    bin_median_1d, bin_centers_1d = _make_median_fitted_model(result_dict["start_time_sorted"],result_dict["mean_qscore"],bins,'median')
    plt_read_1d = plt.plot(bin_centers_1d[0:bin_count],bin_median_1d[0:bin_count],color='salmon',linewidth=1,label="1D")

    bin_median_pass, bin_centers_pass = _make_median_fitted_model(result_dict["read_pass_sorted"],result_dict["qscore_read_pass"],bins,'median')
    plt_read_pass = plt.plot(bin_centers_pass[0:bin_count], bin_median_pass[0:bin_count], color='yellowgreen', linewidth=1, label="1D pass")

    bin_median_fail,bin_centers_fail = _make_median_fitted_model(result_dict["read_fail_sorted"], result_dict["qscore_read_fail"],bins,'median')
    plt_read_fail = plt.plot(bin_centers_fail[0:bin_count],bin_median_fail[0:bin_count],color='orangered',linewidth=1,label="1D fail")

    plt.ylabel("Mean Phred score)")
    plt.xlabel("Time (Hour)")
    plt.xticks(np.arange(0, max(result_dict["start_time_sorted"]), 8))
    plt.legend()
    plt.title(main)

    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

def read_length_during_the_run(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the reads produced along the run against the time(in hour)
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    bins = int(max(result_dict["start_time_sorted"])*5)
    bin_count = _define_bins_count(result_dict["read_pass_sorted"], result_dict["read_pass_speed"],result_dict["read_fail_sorted"], result_dict["read_fail_speed"], bins,methode='count')

    bin_median_1d, bin_centers_1d = _make_median_fitted_model(result_dict["start_time_sorted"],result_dict["sequence_length_template"],bins,'median')
    plt_read_1d = plt.plot(bin_centers_1d[0:bin_count],bin_median_1d[0:bin_count],color='salmon',linewidth=1,label="1D")

    bin_median_pass, bin_centers_pass = _make_median_fitted_model(result_dict["read_pass_sorted"],result_dict["read_pass"],bins,'median')
    plt_read_pass = plt.plot(bin_centers_pass[0:bin_count], bin_median_pass[0:bin_count], color='yellowgreen', linewidth=1, label="1D pass")

    bin_median_fail,bin_centers_fail = _make_median_fitted_model(result_dict["read_fail_sorted"], result_dict["read_fail"],bins,'median')
    plt_read_fail = plt.plot(bin_centers_fail[0:bin_count],bin_median_fail[0:bin_count],color='orangered',linewidth=1,label="1D fail")

    plt.xticks(np.arange(0, max(result_dict["start_time_sorted"]), 8))
    plt.ylabel("Read length ())")
    plt.xlabel("Time (Hour)")
    plt.legend()
    plt.title(main)

    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

def read_quality_multiboxplot(result_dict,main, my_dpi, result_directory, desc):
    """
    Plots a boxplot of reads quality
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi, facecolor='white',edgecolor='black')
    gs = gridspec.GridSpec(nrows=2, ncols=2, height_ratios=[2, 1])

    my_pal = {"1D": "salmon", "1D pass": "yellowgreen", "1D fail": "orangered"}
    order=["1D","1D pass","1D fail"]
    dataframe = pd.DataFrame({"1D": result_dict["albacore.stats.1d.extractor.mean.qscore"], "1D pass": result_dict['albacore.stats.1d.extractor.qscore.read.pass'], "1D fail": result_dict['albacore.stats.1d.extractor.qscore.read.fail']})
    sns.boxplot(data=dataframe, ax=plt.subplot(gs[0]),palette=my_pal,order=order,linewidth=1)
    plt.ylabel('Mean Phred score')

    sns.violinplot(data=dataframe, ax=plt.subplot(gs[1]), palette=my_pal, inner=None, cut=0, order=order,linewidth=1)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    plt.ylabel('Mean Phred score')
    plt.title(main)
    plt.legend()

    dataframe = dataframe[["1D","1D pass","1D fail"]]
    table_html = _make_table_html(dataframe)


    plt.savefig(output_file)
    plt.close()
    return main, output_file, table_html, desc


def phred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the distribution of the phred score
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.subplots_adjust(bottom=0.015, top=1.0)

    sns.distplot(result_dict["albacore.stats.1d.extractor.mean.qscore"], bins=15, color='salmon',
                 hist_kws=dict(edgecolor="k", linewidth=1),hist=True,label="1D")

    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")
    plt.title(main)

    dataframe = pd.DataFrame({"1D": result_dict["albacore.stats.1d.extractor.mean.qscore"]})
    rd = dataframe.describe().drop('count').round(2).reset_index()

    plt.axvline(x=result_dict["albacore.stats.1d.extractor.mean.qscore"].describe()['50%'], color='salmon')

    plt.savefig(output_file)
    plt.close()

    table_html = _make_table_html(rd)

    return main, output_file, table_html, desc

def allphred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the distribution of the phred score
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.subplots_adjust(bottom=0.015, top=1.0)

    sns.distplot(result_dict['albacore.stats.1d.extractor.qscore.read.pass'], bins=15,hist_kws=dict(edgecolor="k", linewidth=1) ,color='yellowgreen',
                 hist=True, label='1D pass')
    sns.distplot(result_dict['albacore.stats.1d.extractor.qscore.read.fail'], bins=15,hist_kws=dict(edgecolor="k", linewidth=1) ,color='orangered', label='1D fail',
                 hist=True)
    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")
    plt.title(main)

    dataframe = pd.DataFrame({"1D": result_dict["albacore.stats.1d.extractor.mean.qscore"], "1D pass": result_dict['albacore.stats.1d.extractor.qscore.read.pass'], "1D fail": result_dict['albacore.stats.1d.extractor.qscore.read.fail']})

    rd = dataframe.describe().drop('count').round(2).reset_index()

    plt.axvline(x=result_dict['albacore.stats.1d.extractor.qscore.read.pass'].describe()['50%'], color='yellowgreen')
    plt.axvline(x=result_dict['albacore.stats.1d.extractor.qscore.read.fail'].describe()['50%'], color='orangered')

    plt.savefig(output_file)
    plt.close()

    dataframe = dataframe[["1D","1D pass","1D fail"]]
    table_html = _make_table_html(dataframe)

    return main, output_file, table_html, desc

def all_scatterplot(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the scatter plot representing the relation between the phred score and the sequence length in log
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    read_pass=plt.scatter(x=result_dict["albacore.stats.1d.extractor.read.pass"], y=result_dict["albacore.stats.1d.extractor.qscore.read.pass"],color="yellowgreen")
    read_fail=plt.scatter(x=result_dict["albacore.stats.1d.extractor.read.fail"], y=result_dict["albacore.stats.1d.extractor.qscore.read.fail"],color="orangered")
    plt.legend((read_pass,read_fail),("1D pass","1D fail"))
    plt.xlim(np.min(result_dict["albacore.stats.1d.extractor.sequence.length.template"].loc[result_dict["albacore.stats.1d.extractor.sequence.length.template"]>0]),np.max(result_dict["albacore.stats.1d.extractor.sequence.length.template"]))
    plt.xscale('log')
    plt.xlabel("Sequence length")
    plt.ylabel("Mean Phred score")
    plt.title(main)
    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

def channel_count_histogram(albacore_log, main, my_dpi, result_directory, desc):
    """
    Plots an histogram of the channel count according to the channel number
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    ax.hist(albacore_log['channel'], edgecolor='black',
            bins=range(min(albacore_log['channel']), max(albacore_log['channel']) + 64, 64))
    ax.set_xlabel("Channel number")
    ax.set_ylabel("Count")
    ax.set_title(main)

    channel_count = albacore_log['channel']
    total_number_reads_per_channel = pd.value_counts(channel_count)
    ax2 = plt.subplot(gs[1])
    _make_table(total_number_reads_per_channel, ax2, metric_suppression=['mean', 'std', '50%', '75%', '25%'])

    plt.savefig(output_file)
    plt.close()
    table = total_number_reads_per_channel.describe()
    table_html = pd.DataFrame.to_html(table)

    return main, output_file, table_html, desc

def _minion_flowcell_layout():
    """
    Represents the layout of a minion flowcell
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
    d2 = df.pivot("Row number", "Column number", "labels")
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    sns.heatmap(d, fmt="", linewidths=.5, cmap="YlGnBu", annot_kws={"size": 7}, cbar_kws={'label': 'Read number per pore channel',"orientation": "horizontal"})
    plt.title(main)

    plt.savefig(output_file)
    plt.close()

    table_html = None

    return main, output_file, table_html, desc

# For each barcode 1D

def barcode_percentage_pie_chart_pass(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of the barcode percentage of a run. Needs the design file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(800 / my_dpi, 800 / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(result_dict['albacore.stats.1d.extractor.barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    barcode_count = result_dict["albacore.stats.1d.extractor.read.pass.barcode"].value_counts()
    count_sorted = barcode_count.sort_index()[barcode_selection]
    total = sum(count_sorted)

    cs = cm.Spectral(np.arange(len(barcode_selection)) / len(barcode_selection))


    sizes = [(100 * chiffre) / total for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        fig1, ax1 = plt.subplots()
        wedges,texts = ax1.pie(sizes, labels=None, startangle=90, colors=cs,wedgeprops={'linewidth':1,'edgecolor':'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right" , bbox_to_anchor =(1.1,1.16), edgecolor="black")

    else:
        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        length = np.arange(0, len(barcode_count))
        ax1.set_title(main)
        ax1.bar(length, barcode_count, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcode_selection)
        plt.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right",bbox_to_anchor =(1.1,1.16))

    plt.savefig(output_file)
    plt.close()

    barcode_table = pd.DataFrame(barcode_count/sum(barcode_count)*100)
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format

    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc

def barcode_percentage_pie_chart_fail(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of the barcode percentage of a run. Needs the design file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(800 / my_dpi, 800 / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(result_dict['albacore.stats.1d.extractor.barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    barcode_count = result_dict["albacore.stats.1d.extractor.read.fail.barcode"].value_counts()
    count_sorted = barcode_count.sort_index()[barcode_selection]
    total = sum(count_sorted)

    cs = cm.Spectral(np.arange(len(barcode_selection)) / len(barcode_selection))


    sizes = [(100 * chiffre) / total for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=None, startangle=90, colors=cs,wedgeprops={'linewidth':1,'edgecolor':'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection, sizes)],loc="upper right",bbox_to_anchor =(1.1,1.16),edgecolor='black')

    else:
        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        length = np.arange(0, len(barcode_count))
        ax1.set_title(main)
        ax1.bar(length, barcode_count, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcode_selection)
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection, sizes)],loc="upper right",bbox_to_anchor =(1.1,1.16))

    plt.savefig(output_file)
    plt.close()

    barcode_table = pd.DataFrame(barcode_count/sum(barcode_count)*100)
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format

    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc

def barcode_length_boxplot(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the length boxplot for each barcode indicated in the sample sheet
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    fig = plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.subplots_adjust(bottom=0.015, top=1.0)

    ax = sns.boxplot(data=result_dict['albacore.stats.1d.extractor.barcode_selection_sequence_length_melted_dataframe'],
                     x='barcodes',y='length',hue='passes_filtering',
                     showfliers=False,palette={True : "yellowgreen", False : "orangered"},
                     hue_order=[True,False])

    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.92, 1), loc=2, borderaxespad=0., labels=["Pass", "Fail"], handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Read length(bp)')
    plt.title(main)

    plt.savefig(output_file)
    plt.close()
    table_html=_make_table_html(result_dict['albacore.stats.1d.extractor.barcode_selection_sequence_length_dataframe'])

    return main, output_file, table_html, desc

def barcoded_phred_score_frequency(result_dict, main,my_dpi, result_directory, desc):
    '''
    Plot the phred score distribution boxplot for each barcode indicated in the sample sheet
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    fig = plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])

    ax = sns.boxplot(data=result_dict['albacore.stats.1d.extractor.barcode_selection_sequence_phred_melted_dataframe'], x='barcodes', y='qscore', hue='passes_filtering', showfliers=False,
                palette={True: "yellowgreen", False: "orangered"}, hue_order=[True, False])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.92, 1), loc=2, borderaxespad=0., labels=["Pass", "Fail"], handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Mean Phred score')
    plt.title(main)

    table_html=_make_table_html(result_dict['albacore.stats.1d.extractor.barcode_selection_sequence_phred_dataframe'])

    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc


#  1Dsqr plots

def dsqr_read_count_histogram(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots the count histograms of count  of the different types of reads eventually available in a Minion run: 1D, full_1Dsquare.
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)

    read_type = [result_dict['albacore.stats.1d.extractor.read.count'],
                 result_dict['albacore.stats.1dsqr.extractor.read.count'],
                 result_dict['albacore.stats.1dsqr.extractor.read.pass.count'],
                 result_dict['albacore.stats.1dsqr.extractor.read.pass.count']]

    label = ("1D", "1Dsquare", "1Dsquare pass", "1Dsquare fail")
    nd = np.arange(len(read_type))

    bars = plt.bar(nd, read_type, align='center', color=["salmon", "orange", "yellowgreen", "orangered"])
    plt.xticks(nd, label)
    plt.xlabel("Read type")
    plt.ylabel("Counts")
    plt.title(main)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., 1 * height, '%d' % int(height), ha='center', va='bottom')
    table_html = None

    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc

def dsqr_read_length_multihistogram(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots an histogram of the reads length by bins of 100 for each of the barcodes described in the design file or without barcode
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    read_1d = result_dict["albacore.stats.1d.extractor.sequence.length.template"]
    read_1dsqr = result_dict['albacore.stats.1dsqr.extractor.sequence.read.length']
    read_pass_1dsqr = result_dict['albacore.stats.1dsqr.extractor.read.pass.length']
    read_fail_1dsqr = result_dict['albacore.stats.1dsqr.extractor.read.fail.length']


    minimum, maximum = min(result_dict["albacore.stats.1d.extractor.sequence.length.template"]), max(result_dict["albacore.stats.1d.extractor.sequence.length.template"])
    read_type=['1D','1Dsquare','1Dsquare pass','1Dsquare fail']

    plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    plt.subplots_adjust(bottom=0.015, top=1)

    n, bins, patches = ax.hist([read_1d,read_1dsqr,read_pass_1dsqr,read_fail_1dsqr],color=["salmon","goldenrod","yellowgreen", "orangered"], edgecolor='black', label=read_type,
                               bins=2 ** np.linspace(_safe_log(minimum), _safe_log(maximum), 30))
    plt.legend()

    ax.set_xscale('log', basex=2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.1f}'))
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    ax.set_xticks(bins)

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_rotation('vertical')
    ax.set_xlabel('Read length(bp)')
    ax.set_ylabel('Read number')
    ax.set_title(main)

    dataframe = pd.DataFrame({"1D": read_1d,'1Dsquare': read_1dsqr ,"1Dsquare pass": read_pass_1dsqr, "1Dsquare fail": read_fail_1dsqr})

    dataframe = dataframe[["1D","1Dsquare","1Dsquare pass","1Dsquare fail"]]
    table_html = _make_table_html(dataframe)

    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc

def dsqr_read_quality_multiboxplot(result_dict, main, my_dpi, result_directory, desc):
    """
    Plots a boxplot of reads quality
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    plt.subplots_adjust(bottom=0.015, top=1.0)
    mean_qscore_1d = result_dict["albacore.stats.1d.extractor.mean.qscore"]

    mean_qscore_1dsqr = result_dict['albacore.stats.1dsqr.extractor.mean.qscore']
    read_pass_1dsqr = result_dict['albacore.stats.1dsqr.extractor.read.pass.qscore']
    read_fail_1dsqr = result_dict['albacore.stats.1dsqr.extractor.read.fail.qscore']

    my_pal = {"1D": "salmon","1Dsquare": "goldenrod", "1Dsquare pass": "yellowgreen", "1Dsquare fail": "orangered"}
    order=["1D","1Dsquare","1Dsquare pass","1Dsquare fail"]
    dataframe = pd.DataFrame({"1D": mean_qscore_1d,"1Dsquare": mean_qscore_1dsqr, "1Dsquare pass": read_pass_1dsqr, "1Dsquare fail": read_fail_1dsqr})
    sns.boxplot(data=dataframe, ax=plt.subplot(gs[0]),palette=my_pal,order=order)


    plt.ylabel('Mean Phred score')
    plt.title(main)
    plt.legend()

    dataframe = dataframe[["1D","1Dsquare","1Dsquare pass","1Dsquare fail"]]
    table_html = _make_table_html(dataframe)

    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc

def dsqr_phred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the distribution of the phred score
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])

    sns.distplot(result_dict['albacore.stats.1dsqr.extractor.mean.qscore'], bins=15, color='goldenrod',
                 hist_kws=dict(edgecolor="k", linewidth=1),hist=True,label="1Dsquare")

    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")
    plt.title(main)

    dataframe = pd.DataFrame({"1Dsquare": result_dict['albacore.stats.1dsqr.extractor.mean.qscore']})
    rd = dataframe.describe().drop('count').round(2).reset_index()

    plt.axvline(x=result_dict['albacore.stats.1dsqr.extractor.mean.qscore'].describe()['50%'], color='goldenrod')

    plt.savefig(output_file)
    plt.close()

    table_html = _make_table_html(rd)

    return main, output_file, table_html, desc

def dsqr_allphred_score_frequency(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the distribution of the phred score
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])
    qscore_1d = result_dict["albacore.stats.1d.extractor.mean.qscore"]
    qscore_1dsqr = result_dict['albacore.stats.1dsqr.extractor.mean.qscore']
    mean_qscore_read_pass = result_dict['albacore.stats.1dsqr.extractor.read.pass.qscore']
    mean_qscore_read_fail = result_dict['albacore.stats.1dsqr.extractor.read.fail.qscore']

    sns.distplot(mean_qscore_read_pass, bins=15,hist_kws=dict(edgecolor="k", linewidth=1) ,color='yellowgreen',
                 hist=True, label='1Dsquare pass')
    sns.distplot(mean_qscore_read_fail, bins=15,hist_kws=dict(edgecolor="k", linewidth=1) ,color='orangered', label='1Dsquare fail',
                 hist=True)
    plt.legend()
    plt.xlabel("Mean Phred score")
    plt.ylabel("Frequency")
    plt.title(main)

    dataframe = pd.DataFrame({"1D": qscore_1d,"1Dsquare": qscore_1dsqr, "1Dsquare pass": mean_qscore_read_pass, "1Dsquare fail": mean_qscore_read_fail})

    rd = dataframe.describe().drop('count').round(2).reset_index()

    plt.axvline(x=mean_qscore_read_pass.describe()['50%'], color='yellowgreen')
    plt.axvline(x=mean_qscore_read_fail.describe()['50%'], color='orangered')

    rd = rd[["1D","1Dsquare","1Dsquare pass","1Dsquare fail"]]
    table_html = _make_table_html(rd)

    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc

def scatterplot_1dsqr(result_dict, main, my_dpi, result_directory, desc):
    '''
    Plot the scatter plot representing the relation between the phred score and the sequence length
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(12, 7), dpi=my_dpi)
    #plt.subplots_adjust(bottom=0.015, top=1.0)

    length_1dsqr_read_pass = result_dict['albacore.stats.1dsqr.extractor.read.pass.length']
    length_1dsqr_read_fail = result_dict['albacore.stats.1dsqr.extractor.read.fail.length']

    qscore_1dsqr_read_pass = result_dict['albacore.stats.1dsqr.extractor.read.pass.qscore']
    qscore_1dsqr_read_fail = result_dict['albacore.stats.1dsqr.extractor.read.fail.qscore']

    read_pass=plt.scatter(x=length_1dsqr_read_pass, y=qscore_1dsqr_read_pass,color="yellowgreen")
    read_fail=plt.scatter(x=length_1dsqr_read_fail, y=qscore_1dsqr_read_fail,color="orangered")
    plt.legend((read_pass,read_fail),("1Dsquare pass","1Dsquare fail"))
    plt.xlim(np.min(result_dict['albacore.stats.1dsqr.extractor.sequence.read.length'].loc[result_dict['albacore.stats.1dsqr.extractor.sequence.read.length']>0]),np.max(result_dict['albacore.stats.1dsqr.extractor.sequence.read.length']))
    plt.xscale('log')
    plt.xlabel("Sequence length")
    plt.ylabel("Mean Phred score")
    plt.title(main)
    plt.savefig(output_file)
    plt.close()

    table_html = None
    return main, output_file, table_html, desc

# For eache barcode 1Dsqr

def barcode_percentage_pie_chart_1dsqr_pass(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of the barcode percentage of a run. Needs the design file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(800 / my_dpi, 800 / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(result_dict['albacore.stats.1dsqr.extractor.barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    barcode_count = result_dict["albacore.stats.1dsqr.extractor.read.pass.barcode"].value_counts()
    count_sorted = barcode_count.sort_index()[barcode_selection]
    total = sum(count_sorted)

    cs = cm.Spectral(np.arange(len(barcode_selection)) / len(barcode_selection))

    sizes = [(100 * chiffre) / total for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=None, startangle=90, colors=cs,wedgeprops={'linewidth':1,'edgecolor':'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right" , bbox_to_anchor =(1.1,1.16), edgecolor="black")

    else:
        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        length = np.arange(0, len(barcode_count))
        ax1.set_title(main)
        ax1.bar(length, barcode_count, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcode_selection)
        plt.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right",bbox_to_anchor =(1.1,1.16))

    plt.savefig(output_file)
    plt.close()
    barcode_table = pd.DataFrame(barcode_count/sum(barcode_count)*100)
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format
    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc

def barcode_percentage_pie_chart_1dsqr_fail(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    """
    Plots a pie chart of the barcode percentage of a run. Needs the design file describing the barcodes to run
    """
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'
    plt.figure(figsize=(800 / my_dpi, 800 / my_dpi), dpi=my_dpi)
    for element in barcode_selection:

        if all(result_dict['albacore.stats.1dsqr.extractor.barcode.arrangement'] != element):
            print("The barcode {} doesn't exist".format(element))
            return False

    barcode_count = result_dict["albacore.stats.1dsqr.extractor.read.fail.barcode"].value_counts()
    count_sorted = barcode_count.sort_index()[barcode_selection]
    total = sum(count_sorted)

    cs = cm.Spectral(np.arange(len(barcode_selection)) / len(barcode_selection))

    sizes = [(100 * chiffre) / total for chiffre in count_sorted.values]
    if len(barcode_selection) <= 10:
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=None, startangle=90, colors=cs,wedgeprops={'linewidth':1,'edgecolor':'k'})
        ax1.axis('equal')
        ax1.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right" , bbox_to_anchor =(1.1,1.18), edgecolor="black")

    else:
        fig = plt.figure(figsize=(20, 10))
        ax1 = fig.add_subplot(111)
        length = np.arange(0, len(barcode_count))
        ax1.set_title(main)
        ax1.bar(length, barcode_count, color=cs)
        ax1.set_xticks(length)
        ax1.set_xticklabels(barcode_selection)
        plt.legend(labels=['%s, %1.1f %%' % (l, s) for l, s in zip(barcode_selection,sizes)], loc="upper right",bbox_to_anchor =(1.1,1.18))

    plt.savefig(output_file)
    plt.close()
    barcode_table = pd.DataFrame(barcode_count/sum(barcode_count)*100)
    barcode_table.sort_index(inplace=True)
    pd.options.display.float_format = '{:.2f}%'.format

    table_html = pd.DataFrame.to_html(barcode_table)

    return main, output_file, table_html, desc

def barcode_length_boxplot_1dsqr(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    '''
    Plot the length boxplot for each barcode indicated in the sample sheet
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    fig = plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])

    ax = sns.boxplot(data=result_dict[('albacore.stats.1dsqr.extractor.barcode_selection_sequence_length_melted_dataframe')],x='barcodes',y='length',hue='passes_filtering', showfliers=False,palette={True : "yellowgreen", False : "orangered"},hue_order=[True,False])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.92, 1), loc=2, borderaxespad=0.,labels=["Pass","Fail"],handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Read length(bp)')
    plt.title(main)

    table_html = _make_table_html(result_dict[('albacore.stats.1dsqr.extractor.barcode_selection_sequence_length_dataframe')])
    plt.savefig(output_file)
    plt.close()
    return main, output_file, table_html, desc

def barcoded_phred_score_frequency_1dsqr(result_dict, main, barcode_selection, my_dpi, result_directory, desc):
    '''
    Plot the 1Dsquare phred score distribution boxplot for each barcode indicated in the sample sheet
    '''
    output_file = result_directory + '/' + '_'.join(main.split()) + '.png'

    fig = plt.figure(figsize=(12, 7), dpi=my_dpi)
    plt.subplots_adjust(bottom=0.015, top=1.0)
    gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2, 1])
    ax = plt.subplot(gs[0])


    ax = sns.boxplot(data=result_dict[('albacore.stats.1dsqr.extractor.barcode_selection_sequence_phred_melted_dataframe')],x='barcodes',y='qscore',hue='passes_filtering', showfliers=False,palette={True : "yellowgreen", False : "orangered"},hue_order=[True,False])
    handles, _ = ax.get_legend_handles_labels()
    plt.legend(bbox_to_anchor=(0.92, 1), loc=2, borderaxespad=0., labels=["Pass", "Fail"], handles=handles)
    plt.xlabel('Barcodes')
    plt.ylabel('Mean Phred score')
    plt.title(main)

    table_html = _make_table_html(result_dict[('albacore.stats.1dsqr.extractor.barcode_selection_sequence_phred_dataframe')])
    plt.savefig(output_file)
    plt.close()

    return main, output_file, table_html, desc