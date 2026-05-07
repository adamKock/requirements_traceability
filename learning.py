
#Week 1 Vars 
import redis


names =["Adam", "Tom", "Steve", "Sam"]
names_start_with_s = []


for name in names[:]:
    if name.startswith("S"):
        names_start_with_s.append(name)
    elif name.startswith("T"):
        names.remove(name)


print(names)
print(names_start_with_s)





