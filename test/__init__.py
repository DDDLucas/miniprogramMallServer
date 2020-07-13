import hashlib

m1 = hashlib.md5()

m = hashlib.sha1()
m.update(b"Nobody inspects")
m.update(b" the spammish repetition")
print(m.hexdigest())