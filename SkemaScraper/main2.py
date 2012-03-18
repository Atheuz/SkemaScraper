# -*- coding: utf-8 -*-

# Filename      skema.py
# Author        Lasse Vang Gravesen <gravesenlasse@gmail.com>
# First edited  13-03-2012 23:01
# Last edited   18-03-2012 18:30

import re
import urllib2, lxml.html
import datetime
import itertools
import sys


class Week:
    def __init__(self, week_num):
        self.week_num   = week_num
        self.monday     = []
        self.tuesday    = []
        self.wednesday  = []
        self.thursday   = []
        self.friday     = []
        self.unknown    = []
        self.original   = []

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

def get_html(url):
    return lxml.html.fromstring(urllib2.urlopen(url).read())

def add_information(days, periods, week, description):
    infod = []
    full = False
    if periods * days >= 4:
        full = True
    if description == "":
        description = "Ingen undervisning."
    infod.append({"days": days,
                  "periods": periods,
                  "total_periods": periods*days,
                  "full": full,
                  "week": week,
                  "description": description})
    
    return infod

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

        con = i.xpath('.//text()')
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

                lectures.extend(add_information(days, periods, week, fixed))
    
    import pprint
    
    pp = pprint.PrettyPrinter(indent=4)
    
    groups = []
    unique_keys = []
    for k, g in itertools.groupby(lectures, lambda x: x["week"]):
        groups.append(list(g))
        unique_keys.append(k)
        
    weeks = []
    
    week_count = 5    
    
    for i in groups:
        n_days = Week(week_count)
        for j in i:
            if j["total_periods"] % 4 == 0:
                total_days = j["total_periods"] / 4
                if total_days > 1:
                    insert_after = i.index(j)
                    j["total_periods"] /= total_days
                    j["days"] /= total_days
                    for k in range(total_days-1):
                        i.insert(insert_after, j.copy())
                        insert_after += 1
                        
                """if total_days == 2:
                    insert_after = i.index(j)
                    j["total_periods"] /= 2
                    j["days"] /= 2
                    i.insert(insert_after, j.copy())
                if total_days == 3:
                    insert_after = i.index(j)
                    j["total_periods"] /= 3
                    j["days"] /= 3
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())
                if total_days == 4:
                    insert_after = i.index(j)
                    j["total_periods"] /= 4
                    j["days"] /= 4
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())
                if total_days == 5:
                    insert_after = i.index(j)
                    j["total_periods"] /= 5
                    j["days"] /= 5
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())
                    insert_after += 1
                    i.insert(insert_after, j.copy())"""
                    
    for i in groups:
        print len(i)
        for j in i:
            print j
        print ""
            
        week_count += 1
        weeks.append(n_days)
        
    sys.exit()    

    return lectures

def test():
    url = "http://www.tnb.aau.dk/fg_2011/dat_sw/DAT_SW_2SEM.html"
    content = get_html(url)
    trs = content.xpath('//tr/td[@align="center" or @class="style42"][1]')
    
    for i in trs:
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
        print "'%s'" % fixed

def main():
    get_lectures()
    #test()

if __name__ == '__main__':
    main()
