# -*- coding: utf-8 -*-

# Filename      skema.py
# Author        Lasse Vang Gravesen <gravesenlasse@gmail.com>
# First edited  02-04-2012 19:03
# Last edited   02-04-2012 21:37

from pprint import pprint
import gethtml
import lxml.html
import re
import sys
import lxml.html.clean as clean
from lxml.html.clean import Cleaner
import HTMLParser

def extract_tables(table_el):
    ll = 0
    count = 0
    temp = []
    table_rows = []
    for row in table_el.xpath('./tr[position() > 1]'):
        if table_el.index(row) % 5 != 0:
            if count == 4:
                table_rows.append(temp)
                temp = []
                count = 0
                ll += 1
            temp.append(row)
            count += 1
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

def main():
    url = "http://www.tnb.aau.dk/fg_2011/dat_sw/DAT_SW_2SEM.html"
    content = gethtml.get_html(url)
    table_el = content.xpath('//div[@align="center"]/table[@class="style3"]')[0]
    table_rows = extract_tables(table_el)
    
    tt = []
    for i in table_rows:
        to_drop = i[0].xpath('./td[position() = 1]')[0]
        to_drop.getparent().remove(to_drop)
        tt.append(i)
    for i in tt:
        for j in i:
            to_drop = j.xpath('./td[@bgcolor="#006699" and @style="width: 41px"]')
            if to_drop:  
                to_drop = to_drop[0]
                to_drop.getparent().remove(to_drop)
                
    
    tags = ['b', 'i', 'u', 'h1', 'h2','h3','br','p','table', 'tr', 'td']
    safe_attrs=clean.defs.safe_attrs
    clean.defs.safe_attrs = frozenset([x for x in safe_attrs if x not in ["width", "align", "height", "class"]])
    cleaner = clean.Cleaner(safe_attrs_only=True, allow_tags=tags, remove_unknown_tags=False)

    tt = [''.join(map(lxml.html.tostring, x)) for x in table_rows]
    tt = [x.replace("<br>", '\n') for x in tt]
    tt = ["<table>" + x + "</table>" for x in tt]
    tt = [cleaner.clean_html(x) for x in tt]
    tt = [lxml.html.fromstring(clean_text(x)) for x in tt]
    
    weeks = []
    
    for i in tt:
        t = lxml.html.tostring(i, pretty_print=True)
        t = lxml.html.fromstring(t)
        table_el = t.xpath('//table')[0]
        table = list(iter_table_normalized(table_el))
        weeks.append(table)
    
    transposed_weeks = [transpose_week(x) for x in weeks]
    
    for i in weeks:
        print len(i)
    
    for i in transposed_weeks:
        if len(i) == 6:
            print i
    
    
    #print transposed_weeks[-2]
    

if __name__ == '__main__':
    main()
