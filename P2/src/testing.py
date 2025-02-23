import numpy as np
import itertools as it

substitution_matrix ={'A': {'A': 0, 'C': 5, 'G': 2, 'T': 5, '-': 5}, 
                    'C': {'A': 5, 'C': 0, 'G': 5, 'T': 2, '-': 5}, 
                    'G': {'A': 2, 'C': 5, 'G': 0, 'T': 5, '-': 5}, 
                    'T': {'A': 5, 'C': 2, 'G': 5, 'T': 0, '-': 5},
                    '-': {'A': 5, 'C': 5, 'G': 5, 'T': 5, '-': 5}}

    
    
def extent(M,A):
    # Let MA be an MSA that is the extension of M with A cf. Gusfields 2-approximation algorithm.

    MA = []
    i = 0
    j = 0

    while i < len(M) and j < len(A):


        # Invariant: (1) MA is a valid merge of all columns before column i in M
        # and all columns before column in A, and (2) the first row of M and A up
        # to (but not including) column i and j respectively is the same string
        # if gaps are removed.
        
        if M[i][0] == '-' and A[j][0] == '-':
            # Case 1: The next column in MA is column i in M extended with the second symbol
            # in column j in A.
            M[i].append(A[j][1])
            MA.append(M[i])
            i = i + 1
            j = j + 1

        elif M[i][0] == '-' and A[j][0] != '-':
            # Case 2: A[j][0] is a character, so the second symbol in column j in A, A[j][1],
            # must be in the column of MA that is the column in M where the first symbol corresponds
            # to A[j][0]. By the invariant, this column in M is the next column in M, where the first
            # symbol is a character, so we just moved forward in M until we find this column.
            M[i].append('-')
            MA.append(M[i])
            i = i + 1

        elif M[i][0] != '-' and A[j][0] == '-':
            # Case 3: M[i][0] is a character, so column i in M must be in the column of MA that also
            # contains the second symbol from the column in A, where the first symbol is the character
            # corresponding to M[i][0]. By the invariant, this column in A is the next column in A,
            # where the first symbol is a character, so we just add columns from A to MA until we
            # find this column.
            c = ['-']*len(M[i])
            c.append(A[j][1])
            MA.append(c)
            j = j + 1

        elif M[i][0] != '-' and A[j][0] != '-':
            # Case 4: By the invariant the characters M[i][0] and A[j][0] are at the same position
            # in the string spelled by the row of M and A if gaps are removed. The next column in
            # MA is thus column i in M extended with the second symbol in column j in A.
            M[i].append(A[j][1])
            MA.append(M[i])
            i = i + 1
            j = j + 1

    if i < len(M):
        # add the remaining coloumns of M to MA
        while i < len(M):
            MA.append(M[i].append('-'))
            i = i + 1
            
    if j < len(A):
        # add the remaining columns of A to MA
        k = len(M[0])
        while j < len(A):
            c = ['-']*(k-1)
            c.append(A[j][1])
            MA.append(c)
            j = j + 1

    return MA

def alignment_of_3_seqs(seq1, seq2, seq3, gapcost, subst_matrix): #build using MSA frpm sldes (slide 19 and 20)
    t = np.zeros((len(seq1)+1, len(seq2)+1, len(seq3)+1))
    for i in range(1, len(seq1)+1):
        for j in range(1, len(seq2)+1):
            for k in range(1, len(seq3)+1):
                v0 = v1 = v2 = v3 = v4 = v5 = v6 = v7 = np.inf
                if i == 1 and j == 1 and k == 1:
                    v0 = 0
                if i > 1 and j > 1 and k > 1:
                    v1 = t[i-1, j-1, k-1] + subst_matrix[seq1[i-1]][seq2[j-1]] + subst_matrix[seq2[j-1]][seq3[k-1]] + subst_matrix[seq1[i-1]][seq3[k-1]]
                if i > 1 and j > 1 and k >= 1:
                    v2 = t[i-1, j-1, k] + subst_matrix[seq1[i-1]][seq2[j-1]] + gapcost + gapcost
                if i > 1 and j >= 1 and k > 1:
                    v3 = t[i-1, j, k-1] + subst_matrix[seq1[i-1]][seq3[k-1]] + gapcost + gapcost
                if i >= 1 and j > 1 and k > 1:
                    v4 = t[i, j-1, k-1] + subst_matrix[seq2[j-1]][seq3[k-1]] + gapcost + gapcost
                if i > 1 and j >= 1 and k >= 1:
                    v5 = t[i-1, j, k] + gapcost + gapcost
                if i >= 1 and j > 1 and k >= 1:
                    v6 = t[i, j-1, k] + gapcost + gapcost
                if i >= 1 and j >= 1 and k > 1:
                    v7 = t[i, j, k-1] + gapcost + gapcost
                t[i, j, k] = min(v0, v1, v2, v3, v4, v5, v6, v7)
    return t[len(seq1),len(seq2),len(seq3)]


# first part making the pairwise global alignment
def global_alignment_linear(seq1, seq2, gap_cost,subst_matrix,output_file = False):
    # Initialize the matrix with zeros
    M = [[0] * (len(seq2) + 1) for i in range(len(seq1) + 1)]
    
    # Initialize the first row and column
    for i in range(1, len(seq1) + 1):
        M[i][0] = M[i-1][0] + gap_cost
    for j in range(1, len(seq2) + 1):
        M[0][j] = M[0][j-1] + gap_cost
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            match_score = M[i-1][j-1] + subst_matrix[seq1[i-1]][seq2[j-1]]
            delete_score = M[i-1][j] + gap_cost
            insert_score = M[i][j-1] + gap_cost
            M[i][j] = min(match_score, delete_score, insert_score)
    return M


def unique_combinations(M: list[list]):
    """
    Precondition: `elements` does not contain duplicates.
    Postcondition: Returns unique combinations of length 2 from `elements`.

    >>> unique_combinations(["apple", "orange", "banana"])
    [("apple", "orange"), ("apple", "banana"), ("orange", "banana")]
    """
    return [list(i) for i in it.combinations([i for i,_ in enumerate(M[1])], 2)]

def sp_score(M,substitution_matrix):
    sum_score = 0
    for i in unique_combinations(M):
        for j,_ in enumerate(M):
            sum_score += substitution_matrix[M[j][i[0]]][M[j][i[1]]]
    return sum_score


# Traceback and compute the alignment
def backtrack(seq1,seq2,gap_cost,M):
    alignment1, alignment2 = "", ""
    i, j = len(seq1), len(seq2)
    while i > 0 or j > 0:
        if i > 0 and M[i][j] == M[i-1][j] + gap_cost:
            alignment1 = seq1[i-1] + alignment1
            alignment2 = "-" + alignment2
            i -= 1
        elif j > 0 and M[i][j] == M[i][j-1] + gap_cost:
            alignment1 = "-" + alignment1
            alignment2 = seq2[j-1] + alignment2
            j -= 1
        else:
            alignment1 = seq1[i-1] + alignment1
            alignment2 = seq2[j-1] + alignment2
            i -= 1
            j -= 1
    # return list of columns of seq1 and seq2
    list_of_columns = [[i] for i in alignment1]
    for i,v in enumerate(alignment2):
        if i > len(list_of_columns):
            list_of_columns.append([v])
        else:
            list_of_columns[i].append(v)
    return list_of_columns

        
# it works uptil here
# now lets try to extend it with storms code
def two_approx_algorithm_for_MSA(list_of_seqs, gap_cost, subst_matrix):
    # the first seq in list be s1 (the reference seq)
    s1 = list_of_seqs[0]
    M = None
    sum_sp = 0
    
    # make the pairwise alignment
    for i in range(1,len(list_of_seqs)):
        pairwise_matrix = global_alignment_linear(s1, list_of_seqs[i], gap_cost,subst_matrix)
        
        sum_sp += pairwise_matrix[len(s1)][len(list_of_seqs[i])]
        print(sum_sp)
    # make pairwise back track, corresponding to the A matrix in slides
        A = backtrack(s1, list_of_seqs[i], gap_cost, pairwise_matrix)
    # construct matrix M
        
        if M is None:
            M = A
        else:
           MA = extent(M,A)
           M = MA
        
    return M, sum_sp


def multiple_alignment(list_of_seqs, subst_matrix, aprox = False, alignment = False):
    """
    Takes a list of sequences and returns the multiple alignment of the sequences
    aprox = True if you want to use the 2-approximation algorithm
    aprox = False if you want to use the exact algorithm
    as of this moment, i dont generate the alignment but only return the score for the exact algorithm
    Furthermore, we need to give a substitution matrix as input, and the substitutuion matrix must look like this:
    {'A': {'A': 0, 'C': 5, 'G': 2, 'T': 5, '-': 5}, where the substitution_matrix['-']['-'] = gapcost
    """
    if aprox:
        M = two_approx_algorithm_for_MSA(list_of_seqs, subst_matrix)
        score = sp_score(M,subst_matrix)
        if alignment:
            return M, score
        else:
            return score
    else:
        score = alignment_of_3_seqs(list_of_seqs, subst_matrix)
        #as of this moment, i dont generate the alignment but only return the score
        return score
    

# sanity check
seq1 = 'ACGT'
seq2 = 'ACGGT'
seq3 = 'ACCCT'

# sanity check
seq1 = 'GTTCCGAAAGGCTAGCGCTAGGCGCC' #27
seq2 = 'ATGGATTTATCTGCTCTTCG'# 21#
seq3 = 'TGCATGCTGAAACTTCTCAACCA' # 24
list_of_seqs = [seq1, seq2, seq3]


substitution_matrix ={'A': {'A': 0, 'C': 5, 'G': 2, 'T': 5, '-': 5}, 
                    'C': {'A': 5, 'C': 0, 'G': 5, 'T': 2, '-': 5}, 
                    'G': {'A': 2, 'C': 5, 'G': 0, 'T': 5, '-': 5}, 
                    'T': {'A': 5, 'C': 2, 'G': 5, 'T': 0, '-': 5},
                    '-': {'A': 5, 'C': 5, 'G': 5, 'T': 5, '-': 5}}

multiple_alignment(list_of_seqs, substitution_matrix, aprox = False)

