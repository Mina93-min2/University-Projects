import numpy as np
from skimage import filters, exposure, feature
from sklearn.cluster import KMeans

# ======================================================================
# BONUS SECTION: ADVANCED IMAGE PROCESSING ALGORITHMS
# ======================================================================

def bonus_sobel(image):
    """
    Applies Sobel operator to detect edges by calculating image gradients.
    It highlights regions of high spatial frequency that correspond to edges.
    """
    # Calculate the gradient magnitude using the Sobel filter
    edge_sobel = filters.sobel(image)
    
    # Scale back to 0-255 range and convert to unsigned 8-bit integer
    return (edge_sobel * 255).astype(np.uint8)


def bonus_hist_eq(image):
    """
    Performs Global Histogram Equalization to enhance image contrast.
    It spreads out the most frequent intensity values across the entire spectrum.
    """
    # Adjust the contrast of the image by equalizing its histogram
    img_eq = exposure.equalize_hist(image)
    
    # Scale back to 0-255 range for display purposes
    return (img_eq * 255).astype(np.uint8)


def bonus_adaptive_thresh(image):
    """
    Applies Adaptive (Local) Thresholding.
    Unlike global methods, it calculates a different threshold for every pixel 
    based on the characteristics of its local neighborhood.
    """
    # Calculate local thresholds using a 35x35 block size
    local_thresh = filters.threshold_local(image, block_size=35, offset=10)
    
    # Create a binary mask: True if pixel > local threshold
    binary = image > local_thresh
    
    # Convert Boolean mask to 0 and 255 grayscale values
    return (binary * 255).astype(np.uint8)

def bonus_kmeans(image, k=3):
    """
    K-Means Clustering for AI-based Segmentation.
    """
    # 1. Reshape to 1D column
    pixel_values = image.reshape((-1, 1)).astype(np.float32)
    
    # 2. Run K-Means
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = kmeans.fit_predict(pixel_values)
    
    # 3. FIX: Convert centers and keep it as a NumPy array
    centers = kmeans.cluster_centers_.astype(np.uint8)
    
    # 4. Map labels back to centers
    segmented_data = centers[labels.flatten()]
    
    # 5. Reshape to original image
    return segmented_data.reshape(image.shape)





def bonus_canny(image):
    """
    Applies the Canny Edge Detection algorithm.
    It is a multi-stage process involving noise reduction, gradient calculation, 
    non-maximum suppression, and hysteresis thresholding.
    """
    # Detect edges using a Gaussian filter with sigma=1.0 for noise reduction
    edges = feature.canny(image, sigma=1.0)
    
    # Convert Boolean edges array to 0 and 255 grayscale values
    return (edges * 255).astype(np.uint8)