#!/usr/bin/env python

import jinja2
import argparse
import os
import json

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("templates", nargs='+', help="templates to parse")
    parser.add_argument("-x", "--extension", help="file extension to export", required=True)
    parser.add_argument("-d", "--output_dir", help="directory to export", default='www')
    parser.add_argument("-j", "--context", help="json context file")
    args = parser.parse_args()

    TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath="templates")
    TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)
    context = None

    if args.context:
        with open(args.context) as data_file:
            context = json.load(data_file)

    for t in args.templates:
        filename, file_extension = os.path.splitext(t)
        template = TEMPLATE_ENV.get_template(t)
        if context is not None:
            template.stream(context).dump("{}/{}.{}".format(args.output_dir, filename, args.extension))
        else:
            template.stream().dump("{}.{}".format(filename, args.extension))
        print "input: {}{} output: {}.{}".format(filename, file_extension, filename, args.extension)
