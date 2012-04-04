#!/usr/bin/python
# -*- coding: utf-8 -*-

# Filename      create_index.py
# Author        Lasse Vang Gravesen <gravesenlasse@gmail.com>
# First edited  17-03-2012 23:41
# Last edited   04-04-2012 22:51

import datetime
import re

try:
    import json;
except ImportError:
    import simplejson as json

def make():
    out = ""

    out += open("head.html", "r").read()
    out += open("body_start.html", "r").read()

    json_file_db = json.loads(open("../weeks.json", "r").read())

    out += '\t<div class="container">\n'

    for uge in range(5,27):
        week_out = json_file_db["uger"][str(uge)]
        out += '\t\t<div>\n'
        out += '\t\t\t<div class="sixteen columns" id="uge%s">\n' % str(uge)
        out += '\t\t\t\t<h4 class="remove-bottom" style="margin-top: 0.5em">Skema for uge %s</h4>\n' % uge
        out += '\t\t\t\t<a href="http://www.tnb.aau.dk/fg_2011/dat_sw/DAT_SW_2SEM.html">Originalt skema</a>\n'
        out += '\t\t\t\t<hr />\n'
        out += '\t\t\t</div>\n'

        out += '\t<ul class="tabs">'
        out += '\t\t<li><a class="active" href="#mandag%s">Ma</a></li>' % str(uge)
        out += '\t\t<li><a href="#tirsdag%s">Ti</a></li>' % str(uge)
        out += '\t\t<li><a href="#onsdag%s">On</a></li>' % str(uge)
        out += '\t\t<li><a href="#torsdag%s">To</a></li>' % str(uge)
        out += '\t\t<li><a href="#fredag%s">Fr</a></li>' % str(uge)
        out += '\t</ul>'

        out += '\n'
        out += '<ul class="tabs-content">\n'
        for i in ["mandag", "tirsdag", "onsdag", "torsdag", "fredag"]:
            content = json_file_db["uger"][str(uge)][i]
            if i == 'mandag':
                out += '<li class="active" id="%s">\n' % (i + str(uge))
            else:
                out += '<li id="%s">\n' % (i + str(uge))

            out += '<div class="five columns alpha">\n'
            out += '<table class="table table-condensed">\n'
            out += """<thead>
                        <tr>
                            <th>%s</th>
                        </tr>
                    </thead>\n""" % i.capitalize()
            out += '<tbody>\n'

            for j in content:
                out += "<tr>\n"
                out += "<td>%s</td>" % j
                out += "</tr>\n"

            out += '</tbody>\n'

            out += '</table>\n'
            out += '</div>\n'
            out += '</li>\n'
        out += "\t\t</div>"

    out += '\t</div>\n'
    out += '</div>'

    out += open("body_end.html", "r").read()

    f = open("index.html", "wb")
    f.write(out.replace('\t', '    ').encode('ISO-8859-1'))
    f.close()


def main():
    make()

if __name__ == '__main__':
    main()

