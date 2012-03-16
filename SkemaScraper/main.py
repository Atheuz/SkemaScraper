# -*- coding: utf-8 -*-

# Filename      skema.py
# Author        Lasse Vang Gravesen <gravesenlasse@gmail.com>
# First edited  13-03-2012 23:01
# Last edited   14-03-2012 18:31

import re
import urllib2, lxml.html
import datetime

class Lecture:
    def __init__(self, index, days, periods, description):
        self.index   = index
        self.dates   = get_dates()
        self.periods = []
        self.days    = []
        self.desc    = description

    def fix_periods(self):
        pass

    def fix_days(self):
        pass

def expand_to_full_day(days, periods, description):
    expanded = []
    if days > 1:
        for i in range(days):
            temp = []
            for i in range(periods):
                temp.append(description)
            expanded.append(temp)
    else:
        temp = []
        for i in range(periods):
            temp.append(description)
        expanded.append(temp)

    for i in expanded:
        if len(i) == 4:
            i[-1] = i[-1] +  "FULL"
            #i.append("FULL")

    #print expanded
    return expanded

def get_dates():
    dates = []
    curr_date = datetime.date(2012, 1, 30)
    while True:
        if curr_date != datetime.date(2012, 6, 29):
            dates.append(curr_date)
            curr_date += datetime.timedelta(days=1)
        else:
            dates.append(datetime.date(2012, 6, 29))
            break

    return [x for x in dates if x.isoweekday() in range(1,6)]

def stretches_n_days(days, periods):
    periods_taken = days * periods
    return periods_taken

def get_html(url):
    return lxml.html.fromstring(urllib2.urlopen(url).read())

def get_lectures():
    lectures = []
    lectures_obj = []
    url = "http://www.tnb.aau.dk/fg_2011/dat_sw/DAT_SW_2SEM.html"
    content = get_html(url)
    trs = content.xpath('//tr/td[@align="center" or @class="style42"]')
    start_of_week = True
    end_of_week = False

    periods = {"1": "8:15-10:00",
               "2": "10:15-12:00",
               "3": "12:30-14:15",
               "4": "14:30-16:15"}

    actual_dates = get_dates()

    week = 5  # Start at week 5
    count = 0 # 20 possible periods for every week, should be counted up to and then reset to 0.
    days_passed = 0
    for i in trs[5:]:
        if count == 20:
            count = 0
            days_passed = 0
            week += 1
        days, periods = i.xpath('@colspan'), i.xpath('@rowspan')
        if days == []:
            days = 1
        else:
            days = int(days[0])
        if periods == []:
            periods = 1
        else:
            periods = int(periods[0])
        count += days * periods
        if count % 4 == 0:
            days_passed += days
        """print "days: %d - periods: %d - stretches: %d - week: %d - days passed: %d - count: %d " % (days, 
                                                                   periods,
                                                                   stretches_n_days(days, periods),
                                                                   week,
                                                                   days_passed, 
                                                                   count),"""
        con = i.xpath('.//text()') #i.text_content() # i.text_content() #i.xpath('.//strong')
        if con:
            con = ' '.join(con)
            if len(con) > 2:
                fixed = re.sub('\xa0', ' ', con)
                fixed = re.sub('\n', ' ', fixed)
                fixed = re.sub('\t', ' ', fixed)
                fixed = re.sub('\r', ' ', fixed)
                fixed = ''.join([x for x in fixed if x > 0x20])
                fixed = re.sub('\s+',' ', fixed)
                fixed = re.sub('\xa0', '', fixed)
                if len(fixed) < 3:
                    fixed = ''
                else:
                    fixed = fixed[1:].strip()
                #print "'%s'" % fixed

                """# (self, index, days, periods, description)
                periods_set = stretches_n_days(days, periods)
                if days > 1 or periods_set >= 4:
                    if periods_set == 4:
                        dates = [actual_dates.pop(0)]
                    if periods_set == 8:
                        dates = [actual_dates.pop(0),
                                 actual_dates.pop(0)]
                    if periods_set == 12:
                        dates = [actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0)]
                    if periods_set == 16:
                        dates = [actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0)]
                    if periods_set == 20:
                        dates = [actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0),
                                 actual_dates.pop(0)]
                    #print dates
                c = 0
                elif days == 1:
                    if periods_set == 2 and if :
                        dates = [actual_dates.pop(0)]
                #l = Lecture(0, , 0, fixed)
                #lectures_obj.append()"""
                lectures.extend(expand_to_full_day(days, periods, fixed))
                #lectures.append(fixed)
    
    import numpy as np
    x = np.array([sum(lectures, [])])
    x = np.reshape(x, (-1,20))
    for i in x[2]:
        print "' %s '" % i
    #split = 0
    #joiner = []
    #weeks = []
   # for i in lectures:
        #split += len(i)
        #if 'FULL' in i:
        #    split -= 1
    #print split
    """if split > 20:
            pass
            #print i
        if split == 20:
            split = 0
            joiner.extend(i)
            weeks.append(joiner)
            joiner = []
            split += len(i)
            if 'FULL' in i:
                split -= 1
        else:
            joiner.extend(i)
            split += len(i)
            if 'FULL' in i:
                split -= 1
        #print i, split

    for i in range(len(weeks)):
        print len(weeks[i])
        print str(i + 5) + "\n"""

    #for i in range(len(lectures)):
        #pass
    #    if 'FULL' not in lectures[i]:
            
        #print lectures[i]
    return lectures

def main():
    get_lectures()

if __name__ == '__main__':
    main()
