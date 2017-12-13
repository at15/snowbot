NEWLINE = '\\newline'
# NEWLINE = '\\\\'

def main():
    with open('dialogs.txt', 'r') as f:
        start = False
        count = 0
        for l in f:
            l = l.rstrip()
            if not l:
                continue
            if l[0] == '#':
                pass
            elif l.startswith('@start'):
                start = True
                count = 0
            elif l.startswith('@end'):
                start = False
                print()
            elif start:
                if count % 2 == 0:
                    print('Q:', l, NEWLINE)
                else:
                    print('A:', l, NEWLINE)
                count += 1
            else:
                print('unknown', l)


if __name__ == '__main__':
    main()
