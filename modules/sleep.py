import time
from modules import log

__all__ = ["TimeSleep"]

class TimeSleep:
    def __init__(self):
        """Initialize params."""
        self.request_interval = 3
        self.request_window = 900

    @property
    def interval(self):
        """Return interval."""
        return self.request_interval

    @interval.setter
    def interval(self, value):
        """Define interval."""
        log.success('Updating request interval to {value}'.format(
            value=self.pretty_time(value)
        ))
        self.request_interval = value

    def sleep_interval(self):
        """Sleep for interval."""
        # log.note('Sleeping for {sleep} to prevent limit rate'.format(
        #     sleep=self.pretty_time(self.request_interval)
        # ))
        if self.request_interval > 0:
            time.sleep(self.request_interval)

    @property
    def window(self):
        """Return window."""
        return self.request_window

    @window.setter
    def window(self, value):
        """Define window."""
        log.success('Updating request window to {value}'.format(
            value=self.pretty_time(value)
        ))
        self.request_window = value

    def sleep_window(self):
        """Sleep for window."""
        log.error('Maximum requests exceeded, sleeping for {sleep}'.format(
            sleep=self.pretty_time(self.request_window)
        ))
        if self.request_window > 0:
            time.sleep(self.request_window)

    @staticmethod
    def pretty_time(seconds):
        """Return human readable time."""
        seconds = int(seconds)
        timestr = []

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

            if count > 0 or (unit['name'] == 'second' and len(timestr) == 0):
                timestr += ['{count} {unit}{s_unit}'.format(
                    count=count,
                    unit=unit['name'],
                    s_unit='' if count == 1 else 's'
                )]

            seconds = int(seconds % unit['seconds'])

        if len(timestr) > 1:
            timestr = ' and '.join([', '.join(timestr[:-1]), timestr[-1]])
        else:
            timestr = timestr[0]

        return timestr
