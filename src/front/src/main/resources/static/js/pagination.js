// Get the list of search results and the pagination links
const resultsList = document.getElementById('resultsList');
const pagination = document.getElementById('pagination');
const resultsPerPage = 10;
const totalResults = resultsList.childElementCount;
const totalPages = Math.ceil(totalResults / resultsPerPage);
let currentPage = 1;

// Function to display the results for the current page and update the pagination links
function displayResults(page) {
    // Calculate the start and end index for the current page
    const startIndex = (page - 1) * resultsPerPage;
    const endIndex = startIndex + resultsPerPage;

    // Hide all the search results
    for (let i = 0; i < totalResults; i++) {
        resultsList.children[i].classList.add('d-none');
    }

    // Show the search results for the current page
    for (let i = startIndex; i < endIndex && i < totalResults; i++) {
        resultsList.children[i].classList.remove('d-none');
    }

    // Update the pagination links
    pagination.innerHTML = '';

    // Create the previous button
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

    // Create the numbered page links
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

    // Create next button
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

    // Add event listeners for next and previous
    previousLink.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayResults(currentPage);
        }
    });
    nextLink.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            displayResults(currentPage);
        }
    });
}

// Display the results for the first page
displayResults(1);