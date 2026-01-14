const fileInput = document.getElementById('fileInput');
const uploadBox = document.getElementById('uploadBox');
const imagePreview = document.getElementById('imagePreview');
const preview = document.getElementById('preview');
const loadingSpinner = document.getElementById('loadingSpinner');

if (uploadBox) {
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#2563EB';
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.style.borderColor = '#D1D5DB';
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = '#D1D5DB';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleFile(file);
        }
    });
}

if (fileInput) {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });
}

function handleFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        uploadBox.style.display = 'none';
        imagePreview.style.display = 'block';
        classifyImage(file);
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    fileInput.value = '';
    uploadBox.style.display = 'block';
    imagePreview.style.display = 'none';
}

async function classifyImage(file) {
    loadingSpinner.style.display = 'flex';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/classify', {
            method: 'POST',
            body: formData
        });

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JSON response');
        }

        const result = await response.json();

        // Check if redirect to error page (THIS IS THE FIX!)
        if (result.redirect) {
            console.log('Redirecting to:', result.redirect);
            window.location.href = result.redirect;
            return;
        }

        if (response.ok) {
            window.location.href = '/result';
        } else {
            alert('ERROR: ' + (result.error || 'Classification failed'));
            loadingSpinner.style.display = 'none';
            resetUpload();
        }
    } catch (error) {
        console.error('Classification error:', error);
        alert('CLASSIFICATION FAILED: ' + error.message);
        loadingSpinner.style.display = 'none';
        resetUpload();
    }
}
