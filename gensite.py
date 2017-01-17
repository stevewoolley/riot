#!/usr/bin/env python

import jinja2
import argparse
import os
import json
import glob

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--templates", help="templates directory", default='templates')
    parser.add_argument("-x", "--extension", help="file extension to export", required=True)
    parser.add_argument("-d", "--output_dir", help="directory to export", default='www')
    parser.add_argument("-j", "--context", help="json context file")
    args = parser.parse_args()

    TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath=args.templates)
    TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)
    context = None

    if args.context:
        with open(args.context) as data_file:
            context = json.load(data_file)

    for t in glob.glob("{}/*.html.jinja2".format(args.templates)):
        orig_filename, orig_file_extension = os.path.splitext(t)
        filename, file_extension = os.path.splitext(orig_filename)
        orig_basename = os.path.basename(t)
        export_filename = "{}{}".format(os.path.basename(filename), file_extension)
        template = TEMPLATE_ENV.get_template(orig_basename)
        if context is not None:
            template.stream(context).dump("{}/{}".format(args.output_dir, export_filename))
        else:
            template.stream().dump("{}/{}".format(args.output_dir, export_filename))
        print "input: {}{} output: {}".format(filename, file_extension, export_filename)
