document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.querySelector('#query');
    const filters = document.querySelectorAll('#filters input, #filters select, #filters [type="radio"]');
    const resultsContainer = document.getElementById('results');
    const resultsNotFound = document.getElementById("results_not_found");
    const resultsNumber = document.getElementById('results_number');

    sendQuery(); 
    queryInput.addEventListener('input', sendQuery);
    new URLSearchParams(window.location.search).get('query')?.trim() && queryInput.dispatchEvent(new Event('input', { bubbles: true }));

    // Filter event listener
    filters.forEach(filter => filter.addEventListener('input', sendQuery));

    document.getElementById('clear-filters').addEventListener('click', clearFilters);

    //Funcion que actualiza el query con el tipo de publicacion seleccionado
    function sendQuery() {
        resultsContainer.innerHTML = '';
        resultsNotFound.style.display = "none";

        const csrfToken = document.getElementById('csrf_token').value;
        const searchCriteria = {
            csrf_token: csrfToken,
            query: queryInput.value,
            publication_type: document.querySelector('#publication_type').value,
            sorting: document.querySelector('[name="sorting"]:checked').value,
            size: document.querySelector('#size').value,
            author: document.querySelector('#authors').value,
            files: document.querySelector('#files').value,
            title: document.querySelector('#title').value
        };

        fetch('/explore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchCriteria),
        })
        .then(response => response.json())
        .then(data => handleResults(data, searchCriteria))
        .catch(console.error);
    }

    function handleResults(data, searchCriteria) {
        const filteredData = data.filter(dataset => filterDataset(dataset, searchCriteria));
        const resultCount = filteredData.length;
        
        resultsNumber.textContent = `${resultCount} ${resultCount === 1 ? 'dataset' : 'datasets'} found`;
        resultsNotFound.style.display = resultCount === 0 ? "block" : "none";

        populateAuthorsFilter(data);
        populateTitleFilter(data);

        filteredData.forEach(dataset => resultsContainer.appendChild(createDatasetCard(dataset)));
    }

    function filterDataset(dataset, { size, author, title, files }) {
        const matchesSize = matchSize(dataset.total_size_in_bytes, size);
        const matchesAuthor = author === "any" || dataset.authors.some(({ name }) => name === author);
        const matchesTitle = title === "any" || matchTitle(dataset.title, title);
        const matchesFiles = matchFiles(dataset.files_count, files);

        return matchesSize && matchesAuthor && matchesTitle && matchesFiles;
    }


    function matchTitle(datasetTitle, title) {
        return Array.isArray(datasetTitle) ? datasetTitle.includes(title) : datasetTitle === title;
    }

    function matchFiles(filesCount, files) {
        // Convert `filesCount` to a number if it's not already
        filesCount = Number(filesCount);
    
        const filesMap = {
            "any": true,
            "1file": filesCount === 1,
            "2files": filesCount === 2,
            "3files": filesCount === 3,
            "4files": filesCount === 4,
            "5files": filesCount === 5,
            "6files": filesCount === 6,
            "7files": filesCount === 7,
            "8files": filesCount === 8,
            "9files": filesCount === 9,
            "moreThan10files": filesCount > 10,
        };
        // List of allowed values for `files`
        const allowedFilesValues = Object.keys(filesMap);

        // Ensure the `files` value is one of the allowed keys
        if (!allowedFilesValues.includes(files)) {
            console.warn(`Invalid files value: ${files}. Defaulting to "any"`);
            files = "any"; // Use default value if not valid
        }
        // If `files` value exists in `filesMap`, use it, otherwise return true by default
        return filesMap[files] ?? true;
    }


    function matchSize(totalSize, size) {
        const sizeMap = {
            lessThan1KB: totalSize < 1024,
            between1KBand2KB: totalSize >= 1024 && totalSize < 2048,
            between2KBand3KB: totalSize >= 2048 && totalSize < 3072,
            between3KBand4KB: totalSize >= 3072 && totalSize < 4096,
            between4KBand5KB: totalSize >= 4096 && totalSize < 5120,
            moreThan5KB: totalSize > 5120,
        };
        // Validate that `size` is one of the expected keys
        if (size in sizeMap) {
            return sizeMap[size];
        } else {
            console.warn(`Invalid size value: ${size}. Returning default value.`);
            return true;  // or return false or another default based on your logic
        }
        return sizeMap[size] ?? true;
    }
    

    function createDatasetCard(dataset) {
        const card = document.createElement('div');
        card.className = 'col-12';
        card.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between">
                        <h2><a href="${dataset.url}">${dataset.title}</a></h2>
                        <div>
                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_publication_type_as_query('${dataset.publication_type}')">${dataset.publication_type}</span>
                        </div>
                    </div>
                    <p class="text-secondary">${formatDate(dataset.created_at)}</p>
                    <div class="row mb-2">
                        <div class="col-md-4 col-12"><span class="text-secondary">Description</span></div>
                        <div class="col-md-8 col-12"><p class="card-text">${dataset.description}</p></div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-md-4 col-12"><span class="text-secondary">Authors</span></div>
                        <div class="col-md-8 col-12">${dataset.authors.map(({ name, affiliation, orcid }) => `<p>${name} ${affiliation ? `(${affiliation})` : ''} ${orcid ? `(${orcid})` : ''}</p>`).join('')}</div>
                    </div>
                    <div class="row mb-2">
                        <div class="col-md-4 col-12"><span class="text-secondary">Tags</span></div>
                        <div class="col-md-8 col-12">${dataset.tags.map(tag => `<span class="badge bg-secondary me-1" style="cursor: pointer;" onclick="set_tag_as_query('${tag}')">${tag}</span>`).join('')}</div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 col-12"></div>
                        <div class="d-flex justify-content-end">
                            <a href="${dataset.url}" class="btn btn-outline-primary btn-sm me-2">View dataset</a>
                            <a href="/dataset/download/${dataset.id}" class="btn btn-outline-success btn-sm">Download (${dataset.total_size_in_human_format})</a>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return card;
    }

    function populateAuthorsFilter(data) {
        populateDropdown(data.flatMap(({ authors }) => authors.map(({ name }) => name)), 'authors');
    }

    function populateTitleFilter(data) {
        populateDropdown(data.map(({ title }) => title), 'title');
    }

    function populateDropdown(items, elementId) {
        const uniqueItems = Array.from(new Set(items));
        const selectElement = document.getElementById(elementId);
        const currentSelection = selectElement.value;

        selectElement.innerHTML = '<option value="any">Any</option>';
        uniqueItems.forEach(item => {
            const option = document.createElement('option');
            option.value = item;
            option.textContent = item;
            selectElement.appendChild(option);
        });

        if (uniqueItems.includes(currentSelection)) {
            selectElement.value = currentSelection;
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleString('en-US', { day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric' });
    }

    function clearFilters() {
        queryInput.value = "";
        document.querySelector('#publication_type').value = "any";
        document.querySelector('#authors').value = "any";
        document.querySelector('#files').value = "any";
        document.querySelector('#size').value = "any";
        document.querySelector('#title').value = "any";
        document.querySelector('#tag').value = "any";
        document.querySelector('[name="sorting"][value="newest"]').checked = true;
        queryInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
});
