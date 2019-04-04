#!/bin/sh
#BATCH --job-name=JW_test
#SBATCH --error=/u/jompoj/tjob.out.%j
#SBATCH --output=/u/jompoj/tjob.err.%j
#SBATCH --mail-user=jompoj.bjstp@gmail.com
#SBATCH --mail-type=END,FAIL
#SBATCH --partition=long.q
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
# # for OpenMP:
#SBATCH --cpus-per-task=24
#SBATCH --mem=60000
#SBATCH -t 72:0:0
#SBATCH --mem=60G
# # module load singularity#SBATCH --reservation=jompoj_21

#module load sigproc

#cd HTRU-S-LOWLAT/storage/pointings/$2/$3/
#icsh /u/jompoj/header_correct.csh $2\64.fil
#./Parks_header_correct.sh ~/HTRU-S-LOWLAT/storage/pointings/$1/$2/ $1.fil 
#echo $1
#echo $2
#cd /
#mkdir /dev/shm/$2
if [ "$1" == "-h" ]; then
	clear
  	echo "Hello, this is the bash script to summit a job to hercules"
	echo "----------Created by J. Wongpjechauxsorn------------------"
	echo "----------Jompoj@mpifr-bonn.mpg.de------------------------"
	echo "----------------03 April 2019-----------------------------"
	echo "summit.py /full/path/to/filterbank filterbankname /full/path/to/config/files"
  exit 0
fi

if [ "$1" == "--help" ]; then
	clear
        echo "Hello, this is the bash script to summit a job to hercules"
        echo "----------Created by J. Wongpjechauxsorn------------------"
        echo "----------Jompoj@mpifr-bonn.mpg.de------------------------"
        echo "----------------03 April 2019-----------------------------"
        echo "summit.py /full/path/to/filterbank filterbankname /full/path/to/config/files"
  exit 0
fi



singularity exec -H $HOME:/home1 -B /u/jompoj/HTRU-S-LOWLAT/:/home/psr/HTRU-S-LOWLAT /u/jompoj/FFA.img python /home1/FFA-Acceration-pipeline/pipeline_1beam.py /home1/HTRU-S-LOWLAT/storage/pointings/$1/$2/ $1.fil /home1/HTRU-S-LOWLAT/riptide_config/ # $1 for filpath $2 for filname and $3 from path to .yaml
