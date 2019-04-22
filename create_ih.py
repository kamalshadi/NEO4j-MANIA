# This file create the basic graph from the parcellation labels
# The default parcellation is MMP1.0 Group Parcellation
# See Glasser, Matthew F., et al. "A multi-modal parcellation of human cerebral cortex." Nature 536.7615 (2016): 171-178.


# MMP1.0 settings
from py2neo import Node, Relationship, Graph
from numpy.random import rand
import numpy as num
from tqdm import tqdm
import pickle as pk

graph = Graph(password='1234')


def readS2R(fn):
    with open(fn) as f:
        for numSeeds,line in enumerate(f):
            if numSeeds == 0:
                w = [int(float(xx)) for xx in line.strip().split()]
                numROIs = len(w)
            else:
                pass
    Z = num.zeros((numSeeds+1,numROIs))
    with open(fn) as f:
        for i,line in enumerate(f):
            w = [int(float(xx)) for xx in line.strip().split()]
            Z[i,:] = w
    return Z

def readS2R_L(fn):
    with open(fn) as f:
        for numSeeds,line in enumerate(f):
            if numSeeds == 0:
                w = [float(xx) for xx in line.strip().split()]
                numROIs = len(w)
            else:
                pass
    Z = num.zeros((numSeeds+1,numROIs))
    with open(fn) as f:
        for i,line in enumerate(f):
            w = [float(xx) for xx in line.strip().split()]
            Z[i,:] = w
    return Z


def data_raw(sub):
    print("------------------------")
    print('Subject:'+sub)
    print("creating relationships R>L")
    for i in tqdm(range(1,181),total=180):
        tmp = 'DATA/XXX/RL'+str(i)+'/matrix_seeds_to_all_targets'
        fn1 = tmp.replace('XXX',sub+'/')
        tmp = 'DATA/XXX/RL'+str(i)+'/matrix_seeds_to_all_targets_lengths'
        fn2 = tmp.replace('XXX',sub+'/')
        T = readS2R(fn1)
        D = readS2R_L(fn2)
        for j in range(1,181):
            weight = max(T[:,j-1])
            if weight > -1:
                # RIGHT HEMESPHERE
                length = D[num.argmax(T[:,j-1]),j-1]
                z = '''MATCH (a:ROI{hemisphere:"R"}),(b:ROI{hemisphere:"L"})
                WHERE a.name = 'AAA' AND b.name = 'BBB'
                CREATE (a)-[:NOS {SUBJECT:XXX,_weight:CCC,_length: DDD,weight:EEE,length:FFF}]->(b)'''.replace('XXX',sub)
                z = z.replace('AAA','R'+str(i))
                z = z.replace('BBB','L'+str(j))
                try:
                    z = z.replace('CCC','['+','.join([str(xx) for xx in T[:,j-1]])+']')
                    z = z.replace('DDD','['+','.join([str(xx) for xx in D[:,j-1]])+']')
                except:
                    print('Right to left:')
                    print("Error for i="+str(i))
                    print('--------')
                z = z.replace('EEE',str(weight))
                z = z.replace('FFF',str(length))
                graph.run(z) #.execute(z)

        # Left hemisphere
        print("creating relationships L>R")
        tmp = 'DATA/XXX/LR'+str(i)+'/matrix_seeds_to_all_targets'
        fn1 = tmp.replace('XXX',sub+'/')
        tmp = 'DATA/XXX/LR'+str(i)+'/matrix_seeds_to_all_targets_lengths'
        fn2 = tmp.replace('XXX',sub+'/')
        T = readS2R(fn1)
        D = readS2R_L(fn2)
        for j in range(1,181):
            weight = max(T[:,j-1])
            if weight > -1:
                # LEFT HEMESPHERE
                length = D[num.argmax(T[:,j-1]),j-1]
                z = '''MATCH (a:ROI{hemisphere:"L"}),(b:ROI{hemisphere:"R"})
                WHERE a.name = 'AAA' AND b.name = 'BBB'
                CREATE (a)-[:NOS { SUBJECT:XXX, _weight:CCC, _length:DDD,weight:EEE,length:FFF}]->(b)'''.replace('XXX',sub)
                z = z.replace('AAA','L'+str(i))
                z = z.replace('BBB','R'+str(j))
                try:
                    z = z.replace('CCC','['+','.join([str(xx) for xx in T[:,j-1]])+']')
                    z = z.replace('DDD','['+','.join([str(xx) for xx in D[:,j-1]])+']')
                except:
                    print('Left:')
                    print("Error for i="+str(i))
                    print('--------')
                z = z.replace('EEE',str(weight))
                z = z.replace('FFF',str(length))
                graph.run(z) #.execute(z)

def assign_labels():
    from labels import D
    for i in range(1,361):
        if i > 180:
            j = i - 180
            K = 'L'
        else:
            j = i
            K = "R"
        z = """MATCH (a:ROI)
        WHERE a.name = 'AAA'
        set a.label='XXX'""".replace('AAA',K+str(j)).replace('XXX',D[i])
        graph.run(z)

def adjacency_physical():
    import nibabel as bl
    img = bl.load("adj.pconn.nii")
    data = img.get_data()
    for i in range(1,361):
        for j in range(i,361):
            if i > 180:
                q = i - 180
                H1 = 'L'
            else:
                q = i
                H1 = "R"
            if j > 180:
                v = j - 180
                H2 = 'L'
            else:
                v = j
                H2 = "R"
            z = """MATCH (a:ROI)-[r:NOS]-(b:ROI)
            WHERE a.name = 'AAA' and b.name = 'BBB'
            set r.border=XXX""".replace('AAA',H1+str(q)).replace('BBB',H2+str(v)).replace('XXX',str(data[i-1,j-1]))
            graph.run(z)



subjects = [xx.strip() for xx in '''
401422  453542  468050'''.split()]

'''188145  206929  238033  360030  401422  453542  468050
192237  208630  248238  368753  413934  454140  481042
206323  227533  325129  392447  421226  463040'''

for sub in subjects:
    print(sub)
    data_raw(sub)
    print('<><><><><><><><><><><><><><><>')
