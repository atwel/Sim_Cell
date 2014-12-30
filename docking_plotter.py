import matplotlib.pyplot as plt



def get_step_count(PRODUCT_TYPES):
    """A utility function to determine how long to run the model.
    """

    STEPS = 270000
    
    if PRODUCT_TYPES == 3:
        STEPS = 410000
    elif PRODUCT_TYPES == 4:
        STEPS = 580000
    elif PRODUCT_TYPES == 5:
        STEPS = 770000
    elif PRODUCT_TYPES == 6:
        STEPS = 980000
    elif PRODUCT_TYPES == 7:
        STEPS = 1210000
    elif PRODUCT_TYPES == 8:
        STEPS = 1460000
    elif PRODUCT_TYPES == 9:
        STEPS = 1720000
                         
    return STEPS




PRODUCT_TYPES = [3,4,5,6,7,8,9]
CHEMISTRY = ["ALL"] # "SOLOH"
INTEL_TYPE = [False] # => "selective"
URN_TYPE = ["fixed-rich","fixed-poor","endo-rich","endo-poor"]
REPRO_TYPE = ["target","source"] # "target"
TOPOLOGY = ["spatial"] # "well-mixed"

stack = {}

for TYPES in PRODUCT_TYPES:
	for CHEM in CHEMISTRY:
		for INTEL in INTEL_TYPE:
			for URN in URN_TYPE:
				for REPRO in REPRO_TYPE:
					for TOPO in TOPOLOGY:
						mystr = "-".join([str(TYPES), CHEM, str(INTEL), URN, REPRO, TOPO])
						datafile = open(mystr+".csv","r+")
						vals = []
						three_vals = []
						cells = []
						rules = []
						count_runs = 0.
						step_count = get_step_count(TYPES)
						
						for line in datafile:
							count_runs += 1
							pre = line.replace("{","|").replace("}","|")
							raw = pre.strip().split("|")
							run = int(raw[0].replace(",",""))
							precycles = raw[1].split(",")
							cycles = {}
							for i in precycles:
   								try:
   									j,k = i.split(":")
   									cycles[int(j)] = int(k)
   								except:
   									cycles = {}

							after = raw[2].split(",")
							if after[2]=='False':
								cells.append(0)
							else:
								cells.append(1)
							rules.append(int(bool(after[2])))

						  	if int(after[4]) > step_count*.95:
								if len(cycles.keys()) > 1:
									vals.append(1)
								else:
									vals.append(0)

							if cycles != {}:
								vals.append(1)
								if len(cycles.keys()) > 1:
									three_vals.append(1)
								else:
									three_vals.append(0)
							else:
								vals.append(0)		
								three_vals.append(0)
                     				

                  				try:
                  					stack[URN+REPRO].append(sum(three_vals)/count_runs)
                  				except:
                  					stack[URN+REPRO] = [sum(three_vals)/count_runs]


x = [2,3,4,5,6,7,8,9]

plt.axis([1,10,-.05,1.1])
plt.plot(x,stack["fixed-richsource"], label="source-rich", color="k", marker="s",markeredgecolor="k",ms=8,linestyle="solid", linewidth=2)
plt.plot(x,stack["fixed-poorsource"], label="souce-poor", color="k", marker="^",linestyle="solid",linewidth=2,markeredgecolor="k",ms=8)
plt.plot(x,stack["endo-richsource"], label="stigmergy-rich", color="r", marker="s",linestyle="solid",linewidth=2,markeredgecolor="r",ms=8)
plt.plot(x,stack["endo-poorsource"], label="stigmergy-poor", color="r", marker="^",linestyle="solid",linewidth=2,markeredgecolor="r",ms=8)
plt.plot(x,stack["fixed-richtarget"], label="target-rich", color="b", marker="s",linestyle="solid",linewidth=2,markeredgecolor="b",ms=8)
plt.plot(x,stack["fixed-poortarget"], label="target-poor", color="b", marker="^",linestyle="solid",linewidth=2,markeredgecolor="b",ms=8)



plt.title("Random Search ALL, Simultaneous Chains starting with Cells")
plt.ylabel("Fraction of 100 runs w/ Hypercycles")
plt.legend(loc="lower left")

plt.show()