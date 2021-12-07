import os
import sys
import cv2
import heapdict

class Cluster:
    def __init__(self, images):
        self.images = images
        if len(images) == 1:
            self.clustroid = images[0]
            self.diameter = 0
        else:
            self.clustroid = self.find_clustroid()
            self.diameter = self.find_diameter()
    
    def get_clustroid(self):
        return self.clustroid

    def get_images(self):
        return self.images
    
    def get_diameter(self):
        return self.diameter
    
    def get_id(self):
        return id(self)
    
    def find_clustroid(self):
        best_dist = sys.maxsize
        clustroid = None

        for i in range(len(self.images)):
            dist = 0
            for c in range(i+1, len(self.images)):
                dist += pdfDist(self.images[i], self.images[c])
            if dist < best_dist:
                best_dist = dist
                clustroid = self.images[i]
        
        return clustroid
    
    def find_diameter(self):
        max_dist = -sys.maxsize

        for i in range(len(self.images)):
            for c in range(i+1, len(self.images)):
                dist = pdfDist(self.images[i], self.images[c])
                if dist > max_dist:
                    max_dist = dist
        
        return max_dist




class Image:
    def __init__(self, image_path):
        self.path = image_path
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        self.height, self.width = self.image.shape

    def get_path(self):
        return self.path

    def get_image(self):
        return self.image

    def get_height(self):
        return self.height
    
    def get_width(self):
        return self.width



def pdfDist(image1, image2):
    '''
    Calculate the percentage of pixels that differ between two images
        Resize images so comparison can be made
    '''

    w1 = image1.get_width()
    h1 = image1.get_height()
    w2 = image2.get_width()
    h2 = image2.get_height()
    w_to_use = -1
    h_to_use = -1

    img1 = image1.get_image()
    img2 = image2.get_image()
    
    if w1*h1 < w2*h2:
        img2 = cv2.resize(img2, (w1, h1))
        w_to_use = w1
        h_to_use = h1
    else:
        img1 = cv2.resize(img1, (w2, h2))
        w_to_use = w2
        h_to_use = h2

    dist = 0

    for y in range(h_to_use):
        for x in range(w_to_use):
            if abs(int(img1[y,x]) - int(img2[y,x])) > 20:
                dist += 1
    
    scaled_dist = dist/(w_to_use*h_to_use)

    return scaled_dist



def get_queue_id(cluster1, cluster2):
    '''
    Find the queue id to be used in the priority queue
    '''
    return str(id(cluster1)) + "-" + str(id(cluster2))



def create_dist_queue(clusters):
    '''
    Create the priority queue of distances between clusters and a dictionary matching object id to cluster
    '''
    priority_dict = heapdict.heapdict()
    queue_dict = {}
    for c1 in range(len(clusters)):
        queue_dict[str(id(clusters[c1]))] = clusters[c1]
        for c2 in range(c1+1, len(clusters)):
            unique_id = get_queue_id(clusters[c1], clusters[c2])
            priority_dict[unique_id] = pdfDist(clusters[c1].get_clustroid(), clusters[c2].get_clustroid())
    
    return queue_dict, priority_dict



def update_dist_queue(priority_queue, clusters, cluster_one, cluster_two, new_cluster):
    '''
    Update the priority queue based on the clusters combined
    '''
    id1 = str(id(cluster_one))
    id2 = str(id(cluster_two))

    # Remove items with old clusters
    keys = list(priority_queue.keys())
    for key in keys:
        if id1 in key or id2 in key:
            priority_queue.pop(key)

    # Add pairwise distances with new cluster to priority queue
    for cluster in clusters:
        unique_id = get_queue_id(new_cluster, cluster)
        priority_queue[unique_id] = pdfDist(new_cluster.get_clustroid(), cluster.get_clustroid())
    
    return priority_queue



def cluster(images):
    '''
    Run the agglomerative clustering algorithm
    '''
    clusters = []

    # Initialize each image in it's own cluster
    for image in images:
        clusters.append(Cluster([image]))
    
    # Continue combining the two closest clusters until the diameter threshold is reached
    cluster_dict, priority_queue = create_dist_queue(clusters)
    running = True
    while running:
        (top_pair, priority) = priority_queue.popitem()
        top_pair = top_pair.split("-")
        cluster_one = cluster_dict[top_pair[0]]
        cluster_two = cluster_dict[top_pair[1]]
        new_images = cluster_one.get_images() + cluster_two.get_images()
        temp_cluster = Cluster(new_images)

        cluster_dict.pop(str(id(cluster_one)))
        cluster_dict.pop(str(id(cluster_two)))
        cluster_dict[str(id(temp_cluster))] = temp_cluster

        clusters.remove(cluster_one) 
        clusters.remove(cluster_two)
        priority_queue = update_dist_queue(priority_queue, clusters, cluster_one, cluster_two, temp_cluster)
        clusters.append(temp_cluster)

        if temp_cluster.get_diameter() > .45:
            clusters.remove(temp_cluster)
            clusters.append(cluster_one)
            clusters.append(cluster_two)
            running = False
        
    return clusters 
        


if __name__ == "__main__":
    # Create image objects for each image to sort
    image_paths = os.listdir("Output_Shape_Images")
    images = []

    for image in image_paths:
        if image.endswith(".jpg"):
            path = "Output_Shape_Images/" + image
            images.append(Image(path))
    
    final_clusters = cluster(images)

    # Place the images into subfolders based on the determined clusters
    for i, cluster in enumerate(final_clusters):
        cluster_path = "Cluster_" + str(i+1)
        os.mkdir("Output_Shape_Images/" + cluster_path)
        for image in cluster.get_images():
            new_path = image.get_path().split("/")
            new_path = "Output_Shape_Images/" + cluster_path + "/" + new_path[1]
            os.rename(image.get_path(), new_path)