let wordList = [];
const cells = document.querySelectorAll('.grid-cell');
const rows = 6;  
const cellsPerRow = 5;

document.addEventListener("DOMContentLoaded", () => {
    const firstCell = document.querySelector('.grid-cell');
    if (firstCell) {
        firstCell.focus();
    }
});

fetch('/get_word_list')
    .then(response => response.json())
    .then(data => {
        wordList = data;
    })
    .catch(error => console.error('Error fetching word list:', error));

const georgianRegex = /^[\u10A0-\u10FF]$/; 

cells.forEach((cell, index) => {
    function moveCursorToEnd(cell) {
        const range = document.createRange();
        const selection = window.getSelection();
        range.selectNodeContents(cell);
        range.collapse(false); 
        selection.removeAllRanges();
        selection.addRange(range);
    }

    cell.addEventListener('focus', () => {
        moveCursorToEnd(cell);
    });

    
    cell.addEventListener('keydown', (event) => {
        if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
            const currentRow = Math.floor(index / cellsPerRow);  

            const rowFilled = Array.from(cells).slice(currentRow * cellsPerRow, (currentRow + 1) * cellsPerRow).every(cell => cell.textContent.length > 0);

            if (rowFilled) {
                event.preventDefault(); 
            } else if (cell.textContent.length === 1) {
                const nextCell = cells[index + 1];
                if (nextCell) {
                    nextCell.focus();
                }
            }

            if (!georgianRegex.test(event.key)) {
                event.preventDefault();  
            }
        }

        if (event.key === 'Backspace') {
            const currentRow = Math.floor(index / cellsPerRow);  
            const firstCellInRow = currentRow * cellsPerRow;  

            if (index === firstCellInRow && cell.textContent.length === 0) {
                event.preventDefault();  
            } else if (cell.textContent.length === 0) {
                const prevCell = cells[index - 1];
                if (prevCell) {
                    prevCell.focus();
                }
            }
        }

        if (event.key === 'Enter') {
            const currentRow = Math.floor(index / cellsPerRow);
            const word = Array.from(cells)
                .slice(currentRow * cellsPerRow, (currentRow + 1) * cellsPerRow)
                .map(cell => cell.textContent)
                .join('')
                .toUpperCase();

            if (wordList.includes(word)) {
                document.getElementById('message').textContent = '';  

                if (currentRow < rows - 1) {
                    const nextRowFirstCell = cells[(currentRow + 1) * cellsPerRow];
                    setTimeout(() => {
                        nextRowFirstCell.focus();
                    }, 100);
                }

                fetch('/submit_guess', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ guess: word, current_row: currentRow }),
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').textContent = data.message;

                    if (data.correct) {
                        if (data.redirect) {
                            window.location.href = '/win';  
                        }
                    } else if (data.redirect) {
                        window.location.href = '/lose';  
                    }

                    const colors = data.colors;
                    Array.from(cells).slice(currentRow * cellsPerRow, (currentRow + 1) * cellsPerRow).forEach((cell, i) => {
                        cell.style.backgroundColor = colors[i];
                    });
                })
                .catch(error => console.error('Error submitting guess:', error));
            } else {
                document.getElementById('message').textContent = 'Not in the word list';
                
            }
        }
    });
});