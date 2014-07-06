#!/usr/bin/env python

# Copyright 2014 linyehui
# Part of https://github.com/linyehui/migrating-from-wikidot-to-jekyll

from wikidot import WikidotToMarkdown ## most important here

import sys ## for sys.exit()
import os ## for os.makedirs()
import optparse ## for optparse.OptionParser()
import markdown ## for markdown.markdown()
import codecs ## for codecs.open()
import datetime as dt # for dt.datetime() and dt.datetime.now()
import time ## for time.sleep()
import  re

DEFAULT_RSS_FILENAME = "./wikidot/rss.html"
DEFAULT_SOURCE_DIR = "./wikidot/source"
DEFAULT_OUTPUT_DIR = "./jekyll"

class ConversionController(object):
    def __init__(self, options):
        self.__input_rss_file = options.rss_filename
        self.__input_source_directory = options.input_source_dir
        self.__output_directory = options.output_dir
        self.__converter = WikidotToMarkdown()

    def __prepare_output_dir(self):
        try:
            os.makedirs(self.__output_directory)
        except OSError as ex:
            print("Could not create output folder "+self.__output_directory+".")
            if ex.errno == os.errno.EEXIST: print("It already exists.")
            else: print "Error %i: %s" % (ex.errno, str(ex)); sys.exit(1)

    def parse_rss(self, text):
        pattern_code = r'<tr>[\s]+?<td><a href="[\s\S]+?</tr>'
        pattern = re.compile(pattern_code)
        matchItems = pattern.findall(text)
        return matchItems

    def parse_index_item(self, text):
        pattern_code = r'<tr>[\s]+?<td><a href="([\s\S]+?)">([\s\S]+?)</a></td>[\s]+?<td><span[\s\S]+?>([\s\S]+?)</span></td>[\s]+?<td>([\s\S]*?)</td>'
        pattern = re.compile(pattern_code)
        item_info = pattern.findall(text)
        return item_info

    def gen_format_tags(self, src_tags):
        format_tags = u""
        if u"" == src_tags:
            return format_tags

        tag_list = src_tags.split(' ')
        if None == tag_list:
            return format_tags

        for item in tag_list:
            format_tags += "    - " + item + "\n"

        return format_tags

    def gen_markdown_context(self, article_url):
        wiki_filename = self.__input_source_directory + "/" + article_url + ".txt"
        #print "gen_markdown_context", wiki_filename
        try:
            f = codecs.open(wiki_filename, encoding='utf-8')
            text = f.read()
            f.close()
            return self.__converter.convert(text)
        except:
            print "Failed to gen_markdown_context : ", wiki_filename
            return None


    def gen_article_context(self, article_url, title, tags):
        context_format = """---\ntitle: '{0}'\nlayout: post\ntags:\n{1}---\n\n{2}"""

        format_tags = self.gen_format_tags(tags)
        format_context = self.gen_markdown_context(article_url)
        if None == format_context:
            return None

        return unicode(context_format).format(title, format_tags, format_context)

    def deal_one_file(self, item_info):
        #print "deal one file: ", item_info

        publish_date = dt.datetime.strptime(item_info[2], '%d %b %Y %H:%M')
        article_url = item_info[0][1:]
        filename = self.__output_directory \
            + publish_date.strftime('/%Y-%m-%d-') \
            + article_url \
            + ".markdown"

        context = self.gen_article_context(article_url, item_info[1], item_info[3])
        if None == context:
            print "Failed to deal : ", article_url
            return None

        #print filename
        md_file = codecs.open(filename, 'w', encoding='utf-8')
        md_file.write(context)
        md_file.close();
        return None

    def get_rss_context(self, filename):
        try:
            f = codecs.open(filename, encoding='utf-8')
            text = f.read()
            f.close()
            return text
        except:
            return None

    def convert(self):
        self.__prepare_output_dir()
        text = self.get_rss_context(self.__input_rss_file)
        if None == text:
            print "Failed to open RSS file: ", self.__input_rss_file
            return None

        # read index info from rss
        index_info = self.parse_rss(text)
        if None == index_info:
            print "there is no index in rss."
            return None

        #print index_info[0]

        # for each index info, deal file one by one
        show_first = False
        for item in index_info:
            item_info = self.parse_index_item(item)
            self.deal_one_file(item_info[0])

        print "====== Success ====="

def main():
    """ Main function called to start the conversion."""
    p = optparse.OptionParser(version="%prog 1.0")

    # set possible CLI options
    p.add_option('--input-rss', '-r', metavar="INPUT_FILE", help="Read from INPUT_FILE.", dest="rss_filename")
    p.add_option('--input-source-dir', '-s', metavar="INPUT_DIRECTORY", help="Read from INPUT_DIRECTORY.", dest="input_source_dir")
    p.add_option('--output-dir', '-o', metavar="OUTPUT_DIRECTORY", help="Save the converted files to the OUTPUT_DIRECTORY.", dest="output_dir")

    # parse our CLI options
    options, arguments = p.parse_args()
    if options.rss_filename == None:
        #p.error("No rss filename for the input file set. Have a look at the parameters using the option -h.")
        #sys.exit(1)
        options.rss_filename = DEFAULT_RSS_FILENAME
        print "using default RSS_FILENAME: " + options.rss_filename
    if options.input_source_dir == None:
        options.input_source_dir = DEFAULT_SOURCE_DIR
        print "using default DEFAULT_SOURCE_DIR: " + options.input_source_dir
    if options.output_dir == None:
        #options.output_dir = raw_input('Please enter an output directory for the converted documents [%s]: ' % DEFAULT_OUTPUT_DIR)
        options.output_dir = DEFAULT_OUTPUT_DIR
        print "using default DEFAULT_OUTPUT_DIR: " + options.output_dir


    converter = ConversionController(options)
    converter.convert()

if __name__ == '__main__':
    main()
