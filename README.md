toulligQC
==========
This program is dedicated to the QC analyses of Oxford Nanopore runs, barcoded or not.
It requires a design file describing the barcodes used if the run was barcoded.
It partly relies on log file produced during the basecalling process by the Oxford Nanopore basecaller, Albacore.
This program will produce a set of graphs and statistic files


# Table of content

 1.Python module

  * [basecalling_stat_plotter1D](#basecalling_stat_plotter1D)

  * [getter1D](#getter1D)

  * [fast5_data_extractor](#fast5_data_extractor)

2.[example](#example)

3.[requirements](#requirements)

Python module
==============

## 1)basecalling_stat_plotter1D


This module provides support for create a report as a word document and a pdf file in the images directory. Files containing statistics for each barcode is provided in the statistics directory.

Several python files are provided:

 #### class basecalling_stat_plotter1D
 
   returns a set of graphs and statistics for the creation of report as well as statistics for the statistics files.

      barcode_meanqscore
     Write the mean qscore extracted from the log file provided by albacore in the statistics files according to the barcodes

     run_date
      Returns the date of a Minion run from the log file provided by albacore in researching the date in the run id field

     stat_generation
        Generates a dictionary of statistics such as quartile, std for the creation of a log file like aozan from the          summary log provided by albacore

    barcode_percentage_pie_chart
        Plots the barcode pie chart from the selection of barcodes

    reads_size_selection_barcode
        Plots the histogram of reads size by bins of 100 for the barcode choosed from design file

    barcode_read_length_histogram
        Gets statistics on the fastq from the file containing the fastq bz2 files decompressed

    read_count_histogram
        Plots the count histograms of count  of the different types of reads eventually available in a Minion run: template, complement, full_2D.

    read_quality_boxplot
        Plots a boxplot of reads quality

    channel_count_histogram
        Plots an histogram of the channel count according to the channel numbe

    read_number_run
        Plots the reads produced along the run against the time(in hour)

    minion_flowcell_layout
        Represents the layout of a minion flowcell

    plot_performance(pore_measure)
        Plots the channels occupancy by the reads
        parameters: pore_measure: reads number per pore

    get_barcode_selection
       Returns the selection of barcode from the design file

    statistics_dataframe
        Presents statitstics retrieved from statistics files in the statistics directory for each barcode as a dataframe to make the reading easier.


## 2)getter1D

This module provided informations about the minion runs and the fastq sequences. The five first methods take a h5py file as an argument.

### get_MinknowVersion
      Gets the Minknow version from fast5 file

### get_FlowcellId
      Gets the flowcell id from fast5 file

### get_Hostname
      Gets the hostname from fast5 file

### get_NumMinION
      Gets the number of Minion run

### get_ProtocolRunId
      Gets the run id protocol from fast5 file

### get_barcode()
      Gets the barcode from a file given in input

### get_fastq(selection)
      Gets the fastq sequence

## 3)fast5_data_extractor
Creates a dataframe from a collection of fast5 files. 
Needs the fast5 file directory as input (where fast5 files are stored) and returns a tuple with a set of information
about the fast5 files.

### fast5_data_extractor(fast5_file_directory)
      Creates a dataframe from collections of fast5 files
      return : tuple with different informations about fast5 files

### write_data(tuple_array)
    Writes the data related to the fast5 files in a tsv file from the tuple array created by the fast5_data_extractor
    function 

### read_data(data_file)
    Reads the tsv file containing the fast5 file data created previously by the write_data

example
==========

First of all a set of files are required before the python scripts run:

* a design file named design.csv which describes the different sample barcoded. It's only the first column which is important. The rest of files may be modified at your convenience. An example might be:

index | Reads | Description | Date | FastqFormat | RepTechGrou
------- | ------- | ------------- | -------- | -------------- | ---------------
 2015341_BC01 | dnacpc14_20170328_FNFAF04250_MN17734_mux_scan_1D_validation_test1_45344_barcode01_template.fastq.bz2 |  WT1_BC01 | 2017-01-24 | fastq-sanger | WT1_BC01

An important thing is that the barcodes must be written with BC followed by two digits (BC01, BC02,....,BC80)

* a configuration file: this file includes the path at your different files. These files numbered four in the following order:

 * the directory where the fast5 are holded
 * the file where the Albacore log is placed
 * the directory where the fastq are located in the form of bz2 files
 * the design file mentioned above

This file must be in the following form with these names:

[config]

fast5.directory=path to our fast5 directory

log.file= path to our log file

bz2.fastq.directory=path to fastq files in the form of bz2 files

design_file=path to design file

The first line is important for the python script because they use a parser in order to parse the configuration file and mustn't be modified

Once the files described above are ready an placed in the dcripts directory, we can launch the programm by means of the following command :
        * python3 main.py name_sample * where name sample represents the Minion run's sample name.


Afterwards two directories are created:

   * statistics containing statistics for each barcode
   * images containing the images generated by the script. It will serve to create the report.

Then two files are also created:

  *  a report .docx containing a set of graphs generated by the script
  *  a pdf file which contains the different graph in the case of some figures will be unreadable or not present in the docx

A file named layout.pdf is necessary. That file represent the layout of a minion flowcell. It must be in the directory where the script is executed. This latter is present in the git directory.

If you use docker you must launch  the program like that:

        docker build -t genomicpariscentre/toulligQC .
        docker run -ti -v mountpoint ... genomicpariscentre/toulligQC bash


For the platform:

The use of shell script is necessary so as to translate the path contained in the configuration file in the true paths corresponding with the server.
For example /home/toto/ in import/rhodos11

This shell script creates another configuration file named docker_config which musn't be modified.

When the shell scripts is runned, it runs docker.

A few rules must be respected when you use this shell scripts:

* don't put / to the end of each line
* modify the file1 and the file2 variables according to your system but don't modify the end of these two variables. Always put config.txt and docker_config.txt
* a file named docker_config.txt is created. Don't modify it.                                                                                                                       

requirements
===============

Some modules needed be installed in order to the script is executed:

* matplotlib
* h5py
* pandas
* seaborn
* numpy
* PyPDF2
* csv
* python-docx
* biopython

This script is written in python3 and not in python2.

A docker file was created containing these modules with the correct version of python.

A config file was created which must be modified according to the configuration of its system.
