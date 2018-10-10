# This module runs group mania on a cohort of subjects.

from rankAggregation import *
import copy
import numpy as num
import pickle as pk
import os
from utils import *
# from optimization_tools import *
import sys
from tqdm import tqdm

sys.setrecursionlimit(10000)

def emergeConfidence(fp,hem,v=0):
	if fp[-1] != '/':
		fp = fp + '/'
	path_to_out = 'S' + fp + '/out/MANIA/'
	fName = path_to_out + hem.upper() + '_raw.res'

	with open(fName,'rb') as f:
		D=pk.load(f,encoding="latin1")
	nROI,nROI=D[0][0].shape
	##### nROI
	B=num.zeros((nROI,nROI))-1
	tot=nROI*(nROI-1)
	for k,d in enumerate(D):
		BM=d[0]
		for i in range(nROI):
			for j in range(nROI):
				if i==j or B[i,j]!=-1:
					continue
				if BM[i,j]==1:
					B[i,j]=-density(BM)
	return B

def mat2lis(W):
	l1,l2=W.shape
	c=0
	l=l1*l1-l1
	L=[0]*l
	for i in range(l1):
		for j in range(l2):
			if i==j:
				continue
			L[c]=W[i,j]
			c=c+1
	return L

def num2edge(a,l):
	c=0
	for i in range(l):
		for j in range(l):
			if i==j:
				continue
			if a==c:
				return (i,j)
			c=c+1

# def edge2num(a,l):
# 	c=0
# 	for i in range(l):
# 		for j in range(l):
# 			if i==j:
# 				continue
# 			if (i,j)==a:
# 				return c
# 			c=c+1
# 	print('Errrrrrrrrrrrrrrrrrrrrror')


#
# def L2E(S):
# 	l=len(S)
# 	E=[(0,0)]*l
# 	for i in range(l):
# 		E[i]=num2edge(S[i],180)
# 	return E

def group_mania(fpl,output_folder):
	l = len(fpl)
	L=[[]]*l
	print('Loading...')
	for i in range(l):
		print('Subject:'+str(i+1)+' of '+str(l))
		W=emergeConfidence(fpl[i])
		L[i]=mat2lis(W)
	l1,l2 = W.shape
	print('Aggregation...')
	S=KendalMatrix(L)
	net=agg(S,range(l1*(l2-1)))
	A=num.zeros((l1,l1))
	B=num.zeros((l1,l1))
	log=[]
	for i,ed in tqdm(enumerate(net),total=len(net)):
		tup=num2edge(ed,l1)
		A[tup[0],tup[1]]=1
		den=density(A)
		nar=NAR(A)
		B=copy.copy(A)
		log.append((B,nar,den,i))
	print('Saving...')
	if output_folder[-1] != '/':
		output_folder = output_folder+'/'
	raw = output_folder + 'agg.res'
	with open(raw,'wb') as f:
		pk.dump(log,f)
	# finalNet(output_folder, v = 1)


# group_mania(['401422','413934','421226','453542'],'GROUP')
