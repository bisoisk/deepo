# -*- coding: utf-8 -*-
from .__module__ import Module, dependency, source
from .tools import Tools
from .boost import Boost
from .python import Python
from .opencv import Opencv


@dependency(Tools, Python, Boost, Opencv)
@source('git')
class Caffe(Module):

    def build(self):
        pyver = self.manager.ver(Python)
        return r'''
            $GIT_CLONE https://github.com/NVIDIA/nccl ~/nccl && \
            cd ~/nccl && \
            make -j"$(nproc)" install && \

            $GIT_CLONE https://github.com/BVLC/caffe ~/caffe && \
            cp ~/caffe/Makefile.config.example ~/caffe/Makefile.config && \
            sed -i 's/# USE_CUDNN/USE_CUDNN/g' ~/caffe/Makefile.config && \
        '''.rstrip() + (
            '' if pyver == '2.7' else r'''
            sed -i 's/# PYTHON_LIBRARIES/PYTHON_LIBRARIES/g' '''
            + r'''~/caffe/Makefile.config && \
            '''.rstrip()
        ) + r'''
            sed -i 's/# WITH_PYTHON_LAYER/WITH_PYTHON_LAYER/g' ''' \
          + r'''~/caffe/Makefile.config && \
            sed -i 's/# OPENCV_VERSION/OPENCV_VERSION/g' ''' \
          + r'''~/caffe/Makefile.config && \
            sed -i 's/# USE_NCCL/USE_NCCL/g' ~/caffe/Makefile.config && \
        '''.rstrip() + (r'''
            sed -i 's/2\.7/3\.5/g' ~/caffe/Makefile.config && \
            ''' if pyver == '3.5' else (
            r'''
            sed -i 's/2\.7/3\.6/g' ~/caffe/Makefile.config && \
            sed -i 's/3\.5/3\.6/g' ~/caffe/Makefile.config && \
            ''' if pyver == '3.6' else
            r'''
            '''
        )).rstrip() + r'''
            sed -i 's/\/usr\/lib\/python/\/usr\/local\/lib\/python/g' ''' \
        + r'''~/caffe/Makefile.config && \
            sed -i 's/\/usr\/local\/include/\/usr\/local\/include ''' \
        + r'''\/usr\/include\/hdf5\/serial/g' ~/caffe/Makefile.config && \
            sed -i 's/hdf5/hdf5_serial/g' ~/caffe/Makefile && \
            cd ~/caffe && \
            make -j"$(nproc)" -Wno-deprecated-gpu-targets distribute && \

            # fix ValueError caused by python-dateutil 1.x
            sed -i 's/,<2//g' ~/caffe/python/requirements.txt && \

            $PIP_INSTALL \
                -r ~/caffe/python/requirements.txt && \

            cd ~/caffe/distribute/bin && \
            for file in *.bin; do mv "$file" "${file%%%%.bin}"; done && \
            cd ~/caffe/distribute && \
            cp -r bin include lib proto /usr/local/ && \
            cp -r python/caffe /usr/local/lib/python%s/dist-packages/ && \
        ''' % pyver
