import os
import sys


# add path to spider folder
sys.path.insert(1, str(os.getcwd() + '/spiders'))

# select name and type for the output
file_name = input("\nWrite the name of the output file: \n")
output_type = input("\nNow write the type of the output file (csv, json, xml): \n")
out = file_name + '.' + output_type

# run script
os.system("scrapy crawl mediamarkt -o {}".format(out))
