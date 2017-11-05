fi = open("names.txt")
names = [line.strip() for line in fi]
print(names)
fi.close()
fi = open("names.txt", "w")
for x in names: fi.write(x+'\n')
fi.write(input('name: '))
fi.close()
