# -*- coding: utf-8 -*-
from . import SublimeWSSettings
from . import SublimeSocketAPISettings

import os
import signal
import sys
import sublime
import sublime_plugin
import subprocess
import shlex
import threading
import glob
import string

class Openpreference(sublime_plugin.TextCommand):
  def run (self, edit) :
    self.openSublimeSocketPreference()

  @classmethod
  def openSublimeSocketPreference(self):
    host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
    port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')
    

    # create path of Preference.html
    currentPackagePath = sublime.packages_path() + "/SublimeSocket/"
    originalHtmlPath = "resource/source.html"
    originalPath = currentPackagePath + originalHtmlPath

    preferenceFilePath = "tmp/preference.html"
    preferencePath = currentPackagePath + preferenceFilePath


    html = ""

    # prepare html contents    
    with open(originalPath, mode='r', encoding='utf-8') as htmlFile:
        html = htmlFile.read()
        
    # replace host:port
    html = html.replace(SublimeWSSettings.SS_HOST_REPLACE, host)
    html = html.replace(SublimeWSSettings.SS_PORT_REPLACE, str(port))

    # replace version
    html = html.replace(SublimeWSSettings.SS_VERSION_REPLACE, SublimeSocketAPISettings.API_VERSION)

    # generate preference
    with open(preferencePath, mode='w', encoding='utf-8') as htmlFile:
        htmlFile.write(html)
        
    # set Target-App to open Preference.html
    targetAppPath = sublime.load_settings("SublimeSocket.sublime-settings").get('preference browser')

    # compose coomand
    command = "open" + " " + "-a" + " " + targetAppPath + " \"" + preferencePath + "\""

    # run on the other thread
    thread = BuildThread(command)
    thread.start()


class BuildThread(threading.Thread):
  def __init__(self, command):
    self.command = command  
    threading.Thread.__init__(self)

  def run(self):
    print("command = ", self.command)
    # run command
    subprocess.call(self.command, shell=True)



