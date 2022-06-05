import sys
import re

option = sys.argv[1]
algorithm = sys.argv[2]

def hexToBin(hex):
    return bin(int(hex, 16))[2:]

def binToHex(bin):
    return hex(int(bin, 2))[2:]

def textToHex(text):
    return text.encode("utf-8").hex()

def hexToText(hex):
    return bytes.fromhex(hex).decode("utf-8")

def findAllOccurrences(text, pattern):
    occurrences = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i+len(pattern)] == pattern:
            occurrences.append(i)
    return occurrences

def encodeEndlineSpaces():
    message = None
    with open('mess.txt') as f:
        message = f.readlines()[0]
    with open('cover.html') as f:
        htmlSource = f.readlines()
        binToEncode = hexToBin(message)

        if len(htmlSource) < len(binToEncode):
            print('Message is too long to encode')
            return

        for i in range(len(binToEncode)):
            htmlSource[i]
            if (binToEncode[i] == '1'):
                htmlSource[i] = htmlSource[i][:-1].rstrip() + f' \n'
            else:
                htmlSource[i] = htmlSource[i][:-1].rstrip()+ '\n'
        with open('watermark.html', 'w') as f:
            f.write("".join(htmlSource))
    
def decodeEndlineSpaces():
    with open('watermark.html') as f:
        htmlSource = f.readlines()
        message = ''
        for i in range(len(htmlSource)):
            if htmlSource[i][-2:-1] == ' ':
                message += '1'
            else:
                message += '0'
        diff = len(message) % 4 + 1
        if diff != 0:
            message = message[:-(diff)]
        while message[-4:] == '0000':
            message = message[:-4]
        hexMessage = binToHex(message)
        with open('detect.txt', 'w') as f:
            f.write(hexMessage)
            f.write('\n')
            f.write(hexToText(hexMessage))

def encodeDoubleSpaces():
    message = None
    with open('mess.txt') as f:
        message = f.readlines()[0]
    with open('cover.html') as f:
        htmlSource = f.readlines()
        binToEncode = hexToBin(message)

        counterSpaces = 0
        for i in range(len(htmlSource)):
            occ = findAllOccurrences(htmlSource[i], ' ')
            counterSpaces += len(occ)

        if counterSpaces < len(binToEncode):
            print('Message is too long to encode')
            return

        for i in range(len(htmlSource)):
            while re.search(r'[ ]{2,}', htmlSource[i]):
                htmlSource[i] = re.sub(r'[ ]{2,}', ' ', htmlSource[i])

        # TODO: create good replacement system for single spaces
        line = 0
        for i in range(len(binToEncode)):
            while not re.search(r'[^ ][ ]{1}[^ ]', htmlSource[line]):
                line += 1
            if (binToEncode[i] == '1'):
                htmlSource[line] = re.sub(r'([^ ])[ ]{1}([^ ]', '  ', htmlSource[line])
        with open('watermark.html', 'w') as f:
            f.write("".join(htmlSource))

def decodeDoubleSpaces():
    pass

if option == '-e':
    if algorithm == '-1':
        encodeEndlineSpaces()
    elif algorithm == '-2':
        encodeDoubleSpaces()
    elif algorithm == '-3':
        pass
    elif algorithm == '-4':
        pass
    else:
        print('Wrong algorithm. Choose 1, 2, 3 or 4.')
    pass
elif option == '-d':
    if algorithm == '-1':
        decodeEndlineSpaces()
    elif algorithm == '-2':
        decodeDoubleSpaces()
    elif algorithm == '-3':
        pass
    elif algorithm == '-4':
        pass
    else:
        print('Wrong algorithm. Choose 1, 2, 3 or 4.')
    pass
else:
    print("Usage: stegano.py -e|-d")
