import numpy as np

from src.utils.constants.simple import Debug


def writeFile(fileName, a, nx, ny, debug_level=Debug.OFF):
    with open(fileName, 'w') as file:
        # Choose an arbitrary heading
        outstring = '-996  ' + str(ny) + '  50.000000     50.000000\n'
        outstring += '637943.187500   678043.187500  4334008.000000  4375108.000000\n'
        outstring += ' ' + str(nx) + ' ' + ' 0.000000   637943.187500  4334008.000000\n'
        outstring += '0     0     0     0     0     0     0\n'
        count = 0
        text = ''
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count >= 5:
                text += '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    print('Write file: ' + fileName)


def readFile(fileName, debug_level=Debug.OFF):
    print('Read file: ' + fileName)
    with open(fileName, 'r') as file:
        inString = file.read()
        words = inString.split()
        ny = int(words[1])
        nx = int(words[8])
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            n = len(words)
            print('Number of words: ' + str(n))
            print('nx,ny: ' + str(nx) + ' ' + str(ny))
            print('Number of values: ' + str(len(words) - 19))
        a = np.zeros(nx * ny, float)
        for i in range(19, len(words)):
            a[i - 19] = float(words[i])
    return a, nx, ny

def writeFileRTF(fileName, a, nx, ny, dx, dy, x0, y0, debug_level=Debug.OFF):
    # Write in Roxar text format
    with open(fileName, 'w') as file:
        outstring = '-996  ' + str(ny) + '  ' + str(dx) + ' ' + str(dy) +'\n'
        outstring += str(x0) + ' ' + str(x0 + nx*dx) + ' ' + str(y0) + ' ' + str(y0+ny*dy) +'\n'
        outstring += ' ' + str(nx) + ' ' + ' 0.000000  ' +  str(x0) + ' ' + str(y0) + '\n'
        outstring += '0     0     0     0     0     0     0\n'
        count = 0
        text = ''
        if debug_level >= Debug.SOMEWHAT_VERBOSE:
            print('len(a): ' + str(len(a)))
        for j in range(len(a)):
            text = text + str(a[j]) + '  '
            count += 1
            if count >= 5:
                text += '\n'
                outstring += text
                count = 0
                text = ''
        if count > 0:
            outstring += text + '\n'
        file.write(outstring)
    print('Write file: ' + fileName)

