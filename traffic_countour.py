import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
import matplotlib.dates as mdates
import datetime
import re

class ContourPlot():
    _df = None
    _contour_interval_min = 5
    _end_time = str(datetime.timedelta() - \
            datetime.timedelta(minutes=_contour_interval_min) +\
            datetime.timedelta(days=1))
    _data_indicies = []
    _filename = None
    _milepost_max = None
    _milepost_min = None
    _milepost_increment = 0.1
    _old_indicies = None
    _cmap = None
    _dates = []

    def __init__(self, filename):
        self._filename = filename
        self.find_data_indicies()


        for i in range(len(self._data_indicies)):
            start = self._data_indicies[i][0] 
            end = self._data_indicies[i][1]
            try:
                contour_title = self._dates[i]
            except IndexError:
                contour_title = '12/01/2020'
            self._df = pd.read_csv(filename, delimiter='\s+', skiprows=start, nrows=end-start)
            self.draw_contour_plot(start, end, contour_title)

    def draw_contour_plot(self, start, end, contour_title):
        self.set_contour_mileposts()
        self.convert_values_to_decimal()
        self.set_equidistant_mileposts()
        self.interpolate_data()
        self.create_color_map()
        self.draw_contour(title=contour_title)

    def create_color_map(self):
        colors = ['green','yellow','red', 'darkred', 'black',  'black']
        nodes = [0.0, 0.15, 0.22, 0.30, 0.5, 1.0]
        cmap1 = LinearSegmentedColormap.from_list('mycmap', colors)
        self._cmap = LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))

    def draw_contour(self, title='Contour Plot'):
        plt.rcParams.update({'figure.autolayout': True})
        fig, ax = plt.subplots()
        hrs = mdates.HourLocator()
        hrs_fmt = mdates.DateFormatter('%HH')

        x = mdates.datestr2num(self._df.index.values)
        y = self._df.columns.values
        X, Y = np.meshgrid(x, y)
        Z = self._df.T.values
        normalize_values = mpl.colors.Normalize(vmin=0, vmax=100)

        CS = ax.contourf(X, Y, Z, cmap = self._cmap, norm=normalize_values)
        ax.xaxis.set_major_locator(hrs)
        ax.xaxis.set_major_formatter(hrs_fmt)
        plt.xticks(rotation=90)
        ax.set_title('Date: ' + title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Milepost')

        norm = mpl.colors.Normalize(vmin=0, vmax=1)
        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=self._cmap))

        img_filename = self.img_output_name(title)
        fig.savefig(img_filename, dpi=600)
        plt.close()


    def img_output_name(self, img_title):
        out = ''
        datetime_value = datetime.datetime.strptime(img_title, '%m/%d/%Y')
        year = str(datetime_value.year)
        month = str(datetime_value.month)
        day = str(datetime_value.day)
        if len(month) < 2:
            month = '0' + month
        if len(day) < 2:
            day = '0' + day
        return out + year + month + day + '.png'

    def convert_values_to_decimal(self):
        df = self._df
        columns = df.columns
        for col in columns:
            df[col] = df[col].str.replace('%','')
            df[col] = pd.to_numeric(df[col])

    def interpolate_data(self):
        df = self._df
        df = df.interpolate(axis=1)
        df = df.T.drop(self._old_indicies).T
        df = df.fillna(value=0)
        self._df = df

    def set_equidistant_mileposts(self):
        df = self._df
        df.columns = pd.to_numeric(df.columns)
        df = df.T
        index_new = np.arange(\
                self._milepost_min,\
                self._milepost_max,\
                self._milepost_increment\
                )
        index_new = np.round(index_new,1)
        index_old = df.index
        index_new = np.sort(np.append(index_new, index_old))
        df = df.reindex(index_new)

        self._old_indicies = index_old
        self._df = df.T

    def set_contour_mileposts(self):
        df = self._df
        np_array = np.array(df.columns).astype(np.float)
        self._milepost_max = self.round_to_interval(np_array.max())
        self._milepost_min = self.round_to_interval(np_array.min())

    def round_to_interval(self, value):
        base = self._milepost_increment
        return round(base * round(float(value)/base),1)

    def get_filename(self):
        return self._filename

    def get_end_time(self):
        return self._end_time

    def find_data_indicies(self):
        start_indicies = []
        end_indicies = []
        date_keyword = 'Date:'
        p = re.compile('\d{2}/\d{2}/\d{4}')
        filename = self.get_filename()
        end_time = self.get_end_time()
        data = open(filename)

        #get start, end, and date index
        for c, i in enumerate(data):
            if 'Data Content' in i:
                start_indicies.append(c+3)
            elif date_keyword in i:
                out = p.findall(i)[0]
                self._dates.append(out)
            elif end_time in i:
                end_indicies.append(c)

        #update class variable
        n = len(start_indicies)
        for i in range(n):
            self._data_indicies.append(\
                    (start_indicies[i],\
                    end_indicies[i])\
                    )

if __name__ == '__main__':
    test_data = '405_big_data_GP_N.txt'
    test_data = 'data.txt'
    data = ContourPlot(test_data)
