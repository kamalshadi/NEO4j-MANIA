# This file create the basic graph from the parcellation labels
# The default parcellation is MMP1.0 Group Parcellation
# See Glasser, Matthew F., et al. "A multi-modal parcellation of human cerebral cortex." Nature 536.7615 (2016): 171-178.


# MMP1.0 settings
from py2neo import Node, Relationship, Graph
from numpy.random import rand
import numpy as num
from tqdm import tqdm
import pickle as pk

graph = Graph("bolt://localhost:7687", password='1234')


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
    left, right = True, True
    if sub.endswith('L'):
        sub = sub[:-1]
        right = False
    elif sub.endswith('R'):
        sub = sub[:-1]
        left = False

    if right:
        print("create right hemisphere nodes")
        for i in range(1,181):
            z = '''MATCH (a:ROI{name:"RXXX"}) return a'''.replace('XXX',str(i))
            mynode = list(graph.run(z))
            if (len(mynode)> 0):
                pass
            else:
                alice = Node("ROI", name="R"+str(i),ind = i, label = "test", hemisphere="R")
                graph.create(alice)

    if left:
        print("create left hemisphere nodes")
        for i in range(1,181):
            z = '''MATCH (a:ROI{name:"LXXX"}) return a'''.replace('XXX',str(i))
            mynode = list(graph.run(z))
            if (len(mynode)> 0):
                pass
            else:
                bob = Node("ROI", name="L"+str(i),ind = i, label = "test", hemisphere="L")
                graph.create(bob)

    print("creating relationships")
    for i in tqdm(range(1,181),total=180):
        if right:
            tmp = 'DATA/XXX/R'+str(i)+'/matrix_seeds_to_all_targets'
            fn1 = tmp.replace('XXX',sub+'/')
            tmp = 'DATA/XXX/R'+str(i)+'/matrix_seeds_to_all_targets_lengths'
            fn2 = tmp.replace('XXX',sub+'/')
            T = readS2R(fn1)
            D = readS2R_L(fn2)
            query = ''
            for j in range(1,181):
                if (i==j):continue
                weight = max(T[:,j-1])
                if weight > -1:
                    # RIGHT HEMESPHERE
                    length = D[num.argmax(T[:,j-1]),j-1]
                    z = '''MATCH (a:ROI{hemisphere:"R"}),(b:ROI{hemisphere:"R"})
                    WHERE a.name = 'AAA' AND b.name = 'BBB'
                    CREATE (a)-[:NOS {SUBJECT:XXX,_weight:CCC,_length: DDD,weight:EEE,length:FFF}]->(b)'''.replace('XXX',sub)
                    z = z.replace('AAA','R'+str(i))
                    z = z.replace('BBB','R'+str(j))
                    try:
                        z = z.replace('CCC','['+','.join([str(xx) for xx in T[:,j-1]])+']')
                        z = z.replace('DDD','['+','.join([str(xx) for xx in D[:,j-1]])+']')
                    except:
                        print('Right:')
                        print("Error for i="+str(i))
                        print('--------')
                    z = z.replace('EEE',str(weight))
                    z = z.replace('FFF',str(length))
                    # graph.run(z) #.execute(z)
                    query = query + '\n\n' + z
            graph.run(query)

        if left:
            # Left hemisphere
            tmp = 'DATA/XXX/L'+str(i)+'/matrix_seeds_to_all_targets'
            fn1 = tmp.replace('XXX',sub+'/')
            tmp = 'DATA/XXX/L'+str(i)+'/matrix_seeds_to_all_targets_lengths'
            fn2 = tmp.replace('XXX',sub+'/')
            T = readS2R(fn1)
            D = readS2R_L(fn2)
            query = ''
            for j in range(1,181):
                if (i==j):continue
                weight = max(T[:,j-1])
                if weight > -1:
                    # LEFT HEMESPHERE
                    length = D[num.argmax(T[:,j-1]),j-1]
                    z = '''MATCH (a:ROI{hemisphere:"L"}),(b:ROI{hemisphere:"L"})
                    WHERE a.name = 'AAA' AND b.name = 'BBB'
                    CREATE (a)-[:NOS { SUBJECT:XXX, _weight:CCC, _length:DDD,weight:EEE,length:FFF}]->(b)'''.replace('XXX',sub)
                    z = z.replace('AAA','L'+str(i))
                    z = z.replace('BBB','L'+str(j))
                    try:
                        z = z.replace('CCC','['+','.join([str(xx) for xx in T[:,j-1]])+']')
                        z = z.replace('DDD','['+','.join([str(xx) for xx in D[:,j-1]])+']')
                    except:
                        print('Left:')
                        print("Error for i="+str(i))
                        print('--------')
                    z = z.replace('EEE',str(weight))
                    z = z.replace('FFF',str(length))
                    # graph.run(z) #.execute(z)
                    query = query + '\n\n' + z
            graph.run(query)

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


def mania_raw(hem,sub):
    # hemishphere and subject are the inputs
    # read the files
    print('READING FILE for SUBJECT:'+str(sub))
    with open('S'+sub + '/out/MANIA/'+hem+'_raw.res','rb') as f:
        A = pk.load(f)
    _NET = [xx[0] for xx in reversed(A)][100:-100]
    _NAR = [xx[1] for xx in reversed(A)][100:-100]
    _density = [xx[2] for xx in reversed(A)][100:-100]
    _threshold = [xx[3] for xx in reversed(A)][100:-100]
    NAR = min(_NAR)
    ind = num.argmin(_NAR)
    density = _density[ind]
    threshold = _threshold[ind]
    NET = _NET[ind]
    z = '''MATCH (:MANIA)-[r:RAW{SUBJECT:XXX}]->(:RES{hemisphere:"GGG"}) return r'''.replace('XXX',sub).replace('GGG',hem.upper())
    print('DOES MANIA ALREAY EXIST')
    r = list(graph.run(z))
    if (len(r)>0):
        z = '''MATCH (:MANIA)-[r:RAW{SUBJECT:XXX}]->(n:RES{hemisphere:"GGG"})
        SET r._density=AAA, r._threshold=BBB, r._NAR=CCC,n.density=DDD,
        n.threshold=EEE, n.NAR=FFF'''.replace('XXX',sub).replace('GGG',hem.upper())
    else:
        z = '''MATCH (m:MANIA)
        CREATE (m)-[r:RAW{SUBJECT:XXX}]->(n:RES{hemisphere:"GGG"})
        SET r._density=AAA, r._threshold=BBB, r._NAR=CCC,n.density=DDD,
        n.threshold=EEE, n.NAR=FFF'''.replace('XXX',sub).replace('GGG',hem.upper())
    z = z.replace('AAA','['+','.join([str(xx) for xx in _density])+']')
    z = z.replace('BBB','['+','.join([str(xx) for xx in _threshold])+']')
    z = z.replace('CCC','['+','.join([str(xx) for xx in _NAR])+']')
    z = z.replace('DDD',str(density))
    z = z.replace('EEE',str(threshold))
    z = z.replace('FFF',str(NAR))
    print('SAVING MANIA RESULTS')
    graph.run(z)
    print('NETWORK UPDATE')
    for i in tqdm(range(180),total=180):
        for j in range(180):
            if i==j:continue
            if NET[i,j] == 0:continue
            z = '''MATCH (n:ROI{name:"AAA"})-[r:MANIA{SUBJECT:XXX}]->(m:ROI{name:"BBB"}) return r'''.replace('XXX',sub)
            z = z.replace('AAA',hem.upper()+str(i+1))
            z = z.replace('BBB',hem.upper()+str(j+1))
            r = list(graph.run(z))
            if (len(r)>0):
                z = '''MATCH (n:ROI{name:"AAA"})-[r:MANIA{SUBJECT:XXX}]->(n:ROI{name:"BBB"})
                set r.connected = 1'''.replace('XXX',sub)
            else:
                z = '''MATCH (n:ROI{name:"AAA"}),(m:ROI{name:"BBB"})
                CREATE (n)-[r:MANIA{SUBJECT:XXX}]->(m)
                set r.connected = 1'''.replace('XXX',sub)
            z = z.replace('AAA',hem.upper()+str(i+1))
            z = z.replace('BBB',hem.upper()+str(j+1))
            r = graph.run(z)

def threshold_raw(hem,sub,T="1500"):
    # hemishphere and subject are the inputs

    # read the files
    print('READING FILE for SUBJECT:'+str(sub))
    with open('S'+sub + '/out/MANIA/'+hem+'_raw.res','rb') as f:
        A = pk.load(f,encoding='latin1')
    _NET = [xx[0] for xx in reversed(A)][100:-100]
    _NAR = [xx[1] for xx in reversed(A)][100:-100]
    _density = [xx[2] for xx in reversed(A)][100:-100]
    _tt = [xx[3] for xx in reversed(A)][100:-100]
    _threshold = [abs(xx[3]-int(T)) for xx in reversed(A)][100:-100]
    ind = num.argmin(_threshold)
    NAR = _NAR[ind]
    density = _density[ind]
    threshold = _tt[ind]
    NET = _NET[ind]
    z = '''MATCH (:THRESHOLD)-[r:RAW{SUBJECT:XXX, T:YYY}]->(:RES{hemisphere:"GGG"}) return r'''.replace('XXX',sub).replace('YYY',T).replace('GGG',hem.upper())
    print('DOES threshold network ALREAY EXIST')
    r = list(graph.run(z))
    if (len(r)>0):
        z = '''MATCH (:THRESHOLD)-[r:RAW{SUBJECT:XXX, T:YYY}]->(n:RES{hemisphere:"GGG"})
        SET r._density=AAA, r._threshold=BBB, r._NAR=CCC,n.density=DDD,
        n.threshold=EEE, n.NAR=FFF'''.replace('XXX',sub).replace('YYY',T).replace('GGG',hem.upper())
    else:
        z = '''MATCH (m:THRESHOLD)
        CREATE (m)-[r:RAW{SUBJECT:XXX,T:YYY}]->(n:RES{hemisphere:"GGG"})
        SET r._density=AAA, r._threshold=BBB, r._NAR=CCC,n.density=DDD,
        n.threshold=EEE, n.NAR=FFF'''.replace('XXX',sub).replace('YYY',T).replace('GGG',hem.upper())
    z = z.replace('AAA','['+','.join([str(xx) for xx in _density])+']')
    z = z.replace('BBB','['+','.join([str(xx) for xx in _threshold])+']')
    z = z.replace('CCC','['+','.join([str(xx) for xx in _NAR])+']')
    z = z.replace('DDD',str(density))
    z = z.replace('EEE',str(threshold))
    z = z.replace('FFF',str(NAR))
    print('SAVING Threshold RESULTS')
    graph.run(z)
    print('NETWORK UPDATE')
    for i in tqdm(range(180),total=180):
        for j in range(180):
            if i==j:continue
            if NET[i,j] == 0:continue
            z = '''MATCH (n:ROI{name:"AAA"})-[r:THRESHOLD{SUBJECT:XXX, T:YYY}]->(m:ROI{name:"BBB"}) return r'''.replace('XXX',sub).replace('YYY',T)
            z = z.replace('AAA',hem.upper()+str(i+1))
            z = z.replace('BBB',hem.upper()+str(j+1))
            r = list(graph.run(z))
            if (len(r)>0):
                z = '''MATCH (n:ROI{name:"AAA"})-[r:THRESHOLD{SUBJECT:XXX, T:YYY}]->(n:ROI{name:"BBB"})
                set r.connected = 1'''.replace('XXX',sub).replace('YYY',T)
            else:
                z = '''MATCH (n:ROI{name:"AAA"}),(m:ROI{name:"BBB"})
                CREATE (n)-[r:THRESHOLD{SUBJECT:XXX, T:YYY}]->(m)
                set r.connected = 1'''.replace('XXX',sub).replace('YYY',T)
            z = z.replace('AAA',hem.upper()+str(i+1))
            z = z.replace('BBB',hem.upper()+str(j+1))
            r = graph.run(z)
# mania_raw('L','401422')
# mania_raw('L','413934')
# mania_raw('L','421226')
subjects = [xx.strip() for xx in '''
206323 208630 401422 248238 413934
192237R 227533R 368753L 453542L 468050L'''.split()]

'''188145'''

for sub in subjects:
    print(sub)
    data_raw(sub)
    print('<><><><><><><><><><><><><><><>')
#     for hem in ['L','R']:
#         print(sub+":"+hem)
#         mania_raw(hem,sub)
#         for i in [1600,1800,2000,2200,2400,2600,2800,3000]:
#             print(sub+":"+hem+":"+str(i))
#             print('---------------------')
#             threshold_raw(hem,sub,str(i))

# adjacency_physical()
# assign_labels()
# data_raw('401422')
# assign_labels()
# adjacency_physical()
# mania_raw("L",'421226')
# mania_raw("L",'453542')
# mania_raw('L','463040')
# mania_raw('L','468050')
# mania_raw('L','481042')
# mania_raw("R",'401422')
# mania_raw("R",'421226')
# mania_raw("R",'453542')
# mania_raw("R",'463040')
# mania_raw("R",'468050')
# mania_raw("R",'481042')
