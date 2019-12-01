import random 

nodes = 50
runs = 500
avg_time = 10
num_blocks = 30

r = [random.random() for i in range(nodes)]
s = sum(r)
hp = [i/s for i in r]
print("Hash power: {}".format(hp))
rate = [1 / ((1 / i) * avg_time) for i in hp]
print("Block rate per minute: {}".format(rate))
print("Sum block rate: {}".format(sum(rate)))

mean = 0
for r in range(runs):
    time = 0
    
    for i in range(num_blocks):
        #print("Block {}".format(i))
        times = []
        for n in range(nodes):
            times.append(random.expovariate(rate[n]))

        time += min(times)
        #print("times to next block {}".format(times))
    mean += time / 60
print(mean / runs)
    

