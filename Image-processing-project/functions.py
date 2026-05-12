import cv2
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from skimage import morphology,filters
from PIL import Image
import base64


# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def ensure_grayscale(image):
    """
    Converts any input image to Grayscale. 
    If it is already Grayscale, it returns it directly.
    """
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


# ======================================================================
# SECTION 1: POINT OPERATIONS
# ======================================================================

# Function: point_add
def point_add(image, bright_constant):
    """
    Increases the overall brightness of the image by adding a constant value to each pixel.
    Pixel values are capped at 255 to prevent overflow.
    """
    height, width = image.shape
    bright_img = np.zeros_like(image)
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j]) 
            bright_value = pixel + bright_constant
            bright_img[i, j] = min(bright_value, 255)
    return bright_img


# Function: point_subtract
def point_subtract(image, dark_constant):
    """
    Decreases the overall brightness of the image by subtracting a constant value from each pixel.
    Pixel values are clamped at 0 to prevent underflow.
    """
    height, width = image.shape
    dark_img = np.zeros_like(image)
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j]) 
            dark_value = pixel - dark_constant
            dark_img[i, j] = max(dark_value, 0)
    return dark_img


# Function: point_multiply
def point_multiply(image, bright_constant):
    """
    Increases image contrast and brightness by multiplying each pixel by a constant factor.
    Pixel values are capped at 255.
    """
    height, width = image.shape
    bright_img = np.zeros_like(image)
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j]) 
            bright_value = pixel * bright_constant
            bright_img[i, j] = min(bright_value, 255)
    return bright_img

# Function: point_divide
def point_divide(image, dark_constant):
    """
    Decreases image contrast and brightness by dividing each pixel by a constant factor.
    Includes a safety check to prevent division by zero errors.
    """
    if dark_constant == 0: dark_constant = 1  # Prevent division by zero
    height, width = image.shape
    dark_img = np.zeros_like(image)
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j]) 
            dark_value = pixel // dark_constant
            dark_img[i, j] = int(max(dark_value, 0))
    return dark_img

# Function: point_complementary
def point_complementary(image):
    """
    Creates a negative (inverted) version of the image by subtracting each pixel value from 255.
    """
    height, width = image.shape
    complement_img = np.zeros_like(image)
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j]) 
            complement_img[i, j] = 255 - pixel
    return complement_img

def solarization(image, threshold, mode='greater'):
    """
    Unified: Applies solarization based on the type (greater or less)
    """
    height, width = image.shape
    result = np.zeros_like(image)
    
    for i in range(height):
        for j in range(width):
            pixel = int(image[i, j])
            
            # Determine condition based on mode
            if mode == 'less':
                condition = pixel < threshold
            else:
                condition = pixel > threshold
                
            if condition:
                result[i, j] = 255 - pixel
            else:
                result[i, j] = pixel
    return result




# Function: compute_histogram
def compute_histogram(image):
    """
    Computes the histogram of a grayscale image manually.
    Returns an array of 256 integers representing the frequency of each intensity value.
    """
    histogram = np.zeros(256, dtype=int)
    height, width = image.shape
    
    for i in range(height):
        for j in range(width):
            intensity = image[i, j]
            histogram[intensity] += 1
            
    return histogram





# Function: histogram_stretching
def histogram_stretching(image):
    """
    Applies contrast stretching to a grayscale image to span the full 0-255 range.
    Uses NumPy to efficiently find the minimum and maximum pixel values.
    """
    height, width = image.shape
    
    # Step 1: Find Minimum and Maximum pixel values using NumPy (Fast)
    I_min = int(np.min(image))
    I_max = int(np.max(image))
            
    # Safeguard: Prevent division by zero if the image is a single solid color
    if I_max == I_min:
        return image.copy()
        
    # Step 2: Apply the stretching formula to each pixel
    stretched = np.zeros((height, width), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            # The Stretching Formula
            new_pixel = int((int(pixel) - I_min) * 255 / (I_max - I_min))
            # Clamp the value between 0 and 255
            stretched[i, j] = min(max(new_pixel, 0), 255)
            
    return stretched






# ======================================================================
# SECTION 2: CONTROL IMAGE
# ======================================================================
# (specific image control/manipulation functions)

# Add section 2 implementation codes here




# Function: control_image_add
def control_image_add(img1, img2):
    """
    Adds two images together pixel by pixel.
    Values are capped at 255. Both images must be grayscale.
    """
    # Resize the second image to match the dimensions of the first image automatically
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    height, width = img1.shape
    added_img = np.zeros_like(img1)
    
    for i in range(height):
        for j in range(width):
            summed = int(img1[i, j]) + int(img2_resized[i, j])
            added_img[i, j] = min(summed, 255)
            
    return added_img

# Function: control_image_blend
def control_image_blend(img1, img2, alpha=0.6, beta=0.4):
    """
    Blends two images using weighted addition.
    Alpha is the weight of the first image, Beta is the weight of the second image.
    """
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    height, width = img1.shape
    blended_img = np.zeros_like(img1)
    
    for i in range(height):
        for j in range(width):
            # Blend by weighted percentages
            summed = (alpha * int(img1[i, j])) + (beta * int(img2_resized[i, j]))
            blended_img[i, j] = int(min(summed, 255))
            
    return blended_img

# Function: control_image_subtract
def control_image_subtract(img1, img2):
    """
    Subtracts the second image from the first image pixel by pixel.
    Used for background subtraction or finding differences. 
    Values are floored at 0.
    """
    img2_resized = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    height, width = img1.shape
    subtracted_img = np.zeros_like(img1)
    
    for i in range(height):
        for j in range(width):
            subtract = int(img1[i, j]) - int(img2_resized[i, j])
            subtracted_img[i, j] = max(subtract, 0)
            
    return subtracted_img












# ======================================================================
# SECTION 3: NEIGHBOURHOOD OPERATIONS
# ======================================================================

# Function: mean_filter
def mean_filter(image, zero_padding=True):
    """
    Sets the pixel value to the mean of its 3x3 neighbourhood.
    Uses numpy's sliding_window_view for real-time vectorized performance.
    """
    # Step 1: Apply Padding if requested
    if zero_padding:
        padded_img = np.pad(image, pad_width=1, mode='constant', constant_values=0)
    else:
        padded_img = image

    # Step 2: Extract all 3x3 windows at once (Replaces the nested for-loops)
    windows = sliding_window_view(padded_img, (3, 3))
    
    # Step 3: Calculate the mean of each 3x3 window
    # axis=(2, 3) means we average across the 3x3 grids
    filtered_img = np.mean(windows, axis=(2, 3))
    
    return filtered_img.astype(np.uint8)

# Function: median_filter
def median_filter(image, zero_padding=True):
    """
    Sets the pixel value to the median of its 3x3 neighbourhood.
    Excellent for removing salt-and-pepper noise while preserving sharp edges.
    """
    if zero_padding:
        padded_img = np.pad(image, pad_width=1, mode='constant', constant_values=0)
    else:
        padded_img = image

    windows = sliding_window_view(padded_img, (3, 3))
    
    # Calculate the median of each 3x3 window
    filtered_img = np.median(windows, axis=(2, 3))
    
    return filtered_img.astype(np.uint8)

# Function: min_filter
def min_filter(image, zero_padding=True):
    """
    Sets the pixel value to the minimum in its 3x3 neighbourhood.
    Useful for removing salt (white) noise.
    """
    if zero_padding:
        padded_img = np.pad(image, pad_width=1, mode='constant', constant_values=0)
    else:
        padded_img = image

    windows = sliding_window_view(padded_img, (3, 3))
    
    # Calculate the minimum of each 3x3 window
    filtered_img = np.min(windows, axis=(2, 3))
    
    return filtered_img.astype(np.uint8)

# Function: max_filter
def max_filter(image, zero_padding=True):
    """
    Sets the pixel value to the maximum in its 3x3 neighbourhood.
    Useful for removing pepper (black) noise.
    """
    if zero_padding:
        padded_img = np.pad(image, pad_width=1, mode='constant', constant_values=0)
    else:
        padded_img = image

    windows = sliding_window_view(padded_img, (3, 3))
    
    # Calculate the maximum of each 3x3 window
    filtered_img = np.max(windows, axis=(2, 3))
    
    return filtered_img.astype(np.uint8)









# ======================================================================
# SECTION 4: SPATIAL FILTERING
# ======================================================================
# (e.g., Smoothing Spatial Filters, Sharpening Spatial Filters)

# Add section 4 implementation codes here



# Function: convolve_optimized
def convolve_optimized(image, filter_mask):
    """
    Applies a generic convolution mask to an image.
    Uses sliding_window_view to eliminate all for-loops for real-time performance.
    """
    h, w = image.shape
    filter_size = filter_mask.shape[0]
    pad = filter_size // 2
    
    # Step 1: Zero Padding
    padded_img = np.pad(image, pad_width=pad, mode='constant', constant_values=0).astype(np.float32)
    
    # Step 2: Extract all windows at once (Replaces the i, j loops)
    windows = sliding_window_view(padded_img, (filter_size, filter_size))
    
    # Step 3: Multiply each window by the filter mask and sum them up
    filtered_img = np.sum(windows * filter_mask, axis=(2, 3))
    
    # Clip values to valid range and return as uint8
    return np.clip(filtered_img, 0, 255).astype(np.uint8)


# Function: create_average_mask
def create_average_mask(filter_size=3):
    """
    Generates a normalized average (mean) filter mask.
    """
    mask = np.ones((filter_size, filter_size), dtype=float)
    mask /= (filter_size * filter_size)
    return mask


# Function: create_gaussian_mask
def create_gaussian_mask(filter_size, sigma):
    """
    Generates a Gaussian filter mask using the 2D Gaussian equation.
    """
    gauss_filter = np.zeros((filter_size, filter_size), np.float32)
    m = filter_size // 2
    n = filter_size // 2
    
    for x in range(-m, m+1):
        for y in range(-n, n+1):
            x1 = 2 * np.pi * (sigma**2)
            x2 = np.exp(-(x**2 + y**2) / (2 * sigma**2))
            gauss_filter[x+m, y+n] = (1 / x1) * x2
            
    # Normalize the mask so the image brightness doesn't change
    gauss_filter /= np.sum(gauss_filter)
    return gauss_filter


# Function: spatial_average_filter
def spatial_average_filter(image, filter_size=3):
    """
    Wrapper function: Applies an average smoothing filter to the image.
    """
    mask = create_average_mask(filter_size)
    return convolve_optimized(image, mask)


# Function: spatial_gaussian_filter
def spatial_gaussian_filter(image, filter_size=3, sigma=1.0):
    """
    Wrapper function: Applies a Gaussian smoothing filter to the image.
    """
    mask = create_gaussian_mask(filter_size, sigma)
    return convolve_optimized(image, mask)







# ======================================================================
# SECTION 5: IMAGE RESTORATION
# ======================================================================
# (e.g., Noise models, Mean filters, Order-statistic filters)

def add_salt_and_pepper_noise(image, noise_ratio=0.05):
    """
    Adds Salt and Pepper noise to a grayscale image.
    Uses flat indexing for fast random placement of noisy pixels.
    """
    noisy_image = image.copy()
    total_pixels = image.size

    # Calculate the number of pixels to add noise to
    num_noisy_pixels = int(total_pixels * noise_ratio)

    # Add salt (white pixels with value 255)
    salt_positions = np.random.randint(0, total_pixels, num_noisy_pixels)
    noisy_image.flat[salt_positions] = 255

    # Add pepper (black pixels with value 0)
    pepper_positions = np.random.randint(0, total_pixels, num_noisy_pixels)
    noisy_image.flat[pepper_positions] = 0

    return noisy_image

# Function: calculate_snr
def calculate_snr(original_image, restored_image):
    """
    Calculates the Signal-to-Noise Ratio (SNR) between the original and restored images.
    Higher SNR means better restoration.
    """
    original_img_float = original_image.astype(np.float32)
    restored_img_float = restored_image.astype(np.float32)

    numerator = np.sum(original_img_float ** 2)
    denominator = np.sum((original_img_float - restored_img_float) ** 2)

    # Protection from division by zero if both images are identical
    if denominator == 0:
        return float('inf')

    snr_value = 10 * np.log10(numerator / denominator)
    
    return snr_value




# ======================================================================
# SECTION 6: MORPHOLOGICAL OPERATIONS
# ======================================================================
# (e.g., Erosion, Dilation, Opening, Closing)



def morph_dilation(image, size=5):
    """
    Dilation: expands an element A by using structuring element B (Square).
    Uses skimage.morphology as shown in the lab.
    """
    
    stru_element = np.ones((size, size), dtype=np.uint8)
    
    
    dilated = morphology.dilation(image, stru_element)
    return dilated


# Function: morph_erosion
def morph_erosion(image, size=5):
    """
    Erosion: shrinking of element A by using element B (Square).
    Uses skimage.morphology as shown in the lab.
    """
    stru_element = np.ones((size, size), dtype=np.uint8)
    
    
    eroded = morphology.erosion(image, stru_element)
    return eroded


# Function: morph_opening
def morph_opening(image, size=5):
    """
    Opening: is the dilation of the erosion of a set A by the same structuring element B.
    Removes small white noise (small bright spots).
    """
    stru_element = np.ones((size, size), dtype=np.uint8)
    
    
    opened = morphology.opening(image, stru_element)
    return opened


# Function: morph_closing
def morph_closing(image, size=5):
    """
    Closing: is the erosion of the dilation of that set.
    Fills small black holes inside white regions.
    """
    stru_element = np.ones((size, size), dtype=np.uint8)
    
    
    closed = morphology.closing(image, stru_element)
    return closed





# ======================================================================
# SECTION 7: SEGMENTATION
# ======================================================================
# (e.g., Point, Line, and Edge Detection, Thresholding, Region-Based Segmentation)

# Function: segmentation_otsu
def segmentation_otsu(image):
    """
    Automatic Thresholding using Otsu's Method.
    It calculates the optimal threshold T to separate the foreground from the background.
    Returns a binary image (0 and 255).
    """
    # Calculate the optimal threshold automatically
    T = filters.threshold_otsu(image)
    
    # Convert the image to Binary (True/False)
    binary = image >= T
    
    # Convert True to 255 and False to 0 so it appears in the GUI
    return (binary * 255).astype(np.uint8)


# Function: segmentation_dithering
def segmentation_dithering(image):
    """
    Error Diffusion Dithering using the Floyd-Steinberg algorithm.
    Used to represent grayscale images in 1-bit (Binary) while preserving visual detail.
    """
    
    pil_img = Image.fromarray(image)
    
   
    dithered_pil = pil_img.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
    
    return (np.array(dithered_pil) * 255).astype(np.uint8)





# ======================================================================
# SECTION 8:Addition 
# ======================================================================
# (e.g., Point, Line, and Edge Detection, Thresholding, Region-Based Segmentation)




def decode_image(data_url):
    """Converts Base64 data from the browser to an OpenCV image array"""
    try:
        # Remove the data:image/png;base64, part
        encoded_data = data_url.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        # Read as grayscale immediately to save processing time
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    except:
        return None

def encode_image(image_array):
    """Converts an OpenCV image array to Base64 text to return to the browser"""
    _, buffer = cv2.imencode('.png', image_array)
    encoded_string = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"