let isProcessing = false; // Gateway guard to prevent server crashes
let secondImageBase64 = null;
// 1. Function to upload and convert image to grayscale immediately
function previewImage(event) {
    const input = event.target;
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    const placeholder = document.getElementById('placeholder-text');
    const resultPlaceholder = document.getElementById('result-placeholder');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                
                ctx.drawImage(img, 0, 0);
                
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                for (let i = 0; i < data.length; i += 4) {
                    let gray = 0.299 * data[i] + 0.587 * data[i+1] + 0.114 * data[i+2];
                    data[i] = data[i+1] = data[i+2] = gray;
                }
                
                ctx.putImageData(imageData, 0, 0);
                const grayDataURL = canvas.toDataURL();
                
                // Display grayscale version in both screens
                mainPreview.src = grayDataURL;
                mainPreview.classList.remove('hidden');
                placeholder.classList.add('hidden');

                resultPreview.src = grayDataURL;
                resultPreview.classList.remove('hidden');
                resultPlaceholder.classList.add('hidden');
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// 2. Real-time processing function (communicate with Flask)
async function applyEffectLive(route, value) {
    if (isProcessing) return; // If a request is running, wait

    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');

    if (!mainPreview.src || mainPreview.classList.contains('hidden')) return;

    isProcessing = true; // Lock the gate

    try {
        const response = await fetch(route, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                value: value,
                image: mainPreview.src // Always send the original grayscale image
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result; // Update result image immediately
        }
    } catch (error) {
        console.error("Processing Error:", error);
    } finally {
        isProcessing = false; // Unlock gate for next request
    }
}

// 3. Connect brightness slider (real-time movement)
document.getElementById('brightness-slider').addEventListener('input', function() {
    // Update UI value immediately
    document.getElementById('b-static-val').innerText = this.value;
    // Request processing from server
    applyEffectLive('/process_brightness', this.value);
});

// 4. Connect divide/multiply slider (real-time movement)
document.getElementById('contrast-slider').addEventListener('input', function() {
    document.getElementById('c-static-val').innerText = this.value;
    applyEffectLive('/process_contrast', this.value);
});


// Connect complementary button
document.getElementById('invert-btn').addEventListener('click', function() {
    // Call the same Live function we created
    // Send 0 because the function doesn't need a value, just for template consistency
    applyEffectLive('/process_complementary', 0);
});


document.getElementById('solar-btn').addEventListener('click', async function() {
    const threshold = document.getElementById('solar-threshold').value;
    const mode = document.getElementById('solar-mode').value;
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');

    if (!mainPreview.src || mainPreview.classList.contains('hidden')) return;

    try {
        const response = await fetch('/process_solarization', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                threshold: threshold,
                mode: mode,
                image: mainPreview.src
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
        }
    } catch (error) {
        console.error("Solarization Error:", error);
    }
});


// Connect histogram stretching button
document.getElementById('stretch-btn').addEventListener('click', function() {
    // Call the unified histogram function
    // Send 0 because the function doesn't require a parameter
    applyEffectLive('/process_hist_stretch', 0);
});








// Connect show histogram button
document.getElementById('show-hist-btn').addEventListener('click', async function() {
    // Important: ID name must match the HTML
    const panel = document.getElementById('histogram-display-panel'); 
    const resultPreview = document.getElementById('result-preview');

    // 1. Show the panel
    if (panel) {
        panel.classList.remove('hidden');
        console.log("Panel is now visible"); // For console verification
    } else {
        console.error("Could not find histogram-display-panel ID");
        return;
    }

    if (!resultPreview.src || resultPreview.classList.contains('hidden')) {
        alert("Please upload an image first!");
        return;
    }

    try {
        const response = await fetch('/get_histogram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: resultPreview.src })
        });
        
        const resData = await response.json();
        if (resData.histogram) {
            drawHistogram(resData.histogram);
        } else {
            console.error("Server error:", resData.error);
        }
    } catch (error) {
        console.error("Fetch Error:", error);
    }
});

// Make sure canvas uses correct display dimensions
function drawHistogram(data) {
    const canvas = document.getElementById('histogram-canvas');
    const ctx = canvas.getContext('2d');
    
    // Important line: adjust drawing dimensions to match box size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const barWidth = canvas.width / 256;
    const maxVal = Math.max(...data);
    const scale = canvas.height / (maxVal + (maxVal * 0.1));

    ctx.fillStyle = '#8b5cf6'; 

    data.forEach((val, i) => {
        const barHeight = val * scale;
        // Draw the bar
        ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth, barHeight);
    });
}





// Main function for toggling between sections
// Named showControls to match the onclick in HTML
function showControls(categoryId) {
    // 1. Hide all containers with class category-content
    const contents = document.querySelectorAll('.category-content');
    contents.forEach(content => {
        content.classList.add('hidden');
    });

    // 2. Show the requested container
    // If 'point-ops' is sent, look for 'point-ops-content' ID
    const selectedContent = document.getElementById(categoryId + '-content');
    
    if (selectedContent) {
        selectedContent.classList.remove('hidden');
        console.log("Section opened:", categoryId); // For console verification
    } else {
        console.warn("Check ID: " + categoryId + "-content is missing!");
    }
}

// 3. Show point ops automatically on page load to prevent empty page
document.addEventListener('DOMContentLoaded', () => {
    showControls('point-ops');
});





// 1. Global variable to store second image data for sending to Python later

// 2. Function that runs when selecting second image from device
function previewSecondImage(event) {
    const input = event.target;
    const preview = document.getElementById('second-preview');
    const placeholder = document.getElementById('second-upload-placeholder');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                // 1. Create temporary canvas for processing
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                
                // 2. Draw original image
                ctx.drawImage(img, 0, 0);
                
                // 3. Get pixel data
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                // 4. Convert each pixel to grayscale (Grayscale Loop)
                for (let i = 0; i < data.length; i += 4) {
                    let gray = 0.299 * data[i] + 0.587 * data[i+1] + 0.114 * data[i+2];
                    data[i] = data[i+1] = data[i+2] = gray; // Make R=G=B
                }
                
                // 5. Apply modified data back to canvas
                ctx.putImageData(imageData, 0, 0);
                
                // 6. Convert result to Base64 and save
                const grayDataURL = canvas.toDataURL('image/png');
                secondImageBase64 = grayDataURL; // Variable to send to Flask
                
                // 7. Update UI
                preview.src = grayDataURL;
                preview.classList.remove('hidden');
                if (placeholder) placeholder.classList.add('hidden');
                
                console.log("Second image converted to grayscale successfully!");
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}




// Connect addition button
document.getElementById('add-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview'); // Image 1
    const resultPreview = document.getElementById('result-preview');
    const resultPlaceholder = document.getElementById('result-placeholder');

    // Check that both images exist
    if (!mainPreview.src || !secondImageBase64) {
        alert("Please upload both images first! 🖼️+🖼️");
        return;
    }

    try {
        const response = await fetch('/process_addition', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image1: mainPreview.src,
                image2: secondImageBase64 // Variable storing second image
            })
        });

        const data = await response.json();
        if (data.result) {
            // Display result in right box
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            if (resultPlaceholder) resultPlaceholder.classList.add('hidden');
            console.log("Image Addition Successful ✅");
        } else {
            console.error("Error from server:", data.error);
        }
    } catch (error) {
        console.error("Addition Request Error:", error);
    }
});



// Connect subtraction button
document.getElementById('subtract-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');

    if (!mainPreview.src || !secondImageBase64) {
        alert("Please upload both images to subtract! 🖼️➖🖼️");
        return;
    }

    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch('/process_subtraction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image1: mainPreview.src,
                image2: secondImageBase64
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Image Subtraction Done! ✅");
        }
    } catch (error) {
        console.error("Subtraction Error:", error);
    } finally {
        isProcessing = false;
    }
});






// Connect blending button
document.getElementById('blend-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    
    // Get current values from sliders
    const alphaVal = document.getElementById('alpha-slider').value;
    const betaVal = document.getElementById('beta-slider').value;

    if (!mainPreview.src || !secondImageBase64) {
        alert("Please upload both images to blend! 🎭");
        return;
    }

    if (isProcessing) return;
    isProcessing = true;

    try {
        const response = await fetch('/process_blending', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image1: mainPreview.src,
                image2: secondImageBase64,
                alpha: alphaVal,
                beta: betaVal
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log(`Blending Done! Alpha: ${alphaVal}, Beta: ${betaVal} ✅`);
        }
    } catch (error) {
        console.error("Blending Error:", error);
    } finally {
        isProcessing = false;
    }
});






// Apply mean filter
document.getElementById('mean-filter-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    
    // Check if user enabled zero padding
    const isPadding = document.getElementById('padding-toggle').checked;

    if (!mainPreview.src) {
        alert("Please upload an image first! 🖼️");
        return;
    }

    try {
        const response = await fetch('/process_mean_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                padding: isPadding
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Mean Filter Done ✅ (Padding: " + isPadding + ")");
        }
    } catch (error) {
        console.error("Error applying Mean Filter:", error);
    }
});



// Apply median filter
document.getElementById('median-filter-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    const isPadding = document.getElementById('padding-toggle').checked;

    if (!mainPreview.src) {
        alert("Please upload an image first! 🖼️");
        return;
    }

    try {
        const response = await fetch('/process_median_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                padding: isPadding
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Median Filter Done! (Padding: " + isPadding + ") ✅");
        }
    } catch (error) {
        console.error("Median Filter Error:", error);
    }
});




// Apply min filter
document.getElementById('min-filter-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    const isPadding = document.getElementById('padding-toggle').checked;

    if (!mainPreview.src) {
        alert("Please upload an image first! 🖼️");
        return;
    }

    try {
        const response = await fetch('/process_min_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                padding: isPadding
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Min Filter Applied ✅");
        }
    } catch (error) {
        console.error("Min Filter Error:", error);
    }
});















// Apply max filter
document.getElementById('max-filter-btn').addEventListener('click', async function() {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');
    const isPadding = document.getElementById('padding-toggle').checked;

    if (!mainPreview.src) {
        alert("Please upload an image first! 🖼️");
        return;
    }

    try {
        const response = await fetch('/process_max_filter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                padding: isPadding
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Max Filter Applied ✅");
        }
    } catch (error) {
        console.error("Max Filter Error:", error);
    }
});





// Make sure this line is at the very beginning of the file outside any function

// Function executed when page loads
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Connect average button
    const avgBtn = document.getElementById('average-spatial-btn');
    if (avgBtn) {
        avgBtn.addEventListener('click', function() {
            console.log("Average Button Clicked! 🖱️"); // For debugging
            const size = document.getElementById('average-size').value;
            applySpatialFilter('average', { size: parseInt(size) });
        });
    }

    // 2. Connect Gaussian button
    const gaussBtn = document.getElementById('gaussian-spatial-btn');
    if (gaussBtn) {
        gaussBtn.addEventListener('click', function() {
            console.log("Gaussian Button Clicked! 🖱️"); // For debugging
            const size = document.getElementById('gaussian-size').value;
            const sigma = document.getElementById('gaussian-sigma').value;
            applySpatialFilter('gaussian', { size: parseInt(size), sigma: parseFloat(sigma) });
        });
    }
});

// Function that communicates with Python backend
async function applySpatialFilter(type, params) {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');

    if (!mainPreview.src || mainPreview.src === "") {
        alert("Please upload an image first! 🖼️");
        return;
    }

    if (isProcessing) return;
    isProcessing = true;
    console.log(`Sending ${type} request to server... 🚀`);

    try {
        const response = await fetch('/process_spatial', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                filter_type: type,
                ...params
            })
        });

        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log(`${type} applied successfully! ✅`);
        } else {
            console.error("Server Error:", data.error);
        }
    } catch (e) {
        console.error("Fetch Error:", e);
    } finally {
        isProcessing = false;
    }
}








// Make sure this is inside the DOMContentLoaded
const noiseBtn = document.getElementById('add-noise-btn');
if (noiseBtn) {
    noiseBtn.addEventListener('click', function() {
        console.log("Noise Button Clicked! 🧂"); // For debugging
        const ratio = document.getElementById('noise-slider').value;
        processRestoration('noise', { ratio: parseFloat(ratio) });
    });
}

const snrBtn = document.getElementById('calculate-snr-btn');
if (snrBtn) {
    snrBtn.addEventListener('click', function() {
        console.log("SNR Button Clicked! 📏");
        calculateMetrics();
    });
}

// Unified function for adding noise
async function processRestoration(type, params) {
    const mainPreview = document.getElementById('main-preview');
    const resultPreview = document.getElementById('result-preview');

    if (!mainPreview.src || mainPreview.src.includes('window.location')) {
        alert("Please upload an image first!");
        return;
    }

    try {
        const response = await fetch('/process_noise', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                ...params
            })
        });
        const data = await response.json();
        if (data.result) {
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
            console.log("Noise added successfully! ✅");
        }
    } catch (e) { console.error("Restoration Error:", e); }
}

// SNR calculation function
async function calculateMetrics() {
    const resultImg = document.getElementById('result-preview').src; // Cleaned image
    // secondImageBase64 is the original image uploaded in Image 2
    
    if (!resultImg || !secondImageBase64) {
        alert("You need a result on the right and original image in Image 2!");
        return;
    }

    try {
        const response = await fetch('/calculate_metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original: secondImageBase64,
                restored: resultImg
            })
        });
        const data = await response.json();
        if (data.snr !== undefined) {
            // Display result in UI
            document.getElementById('snr-result-text').innerText = data.snr.toFixed(2) + " dB";
        }
    } catch (e) { console.error("SNR Calculation Error:", e); }
}




// Custom function to display second image in restoration section
function updateRestorationImage() {
    const preview = document.getElementById('second-preview-restoration');
    const placeholder = document.getElementById('restoration-placeholder');

    // Check that image exists in the variable used for SNR calculation
    if (secondImageBase64 && preview) {
        preview.src = secondImageBase64;
        preview.classList.remove('hidden'); // Show the image
        if (placeholder) placeholder.classList.add('hidden'); // Hide the + icon
        console.log("Restoration Image Updated! 🖼️✅");
    }
}




// Connect morphology buttons
document.addEventListener('DOMContentLoaded', () => {
    const morphButtons = {
        'erosion-btn': 'erosion',
        'dilation-btn': 'dilation',
        'opening-btn': 'opening',
        'closing-btn': 'closing'
    };

    Object.entries(morphButtons).forEach(([id, type]) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.addEventListener('click', () => {
                const size = document.getElementById('morph-size-slider').value;
                applyMorphology(type, parseInt(size));
            });
        }
    });
});

async function applyMorphology(type, size) {
    const mainPreview = document.getElementById('main-preview');
    if (!mainPreview.src) return alert("Upload image first!");

    try {
        const response = await fetch('/process_morphology', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                morph_type: type,
                size: size
            })
        });
        const data = await response.json();
        if (data.result) {
            document.getElementById('result-preview').src = data.result;
            document.getElementById('result-preview').classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
        }
    } catch (e) { console.error("Morph Error:", e); }
}



// Connect segmentation buttons
const otsuBtn = document.getElementById('otsu-btn');
if (otsuBtn) {
    otsuBtn.addEventListener('click', () => applySegmentation('otsu'));
}

const ditherBtn = document.getElementById('dithering-btn');
if (ditherBtn) {
    ditherBtn.addEventListener('click', () => applySegmentation('dithering'));
}

async function applySegmentation(type) {
    const mainPreview = document.getElementById('main-preview');
    if (!mainPreview.src) return alert("Upload image first!");

    try {
        const response = await fetch('/process_segmentation', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainPreview.src,
                seg_type: type
            })
        });
        const data = await response.json();
        if (data.result) {
            const resultPreview = document.getElementById('result-preview');
            resultPreview.src = data.result;
            resultPreview.classList.remove('hidden');
            document.getElementById('result-placeholder').classList.add('hidden');
        }
    } catch (e) { console.error("Segmentation Error:", e); }
}



// 1. Map button IDs to filter names in Python
const goldBonusActions = {
    'sobel-btn': 'sobel',
    'hist-eq-btn': 'hist_eq',
    'adaptive-btn': 'adaptive',
    'kmeans-btn': 'kmeans',
    'canny-btn': 'canny'
};

// 2. Add event listener to each bonus button
Object.entries(goldBonusActions).forEach(([buttonId, filterType]) => {
    const button = document.getElementById(buttonId);
    if (button) {
        button.addEventListener('click', () => {
            console.log(`Gold Filter Triggered: ${filterType} 🏆`);
            executeBonusFilter(filterType);
        });
    }
});

// 3. Main function to send request to server
async function executeBonusFilter(type) {
    const mainImgElement = document.getElementById('main-preview');
    
    // Check that an image is uploaded first
    if (!mainImgElement.src || mainImgElement.src.includes('placeholder')) {
        return alert("Please upload an image first to apply bonus filters! 🖼️");
    }

    try {
        // Show loading state (optional if you have a spinner)
        console.log("Processing...");

        const response = await fetch('/process_bonus', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: mainImgElement.src, // Base64 image
                filter_type: type
            })
        });

        const data = await response.json();

        if (data.result) {
            // Update result image and hide placeholder
            const resultImg = document.getElementById('result-preview');
            const resultPlaceholder = document.getElementById('result-placeholder');

            resultImg.src = data.result;
            resultImg.classList.remove('hidden');
            if (resultPlaceholder) resultPlaceholder.classList.add('hidden');
            
            console.log(`${type} applied successfully! ✅`);
        } else {
            alert("Error: " + (data.error || "Unknown error occurred"));
        }
    } catch (err) {
        console.error("Connection Error:", err);
        alert("Server not responding. Make sure Flask is running!");
    }
}



document.addEventListener('DOMContentLoaded', () => {
    const downloadBtn = document.getElementById('download-results-btn');
    const resultImg = document.getElementById('result-preview');

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            // Check that a processed image is ready for download
            if (!resultImg.src || resultImg.classList.contains('hidden')) {
                return alert("No result available to download! Apply a filter first. 🖼️");
            }

            // Create a dummy link for download
            const link = document.createElement('a');
            link.href = resultImg.src; // Source of the processed image
            
            // Set filename and extension (PNG preserves edge quality)
            link.download = 'Project_Result.png'; 
            
            // Execute download and delete link immediately
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log("Image saved successfully! 📥");
        });
    }
});
