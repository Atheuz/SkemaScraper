# -*- coding: utf-8 -*-

# Filename      skema.py
# Author        Lasse Vang Gravesen <gravesenlasse@gmail.com>
# First edited  02-04-2012 19:03
# Last edited   04-04-2012 20:31

from pprint import pprint
import gethtml
import lxml.html
import re
import sys
import lxml.html.clean as clean
from lxml.html.clean import Cleaner
import HTMLParser
from collections import defaultdict, OrderedDict
import json
import datetime
import csv


# Credit for these functions go to reclosedev, from this Stackoverflow question: 
# http://stackoverflow.com/questions/9978445/parsing-a-table-with-rowspan-and-colspan
def table_to_list(table):
    dct = table_to_2d_dict(table)
    return list(iter_2d_dict(dct))

def table_to_2d_dict(table):
    result = defaultdict(lambda : defaultdict(unicode))
    for row_i, row in enumerate(table.xpath('./tr')):
        for col_i, col in enumerate(row.xpath('./td|./th')):
            colspan = int(col.get('colspan', 1))
            rowspan = int(col.get('rowspan', 1))
            col_data = col.text_content()
            while row_i in result and col_i in result[row_i]:
                col_i += 1
            for i in range(row_i, row_i + rowspan):
                for j in range(col_i, col_i + colspan):
                    result[i][j] = col_data
    return result

def iter_2d_dict(dct):
    for i, row in sorted(dct.items()):
        cols = []
        for j, col in sorted(row.items()):
            cols.append(col)
        yield cols


def extract_tables(table_el):
    ll = 0
    count = 0
    temp = []
    table_rows = []
    cc = []
    for row in table_el.xpath('./tr[position() > 1]'):
        if table_el.index(row) % 5 != 0:
            if count == 4:
                table_rows.append(temp)
                temp = []
                count = 0
                ll += 1
            
            to_drop = row.xpath('./td[position() = 1]')[0]
            if re.search("Uge \d+", to_drop.text_content()):
                to_drop.getparent().remove(to_drop)
            to_drop = row.xpath('./td[position() = 1]')[0]
            if re.search("\d+:\d+-\d+:\d+", to_drop.text_content()):
                to_drop.getparent().remove(to_drop)
            
            temp.append(row)
            count += 1
            
            if count == 4:
                table_rows.append(temp)
                temp = []
                count = 0
                ll += 1

    return table_rows
    
def clean_text(s):
    con = s
    fixed = re.sub('\xa0', ' ', con)
    fixed = re.sub('\n', '\n', fixed)
    fixed = re.sub('\t', ' ', fixed)
    fixed = re.sub('\r', '\n', fixed)
    fixed = ''.join([x for x in fixed if x > 0x20])
    fixed = re.sub('\s+',' ', fixed)
    fixed = re.sub('\xa0', '', fixed)
    return fixed

def extract_text(element):
    con = element.text_content()
    if len(con) > 2:
        fixed = re.sub('\xa0|\xc2', ' ', con)
        fixed = re.sub('\n', '\n', fixed)
        fixed = re.sub('\t', ' ', fixed)
        fixed = re.sub('\r', '\n', fixed)
        fixed = ''.join([x for x in fixed if x > 0x20])
        fixed = re.sub('\s+',' ', fixed)
        fixed = re.sub('\xa0|\xc2', ' ', fixed)
        if len(fixed) < 3:
            fixed = ''
        else:
            fixed = fixed[1:].strip()
        return fixed
    return con

def iter_table_normalized(table, data_extractor=extract_text):
    """Normalizes table, properly handles rowspan's and colspan's

    :param table: lxml <table></table> element
    :returns: iterator - rows of columns
    """
    last_row = None
    #tt = table.xpath('./tr[position() > 1]')
    for row in table.xpath('./tr'):
        cols = []
        rows_count = 0
        for col in row.xpath('./td|./th'):
            colspan = int(col.get('colspan', 1))
            #rows_count += int(col.get('rowspan', 0))#TODO if we don't count this - it's good for analyze, but bad for converting to other format, such as excel
            col_data = data_extractor(col) if data_extractor else col
            for i in range(colspan):
                cols.append(col_data)
        if last_row:
            len_diff = len(last_row) - len(cols)
            if len_diff > 0:
                cols = last_row[:len_diff] + cols
        last_row = cols
        for i in range(rows_count - 1):
            yield cols
        yield cols

def transpose_week(week):
    return zip(*week)

def generate_weeks():
    url = "http://www.tnb.aau.dk/fg_2011/dat_sw/DAT_SW_2SEM.html"
    content = gethtml.get_html(url)
    table_el = content.xpath('//div[@align="center"]/table[@class="style3"]')[0]
    table_rows = extract_tables(table_el)
     
    tt = [x for x in table_rows]
                
    
    tags = ['b', 'i', 'u', 'h1', 'h2','h3','br','p','table', 'tr', 'td']
    safe_attrs=clean.defs.safe_attrs
    clean.defs.safe_attrs = frozenset([x for x in safe_attrs if x not in ["width", "align", "height", "class"]])
    cleaner = clean.Cleaner(safe_attrs_only=True, allow_tags=tags, remove_unknown_tags=False)

    tt = [''.join(map(lxml.html.tostring, x)) for x in table_rows]
    tt = [x.replace("<br>", '\n') for x in tt]
    tt = ["<table>" + x + "</table>" for x in tt]
    tt = [cleaner.clean_html(x) for x in tt]
    tt = [re.sub("&#194;", " ", x) for x in tt]
    tt = [re.sub("\s+", " ", x) for x in tt]
    tt = [lxml.html.fromstring(clean_text(x)) for x in tt]
    
    weeks = []
    
    for i in tt:
        t = lxml.html.tostring(i, pretty_print=True).replace('&#194;', '')
        t = re.sub("\s+", " ", t)
        t = lxml.html.fromstring(t)
        to_drop = t.xpath('./tr/td')
        table_el = t.xpath('//table')[0]
        table = table = table_to_list(table_el) #list(iter_table_normalized(table_el))
        weeks.append(table)
    
    j = 1
    
    transposed_weeks = [transpose_week(x) for x in weeks]
    
    return transposed_weeks

def make_json(weeks):
    d = {"uger": {}}
    current_week = 5
    weekdays = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag"]
    for i in weeks:
        d["uger"][str(current_week)] = {}
        curr_weekday = 0
        for j in i:
            d["uger"][str(current_week)][weekdays[curr_weekday]] = []
            for k in j:
                if len(k) > 3:
                    d["uger"][str(current_week)][weekdays[curr_weekday]].append(k.encode('ISO-8859-1'))
                else:
                    d["uger"][str(current_week)][weekdays[curr_weekday]].append("Ingen undervisning.".encode('ISO-8859-1'))
            curr_weekday += 1
        current_week += 1
    
    json.dump(d, open("./weeks.json", "w"), sort_keys=True, indent=4)

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

def make_csv(weeks):
    dates = get_dates()
    dates = [x.strftime("%d-%m-%Y") for x in dates]
    possible_times = [("8:15", "10:00"),
                      ("10:15","12:00"),
                      ("12:30", "14:15"),
                      ("14:30","16:15")]

    csv_writer = csv.writer(open("weeks.csv", "wb"), delimiter=',', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(["Subject", "Start Date", "Start Time", "End Date", "End Time", "Description"])
    
    
    to_tuples = []
    
    for week in weeks:
        for day in week:
            curr_day = dates.pop(0)
            curr_period = 0
            for period in day:
                if len(period) > 3:
                    period = period.lstrip().rstrip()
                else:
                    period = "Ingen forelæsning."

                to_tuples.append((period.encode('ISO-8859-1'),
                                  curr_day,
                                  possible_times[curr_period][0],
                                  curr_day,
                                  possible_times[curr_period][1],
                                  period.encode('ISO-8859-1')))

                if curr_period == 3:
                    curr_period = 0
                else:
                    curr_period += 1
                    
    csv_writer.writerows(to_tuples)
    
    """s = []
    
    for line in open("weeks.csv", "r"):
        print line
        s.append(line.decode('ISO-8859-1').encode('utf-8'))
    print len(s)
    sys.exit()
    with open("weeks.csv", "a") as w:
        w.write(''.join(f))
        w.close()"""
    
    
    
def main():
    weeks = generate_weeks()
    make_csv(weeks)
    #make_json(weeks)

if __name__ == '__main__':
    main()
