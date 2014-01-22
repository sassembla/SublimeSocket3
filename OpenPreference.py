# -*- coding: utf-8 -*-
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
    
    self.generateHTML(
        {
            SublimeSocketAPISettings.SS_HOST_REPLACE:host,
            SublimeSocketAPISettings.SS_PORT_REPLACE:port
        }, 
        "resource/source.html", 
        "tmp/preference.html")
    
  @classmethod
  def generateHTML(self, replaceableDict, sourcePath, outputPath):
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
    for key in replaceableDict:
        if key in SublimeSocketAPISettings.HTML_REPLACEABLE_KEYS:
            target = key
            value = replaceableDict[key]
            html = html.replace(target, str(value))

    # replace version
    html = html.replace(SublimeSocketAPISettings.SS_VERSION_REPLACE, SublimeSocketAPISettings.API_VERSION)

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
    host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
    port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')
    
    testHTMLPath = sublime.load_settings("SublimeSocket.sublime-settings").get('testHtml')
    testSuitePath = sublime.load_settings("SublimeSocket.sublime-settings").get('testSuite')

    # get current Plugin's resource/tests path.
    testBasePath = sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/"+"resource/tests"

    self.generateHTML(
        {
            SublimeSocketAPISettings.SS_HOST_REPLACE:host, 
            SublimeSocketAPISettings.SS_PORT_REPLACE:port,
            SublimeSocketAPISettings.SS_TESTSUITE_PATH_REPLACE:testBasePath,
            SublimeSocketAPISettings.SS_TESTSUITE_FILENAME_REPLACE:testSuitePath
        },
        "resource/tests/tests.html", 
        "tmp/tests.html")


class BuildThread(threading.Thread):
  def __init__(self, command):
    self.command = command  
    threading.Thread.__init__(self)

  def run(self):
    print("command = ", self.command)
    # run command
    subprocess.call(self.command, shell=True)



