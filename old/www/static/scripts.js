document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(this);

    // Display uploaded images in a 2x2 grid
    const uploadedImagesContainer = document.getElementById('uploaded-images');
    uploadedImagesContainer.innerHTML = '';
    const files = this.elements['images'].files;
    for (const file of files) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        uploadedImagesContainer.appendChild(img);
    }

    // Show normal map loader and status
    document.getElementById('normal-map-loader').style.display = 'block';
    document.getElementById('normal-map-status').style.display = 'block';

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();

        if (data.status === 'normal_map_ready') {
            // Hide normal map loader and status, show normal map image
            document.getElementById('normal-map-loader').style.display = 'none';
            document.getElementById('normal-map-status').style.display = 'none';
            document.getElementById('normal-map').src = data.normalMapUrl;
            document.getElementById('normal-map').style.display = 'block';

            // Show download loader and status
            document.getElementById('download-loader').style.display = 'block';
            document.getElementById('download-status').style.display = 'block';

            // Request to process normals
            const normalsResponse = await fetch('/process_normals', {
                method: 'POST'
            });

            if (normalsResponse.ok) {
                const normalsData = await normalsResponse.json();

                if (normalsData.status === 'obj_ready') {
                    // Hide download loader and status, show download link
                    document.getElementById('download-loader').style.display = 'none';
                    document.getElementById('download-status').style.display = 'none';
                    document.getElementById('download-link').href = normalsData.objUrl;
                    document.getElementById('download-link').style.display = 'block';
                }
            } else {
                alert('Error processing normals');
            }
        }
    } else {
        alert('Error processing images');
    }
});