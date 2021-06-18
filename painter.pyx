import cython
from functools import lru_cache

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
char_range = int(255 / len(characters))

@lru_cache
def get_char(val):
    return characters[min(int(val/char_range), len(characters)-1)]

@cython.boundscheck(False)
cpdef paint_screen(window, unsigned char [:, :] frame, int width, int height):
    cdef int x, y

    for y in range(0, frame.shape[0]):
        for x in range(0, frame.shape[1]):
            try:                
                window.addch(y, x, get_char(frame[y, x]))
            except:
                pass
