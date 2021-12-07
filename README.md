## **Grouping PDFs by Format with Hierarchical Clustering**

### **What is it?**

This code performs agglomerative hierarchical clustering on page abstractions of PDFs. The goal is to sort the PDFs by format. The code uses the percentage of pixels that differ in color between two images as a measure of distance. It compares clusters by comparing their clustroids, or the item in the cluster that minimizes the distance to all other items. It stops combining clusters when the diameter of the newly created cluster passes a particular threshold. The diameter of a cluster is the farthest distance between two items in the cluster. This is an adjustment from the original project proposal, which suggested stopping the algorithm when the change in average diameter exceeded a particular threshold. Experimentation determined that thresholding by the diameter of a new cluster was more effective. I have implemented a speedup to try and combat the inefficiency of the clustering algorithm. Instead of searching for the pair of clusters with the shortest distance, it maintains a priority queue of the distances between each pair of clusters, and just updates the queue when new clusters are formed. The code finally rearranges the images into subfolders based on the clusters it outputs.

### **How to run the code?**

First, log into mirage, or whatever environment will be used to run this code.

Then, run the follow commands to install the necessary dependencies:
    pip install opencv-python
    pip install HeapDict

Finally, run the code:
    python3 agglomerative_clustering.py
    
The code takes about 8-13 minutes to sort 250 images on my machine.

### **How to interpret the results?**

The code has run correctly if the original *Output_Shape_Images* folder is now full of subfolders representing the clusters with images sorted into them. These images are grouped by the percentage of pixels that are the same color. Ideally, this should act as a proxy for PDF format.
