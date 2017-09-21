#!/usr/bin/python
import pickle
import numpy as np
from os.path import join, exists, dirname
from os import makedirs
#import argparse
import sys
from functools import partial

from bokeh.io import curdoc
from bokeh.core.properties import field
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import Button, ColumnDataSource, Range1d, Whisker, LinearColorMapper, Legend
from bokeh.models.widgets import Select, PreText, Button, Paragraph, TextInput
from bokeh.plotting import figure
from bokeh.palettes import RdBu4 as palette

from light_curve_handler import get_lc_data

classes = ["RR Lyrae", "Eclipsing Binary", "Cepheid", "Other"]

def get_plot_title_string(lc_index, lc_name, lc_period, lc_class=-1):
    if lc_class == -1 :
        return "%d) File: %s Period: %0.4f [days]" %(lc_index, lc_name, lc_period)
    else:
        return "%d) File: %s Period: %0.4f [days] Class: %s" %(lc_index, lc_name, lc_period, classes[lc_class])

class Main_Interface:
    def __init__(self, N_rows=3, N_cols=3):
        self.N_rows = N_rows
        self.N_cols = N_cols
        self.plot_list = []
        self.source_list = [] 
        self.prev_batch = Button(label="Previous page")
        self.curr_batch = PreText()
        self.next_batch = Button(label="Next page")
        self.prev_lc = Button(label="Go back one")
        self.find_unlabeled = Button(label="Find first unlabeled")
        self.class_buttons = []
        for class_name in classes:
            self.class_buttons.append(Button(label=class_name))
        self.page_index = 0
        self.labeling_index = 0
        color_mapper = LinearColorMapper(palette=palette)
        for i in range(N_rows):
            for j in range(N_cols):
                p = figure(toolbar_location='above', x_range=(0.0, 4.0), y_range=(0.0, 1.0), 
                        tools='pan, box_zoom, reset, save', toolbar_sticky=False)
                source = ColumnDataSource(data=dict(x=[], y=[], x_err=[], y_err=[], c=[]))
                p.circle(x='x', y='y', size=2, color={'field': 'c', 'transform': color_mapper}, source=source)
                p.multi_line(xs='x_err', ys='y_err', color={'field': 'c', 'transform': color_mapper}, source=source)
                p.xaxis.bounds = (0, 4)
                self.plot_list.append(p)
                self.source_list.append(source)
                p.outline_line_width = 8
                p.outline_line_color = "red"
                p.outline_line_alpha = 0.0
        self.plot_list[0].outline_line_alpha = 0.5
        grid = gridplot(self.plot_list, ncols=N_cols, plot_width=450, plot_height=250, merge_tools=True)
        self.update_curr_batch()
        self.update_plots()
        self.prev_batch.on_click(self.change_batch_backward)
        self.next_batch.on_click(self.change_batch_forward)
        widget_list = []
        widget_list.append(Paragraph(text="Browse the dataset using these widgets:", width=180))
        widget_list += [self.prev_batch, self.curr_batch, self.next_batch]
        widget_list.append(Paragraph(text="Please choose a label for the currently selected light curve:", width=180))
        widget_list.append(self.prev_lc)
        self.prev_lc.on_click(self.go_back_one_label)
        for i, button in enumerate(self.class_buttons):
            button.on_click(partial(self.set_new_label, fill_value=i))
            widget_list.append(button)
        widget_list.append(self.find_unlabeled)
        self.find_unlabeled.on_click(self.find_first_unlabeled)
        widget_list.append(Paragraph(text="Plot's legend: (blue dots) Folded with reported period, (red dots) folded with twice the reported period", width=180))
        self.figure = row(widgetbox(widget_list, width=200), grid)
    
    def set_new_label(self, fill_value=0):
        lc_index = self.page_index*self.N_cols*self.N_rows + self.labeling_index
        lc_dict['user_label'][lc_index] = fill_value
        lc_name = lc_dict['list'][lc_index]
        lc_period = lc_dict['periods'][lc_index]
        self.plot_list[self.labeling_index].title.text = get_plot_title_string(lc_index, lc_name, lc_period, fill_value)
        self.plot_list[self.labeling_index].outline_line_alpha = 0.0
        if lc_index + 1 < len(lc_dict['list']):
            self.labeling_index += 1
        # TODO: When is the best moment to save results?
        if self.labeling_index == self.N_cols*self.N_rows:
            self.labeling_index = 0
            self.change_batch_forward()
            backup_path = curdoc().template_variables["backup_path"]
            print("Saving backup at %s" %(backup_path))
            pickle.dump(lc_dict['user_label'], open(backup_path, "wb"), protocol=2) 
        self.plot_list[self.labeling_index].outline_line_alpha = 0.5

    def go_back_one_label(self):
        self.plot_list[self.labeling_index].outline_line_alpha = 0.0
        self.labeling_index -= 1
        if self.labeling_index < 0:
            if self.page_index > 0:
                self.change_batch_backward()
                self.labeling_index = self.N_cols*self.N_rows - 1
            else:
                self.labeling_index = 0
        self.plot_list[self.labeling_index].outline_line_alpha = 0.5


    def update_curr_batch(self):
        self.curr_batch.text = "Page %d out of %d" %(self.page_index, len(lc_dict['list'])/(self.N_cols*self.N_rows))
   

    def find_first_unlabeled(self):
        labels = lc_dict['user_label']
        unlabeled_index = np.where(labels == -1)[0]
        if len(unlabeled_index) > 0:
            first_index = unlabeled_index[0]
            self.page_index = int(first_index/(self.N_cols*self.N_rows))
            self.plot_list[self.labeling_index].outline_line_alpha = 0.0
            self.labeling_index = np.mod(first_index, self.N_cols*self.N_rows)
            self.plot_list[self.labeling_index].outline_line_alpha = 0.5
            self.update_curr_batch()
            self.update_plots()

    def change_batch_backward(self):
        self.page_index -= 1
        if self.page_index < 0:
            self.page_index = 0
        self.update_curr_batch()
        self.update_plots()

    def change_batch_forward(self):
        if self.page_index + 1 < len(lc_dict['list'])/(self.N_cols*self.N_rows):
            self.page_index += 1
        self.update_curr_batch()
        self.update_plots()

    def update_plots(self):
        for i in range(self.N_rows):
            for j in range(self.N_cols):
                plot_index = self.N_cols*i + j
                x_err, y_err = [], []
                lc_index = self.page_index*self.N_cols*self.N_rows + plot_index
                if lc_index < len(lc_dict['list']):
                    lc_name = lc_dict['list'][lc_index]
                    period = lc_dict['periods'][lc_index]
                    phi, mag, err = get_lc_data(join(lc_dict['path'], lc_name), period)
                    for x, y, yerr in zip(phi, mag, err):
                        x_err.append((x, x))
                        y_err.append((y - yerr, y + yerr))
                    c = np.zeros(shape=(len(phi),))
                    c[:int(len(phi)/2)] = 1
                    self.source_list[plot_index].data = dict(x=phi, y=mag, x_err=x_err, y_err=y_err, c=c)
                    #mean = np.average(mag, weights=1.0/err**2)
                    mean = np.median(mag)
                    #scale = np.sqrt(np.average((mag-mean)**2, weights=1.0/err**2))
                    scale = np.percentile(mag, 75) - np.percentile(mag, 25)
                    #self.plot_list[plot_index].y_range.start = np.amin([np.amax(mag+err), mean + 5*scale])
                    #self.plot_list[plot_index].y_range.end = np.amax([np.amin(mag-err), mean - 5*scale])
                    self.plot_list[plot_index].y_range.start = mean + 3*scale
                    self.plot_list[plot_index].y_range.end = mean - 3*scale
                    plot_label = lc_dict['user_label'][lc_index]
                    self.plot_list[plot_index].title.text = get_plot_title_string(lc_index, lc_name, period, plot_label)
                else:
                    self.source_list[plot_index].data = dict(x=[0], y=[0], x_err=[1], y_err=[1], c=[0])
                    self.plot_list[plot_index].title.text = ""

class Auth_Interface:
    def __init__(self, document):
        self.document = document
        self.text_input = TextInput(placeholder="Write username")
        self.ready_button = Button(label="Ready")
        self.interface = widgetbox(self.text_input, self.ready_button, width=200)
        self.ready_button.on_click(self.ready_callback)
        self.document.add_root(self.interface)
    
    def ready_callback(self):
        if not self.text_input.value == "":
            user_data_folder = join(path_results, self.text_input.value)
            if not exists(user_data_folder):
                makedirs(user_data_folder)
            backup_path = join(user_data_folder, "backup.pkl")
            if exists(backup_path):
                print("Found backup at %s, loading it" % (backup_path))
                lc_dict['user_label'] = pickle.load(open(backup_path, "rb"))
            self.document.template_variables["backup_path"] = backup_path
            print("Changing interface")
            self.document.remove_root(self.interface)
            main_interface = Main_Interface(N_rows=3, N_cols=3)
            self.document.add_root(main_interface.figure)
 

lc_data_path = sys.argv[1]
feature_file = sys.argv[2]
path_results = join(dirname(__file__), sys.argv[3])
if not exists(path_results):
    print("Creating folder")
    makedirs(path_results)

document = curdoc()
document.title = "Light curve inspector and labeler"
#lc_list, lc_periods, lc_features, _, _ = pickle.load(open(feature_file, "rb"))
features  = pickle.load(open(feature_file, "rb"))
lc_list, lc_periods = np.array(features[0]), features[1]

if len(sys.argv) > 4:
    sub_idx_file = sys.argv[4]
    sub_idx = pickle.load(open(sub_idx_file, "rb"))
    lc_list = lc_list[sub_idx]
    lc_periods = lc_periods[sub_idx]
#    lc_features = lc_features[sub_idx]

lc_dict = {'list': lc_list, 'periods': lc_periods, #'features': lc_features, 
        'path': lc_data_path, 'user_label': -1*np.ones(shape=(len(lc_list),), dtype=int)}
Auth_Interface(document)

