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

from utils import avinfo, AspectRatio, run_command


def command(program):
    local = os.path.expanduser('~/.ox/bin/%s' % program)
    if os.path.exists(local):
        program = local
    return program

def frame(video, target, position):
    fdir = os.path.dirname(target)
    if fdir and not os.path.exists(fdir):
        os.makedirs(fdir)

    '''
    #oxframe
    cmd = ['oxframe', '-i', video, '-p', str(position), '-o', target]
    print cmd
    r = run_command(cmd)
    return r == 0
    '''

    '''
    #mplayer
    cwd = os.getcwd()
    target = os.path.abspath(target)
    framedir = tempfile.mkdtemp()
    os.chdir(framedir)
    cmd = ['mplayer', '-noautosub', video, '-ss', str(position), '-frames', '2', '-vo', 'png:z=9', '-ao', 'null']
    print cmd
    r = run_command(cmd)
    images = glob('%s/*.png' % framedir)
    if images:
        shutil.move(images[-1], target)
        r = 0
    else:
        r = 1
    os.chdir(cwd)
    shutil.rmtree(framedir)
    return r == 0
    '''
    #ffmpeg
    pre = position - 2
    if pre < 0:
        pre = 0
    else:
        position = 2
    ''' wafaa commented the following command and replaced it with convert
    cmd = [command('ffmpeg'), '-y', '-ss', str(pre), '-i', video, '-ss', str(position),
            '-vf', 'scale=iw*sar:ih',
            '-an', '-vframes', '1', target]
    '''
    #wafaa cmd = [command('ffmpeg'), '-y', '-ss', str(position), '-i', video, '-an', '-vframes', '1', target]
    cmd = [command('convert'), video, '-resize', '50', target]
    r = run_command(cmd)
    return r == 0
'''This function is not used till now'''
def supported_formats():
    #wafaa commented the following line of code
		#p = subprocess.Popen([command('ffmpeg'), '-codecs'],
    #wafaa p = subprocess.Popen([command('identify'), '-list', 'format'],		
    #wafaa replaced the previous commented line with following cmd
    p = subprocess.Popen([command('convert')],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return {
      #'ogg': 'libtheora' in stdout and 'libvorbis' in stdout,
      #wafaa commented the following two lines and replaced them with coming lines
		  #'webm': 'libvpx' in stdout and 'libvorbis' in stdout,
		  #'mp4': 'libx264' in stdout and 'libvo_aacenc' in stdout,
      #wafaa added the following 5 lines
			'jpg' in stdout,
			'jpeg' in stdout,
			'png' in stdout,	
       #wafaa 'webp': 'libwebp2' in stdout,
       #'webp' in stdout,
    }

'''
wafaa We need to add img_cmd() func in future
'''

def image_cmd(video, target, profile, info):

    if not os.path.exists(target):
        ox.makedirs(os.path.dirname(target))

    '''
        look into
            lag
            mb_static_threshold
            qmax/qmin
            rc_buf_aggressivity=0.95
            token_partitions=4
            level / speedlevel
            bt?
    '''
    profile, format = profile.split('.')
    bpp = 0.17

    if profile == '1080p':
        height = 1080

        audiorate = 48000
        audioquality = 6
        audiobitrate = None
        audiochannels = None

    if profile == '720p':
        height = 720

        audiorate = 48000
        audioquality = 5
        audiobitrate = None
        audiochannels = None
    if profile == '480p':
        height = 480

        audiorate = 44100
        audioquality = 3
        audiobitrate = None
        audiochannels = 2
    elif profile == '432p':
        height = 432
        audiorate = 44100
        audioquality = 2
        audiobitrate = None
        audiochannels = 2
    elif profile == '360p':
        height = 360

        audiorate = 44100
        audioquality = 1
        audiobitrate = None
        audiochannels = 1
    elif profile == '288p':
        height = 288

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '240p':
        height = 240

        audiorate = 44100
        audioquality = 0
        audiobitrate = None
        audiochannels = 1
    elif profile == '144p':
        height = 144

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1
    else:
        height = 96

        audiorate = 22050
        audioquality = -1
        audiobitrate = '22k'
        audiochannels = 1

    cmd = [command('convert'), video, '-resize', 'x720', target]
    #x = 'x'
    #res_val = x + str(height)
    #cmd = [command('convert'), video, '-resize', res_val, target]
    #cmd = [command('convert'), video, target]
    print "cmd print %s" % cmd
    return cmd

'''wafaa added function to keep original file by copying it to the server'''
'''
def copy_orig(video, target2, orig_profile, info):
    cmd = [command('cp'), video, target]
    return cmd
'''
def image(video, target, profile, info):
    cmd = image_cmd(video, target, profile, info)
    profile, format = profile.split('.')
    #r = run_command(cmd, -1)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        p.wait()
        r = p.returncode
        if format == 'mp4':
            cmd = [command('qt-faststart'), "%s.mp4" % target, target]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                      stdout=open('/dev/null', 'w'),
                                      stderr=subprocess.STDOUT)
            p.communicate()
            os.unlink("%s.mp4" % target)
        print 'Input:\t', video
        print 'Output:\t', target
        #print 'Output:\t', jpgtarget
    except KeyboardInterrupt:
        p.kill()
        r = 1
        if os.path.exists(target):
            print "\n\ncleanup unfinished encoding:\nremoving", target
            print "\n"
            os.unlink(target)
        if format == 'mp4' and os.path.exists("%s.mp4" % target):
            os.unlink("%s.mp4" % target)
        sys.exit(1)
    return r == 0
