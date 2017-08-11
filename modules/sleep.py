import time
from modules import log

__all__ = ["timeSleep"]

class timeSleep:
    def __init__(self):
        self.request_interval = 3
        self.request_window = 900

    @property
    def interval(self):
        return self.request_interval

    @interval.setter
    def interval(self, value):
        log.success('Updating request interval to {value}'.format(value=self.prettyTime(value)))
        self.request_interval = value

    def sleepInterval(self):
        # log.note('Sleeping for {sleep} to prevent limit rate'.format(sleep=self.prettyTime(self.request_interval)))
        if self.request_interval > 0:
            time.sleep(self.request_interval)

    @property
    def window(self):
        return self.request_window

    @window.setter
    def window(self, value):
        log.success('Updating request window to {value}'.format(value=self.prettyTime(value)))
        self.request_window = value

    def sleepWindow(self):
        log.error('Maximum requests exceeded, sleeping for {sleep}'.format(sleep=self.prettyTime(self.request_window)))
        if self.request_window > 0:
            time.sleep(self.request_window)

    def prettyTime(self, seconds):
        seconds = int(seconds)
        time = []

        units = [
            {
                'name': 'week',
                'seconds': 604800
            },
            {
                'name': 'day',
                'seconds': 86400
            },
            {
                'name': 'hour',
                'seconds': 3600
            },
            {
                'name': 'minute',
                'seconds': 60
            },
            {
                'name': 'second',
                'seconds': 1
            }
        ]

        for unit in units:
            count = int(seconds / unit['seconds'])

            if count > 0 or (unit['name'] == 'second' and len(time) == 0):
                time += ['{count} {unit}{s_unit}'.format(count=count, unit=unit['name'], s_unit='' if count == 1 else 's')]

            seconds = int(seconds % unit['seconds'])

        if len(time) > 1:
            time = ' and '.join([', '.join(time[:-1]), time[-1]])
        else:
            time = time[0]

        return time

