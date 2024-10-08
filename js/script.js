const apiUrl = 'https://6703f9f6ab8a8f8927327c94.mockapi.io/files';

document.addEventListener('DOMContentLoaded', () => {
    fetchFiles();

    const uploadForm = document.getElementById('uploadForm');
    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName').value;
        const file = fileInput.files[0];

        // Создаем временный URL для загружаемого файла
        const fileUrl = URL.createObjectURL(file);
        saveFileToMockAPI(fileName, fileUrl);
    });
});

function fetchFiles() {
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(files => {
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '';
            files.forEach(file => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="${file.url}" download>${file.name}</a>`;
                fileList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function saveFileToMockAPI(name, url) {
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, url })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to save file to MockAPI');
        }
        return response.json();
    })
    .then(() => {
        fetchFiles();
        document.getElementById('uploadForm').reset();
    })
    .catch(error => {
        console.error('Error saving file to MockAPI:', error);
    });
}
