
        document.addEventListener('DOMContentLoaded', function() {
        const container = document.getElementById('colunas-container');
        const addButton = document.getElementById('adicionar-coluna');
        const template = document.getElementById('coluna-template');

        // Função para encontrar o maior índice existente (ex: se o último é 'colunas-2', o próximo é '3')
        function getNextIndex() {
            const entries = container.querySelectorAll('.coluna-entry');
            let maxIndex = -1;
            entries.forEach(entry => {
                const index = parseInt(entry.dataset.index);
                if (!isNaN(index) && index > maxIndex) {
                    maxIndex = index;
                }
            });
            return maxIndex + 1;
        }

        addButton.addEventListener('click', function() {
            const nextIndex = getNextIndex();
            
            // Clona o HTML do molde e substitui o placeholder '__ID__' pelo novo índice
            const newEntryHTML = template.innerHTML.replace(/__ID__/g, nextIndex);
            
            // Cria um novo elemento div para injetar o HTML
            const newEntry = document.createElement('div');
            newEntry.innerHTML = newEntryHTML;
            
            // Adiciona a nova estrutura ao container principal
            container.appendChild(newEntry.firstElementChild); 
            
            // Opcional: Focar no novo campo para usabilidade
            document.getElementById(`colunas-${nextIndex}-nome_coluna`)?.focus();
        });
    });
