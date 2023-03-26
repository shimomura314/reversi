import matplotlib.pyplot as plt


with open("./strategy/QL_dict/averageQ.txt", "r") as f:
    ave_q = f.readlines()

ave_q = list(map(float, ave_q))
ave_q[0] = 0
fig = plt.figure()
plt.plot(ave_q)
plt.show()
