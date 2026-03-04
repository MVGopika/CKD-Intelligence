import numpy as np
from sklearn.preprocessing import label_binarize

y = np.array([1, 2, 3, 4])
classes = [1, 2, 3, 4, 5]

try:
    print("Test 1: y=[1,2,3,4], classes=[1,2,3,4,5]")
    y_bin = label_binarize(y, classes=classes)
    print("Success 1, shape:", y_bin.shape)
except Exception as e:
    print("Fail 1:", e)

y2 = np.array([1, 2, 3, 4, 5])
classes2 = [1, 2, 3, 4]
try:
    print("\nTest 2: y=[1,2,3,4,5], classes=[1,2,3,4]")
    y_bin2 = label_binarize(y2, classes=classes2)
    print("Success 2, shape:", y_bin2.shape)
except Exception as e:
    print("Fail 2:", e)
