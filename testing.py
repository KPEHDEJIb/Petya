import time
from PIL import Image

start_time = time.time()

img = Image.open('Монополия/field.png')

pos1 = pos2 = pos3 = 0
field = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [],
         11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: [], 18: [], 19: [], 20: [],
         21: [], 22: [], 23: [], 24: [], 25: [], 26: [], 27: [], 28: [], 29: [], 30: [],
         31: [], 32: [], 33: [], 34: [], 35: [], 36: [], 37: [], 38: [], 39: [], 40: []}
for i in field:
    if type(field[i]) == list:
        print(i, 'list')
    else:
        print(i, 'str')

print(time.time() - start_time)
