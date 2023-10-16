# import numpy as np
# a = np.array([1,2,3]) or
# a = np.array([list_1,list_2,list_3]) where list_1 = [1,2,3]
# list_2 = [1,4,5], list_3 = [3,8,9]
# a = np.array([1,2,3]) a.shape => (3,) or
# a = np.array([[1,2,3], [4,5,6]]) a.shape => (2,3)
# a = np.array([[[1,2,3],[4,5,6]],[[1,2,3],[4,5,6]]]) a.shape => (2,2,3)
# b = np.array([[[1,2,3],[4,5,6]],[[1,2,3],[4,5,6]]]) b.ndim => 3 //no of dimensions/axes
# a = np.array([1,2,3,4,5,6]) a * 2 => [2,4,6,8,10,12]
# b = np.array([ [1,2], [5,6] ]) c = b [1] * 2 => [10,12]
#                                d = b[0][1] => 2
# a = np.array([1,2,3,4,5]) a.mean() => 3.0
# b = np.array([ [1,2,3,4,5], [6,7,8,9,10] ])
#     np.mean(b, axis = 0) => [3.5 4.5 5.5 6.5 7.5] /average accross rows
#     np.mean(b, axis = 1) => [3. 8.] //average accross columns
# a = [1,2,3], b = [2,4,6]
#    a . b = (1x2) + (2x4) + (3x6) = 2+8+18 = 28
# using numpy: a = np.array([1,2,3]), b = np.array([2,4,6])
#      dp = np.dot(a,b) => 18
# b = np.array([ [1,2,3,4,5],[6,7,8,9,10]]), list_to_add = [3,6,9,12,15]
#   b = np.vstack([b, list_to_add]) b => [ [1,2,3,4,5],[6,7,8,9,10],[3,6,9,12,15] ]
# b = np.array([ [1,2,3,4,5],[6,7,8,9,10] ]), column_to_add = [ [6],[12] ]
#   b = np.hstack([b, column_to_add]) b => [ [1,2,3,4,5,6] [6,7,8,9,10,12] ]
# b = np.array([ [1,2,3,4,5], [5,6,7,8,9]])
#   b = np.unique(b) => [1,2,3,4,5,6,7,8,9]
# b = np.array([ [1,2,3], [4,5,6], [1,2,3] ])
#    b = np.unique(b, axis=0) b => [ [1 2 3] [4 5 6] ]
# why use numpy? It's very fast as compared to normal computation
# Pandas always work hand in hand with numpy so you need to learn about them
