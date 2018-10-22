#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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
# For more information on the ToulligQC project and its aims,
# visit the home page at:
#
#      https://github.com/GenomicParisCentre/toulligQC
#
# First author: Lionel Ferrato-Berberian
# Maintainer: Bérengère Laffay
# Since version 0.1
#
# Toulligqc.py: Main's constitution
# 1. It scans the user command line and creates the output directory
# 2. Depending on the options selected, it creates a list of the necessary extractors
# 3. For each extractor, it successively call the _check_conf, init, extract, graph_generation and clean methods
# to fill in the result_dict dictionary
# 4. In the case of barcoded sequencing, it defines the selected barcodes in the samplesheet file
# 5. It uses all the information collected to generate a qc in the form of a htl-report and a report.data file

import matplotlib
matplotlib.use('Agg')
import shutil
import sys
import csv
import re
import argparse
import os
import time
import platform as pf
import tempfile as tp
from toulligqc import toulligqc_extractor
from toulligqc import report_data_file_generator
from toulligqc import html_report_generator
from toulligqc import version
from pathlib import Path
from toulligqc import configuration


def _parse_args(config_dictionary):
    """
    Parsing the command line
    :return: config_dictionary containing the paths containing in the configuration file or specify by line arguments
    """

    home = str(Path.home())
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf-file", help="Specify config file", metavar="FILE")
    parser.add_argument("-n", "--report-name", action='store', dest="report_name", help="Report name", type=str)
    parser.add_argument('-f', '--fast5-source', action='store', dest='fast5_source', help='Fast5 file source')
    parser.add_argument('-a', '--albacore-summary-source', action='store', dest='albacore_summary_source',
                        help='Albacore summary source')
    parser.add_argument('-d', '--albacore-1dsqr-summary-source', action='store', dest='albacore_1dsqr_summary_source',
                        help='Albacore 1dsq summary source', default=False)
    parser.add_argument('-p', '--albacore-pipeline-source', action='store', dest='albacore_pipeline_source',
                        help='Albacore pipeline source', default=False)
    parser.add_argument('-q', '--fastq-source', action='store', dest='fastq_source',
                        help='Fastq file source', default=False)
    parser.add_argument('-o', '--output', action='store', dest='output', help='Output directory')
    parser.add_argument('-s', '--samplesheet-file', action='store', dest='sample_sheet_file',
                        help='Path to sample sheet file')
    parser.add_argument("-b", "--barcoding", action='store_true', dest='is_barcode', help="Barcode usage",
                        default=False)
    parser.add_argument("--quiet", action='store_true', dest='is_quiet', help="Quiet mode",
                        default=False)
    parser.add_argument("-l", "--devel-quick-launch", action='store_true', dest='is_quicklaunch',
                        help=argparse.SUPPRESS, default=False)
    parser.add_argument('--version', action='version', version=version.__version__)

    # Parsing lone arguments and assign each argument value to a variable
    argument_value = parser.parse_args()
    conf_file = argument_value.conf_file
    fast5_source = argument_value.fast5_source
    albacore_summary_source = argument_value.albacore_summary_source
    albacore_1dsqr_summary_source = argument_value.albacore_1dsqr_summary_source
    albacore_pipeline_source = argument_value.albacore_pipeline_source
    fastq_source = argument_value.fastq_source
    report_name = argument_value.report_name
    is_barcode = argument_value.is_barcode
    result_directory = argument_value.output
    sample_sheet_file = argument_value.sample_sheet_file
    is_quiet = argument_value.is_quiet
    is_quicklaunch = argument_value.is_quicklaunch

    config_dictionary['report_name'] = report_name

    # Checking of the presence of a configuration file
    if argument_value.conf_file:
        config_dictionary.load(conf_file)
    elif os.path.isfile(home + '/.toulligqc/config.txt'):
        config_dictionary.load(home + '/.toulligqc/config.txt')

    # Rewrite the configuration file value if argument option is present
    source_file = {
        ('fast5_source', fast5_source),
        ('albacore_summary_source', albacore_summary_source),
        ('albacore_1dsqr_summary_source', albacore_1dsqr_summary_source),
        ('albacore_pipeline_source', albacore_pipeline_source),
        ('fastq_source', fastq_source),
        ('result_directory', result_directory),
        ('sample_sheet_file', sample_sheet_file),
        ('barcoding', is_barcode),
        ('quiet', is_quiet),
        ('is_quicklaunch', is_quicklaunch)
    }

    # Put arguments values in configuration object
    for key, value in source_file:
        if value:
            config_dictionary[key] = value

    # Directory paths must ends with '/'
    for key, value in config_dictionary.items():
        if type(value) == str and os.path.isdir(value) and (not value.endswith('/')):
            config_dictionary[key] = value + '/'

    # Convert all configuration values in strings
    for key, value in config_dictionary.items():
        config_dictionary[key] = str(value)

    return config_dictionary


def _check_conf(config_dictionary):
    """
    Check the configuration
    :param config_dictionary: configuration dictionary containing the file or directory paths
    """

    if 'fast5_source' not in config_dictionary or not config_dictionary['fast5_source']:
        sys.exit('The fast5 source argument is empty')

    if 'albacore_summary_source' not in config_dictionary or not config_dictionary['albacore_summary_source']:
        sys.exit('The albacore summary source argument is empty')

    if config_dictionary['barcoding'] == 'True':
        if not config_dictionary['sample_sheet_file']:
            sys.exit('The sample sheet source argument is empty')

    if 'result_directory' not in config_dictionary or not config_dictionary['result_directory']:
        sys.exit('The output directory argument is empty')

    # Create the root output directory if not exists
    if not os.path.isdir(config_dictionary['result_directory']):
        os.makedirs(config_dictionary['result_directory'])

    # Define the output directory
    config_dictionary['result_directory'] = \
        config_dictionary['result_directory'] + ('/' + config_dictionary['report_name'] + '/')

    if os.path.isdir(config_dictionary['result_directory']):
        shutil.rmtree(config_dictionary['result_directory'], ignore_errors=True)
        os.makedirs(config_dictionary['result_directory'])
    else:
        os.makedirs(config_dictionary['result_directory'])


def _get_barcode(samplesheet):
    """
    Get the barcode from the samplesheet file given in input
    :param samplesheet: sample sheet directory
    :return: sorted list containing the barcode indicated in the sample sheet
    """
    barcode_file = samplesheet

    set_doublon = set()

    with open(barcode_file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')

        for row in spamreader:

            # Do not handle comment lines
            if row[0].startswith('#'):
                continue

            pattern = re.search(r'BC(\d{2})', row[0])

            if pattern:
                barcode = 'barcode{}'.format(pattern.group(1))
                set_doublon.add(barcode)

    return sorted(set_doublon)


def _create_output_directories(config_dictionary):
    """
    Create output directories
    :param config_dictionary: configuration dictionary
    """
    image_directory = config_dictionary['result_directory'] + 'images/'
    statistic_directory = config_dictionary['result_directory'] + 'statistics/'
    os.makedirs(image_directory)
    os.makedirs(statistic_directory)


def _welcome(config_dictionary):
    """
    Print welcome message
    """
    _show(config_dictionary, "ToulligQC version " + config_dictionary['app.version'])


def _show(config_dictionary, msg):
    """
    Print a message on the screen
    :param config_dictionary: configuration dictionary
    :param msg: message to print
    """
    if 'quiet' not in config_dictionary or config_dictionary['quiet'].lower() != 'true':
        print(msg)


def _format_time(t):
    """
    Format a time duration for humans
    :param t: time in milliseconds
    :return: a string with the duration
    """

    return time.strftime("%H:%M:%S", time.gmtime(t))


def _extractors_list_and_result_dictionary_initialisation(config_dictionary, result_dict):
    """
    Initialization of the result_dict with the OS parameters and the extractors list
    :param config_dictionary: details from command user line
    :return: result_dict dictionary and extractors list
    """
    result_dict['toulligqc.info.username'] = os.environ.get('USERNAME')
    result_dict['toulligqc.info.user.home'] = os.environ['HOME']
    result_dict['toulligqc.info.temporary.directory'] = tp.gettempdir()
    result_dict['toulligqc.info.operating.system'] = pf.processor()
    result_dict['toulligqc.info.python.version'] = pf.python_version()
    result_dict['toulligqc.info.python.implementation'] = pf.python_implementation()
    result_dict['toulligqc.info.hostname'] = os.uname()[1]
    result_dict['toulligqc.info.report.name'] = config_dictionary['report_name']
    result_dict['toulligqc.info.start.time'] = time.strftime("%x %X %Z")
    result_dict['toulligqc.info.command.line'] = sys.argv
    result_dict['toulligqc.info.executable.path'] = sys.argv[0]
    result_dict['toulligqc.info.version'] = config_dictionary['app.version']
    result_dict['toulligqc.info.output.dir'] = config_dictionary['result_directory']
    result_dict['toulligqc.info.barcode.option'] = "False"
    if config_dictionary['barcoding'].lower() == 'true':
        result_dict['toulligqc.info.barcode.option'] = "True"
        result_dict['toulligqc.info.barcode.selection'] = _get_barcode(config_dictionary['sample_sheet_file'])
    return result_dict


def dependancies_version(result_dict):
    for name, module in sorted(sys.modules.items()):
        if hasattr(module, '__version__'):
            result_dict['toulligqc.info.dependancy.' + name + '.version'] = module.__version__
        elif hasattr(module, 'VERSION'):
            result_dict['toulligqc.info.dependancy.' + name + '.version'] = module.VERSION
    for name, value in os.environ.items():
        result_dict['toulligqc.info.env.' + name] = value


def main():
    """
    Main function creating graphs and statistics
    """
    config_dictionary = configuration.ToulligqcConf()
    _parse_args(config_dictionary)
    _check_conf(config_dictionary)
    _create_output_directories(config_dictionary)

    if not config_dictionary:
        sys.exit("Error, dico_path is empty")

    if config_dictionary['barcoding'].lower() == 'true':
        sample_sheet_file = config_dictionary['sample_sheet_file']
        barcode_selection = _get_barcode(sample_sheet_file)
        config_dictionary['barcode_selection'] = barcode_selection
        if barcode_selection == '':
            sys.exit("Sample sheet is empty")
    else:
        config_dictionary['barcode_selection'] = ''

    if os.path.isdir(config_dictionary['albacore_summary_source']):
        config_dictionary['albacore_summary_source'] = config_dictionary['albacore_summary_source'] \
                                                       + config_dictionary['report_name'] + '/sequencing_summary.txt'


    # Print welcome message
    _welcome(config_dictionary)

    # Configuration checking and initialisation of the extractors
    _show(config_dictionary, "* Initialize extractors")

    extractors_list = []
    result_dict = {'unwritten.keys': ['unwritten.keys']}
    result_dict = _extractors_list_and_result_dictionary_initialisation(config_dictionary, result_dict)
    dependancies_version(result_dict)

    toulligqc_extractor.ToulligqcExtractor.init(config_dictionary)
    toulligqc_extractor.ToulligqcExtractor.extract(config_dictionary, extractors_list, result_dict)

    graphs = []
    qc_start = time.time()

    # Information extraction about statistics and generation of the graphs
    for extractor in extractors_list:
        extractor.check_conf()
        extractor.init()
        _show(config_dictionary, "* Start {0} extractor".format(extractor.get_name()))

        extractor_start = time.time()
        extractor.extract(result_dict)
        graphs.extend(extractor.graph_generation(result_dict))
        extractor.clean(result_dict)
        extractor_end = time.time()
        extract_time = extractor_end - extractor_start
        result_dict['{}.duration'.format(extractor.get_report_data_file_id())] = round(extract_time, 2)

        _show(config_dictionary, "* End of {0} extractor (done in {1})".format(extractor.get_name(),
                                                                               _format_time(extract_time)))

    # HTML report and statistics file generation
    _show(config_dictionary, "* Write HTML report")
    html_report_generator.html_report(config_dictionary, result_dict, graphs)

    qc_end = time.time()
    result_dict['toulligqc.info.execution.duration'] = round((qc_end - qc_start), 2)

    if config_dictionary['is_quicklaunch'].lower() != 'true':
        _show(config_dictionary, "* Write statistics files")
        report_data_file_generator.statistics_generator(config_dictionary, result_dict)
    _show(config_dictionary, "* End of the QC extractor (done in {})".format(_format_time(qc_end - qc_start)))


if __name__ == "__main__":
    main()
