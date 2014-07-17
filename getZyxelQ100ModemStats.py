#!/usr/bin/python
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Mike Shoup
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#
# =============================================================================
# 
# Grabs WAN statistics from a ZyXEL Q100z modem.
# Formats the statistics such that Cacti can interpret them
# Assumes a username/password is required on the interface.
# Based on the status screen from firmware QZQ002-4.2.001.1-Q100.
# May not work with other firmware versions
# Execute with -h for usage

import urllib, urllib2, cookielib
from HTMLParser import HTMLParser
from optparse import OptionParser

# Used to parse information from the wanstatus page
class StatsParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.downstream = -3
    self.upstream = -3
    self.packetsrx = -3
    self.retrains = -3
    self.retrain_timer = -3
    self.near_crc_int = -3
    self.near_crc_fast = -3
    self.far_crc_int = -3
    self.far_crc_fast = -3
    self.near_fec_int = -3
    self.near_fec_fast = -3
    self.far_fec_int = -3
    self.far_fec_fast = -3
    self.snr_down = -3
    self.snr_up = -3
    self.atten_down = -3
    self.atten_up = -3
    self.power_down = -3
    self.power_up = -3

  def handle_starttag(self, tag, attributes):
    if tag != 'span':
      return
    for name, value in attributes:
      if name == 'id' and value == 'dspeed':
        self.downstream = -2
      elif name == 'id' and value == 'uspeed':
        self.upstream = -2
      elif name == 'id' and value == 'xtmpktrx':
        self.packetsrx = -2
      elif name == 'id' and value == 'retrain':
        self.retrains = -2
      elif name == 'id' and value == 'rtimer':
        self.retrain_timer = -2
      elif name == 'id' and value == 'RNECRCINT':
        self.near_crc_int = -2
      elif name == 'id' and value == 'RNECRCFP':
        self.near_crc_fast = -2
      elif name == 'id' and value == 'RFECRCINT':
        self.far_crc_int = -2
      elif name == 'id' and value == 'RFECRCFP':
        self.far_crc_fast = -2
      elif name == 'id' and value == 'RNEFECINT':
        self.near_fec_int = -2
      elif name == 'id' and value == 'RNEFECFP':
        self.near_fec_fast = -2
      elif name == 'id' and value == 'RFEFECINT':
        self.far_fec_int = -2
      elif name == 'id' and value == 'RFEFECFP':
        self.far_fec_fast = -2
      elif name == 'id' and value == 'RSNRDOWN':
        self.snr_down = -2
      elif name == 'id' and value == 'RSNRUP':
        self.snr_up = -2
      elif name == 'id' and value == 'RATTENDOWN':
        self.atten_down = -2
      elif name == 'id' and value == 'RATTENUP':
        self.atten_up = -2
      elif name == 'id' and value == 'RPOWERDOWN':
        self.power_down = -2
      elif name == 'id' and value == 'RPOWERUP':
        self.power_up = -2
  
  def handle_data(self, data):
    if self.downstream == -2:
      self.downstream = int(data)*1000
    elif self.upstream == -2:
      self.upstream = int(data)*1000
    elif self.packetsrx == -2:
      self.packetsrx = data
    elif self.retrains == -2:
      self.retrains = data
    elif self.retrain_timer == -2:
      self.retrain_timer = data
    elif self.near_crc_int == -2:
      if data == 'N/A':
        self.near_crc_int = -1
      else:
        self.near_crc_int = data
    elif self.near_crc_fast == -2:
      if data == 'N/A':
        self.near_crc_fast = -1
      else:
        self.near_crc_fast = data
    elif self.far_crc_int == -2:
      if data == 'N/A':
        self.far.crc_int = -1
      else:
        self.far_crc_int = data
    elif self.far_crc_fast == -2:
      if data == 'N/A':
        self.far_crc_fast = -1
      else:
        self.far_crc_fast = data
    elif self.near_fec_int == -2:
      if data == 'N/A':
        self.near_fec_int = -1
      else:
        self.near_fec_int = data
    elif self.near_fec_fast == -2:
      if data == 'N/A':
        self.near_fec_fast = -1
      else:
        self.near_fec_fast = data
    elif self.far_fec_int == -2:
      if data == 'N/A':
        self.far_fec_int = -1
      else:
        self.far_fec_int = data
    elif self.far_fec_fast == -2:
      if data == 'N/A':
        self.far_fec_fast = -1
      else:
        self.far_fec_fast = data
    elif self.snr_down == -2:
      self.snr_down = data.strip()
    elif self.snr_up == -2:
      self.snr_up = data.strip()
    elif self.atten_down == -2:
      self.atten_down = data.strip()
    elif self.atten_up == -2:
      self.atten_up = data.strip()
    elif self.power_down == -2:
      self.power_down = data.strip()
    elif self.power_up == -2:
      self.power_up = data.strip()

  # Returns a string that is "human readable"
  def readable_str(self):
    if self.downstream > 1000000:
      downstream_rate = str(self.downstream/1000000.0) + "mbit/s"
    else:
      downstream_rate = str(self.downstream/1000) + "kbit/s"

    if self.upstream > 1000000:
      upstream_rate = str(self.upstream/1000000.0) + "mbit/s"
    else:
      upstream_rate = str(self.upstream/1000) + "kbit/s"
    
    return (
          "Downstream Speed:        " + downstream_rate +
        "\nUpstream Speed:          " + upstream_rate + 
        "\nPackets Received:        " + str(self.packetsrx) + 
        "\nRetrains:                " + str(self.retrains) +
        "\nRetrain Timer:           " + str(self.retrain_timer) +
        "\nNear End CRC Interleave: " + str(self.near_crc_int) + 
        "\nNear End CRC Fastpath:   " + str(self.near_crc_fast) +
        "\nFar End CRC Interleave:  " + str(self.far_crc_int) +
        "\nFar End CRC Fastpath:    " + str(self.far_crc_fast) +
        "\nNear End FEC Interleave: " + str(self.near_fec_int) +
        "\nNear End FEC Fastpath:   " + str(self.near_fec_fast) + 
        "\nFar End FEC Interleave:  " + str(self.far_fec_int) +
        "\nFar End FEC Fastpath:    " + str(self.far_fec_fast) + 
        "\nSNR Downstream:          " + str(self.snr_down) + "dB" +
        "\nSNR Upstream:            " + str(self.snr_up) + "dB" +
        "\nAttenuation Downstream:  " + str(self.atten_down) + "dB" +
        "\nAttenuation Upstream:    " + str(self.atten_up) + "dB" +
        "\nPower Downstream:        " + str(self.power_down) + "dBm" +
        "\nPower Upstream:          " + str(self.power_up)) + "dBm"

  # Returns a string that is formatted for use with Cacti
  def __str__(self):
    return (
         "downstream:" + str(self.downstream) +
        " upstream:" + str(self.upstream) +
        " packetsrx:" + str(self.packetsrx) +
        " retrains:" + str(self.retrains) +
        #" retrain_timer:" + str(self.retrain_timer) +
        " near_crc_int:" + str(self.near_crc_int) +
        " near_crc_fast:" + str(self.near_crc_fast) +
        " far_crc_int:" + str(self.far_crc_int) +
        " far_crc_fast:" + str(self.far_crc_fast) +
        " near_fec_int:" + str(self.near_fec_int) +
        " near_fec_fast:" + str(self.near_fec_fast) +
        " far_fec_int:" + str(self.far_fec_int) +
        " far_fec_fast:" + str(self.far_fec_fast) +
        " snr_down:" + str(self.snr_down) +
        " snr_up:" + str(self.snr_up) +
        " atten_down:" + str(self.atten_down) +
        " atten_up:" + str(self.atten_up) +
        " power_down:" + str(self.power_down) +
        " power_up:" + str(self.power_up))

# All the real logic happens here
def main():
  options_parser = OptionParser()
  options_parser.add_option("-H","--host",dest="host",
                            help="DNS or IP address of DSL modem")
  options_parser.add_option("-u","--username",dest="username",
                            help="Admin username")
  options_parser.add_option("-p","--password",dest="password",
                            help="Admin password")
  options_parser.add_option("-r","--human-readable",action="store_true",dest="human_readable",
                            help="Makes the output human readable instead of Cacti readable")

  (options, args) = options_parser.parse_args()

  if not options.host:
    options_parser.error("No host provided")
  if not options.username:
    options_parser.error("No username provided")
  if not options.password:
    options_parser.error("No password provided")

  login_url = "http://"+options.host+"/login.cgi"
  status_url = "http://"+options.host+"/modemstatus_wanstatus.html"

  login_data = [
    ('admin_username',options.username),
    ('admin_password',options.password)
  ]

  headers = {
    'Referer': 'http://'+options.host+'/'
  }

  # Setup the cookie jar
  cj = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  opener.addheaders = headers.items()

  # Login and get the cookies
  resp = opener.open(login_url, urllib.urlencode(login_data))
  resp.close()
  
  # Get the modem status
  resp = opener.open(status_url)
  status_html = resp.read()
  resp.close()
  
  status = StatsParser()
  status.feed(status_html)
  if options.human_readable:
    print status.readable_str()
  else:
    print status

if __name__ == "__main__":
  main()
