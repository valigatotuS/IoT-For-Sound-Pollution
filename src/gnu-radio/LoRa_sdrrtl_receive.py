#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: LoRa Receiver with RTL-SDR dongle
# Author: valigatotuS
# Description: Receive LoRa frames
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
import osmosdr
import time
from gnuradio import qtgui

class LoRa_sdrrtl_receive(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LoRa Receiver with RTL-SDR dongle")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LoRa Receiver with RTL-SDR dongle")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "LoRa_sdrrtl_receive")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.freq_slider = freq_slider = 868e6
        self.channel_freq = channel_freq = 868.2e6

        ##################################################
        # Blocks
        ##################################################
        self._freq_slider_range = Range(867e6, 869e6, 1, 868e6, 200)
        self._freq_slider_win = RangeWidget(self._freq_slider_range, self.set_freq_slider, 'Frequency', "counter_slider", float)
        self.top_grid_layout.addWidget(self._freq_slider_win)
        self._channel_freq_tool_bar = Qt.QToolBar(self)
        self._channel_freq_tool_bar.addWidget(Qt.QLabel('Channel frequency' + ": "))
        self._channel_freq_line_edit = Qt.QLineEdit(str(self.channel_freq))
        self._channel_freq_tool_bar.addWidget(self._channel_freq_line_edit)
        self._channel_freq_line_edit.returnPressed.connect(
            lambda: self.set_channel_freq(eng_notation.str_to_num(str(self._channel_freq_line_edit.text()))))
        self.top_grid_layout.addWidget(self._channel_freq_tool_bar)
        self.rtlsdr_source_0_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + 'str(grgsm.device.get_default_args(args))'
        )
        self.rtlsdr_source_0_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0_0.set_center_freq(freq_slider, 0)
        self.rtlsdr_source_0_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0_0.set_gain(0, 0)
        self.rtlsdr_source_0_0.set_if_gain(0, 0)
        self.rtlsdr_source_0_0.set_bb_gain(0, 0)
        self.rtlsdr_source_0_0.set_antenna('', 0)
        self.rtlsdr_source_0_0.set_bandwidth(1e6, 0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            firdes.WIN_HAMMING, #wintype
            channel_freq, #fc
            samp_rate*4, #bw
            "", #name
            1 #number of inputs
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(True)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            freq_slider, #fc
            samp_rate, #bw
            "", #name
            1
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.rtlsdr_source_0_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.rtlsdr_source_0_0, 0), (self.qtgui_waterfall_sink_x_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "LoRa_sdrrtl_receive")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_slider, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.channel_freq, self.samp_rate*4)
        self.rtlsdr_source_0_0.set_sample_rate(self.samp_rate)

    def get_freq_slider(self):
        return self.freq_slider

    def set_freq_slider(self, freq_slider):
        self.freq_slider = freq_slider
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_slider, self.samp_rate)
        self.rtlsdr_source_0_0.set_center_freq(self.freq_slider, 0)

    def get_channel_freq(self):
        return self.channel_freq

    def set_channel_freq(self, channel_freq):
        self.channel_freq = channel_freq
        Qt.QMetaObject.invokeMethod(self._channel_freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.channel_freq)))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.channel_freq, self.samp_rate*4)



def main(top_block_cls=LoRa_sdrrtl_receive, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
