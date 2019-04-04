
 

This is an FFA pipeline for HTRU_south_low_lat which is still under development.

If you want to use it please do this,

1 git clone https://gitlab.mpifr-bonn.mpg.de/jompoj/FFA_pipeline.git

2 setting parameter in all .yaml file (espically downsampling factor!! the sampling time * bin_mins need to be bigger than minimum period)

3 Put your birdy list file as blist in the folder with yaml files 

4 run python python pipeline_1beam.py $PATH_TO_FILFILE FILFILENAME PATH_TO_ALL_YAML

****Right now I still have not implemented way to calculate acceration step yet  