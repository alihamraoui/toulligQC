<a href="https://raw.githubusercontent.com/GenomicParisCentre/toulligQC/master/Docs/Toulligqc.png"><img src="https://raw.githubusercontent.com/GenomicParisCentre/toulligQC/master/Docs/Toulligqc.png" align="middle" height="50" width="190" > </a> 
[![PyPI version](https://badge.fury.io/py/toulligqc.svg)](https://badge.fury.io/py/toulligqc) [![Downloads](https://pepy.tech/badge/toulligqc)](https://pepy.tech/project/toulligqc) [![Python 3.6](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-360/)  [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) 


ToulligQC is a program written in Python and developped by the [Genomic facility](https://genomique.biologie.ens.fr/) of the [Institute of Biology of the Ecole Normale Superieure (IBENS)](http://www.ibens.bio.ens.psl.eu/).

This program is dedicated to the QC analyses of Oxford Nanopore runs.
Moreover it is adapted to RNA-Seq along with DNA-Seq and it is compatible with 1D² runs.
It can work with Guppy outputs. 
It also needs a single FAST5 file (to catch the flowcell Id and the run date) if a telemetry file is not provided.
Flow cells and kits version are retrieved using the telemetry file.
ToulligQC can take barcoding samples by adding the barcode list as a command line option.

To do so, ToulligQC deals with different file formats: gz, tar.gz, bz2, tar.bz2 and .fast5 to retrieve a FAST5 information.
This tool will produce a set of graphs, statistic files in txt format and a HTML report.

<a href="https://htmlpreview.github.com/?https://github.com/GenomicParisCentre/toulligQC/blob/master/Docs/report_v1.2_1dsqr.html" rel="some text">![Report preview](https://raw.githubusercontent.com/GenomicParisCentre/toulligQC/master/Docs/images.png)</a>

Click on the [image](https://htmlpreview.github.com/?https://github.com/GenomicParisCentre/toulligQC/blob/master/Docs/report.html) to see an report example! 

## Authors / Support

Karine Dias, Bérengère Laffay, Lionel Ferrato-Berberian, Laurent Jourdren, Sophie Lemoine and Stéphane Le Crom.

Support is availlable on [GitHub issue page](https://github.com/GenomicParisCentre/toulligQC/issues) and at **toulligqc** **at** **bio.ens.psl.eu**.

## Table of Contents

* 1.[Get ToulligQC](#get-toulligqc)
  * 1.1 [Local installation](#local-installation)
  * 1.2 [PyPi package installation](#pypi-installation) 
  * 1.3 [Docker](#docker)
     *  [Docker image recovery](#docker-image-recovery)    
     *  [Launching Docker image with docker run](#launching-Docker-image-with-docker-run)
     
* 2.[Usage](#usage)
  * 2.1 [Command line](#command-line)
      * [Options](#options)
      * [Examples](#examples)
  * 2.2 [Sample data](#sample-data)
  
* 3.[Output](#output) 


<a name="get-toulligqc"></a>
## 1. Get ToulligQC 
<a name="local-installation"></a>
### 1.1 Local
This option is also suitable if you are interested in further developments of the package, but requires a little bit more hands-on. Install the dependencies required and clone the repository locally.

```bash
$ git clone https://github.com/GenomicParisCentre/toulligQC.git
# X.X here is the version of ToulligQC to install
$ git checkout vX.X
$ cd toulligqc && python3 setup.py build install
```

* **Requirements**

ToulligQC is written with Python 3.
To run ToulligQC without Docker, you need to install the following Python modules:

* matplotlib
* plotly
* seaborn
* h5py
* pandas
* numpy
* scipy
* scikit-learn


<a name="pypi-installation"></a>
### 1.3 Using a PyPi package

ToulligQC can be more easlily installed with a pip package availlable on the PyPi repository. The following command line  will install the latest version of ToulligQC: 
```bash
$ pip3 install toulligqc
```

<a name="docker"></a>
### 1.3 Using Docker
ToulligQC and its dependencies are available through a Docker image. To install docker on your system, go to the Docker website(https://docs.docker.com/engine/installation/). 
Even if Docker can run on Windows or macOS virtual machines, we recommend to run ToulligQC on a Linux host. 
<a name="docker-image-recovery"></a>
* ####  Docker image recovery
An image of ToulligQC is hosted on the Docker hub on the genomicpariscentre repository(genomicpariscentre/toulligqc).

```bash
$ docker pull genomicpariscentre/toulligqc:latest
```


<a name="launching-docker-image-with-a-shell-script"></a>
* ####  Launching Docker image with docker run

```
$ docker run -ti \
             -u $(id -u):$(ig -g) \
             --rm \  
             -v /path/to/basecaller/sequencing/summary/file:/path/to/basecaller/sequencing/summary/file \
             -v /path/to/basecaller/sequencing/telemetry/file:/path/to/basecaller/telemetry/summary/file \
             -v /path/to/result/directory:/path/to/result/directory \
             toulligqc:latest 
```
<a name="usage"></a>
## 2. Usage
<a name="command-line"></a>

To run ToulligQC, you need one of your initial Fast5 ONT file (or the telemetry file) and you may also need an Albacore output directory to get the ``` Fastq files ```  and ``` the sequencing_summary.txt ```.
ToulligQC can perform analyses on your data if the directory is organise as following:

```
RUN_ID
├── sequencing_summary.txt
├── pipeline.log
├── configuration.cfg
├── sequencing_telemetry.js
└── workspace
    └── run_id.fastq
```

or 

```
RUN_ID
├── sequencing_summary.txt
├── pipeline.log
├── configuration.cfg
├── sequencing_telemetry.js
└── workspace
    └── pass
        └── run_id.fastq
```
for 1D² analysis

```
RUN_ID
├── sequencing_summary.txt
├── pipeline.log
├── configuration.cfg
├── workspace
│   └── pass
│       └── run_id.fastq
└── 1dsq_analysis
    └── sequencing_1dsq_summary.txt
 ```

### 2.1 Command line

<a name="options"></a>
* #### Options

General Options:
```
usage:  [-h] [-n REPORT_NAME] [-f FAST5_SOURCE]
        [-a SEQUENCING_SUMMARY_SOURCE] [-d SEQUENCING_SUMMARY_1DSQR_SOURCE]
        [-t TELEMETRY_SOURCE]
        [-o OUTPUT] [-b] [-l BARCODES] [--quiet]
        [--version]

optional arguments:
  -h, --help                                                       show this help message and exit
  -n REPORT_NAME,
  --report-name REPORT_NAME                                        Report name
  -f FAST5_SOURCE,
  --fast5-source FAST5_SOURCE                                      Fast5 file source
  -a SEQUENCING_SUMMARY_SOURCE,
  --sequencing-summary-source SEQUENCING_SUMMARY_SOURCE,           Basecaller sequencing summary source
  -d SEQUENCING_SUMMARY_1DSQR_SOURCE,
  --sequencing-summary-1dsqr-source SEQUENCING_SUMMARY_1DSQR_SOURCE, Basecaller 1dsq summary source
  -t TELEMETRY_SOURCE,
   --telemetry-source TELEMETRY_SOURCE                             Telemetry file source
  -o OUTPUT,
  --output OUTPUT                                                  Output directory
  -b,
  --barcoding                                                      Barcode usage
  -l BARCODES,
  --barcodes BARCODES                                              Coma separated barcode list
  --quiet                                                          Quiet mode
  --version                                                        show program's version number and exit

```

 <a name="example"></a>
 * #### Examples
 

Example with optional arguments:

```bash
$ toulligqc --report-name FAF0256 \
            --telemetry-source /path/to/basecaller/output/sequencing_telemetry.js \
            --sequencing-summary-source /path/to/basecaller/output/sequencing_summary.txt \
            --sequencing-summary-1dsqr-source /path/to/basecaller/output/sequencing_1dsqr_summary.txt \ (optional)
            --output /path/to/output/directory \
```


Example with optional arguments to deal with barcoded samples:

```bash
$ toulligqc --report-name FAF0256 \
            --barcoding \
            --telemetry-source /path/to/basecaller/output/sequencing_telemetry.js \
            --sequencing-summary-source /path/to/basecaller/output/sequencing_summary.txt \
            --sequencing-summary-source /path/to/basecaller/output/barcoding_summary_pass.txt \         (optional)
            --sequencing-summary-source /path/to/basecaller/output/barcoding_summary_fail.txt \         (optional)
            --sequencing-summary-1dsqr-source /path/to/basecaller/output/sequencing_1dsqr_summary.txt \ (optional)
            --sequencing-summary-1dsqr-source /path/to/basecaller/output/barcoding_summary_pass.txt \   (optional)
            --sequencing-summary-1dsqr-source /path/to/basecaller/output/barcoding_summary_fail.txt \   (optional)
            --output /path/to/output/directory \
            --barcodes BC1,BC2,BC3
``` 


<a name="sample-data"></a>
### 2.2 Sample data

We provide [sample raw data](http://outils.genomique.biologie.ens.fr/leburon/downloads/toulligqc-example/toulligqc_demo_data.tar.bz2) that can be used to launch and evaluate our software.
This demo data has been generated using a MinION MKIb with a R9.4.1 flowcell (FLO-MIN106) in 1D (SQK-LSK108) mode with barcoded samples (BC01, BC02, BC03, BC04, BC05 and BC07).
Data acquisition was performed using MinKNOW 1.11.5 and basecalling/demultiplexing was completed using Guppy 3.2.4.

* First download and uncompress sample data:
```bash
$ wget http://outils.genomique.biologie.ens.fr/leburon/downloads/toulligqc-example/toulligqc_demo_data.tar.bz2
$ tar -xzf toulligqc_demo_data.tar.bz2
$ cd toulligqc_demo_data
```
* Then, you can launch the ToulligQC analysis of the demo data with the `run-toulligqc-with-docker.sh` script if you want to use a Docker container:
```bash
$ ./run-toulligqc-with-docker.sh
```
* Or with `run-toulligqc.sh` script if ToulligQC is already installed on your system:
```bash
$ ./run-toulligqc.sh
```
* Of course, you can also launch manually ToulligQC on the sample data with the following command line:
```bash
$ toulligqc \
    --report-name               ToulligQC_Demo_Data \
    --barcoding \
    --telemetry-source          sequencing_telemetry.js \
    --sequencing-summary-source sequencing_summary.txt \
    --sequencing-summary-source barcoding_summary_pass.txt \
    --sequencing-summary-source barcoding_summary_fail.txt \
    --barcodes                  BC01,BC02,BC03,BC04,BC05,BC07 \
    --output                    output
```

With this scripts or command line, ToulligQC will create an `output` directory with output HTML report.
More information about this sample data and scripts can be found in the `README` file of the tar archive.



## 3.Output



ToulligQC gives different informations such as:

Found in the HTML report:
- A graph allowing to locate potential flowcell spatial biaises
- A read length histogram adapted to transcripts
- A graph checking that the sequencing was homogeneous during a run
- Graphs representing the phred score frequency
- A set of graphs providing quality, length informations and read counts for each barcode

Found in the report.data log file: 
- The information about ToulligQC execution
- The environment variables
- Full statistics are provided for complementary analyses if needed : The information by modules is retained in a key-value form, the prefix of a key being the report data file id of the module
- The nucleotide rate per read or per read and per barcode if FastQ files have been processed 

Organised in a output directory  like this : 
   
```
RUN_ID
├── report.html
├── statistics
│   └── report.data                                                                                                                                                                                                                                              
└── images
    └── graphes.png
```
