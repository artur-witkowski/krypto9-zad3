import sys
import re

if len(sys.argv) < 3:
    print('Usage: python stegano.py <-e/-d> <-1/-2/-3/-4>')
    exit(1)

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

        line = 0
        startIndex = 0
        for i in range(len(binToEncode)):
            foundPlace = None
            while foundPlace == None:
                occ = [(m.start(0), m.end(0)) for m in re.finditer(r'^[ ]{1}[^ ]|[^ ][ ]{1}$|[^ ][ ]{1}[^ ]', htmlSource[line])]
                for j in range(len(occ)):
                    if occ[j][0] >= startIndex:
                        foundPlace = occ[j]
                        break
                if foundPlace != None:
                    break
                line += 1
                startIndex = 0
            [start, end] = foundPlace
            if (binToEncode[i] == '1'):
                if start > 0: start = start + 1
                if end < len(htmlSource[line])-1: end = end - 1
                htmlSource[line] = htmlSource[line][:start] + '  ' + htmlSource[line][end:]
                startIndex += 1
            startIndex = foundPlace[0] + 1
                
        with open('watermark.html', 'w') as f:
            f.write("".join(htmlSource))

def decodeDoubleSpaces():
    with open('watermark.html') as f:
        htmlSource = f.readlines()
        message = ''
        for i in range(len(htmlSource)):
            occ = [(m.start(0), m.end(0)) for m in re.finditer(r'[ ]+', htmlSource[i])]
            for [start, end] in occ:
                if end - start == 2:
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

def encodeWrongCSS():
    message = None
    with open('mess.txt') as f:
        message = f.readlines()[0]
    with open('cover.html') as f:
        htmlSource = f.readlines()
        binToEncode = hexToBin(message)
        tagRegex = r'<[a-zA-Z]+>'
        wrongCSS = ' style="margin-botom: 0cm; lineheight: 100%"'

        counterTages = 0
        for i in range(len(htmlSource)):
            occ = [(m.start(0), m.end(0)) for m in re.finditer(tagRegex, htmlSource[i])]
            counterTages += len(occ)

        if counterTages < len(binToEncode):
            print('Message is too long to encode')
            return

        line = 0
        startIndex = 0
        for i in range(len(binToEncode)):
            foundPlace = None
            while foundPlace == None:
                occ = [(m.start(0), m.end(0)) for m in re.finditer(tagRegex, htmlSource[line])]
                for j in range(len(occ)):
                    if occ[j][0] >= startIndex:
                        foundPlace = occ[j]
                        break
                if foundPlace != None:
                    break
                line += 1
                startIndex = 0
            [start, end] = foundPlace
            if (binToEncode[i] == '1'):
                htmlSource[line] = htmlSource[line][:end-1] + wrongCSS + htmlSource[line][end-1:]
            startIndex = start + 1
        
        with open('watermark.html', 'w') as f:
            f.write("".join(htmlSource))
    
def decodeWrongCSS():
    with open('watermark.html') as f:
        htmlSource = f.readlines()
        tagRegex = r'<[a-zA-Z]+>'
        wrongCSS = ' style="margin-botom: 0cm; lineheight: 100%"'
        message = ''

        for i in range(len(htmlSource)):
            occTag = [m.start(0) for m in re.finditer(tagRegex, htmlSource[i])]
            occWrong = [m.start(0) for m in re.finditer(wrongCSS, htmlSource[i])]
            maxTag, maxWrong = 0, 0
            if len(occTag) > 0:
                maxTag = occTag[-1]
            if len(occWrong) > 0:
                maxWrong = occWrong[-1]
            for j in range(max(maxTag, maxWrong)+1):
                if j in occTag:
                    message += '0'
                elif j in occWrong:
                    message += '1'
                
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

def encodeEmptyTags():
    message = None
    with open('mess.txt') as f:
        message = f.readlines()[0]
    with open('cover.html') as f:
        htmlSource = f.readlines()
        binToEncode = hexToBin(message)
        tagOpen = '<font>'
        tagEnd = '</font>'
        tagOpenFiller = '<font></font><font>'
        tagEndFiller = '</font><font></font>'

        counterTages = 0
        for i in range(len(htmlSource)):
            occ = [(m.start(0), m.end(0)) for m in re.finditer(tagOpen, htmlSource[i])]
            counterTages += len(occ)

        if counterTages < len(binToEncode):
            print('Message is too long to encode')
            return

        line = 0
        startIndex = 0
        for i in range(len(binToEncode)):
            foundPlace = None
            while foundPlace == None:
                occ = []
                if binToEncode[i] == '1':
                    occ = [(m.start(0), m.end(0)) for m in re.finditer(tagOpen, htmlSource[line])]
                else:
                    occ = [(m.start(0), m.end(0)) for m in re.finditer(tagEnd, htmlSource[line])]
                for j in range(len(occ)):
                    if occ[j][0] >= startIndex:
                        foundPlace = occ[j]
                        break
                if foundPlace != None:
                    break
                line += 1
                startIndex = 0
            [start, end] = foundPlace
            if (binToEncode[i] == '1'):
                htmlSource[line] = htmlSource[line][:start] + tagOpenFiller + htmlSource[line][end:]
            else:
                htmlSource[line] = htmlSource[line][:start] + tagEndFiller + htmlSource[line][end:]
            line += 1
            startIndex = 0
        
        with open('watermark.html', 'w') as f:
            f.write("".join(htmlSource))
    
def decodeEmptyTags():
    with open('watermark.html') as f:
        htmlSource = f.readlines()
        tagOpenFiller = '<font></font><font>'
        tagEndFiller = '</font><font></font>'
        message = ''

        for i in range(len(htmlSource)):
            occOpen = [m.start(0) for m in re.finditer(tagOpenFiller, htmlSource[i])]
            occEnd = [m.start(0) for m in re.finditer(tagEndFiller, htmlSource[i])]
            maxOpen, maxEnd = 0, 0
            if len(occOpen) > 0:
                maxOpen = occOpen[-1]
            if len(occEnd) > 0:
                maxEnd = occEnd[-1]
            for j in range(max(maxOpen, maxEnd)+1):
                if j in occOpen:
                    message += '1'
                elif j in occEnd:
                    message += '0'

        hexMessage = binToHex(message)
        with open('detect.txt', 'w') as f:
            f.write(hexMessage)
            f.write('\n')
            f.write(hexToText(hexMessage))


if option == '-e':
    if algorithm == '-1':
        encodeEndlineSpaces()
    elif algorithm == '-2':
        encodeDoubleSpaces()
    elif algorithm == '-3':
        encodeWrongCSS()
    elif algorithm == '-4':
        encodeEmptyTags()
    else:
        print('Wrong algorithm. Choose 1, 2, 3 or 4.')
    pass
elif option == '-d':
    if algorithm == '-1':
        decodeEndlineSpaces()
    elif algorithm == '-2':
        decodeDoubleSpaces()
    elif algorithm == '-3':
        decodeWrongCSS()
    elif algorithm == '-4':
        decodeEmptyTags()
    else:
        print('Wrong algorithm. Choose 1, 2, 3 or 4.')
    pass
else:
    print("Usage: stegano.py -e|-d")
