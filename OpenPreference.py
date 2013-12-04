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

MY_PLUGIN_PATHNAME = os.path.split(os.path.dirname(os.path.realpath(__file__)))[1]
class Openpreference(sublime_plugin.TextCommand):
  def run (self, edit) :
    self.openSublimeSocketPreference()

  @classmethod
  def openSublimeSocketPreference(self):
    host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
    port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')
    
    self.generateHTML(host, port, "resource/source.html", "tmp/preference.html")
    
  @classmethod
  def generateHTML(self, host, port, sourcePath, outputPath):
    # create path of Preference.html
    currentPackagePath = sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/"
    originalHtmlPath = sourcePath
    originalPath = currentPackagePath + originalHtmlPath

    preferenceFilePath = outputPath
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

  @classmethod
  def openSublimeSocketTest(self):
    print("openSublimeSocketTest!!!")
    host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
    port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')
    
    self.generateHTML(host, port, "resource/tests/tests.html", "tmp/tests.html")


class BuildThread(threading.Thread):
  def __init__(self, command):
    self.command = command  
    threading.Thread.__init__(self)

  def run(self):
    print("command = ", self.command)
    # run command
    subprocess.call(self.command, shell=True)



