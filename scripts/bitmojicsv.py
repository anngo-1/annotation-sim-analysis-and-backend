import csv
import numpy as np
import re

bitmoji_list = []
with open('bitmoji-nose-tag.csv', newline='') as csvfile:
    bitmoji_reader = csv.reader(csvfile)
    for line in bitmoji_reader:
        bitmoji_list.append(line)

transposed_list = np.array(bitmoji_list).T.tolist()

tag_list = []
for tag in transposed_list[1]:
    user_image_tags = re.findall(r'"(.*?)"', tag)
    tag_list.append(user_image_tags)

bitmoji_dict = dict(zip(transposed_list[0], tag_list))
# print(bitmoji_dict)
