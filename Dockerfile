FROM python:3.8

# Initiation of system
RUN export MCR_CACHE_VERBOSE=true
RUN apt-get update -y \
 && apt-get install -y wget unzip libxext-dev libxt-dev libxmu-dev libglu1-mesa-dev libxrandr-dev build-essential \
 && mkdir -p /tmp_mcr \
 && cd /tmp_mcr \
 && wget https://ssd.mathworks.com/supportfiles/downloads/R2022b/Release/9/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2022b_Update_9_glnxa64.zip \
 && unzip MATLAB_Runtime_R2022b_Update_9_glnxa64.zip \
 && ./install -destinationFolder /usr/local/MATLAB/MATLAB_Runtime/ -mode silent -agreeToLicense yes \
 && mkdir -p /computation \
 && mkdir /computation/groupica_v4.0.4.11 \
 && rm -rf /tmp_mcr \
 && wget -P /computation/groupica_v4.0.4.11/ https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/bids/v4.0.5.2M2022b/groupica
# groupica is compiled using MATLAB version R2022b.

# Environment variables
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu/:/usr/local/MATLAB/MATLAB_Runtime/R2022b/:/usr/local/MATLAB/MATLAB_Runtime/R2022b/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/R2022b/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/R2022b/sys/os/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/R2022b/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:/usr/local/MATLAB/MATLAB_Runtime/R2022b/sys/java/jre/glnxa64/jre/lib/amd64/server:/usr/local/MATLAB/MATLAB_Runtime/R2022b/sys/java/jre/glnxa64/jre/lib/amd64
ENV XAPPLRESDIR=/usr/local/MATLAB/MATLAB_Runtime/R2022b/X11/app-defaults
ENV MCR_CACHE_VERBOSE=true
ENV MCR_CACHE_ROOT=/tmp
ENV PATH=$PATH:/computation/groupica_v4.0.4.11:
ENV MATLAB_VER=R2022b
ENV GICA_VER=v4.0.5.2
ENV GICA_INSTALL_DIR=/computation/groupica_v4.0.4.11

# Building entrypoint
WORKDIR /computation
RUN chmod +x /computation/groupica_v4.0.4.11/groupica
#ENTRYPOINT ["/app/run.sh"]














#FROM --platform=linux/amd64 python:3.8-slim
#ENV MCRROOT=/usr/local/MATLAB/MATLAB_Runtime/v91
#ENV MCR_CACHE_ROOT=/tmp

#RUN apt-get clean && apt-get update && apt-get install -y \
#    zip unzip wget \
#    libx11-dev libxcomposite-dev \
#    libxcursor-dev libxdamage-dev libxext-dev \
#    libxfixes-dev libxft-dev libxi-dev \
#    libxrandr-dev libxt-dev libxtst-dev \
#    libxxf86vm-dev libasound2-dev libatk1.0-dev \
#    libcairo2-dev gconf2 \
#    libsndfile1-dev libxcb1-dev libxslt-dev \
#    curl \
#    libgtk-3-dev \ 
#    build-essential \
#    libatlas-base-dev \
#    liblapack-dev \
#    gfortran \
#    && rm -rf /var/lib/apt/lists/*

#RUN mkdir /tmp/mcr_installer && \
#    cd /tmp/mcr_installer && \
#    wget http://ssd.mathworks.com/supportfiles/downloads/R2016b/deployment_files/R2016b/installers/glnxa64/MCR_R2016b_glnxa64_installer.zip && \
#    unzip MCR_R2016b_glnxa64_installer.zip && \
#    ./install -mode silent -agreeToLicense yes && \
#    rm -Rf /tmp/mcr_installer

# Copy the current directory contents into the container
#WORKDIR /app
#COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
#RUN pip install -r requirements.txt
COPY ./groupicatv4.0b/icatb/nipype-0.10.0/nipype/interfaces/gift /usr/local/lib/python3.8/site-packages/nipype/interfaces/gift

#RUN chmod -R a+wrx /app
#RUN chmod -R a+wrx /usr/local/MATLAB/MATLAB_Runtime/v91

#ENV MCRROOT=/usr/local/MATLAB/MATLAB_Runtime/v91
#ENV MCR_CACHE_ROOT=/computation/mcrcache

# Copy the current directory contents into the container
#WORKDIR /computation
#COPY requirements.txt /computation
COPY coinstac_python_requirements.txt /computation

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r coinstac_python_requirements.txt
#RUN pip install -r requirements.txt
#RUN pip install awscli s3utils
#RUN pip install nipy==0.5.0
#RUN pip install -U numpy
#RUN pip install nipy

#RUN mkdir -p /computation/mcrcache

#RUN mkdir /output

# Add new version of GIFT at 09/07/2023
# GIFT version 4.0.4.11, including sliced masks still running on MATLAB 2016b
#RUN wget -P /computation/groupica_v4.0.4.11 https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/stand_alone/coinstac/082223/coinstac-giftv4.0.4.11_Lnx2016b/groupica
#RUN wget -P /computation/groupica_v4.0.4.11 https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/stand_alone/coinstac/082223/coinstac-giftv4.0.4.11_Lnx2016b/run_groupica.sh
#RUN wget -P /computation/groupica_v4.0.4.11 https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/stand_alone/coinstac/082223/coinstac-giftv4.0.4.11_Lnx2016b/requiredMCRProducts.txt
#RUN wget -P /computation/groupica_v4.0.4.11 https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/stand_alone/coinstac/082223/coinstac-giftv4.0.4.11_Lnx2016b/readme.txt
#RUN wget -P /computation/groupica_v4.0.4.11 https://trends-public-website-fileshare.s3.amazonaws.com/public_website_files/software/gift/software/stand_alone/coinstac/082223/coinstac-giftv4.0.4.11_Lnx2016b/mccExcludedFiles.log

COPY ./run_groupica.sh /computation/groupica_v4.0.4.11/
#RUN (timeout 20s /computation/groupica_v4.0.4.11/run_groupica.sh /usr/local/MATLAB/MATLAB_Runtime/v91/; exit 0)

COPY ./coinstac_node_ops /computation/coinstac_node_ops
COPY ./coinstac_regression_vbm /computation/coinstac_regression_vbm
COPY ./coinstac_spatially_constrained_ica /computation/coinstac_spatially_constrained_ica
COPY ./local_data /computation/local_data

COPY ./*.py /computation/


RUN chmod -R a+wrx /computation
ENV PYTHONPATH=/computation
ENV PYTHONPATH=${PATH}:/computation

CMD ["python", "/computation/entry.py"]
