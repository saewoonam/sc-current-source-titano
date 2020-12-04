import storage

f = open('/readonly.txt')
state = f.readline().strip()
state = int(state)
f.close();
if (state == 1):
    print('readonly')
    storage.remount("/", readonly=True)
else:
    print('read write')
    storage.remount("/", readonly=False)