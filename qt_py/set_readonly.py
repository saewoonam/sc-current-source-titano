import storage

def set_readonly(default=True):
    f = open('/readonly.txt','w')
    if default:
        f.write('1\r\n')
    else:
        f.write('0\r\n')
    f.close()