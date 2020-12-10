import storage

def set_readonly(default=True):
    f = open('/readonly.txt','w')
    if default:
        f.write('1\r\n')
    else:
        f.write('0\r\n')
    f.close()

def get_readonly():
    f = open('/readonly.txt')
    state = f.readline().strip()
    state = int(state)
    f.close();
    if (state == 0):
        return False
    else:
        return True

def set_name(default='Unnamed'):
    f = open('/name.txt','w')
    f.write(default+'\r\n')
    f.close()

def get_name():
    try:
        f = open('/name.txt')
        name = f.readline().strip()
        f.close();
    except Exception as e:
        print("can't read name", e)
        name = "Unnamed"
    return name

