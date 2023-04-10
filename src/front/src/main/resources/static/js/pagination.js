const resultsList = document.getElementById("resultsList");
let finalIds = null;
const pagination = document.getElementById("pagination");
const resultsPerPage = 10;
const totalResults = resultsList.childElementCount;
const totalPages = Math.ceil(totalResults / resultsPerPage);
let currentPage = 1;

async function displayResults(page) {
    finalIds = finalIds || resultsList.cloneNode(true);
    const idsToFetch = getIdsToFetch(page);
    const results = await fetchDataForIds(idsToFetch);
    displayFetchedData(results);
    handlePagination();
}

function getIdsToFetch(page) {
    const startIndex = (page - 1) * resultsPerPage;
    const endIndex = startIndex + resultsPerPage;

    return Array.from(finalIds.children)
        .slice(startIndex, endIndex)
        .map((elem) => parseInt(elem.querySelector(".doc_id").innerText));
}

function handlePagination() {
    pagination.innerHTML = "";
    createPreviousButton();
    createPageLinks();
    createNextButton();
}

function createPreviousButton() {
    const previousButton = document.createElement('li');
    previousButton.classList.add('page-item');
    if (currentPage === 1) {
        previousButton.classList.add('disabled');
    }
    const previousLink = document.createElement('a');
    previousLink.classList.add('page-link');
    previousLink.href = '#';
    previousLink.innerText = 'Previous';
    previousButton.appendChild(previousLink);
    pagination.appendChild(previousButton);

    // Event Listener
    previousLink.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayResults(currentPage);
        }
    });
}

function createPageLinks() {
    const pageLinks = [];
    if (totalPages <= 15) {
        for (let i = 1; i <= totalPages; i++) {
            pageLinks.push(i);
        }
    } else {
        if (currentPage <= 7) {
            for (let i = 1; i <= 10; i++) {
                pageLinks.push(i);
            }
            pageLinks.push('...');
            pageLinks.push(totalPages - 2);
            pageLinks.push(totalPages - 1);
            pageLinks.push(totalPages);
        } else if (currentPage > 7 && currentPage <= totalPages - 7) {
            pageLinks.push(1);
            pageLinks.push(2);
            pageLinks.push(3);
            pageLinks.push('...');
            for (let i = currentPage - 2; i <= currentPage + 2; i++) {
                pageLinks.push(i);
            }
            pageLinks.push('...');
            pageLinks.push(totalPages - 2);
            pageLinks.push(totalPages - 1);
            pageLinks.push(totalPages);
        } else {
            pageLinks.push(1);
            pageLinks.push(2);
            pageLinks.push(3);
            pageLinks.push('...');
            for (let i = totalPages - 9; i <= totalPages; i++) {
                pageLinks.push(i);
            }
        }
    }

    for (let i = 0; i < pageLinks.length; i++) {
        const pageButton = document.createElement('li');
        pageButton.classList.add('page-item');
        if (pageLinks[i] === currentPage) {
            pageButton.classList.add('active');
        }
        const pageLink = document.createElement('a');
        pageLink.classList.add('page-link');
        pageLink.href = '#';
        pageLink.innerText = pageLinks[i];
        pageButton.appendChild(pageLink);
        pagination.appendChild(pageButton);

        if (pageLinks[i] === '...') {
            pageButton.classList.add('disabled');
            pageLink.removeAttribute('href');
        } else {
            pageLink.addEventListener('click', () => {
                currentPage = pageLinks[i];
                displayResults(currentPage);
            });
        }
    }
}

function createNextButton() {
    const nextButton = document.createElement('li');
    nextButton.classList.add('page-item');
    if (currentPage === totalPages) {
        nextButton.classList.add('disabled');
    }
    const nextLink = document.createElement('a');
    nextLink.classList.add('page-link');
    nextLink.href = '#';
    nextLink.innerText = 'Next';
    nextButton.appendChild(nextLink);
    pagination.appendChild(nextButton);

    // Event listener
    nextLink.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            displayResults(currentPage);
        }
    });
}

async function fetchDataForIds(ids) {
    // Make the API call to fetch data for the given document IDs
    const response = await fetch('http://vmi1224404.contaboserver.net:5000/fetch_data/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(ids),
    });

    if (response.ok) {
        return await response.json();
    } else {
        console.error('Failed to fetch data for the given document IDs');
        return [];
    }
}

function displayFetchedData(fetchedData) {
    // Clear the existing content in the resultsList
    resultsList.innerHTML = '';

    // Iterate through the fetched data and display it in the resultsList
    fetchedData.forEach(data => {
        // Create a new element to display the data (e.g., a div, list item, or any other appropriate element)
        const resultElement = document.createElement('div');
        resultElement.classList.add('result-container');

        // Truncate the description and title after a specified number of words
        const snippet = truncateAfterWords(data.abstract, 100); // 100-word limit for snippet
        const title = truncateAfterWords(data.title, 20); // 20-word limit for title

        // Populate the resultElement with the data (customize this according to your data structure)
        resultElement.innerHTML = `<p class="result-url">${data.URL}</p>
            <a href="${data.URL}" target="_blank" class="result-title">${title}</a>
            <p class="result-snippet">${snippet}</p>`;

        // Add the resultElement to the resultsList
        resultsList.appendChild(resultElement);
    });
}

// Function to truncate text after a specified number of words
function truncateAfterWords(text, wordLimit) {
    const words = text.split(' ');
    return words.length > wordLimit ? words.slice(0, wordLimit).join(' ') + '...' : text;
}

displayResults(1);
