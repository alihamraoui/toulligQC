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

# Class for generating Plotly and MPL graphs and statistics tables in HTML format, they use the result_dict or dataframe_dict_1dsqr dictionnaries.

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
from scipy.stats import norm
from sklearn.utils import resample
import plotly.graph_objs as go
import plotly.offline as py
import plotly.colors as colors
from collections import defaultdict
from scipy.ndimage.filters import gaussian_filter1d

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

def _make_desribe_dataframe(value):
    """
    Creation of a statistics table printed with the graph in report.html
    :param value: information measured (series)
    """

    desc = value.describe()
    desc.loc['count'] = desc.loc['count'].astype(int).astype(str)
    desc.iloc[1:] = desc.iloc[1:].applymap(lambda x: '%.2f' % x)
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
#  1D² plots
#


def dsqr_read_count_histogram(result_dict, dataframe_dict_1dsqr, main, my_dpi, result_directory, desc):
    """
    Plots the histogram of 1D² count of the different types of reads:
    FastQ return by MinKNOW
    1D² read return by Guppy
    1D² pass read return by Guppy (Qscore >= 7)
    1D² fail read return by Guppy (Qscore < 7)
    """
    output_file = result_directory + '/' + '_'.join(main.split())

    # Histogram with barcoded read counts
    if 'read.pass.barcoded.count' in dataframe_dict_1dsqr:

        data = {
            '1D² Read Count': result_dict["basecaller.sequencing.summary.1d.extractor.read.count"],
            '1D² Read Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count"],
            '1D² Read Pass Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.count"],
            '1D² Read Pass Barcoded Count': dataframe_dict_1dsqr["read.pass.barcoded.count"],
            '1D² Read Fail Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.count"],
            '1D² Read Fail Barcoded Count': dataframe_dict_1dsqr["read.fail.barcoded.count"]
        }

        colors = ["#54A8FC", "#cb4335 ", "salmon", '#ffa931', "#50c878", "SlateBlue"]

        trace = go.Bar(x=[*data], y=list(data.values()),
                                hovertext=["<b>Total number of reads</b>",
                                           "<b>Number of 1D² reads</b>",
                                           "<b>1D² Reads of qscore > 7</b>",
                                           "<b>1D² Barcoded reads with qscore > 7</b>",
                                           "<b>1D² Reads of qscore < 7</b>",
                                           "<b>1D² Barcoded reads with qscore < 7</b>"],
                                name="Barcoded graph",
                                marker_color=colors,
                                marker_line_color="black",
                                marker_line_width=1.5, opacity=0.9)

        # Array of data for HTML table with barcode reads
        array = np.array(
            #count
            [[result_dict["basecaller.sequencing.summary.1d.extractor.read.count"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.count"],
              dataframe_dict_1dsqr["read.pass.barcoded.count"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.count"],
              dataframe_dict_1dsqr["read.fail.barcoded.count"]],
             #frequencies
             [result_dict["basecaller.sequencing.summary.1d.extractor.read.count.frequency"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count.frequency"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.frequency"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.barcoded.frequency"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.frequency"],
              result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.barcoded.frequency"]]])

        dataframe = pd.DataFrame(array, index=['count', 'frequency'],
                                 columns=["Read count", "1D² Read count","1D² pass", "1D² pass barcoded", "1D² fail", "1D² fail barcoded"])

    # Histogram without barcodes
    else:

        data = {
            'Read Count': result_dict['basecaller.sequencing.summary.1d.extractor.read.count'],
            '1D² Read Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count"],
            'Read Pass Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.count"],
            'Read Fail Count': result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.count"]
        }

        colors = ["#54A8FC", "#cb4335", "salmon", "#50c878"]

        trace = go.Bar(x=[*data], y=list(data.values()),
                       hovertext=["<b>Total number of reads</b>",
                                  "<b>Reads of qscore > 7</b>",
                                  "<b>Barcoded reads with qscore > 7</b>",
                                  "<b>Reads of qscore < 7</b>",
                                  "<b>Barcoded reads with qscore < 7</b>"],
                       name="Barcoded graph",
                       marker_color=colors,
                       marker_line_color="black",
                       marker_line_width=1.5, opacity=0.9)

        # Array of data for HTML table without barcode reads
        array = np.array([[result_dict["basecaller.sequencing.summary.1d.extractor.read.count"],
                           result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count"],
                           result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.count"],
                           result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.count"]],
                          # frequencies
                          [result_dict["basecaller.sequencing.summary.1d.extractor.read.count.frequency"],
                            result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.count.frequency"],
                          result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.pass.frequency"],
                          result_dict["basecaller.sequencing.summary.1dsqr.extractor.read.fail.frequency"]]])

        # Create dataframe with array data
        dataframe = pd.DataFrame(array, index=['count', 'frequency'],
                                 columns=["Read count", "1D² Read count", "1D² pass", "1D² fail"])

    layout = go.Layout(
        hovermode="x",
        title={
            'text': "<b>1D² Read count histogram</b>",
            'y': 0.95,
            'x': 0,
            'xanchor': 'left',
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
                   ),
                   categoryorder="trace"
                   ),
        yaxis=dict(title="<b>Counts</b>",
                   linecolor="black",
                   titlefont=dict(
                       family="Calibri",
                       size=18,
                       color="black"
                   )),
        width=800,
        height=600,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    fig = go.Figure(data=trace, layout=layout)
    div = py.plot(fig,
                  include_plotlyjs=False,
                  output_type='div',
                  auto_open=False,
                  show_link=False)
    py.plot(fig, filename=output_file, output_type="file", include_plotlyjs="directory", auto_open=False)

    # HTML table
    dataframe.iloc[0] = dataframe.iloc[0].astype(int).astype(str)
    dataframe.iloc[1:] = dataframe.iloc[1:].applymap('{:.2f}'.format)
    table_html = pd.DataFrame.to_html(dataframe)

    return main, output_file, table_html, desc, div

def dsqr_read_length_multihistogram(result_dict, sequence_length_1dsqr, main, my_dpi, result_directory, desc):

    output_file = result_directory + '/' + '_'.join(main.split())
    
    all_read = sequence_length_1dsqr.loc[sequence_length_1dsqr >= 10].values
    read_pass = result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.pass.length'].loc[result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.pass.length'] >= 10]
    read_fail = result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.fail.length'].loc[result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.fail.length'] >= 10]
  
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(x=all_read,
                               name='All reads',
                               nbinsx=500,
                               marker_color='#fca311'  # yellow
                               ))

    fig.add_trace(go.Histogram(x=read_pass,
                               name='Pass reads',
                            nbinsx=500,
                               marker_color='#51a96d'  # green
                               ))

    fig.add_trace(go.Histogram(x=read_fail,
                            nbinsx=500,
                               name='Fail reads',
                               marker_color='#d90429'  # red
                               ))
    
    fig.update_layout(
        title={
            'text': "<b>Distribution of 1D² read length</b>",
            'y': 0.95,
            'x': 0,
                    'xanchor': 'left',
                    'yanchor': 'top',
                    'font': dict(
                        family="Open Sans",
                        size=26,
                        color="black")},
        xaxis=dict(
            title="<b>Read length (bp)</b>",
            titlefont_size=16,
            range=[0, 5000]
        ),
        yaxis=dict(
            title='<b>Number of sequences</b>',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=1.02,
            y=0.95,
            title_text="<b>Legend</b>",
            title=dict(font=dict(size=16)),
            bgcolor='white',
            bordercolor='white',
            font=dict(size=15)
        ),
        hovermode='x',
        height=800, width=1400
    )

    div = py.plot(fig,
                  include_plotlyjs=False,
                  output_type='div',
                  auto_open=False,
                  show_link=False)
    py.plot(fig, filename=output_file, output_type="file", include_plotlyjs="directory", auto_open=False)

    table_html = None

    return main, output_file, table_html, desc, div

def dsqr_read_quality_multiboxplot(result_dict, dataframe_dict_1dsqr, main, my_dpi, result_directory, desc):
    """
    Boxplot of PHRED score between read pass and read fail
    Violin plot of PHRED score between read pass and read fail
    """
    output_file = result_directory + '/' + '_'.join(main.split())

    df = pd.DataFrame(
        {"1D²": dataframe_dict_1dsqr["mean.qscore"],
         "1D² pass": result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.pass.qscore'],
         "1D² fail": result_dict['basecaller.sequencing.summary.1dsqr.extractor.read.fail.qscore']
         })

    # If more than 10.000 reads, interpolate data
    if len(df["1D²"]) > 10000:
        dataframe = pd.DataFrame({
        "1D²" : _interpolate(df["1D²"], 1000),
        "1D² pass" : _interpolate(df["1D² pass"], 1000),
        "1D² fail" : _interpolate(df["1D² fail"], 1000)
    })
    else:
        dataframe = df
    names = {"1D²": "All reads",
             "1D² pass": "Read pass",
             "1D² fail": "Read fail"}

    colors = {"1D²": '#fca311',
              "1D² pass": '#51a96d',
              "1D² fail": '#d90429'}

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("<b>PHRED score boxplot</b>",
                                        "<b>PHRED score violin plot</b>"),
                        horizontal_spacing=0.15)

    for column in dataframe.columns:
        fig.append_trace(go.Box(
            y=dataframe[column],
            name=names[column],
            marker=dict(
                opacity=0.3,
                color=colors[column]

            ),
            boxmean=True,
            showlegend=False
        ), row=1, col=1)

        fig.add_trace(go.Violin(y=dataframe[column],
                            name=names[column],
                            meanline_visible=True,
                      marker=dict(color=colors[column])),
                      row=1, col=2)


    fig.update_layout(
        title={
            'text': "<b>1D² PHRED score distribution of all read types</b>",
            'y': 0.95,
            'x': 0.45,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(
                        family="Calibri, sans",
                        size=26,
                        color="black")},
        xaxis=dict(
            title="<b>Read type</b>",
            titlefont_size=16
        ),
        yaxis=dict(
            title='<b>PHRED score</b>',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=1.02,
            y=0.95,
            title_text="<b>Legend</b>",
            title=dict(font=dict(size=16)),
            bgcolor='white',
            bordercolor='white',
            font=dict(size=15)
        ),
        hovermode='x',
        height=800, width=1400
    )

    div = py.plot(fig,
                  include_plotlyjs=False,
                  output_type='div',
                  auto_open=False,
                  show_link=False)
    py.plot(fig, filename=output_file, output_type="file", include_plotlyjs="directory", auto_open=False)

    df = df[["1D²", "1D² pass", "1D² fail"]]
    table_html = pd.DataFrame.to_html(_make_desribe_dataframe(df))

    return main, output_file, table_html, desc, div

def _interpolate(x, npoints:int, y=None, interp_type=None, axis=-1):
    """
    Function returning an interpolated version of data passed as input
    :param x: array of data
    :param npoints: number of desired points after interpolation (int)
    :param y: second array in case of 2D data
    :param interp_type: string specifying the type of interpolation (i.e. linear, nearest, cubic, quadratic etc.)
    :param axis: number specifying the axis of y along which to interpolate. Default = -1
    """
    # In case of single array of data, use
    if y is None:
        return np.sort(resample(x, n_samples=npoints, random_state=1))
    else:
        f = interp1d(x, y, kind=interp_type, axis=axis)
        x_int = np.linspace(min(x), max(x), npoints)
        y_int = f(x_int)
        return pd.Series(x_int), pd.Series(y_int)
