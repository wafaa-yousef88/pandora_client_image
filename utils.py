#!/usr/bin/python
# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2010
from __future__ import division, with_statement

import fractions
from glob import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import shutil
import tempfile
import time

import ox


class AspectRatio(fractions.Fraction):
    def __new__(cls, numerator, denominator=None):
        if not denominator:
            ratio = map(int, numerator.split(':'))
            if len(ratio) == 1: ratio.append(1)
            numerator = ratio[0]
            denominator = ratio[1]
            #if its close enough to the common aspect ratios rather use that
            if abs(numerator/denominator - 4/3) < 0.03:
                numerator = 4
                denominator = 3
            elif abs(numerator/denominator - 16/9) < 0.02:
                numerator = 16
                denominator = 9
        return super(AspectRatio, cls).__new__(cls, numerator, denominator)

    @property
    def ratio(self):
        return "%d:%d" % (self.numerator, self.denominator)

#wafaa created imginfo func
'''
def imginfo(filename, cached=True):
    if cached:
        return cache(filename, 'info')
    if os.path.getsize(filename):
        ffmpeg2theora = cmd('ffmpeg2theora')
        p = subprocess.Popen([ffmpeg2theora], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info, error = p.communicate()
        version = info.split('\n')[0].split(' - ')[0].split(' ')[-1]
        if version < '0.27':
            raise EnvironmentError('version of ffmpeg2theora needs to be 0.27 or later, found %s' % version)
        p = subprocess.Popen([ffmpeg2theora, '--info', filename],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        info, error = p.communicate()
        try:
            info = json.loads(info)
        except:
            #remove metadata, can be broken
            reg = re.compile('"metadata": {.*?},', re.DOTALL)
            info = re.sub(reg, '', info)
            info = json.loads(info)
        #wafaa
        #if 'video' in info:
            #for v in info['video']:
                #if not 'display_aspect_ratio' in v and 'width' in v:
                    #v['display_aspect_ratio'] = '%d:%d' % (v['width'], v['height'])
                    #v['pixel_aspect_ratio'] = '1:1'
        return info

    return {'path': filename, 'size': 0}
'''
def avinfo(filename):
    if os.path.getsize(filename):
        info = ox.avinfo(filename)
				#info = imginfo(filename)
        '''wafaa commented following part if 'video' in info and info['video'] and 'width' in info['video'][0]:
            if not 'display_aspect_ratio' in info['video'][0]:
                dar = AspectRatio(info['video'][0]['width'], info['video'][0]['height'])
                info['video'][0]['display_aspect_ratio'] = dar.ratio'''

        '''if 'image' in info and info['image'] and 'width' in info['image'][0]:
            if not 'display_aspect_ratio' in info['image'][0]:
                dar = AspectRatio(info['image'][0]['width'], info['image'][0]['height'])
                info['image'][0]['display_aspect_ratio'] = dar.ratio'''
        del info['path']
        if os.path.splitext(filename)[-1] in ('.srt', '.sub', '.idx', '.rar') and 'error' in info:
            del info['error']
        if 'code' in info and info['code'] == 'badfile':
            del info['code']
        return info
    return {'path': filename, 'size': 0}

def hash_prefix(h):
    return [h[:2], h[2:4], h[4:6], h[6:]]

def run_command(cmd, timeout=25):
    #print cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    while timeout > 0:
        time.sleep(0.2)
        timeout -= 0.2
        if p.poll() != None:
            return p.returncode
    if p.poll() == None:
        os.kill(p.pid, 9)
        killedpid, stat = os.waitpid(p.pid, os.WNOHANG)
    return p.returncode

#wafaa
def video_frame_positions(duration):
    pos = duration / 2
    #return [pos/4, pos/2, pos/2+pos/4, pos, pos+pos/2, pos+pos/2+pos/4]
    return map(int, [pos/2, pos, pos+pos/2])

