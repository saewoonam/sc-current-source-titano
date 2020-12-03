import storage

f = open('/readonly.txt')
state = f.readline().strip()
state = int(state)
f.close();
if (state == 0):
    print('read write')
    storage.remount("/", readonly=False)
else:
    print('readonly')
    storage.remount("/", readonly=True)