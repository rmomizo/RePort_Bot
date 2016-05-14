from __future__ import division
import itertools
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import random
from random import shuffle
from collections import Counter

def flatten_list(somelist):
        if any(isinstance(el, list) for el in somelist) == False:
                return somelist
        flat_list = list(itertools.chain(*somelist))
        return flat_list

def term_frequency(somelist):
        """Returns the term frequency of each unique token in the term list"""
        somelist = flatten_list(somelist)
        term_freqs = dict(Counter(somelist))
        return term_freqs

def tf_ranks(somelist):
        term_freqs = term_frequency(somelist)

        #sort term frequencies from largest to smallest
        freqs = list(set([v for (k,v) in term_freqs.items()]))
        
        #add ranks to sorted term frequencies, creating tuple (term_freqs, rank)
        i = 1
        rfreqs = []
        for item in sorted(freqs, reverse=True):
                rfreqs.append((item, i))
                i = i + 1
                
        #create dict of keys based on terms
        term_ranks ={}
        for k, v in term_freqs.items():
                term_ranks.setdefault(k, [])

        #add (term_freq, rank) to keys
        for k, v in term_freqs.items():
                for item in rfreqs:
                        if v == item[0]:
                                term_ranks[k] = item
        return term_ranks

def find_h_index(somelist):
        tranks = tf_ranks(somelist)
        
        #h_index = [(key, (val2, 1/(val1-val2)) for (key, (val1, val2)) in tranks.iteritems()]

        #plot h_points
        values = []
        for key, (val1, val2) in tranks.iteritems():
                if val1-val2 == 0:
                    h_point = key, (val1, val2)
                    #return 'h-point is: ' + str(h_point)
                else:
                    values.append((val2, 1/(val1-val2)))

        #[(val2, 1/(val1-val2)) for key, (val1, val2) in tranks.iteritems()]

        sorted_values = sorted(values)
        xvalues = [val1 for (val1, val2) in sorted_values]
        yvalues = [val2 for (val1, val2) in sorted_values]
        # plt.scatter(xvalues, yvalues)
        # plt.title('h point')
        # plt.ylabel('1/ranks - frequency')
        # plt.xlabel('ranks')
        # plt.show()
        d = zip(xvalues, yvalues)
        data = [[x,y] for (x,y) in d ]

        return data

def find_abmin(somelist):
        tranks = tf_ranks(somelist)
        subs = []
        for key, (val1, val2) in tranks.iteritems():
                subs.append((val1-val2))
        abmin = min(subs, key=abs)
        return abmin
        
def find_h(somelist):
        tranks = tf_ranks(somelist)
        abmin = find_abmin(somelist)
        
        for key, (val1, val2) in tranks.iteritems():
                if val1-val2 == 0:
                        h_point = key, (val1, val2)
                        return h_point
                elif val1-val2 ==abmin:
                        h_point = key, (val1, val2), val1-val2
                        return h_point

def fast_h(somelist):
        h_point = find_h(somelist)
        tranks = tf_ranks(somelist)
        fast =[]

        boundary = h_point[1][1]

        for key, (val1, val2) in tranks.iteritems():
                if val2 <= boundary:
                        fast.append((key, (val1, val2)))

        return fast

def slow_h(somelist):
        h_point = find_h(somelist)
        tranks = tf_ranks(somelist)
        slow =[]

        boundary = h_point[1][1]

        for key, (val1, val2) in tranks.iteritems():
                if val2 > boundary:
                        slow.append((key, (val1, val2)))

        return slow

def h_tag_nodes(somelist):
        """
        Tag tokens in a processed list as either autosemantic(fast) or synsematic(slow).
        """
        fast = fast_h(somelist)
        fasth = [(word, {'h':'syns'}) for (word, rank) in fast]
        slow = slow_h(somelist)
        slowh = [(word, {'h':'auto'}) for (word,rank) in slow]

        h_tags = fasth + slowh

        return h_tags
        

def extract_fast_h(list_of_cycle_length_freqs, cycles):
        """
    This is specifically designed to extract lists from lists by comparing the length
    of the nested list to the most frequent cycles lengths found using fast_h method
        """
        fh = [key for (key, (val1, val2)) in fast_h(list_of_cycle_length_freqs)]
        fast_cycles = [cycle for cycle in cycles if len(cycle) in fh]

        return fast_cycles

def extract_slow_h(list_of_cycle_length_freqs, cycles):
        """
    This is specifically designed to extract lists from lists by comparing the length
    of the nested list to the most frequent cycles lengths found using slow_h method
        """
        sh = [key for (key, (val1, val2)) in slow_h(list_of_cycle_length_freqs)]
        slow_cycles = [cycle for cycle in cycles if len(cycle) in sh]

        return slow_cycles

def h_cycles(cycle_length):
        fast = [key for (key, (va1, val2)) in fast_h(cycle_length)]
        slow = [key for (key, (val1, val2)) in slow_h(cycle_length)]
        h_cycles = []
        for cycle in cycle_length:
                if cycle in fast:
                        h_cycles.append((cycle, 'autosemantic'))
                elif cycle in slow:
                        h_cycles.append((cycle, 'synsemantic'))
        return h_cycles                
                        

def find_a_param(somelist):
        h_point = find_h(somelist)
        a = len(somelist) / h_point**2
        return a
