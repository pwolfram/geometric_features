#!/usr/bin/env python

"""

This script has two modes of usage:
1. To create a new file (features.geojson) containing one or more features that
are pointed to using the -f or -d flags.

2. To append one or more features on an already existing features.geojson file,
again defined by the -f and -d flags.

The usage mode is automatically detected for you, depending on if the
features.geojson file exists or not before calling this script.

When using this script, you can optionally give a list of tags in a semicolon
delimited list (e.g. "tag1;tag2;tag3"). Features are only added to
features.geojson if their tags property contains all of the tags listed on the
input line.

"""

import sys, os, glob, shutil, numpy
import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import *
from utils.feature_test_utils import *

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file", help="Single feature file to append to features.geojson", metavar="FILE")
parser.add_argument("-d", "--features_directory", dest="features_dir", help="Directory containing multiple feature files, each will be appended to features.geojson", metavar="PATH")
parser.add_argument("-t", "--tags", dest="tags", help="Semicolon separated list of tags to match features against.", metavar='"TAG1;TAG2;TAG3"')

args = parser.parse_args()

if not args.feature_file and not args.features_dir:
	parser.error('Either a feature file (-f) or a feature directory (-d) is required.')

if args.features_dir:
	if not os.path.exists(args.features_dir):
		parser.error('The path %s does not exist.'%(args.features_dir))

if args.feature_file:
	if not os.path.exists(args.feature_file):
		parser.error('The file %s does not exist.'%(args.feature_file))

master_tag_list = []
if args.tags:
	for tag in args.tags.split(';'):
		master_tag_list.append(tag)

file_to_append = "features.geojson"
all_features = defaultdict(list)

new_file = True
first_feature = True
if os.path.exists(file_to_append):
	new_file = False
	with open(file_to_append) as f:
		appended_file = json.load(f)
		for feature in appended_file['features']:
			all_features['features'].append(feature)
		del appended_file

out_file = open(file_to_append, 'w')

if args.feature_file:
	with open(args.feature_file) as f:
		feature_file = json.load(f)

		for feature in feature_file['features']:
			if match_tag_list(feature, master_tag_list):
				if not feature_already_exists(all_features, feature):
					all_features['features'].append(feature)

		del feature_file

if args.features_dir:
	for (dirpath, dirnames, filenames) in os.walk(args.features_dir):
		for filename in sorted(filenames):
			with open('%s/%s'%(dirpath, filename), 'r') as f:
				feature_file = json.load(f)
				for feature in feature_file['features']:
					if match_tag_list(feature, master_tag_list):
						if not feature_already_exists(all_features, feature):
							all_features['features'].append(feature)
				del feature_file

out_file.write('{"type": "FeatureCollection",\n')
out_file.write(' "features":\n')
out_file.write('\t[\n')
write_all_features(all_features, out_file, '\t\t')
out_file.write('\n')
out_file.write('\t]\n')
out_file.write('}\n')

