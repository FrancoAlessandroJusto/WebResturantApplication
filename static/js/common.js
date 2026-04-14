/**
 * Common JavaScript Library - Funzioni condivise per tutta l'applicazione
 * Elimina duplicazioni e standardizza comportamenti
 */

class UIHelper {
    /**
     * Mostra un messaggio notifica
     * @param {string} message - Messaggio da mostrare
     * @param {string} type - Tipo: 'success', 'error', 'info', 'warning'
     * @param {number} duration - Durata in ms (default 3000)
     */
    static showMessage(message, type = 'info', duration = 3000) {
        // Rimuovi messaggi esistenti
        const existing = document.querySelector('.ui-message');
        if (existing) {
            existing.remove();
        }

        // Crea nuovo messaggio
        const messageDiv = document.createElement('div');
        messageDiv.className = `ui-message fixed top-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            type === 'warning' ? 'bg-yellow-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        
        messageDiv.innerHTML = `
            <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-sm">
                    ${type === 'success' ? 'check_circle' : 
                      type === 'error' ? 'error' : 
                      type === 'warning' ? 'warning' : 
                      'info'}
                </span>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(messageDiv);

        // Auto rimozione
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.style.opacity = '0';
                setTimeout(() => messageDiv.remove(), 300);
            }
        }, duration);
    }

    /**
     * Toggle dark/light mode
     */
    static toggleDarkMode() {
        const html = document.documentElement;
        const isDark = html.classList.contains('dark');
        
        if (isDark) {
            html.classList.remove('dark');
            html.classList.add('light');
            localStorage.setItem('theme', 'light');
        } else {
            html.classList.remove('light');
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    }

    /**
     * Inizializza il tema dal localStorage o preferenza system
     */
    static initializeTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.add('light');
        }
    }

    /**
     * Formatta prezzo in Euro
     * @param {number} price - Prezzo da formattare
     * @return {string} Prezzo formattato
     */
    static formatPrice(price) {
        return new Intl.NumberFormat('it-IT', {
            style: 'currency',
            currency: 'EUR'
        }).format(price);
    }

    /**
     * Debounce per performance
     * @param {Function} func - Funzione da debounce
     * @param {number} delay - Delay in ms
     * @return {Function} Funzione debounced
     */
    static debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Setup form validation
     * @param {HTMLFormElement} form - Form da validare
     * @param {Object} rules - Regole di validazione
     */
    static setupFormValidation(form, rules = {}) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            let isValid = true;
            const formData = new FormData(form);
            
            // Valida ogni campo
            for (const [fieldName, rule] of Object.entries(rules)) {
                const value = formData.get(fieldName);
                const input = form.querySelector(`[name="${fieldName}"]`);
                
                if (rule.required && (!value || value.trim() === '')) {
                    UIHelper.showFieldError(input, 'Campo obbligatorio');
                    isValid = false;
                } else if (rule.min && parseFloat(value) < rule.min) {
                    UIHelper.showFieldError(input, `Valore minimo: ${rule.min}`);
                    isValid = false;
                } else if (rule.max && parseFloat(value) > rule.max) {
                    UIHelper.showFieldError(input, `Valore massimo: ${rule.max}`);
                    isValid = false;
                } else {
                    UIHelper.clearFieldError(input);
                }
            }
            
            if (isValid && form.onValidSubmit) {
                form.onValidSubmit(formData);
            }
        });
    }

    /**
     * Mostra errore su campo form
     * @param {HTMLElement} input - Campo input
     * @param {string} message - Messaggio di errore
     */
    static showFieldError(input, message) {
        UIHelper.clearFieldError(input);
        
        input.classList.add('border-red-500');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
    }

    /**
     * Rimuovi errore da campo form
     * @param {HTMLElement} input - Campo input
     */
    static clearFieldError(input) {
        input.classList.remove('border-red-500');
        const errorDiv = input.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Setup confirm dialog
     * @param {string} message - Messaggio di conferma
     * @param {Function} onConfirm - Callback conferma
     * @param {Function} onCancel - Callback annulla
     */
    static confirmDialog(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white dark:bg-[#2a1f1a] rounded-xl p-6 max-w-sm w-full mx-4 border border-[#e5e5e5] dark:border-[#4a3a30]">
                <h3 class="text-lg font-semibold text-[#181311] dark:text-white mb-4">Conferma</h3>
                <p class="text-[#666] dark:text-[#a09080] mb-6">${message}</p>
                <div class="flex gap-3">
                    <button class="confirm-cancel flex-1 px-4 py-2 border border-[#e5e5e5] dark:border-[#4a3a30] rounded-lg text-[#181311] dark:text-white hover:bg-[#f8f6f6] dark:hover:bg-[#3d2a22] transition-colors">
                        Annulla
                    </button>
                    <button class="confirm-ok flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors">
                        Conferma
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event handlers
        modal.querySelector('.confirm-ok').onclick = () => {
            modal.remove();
            if (onConfirm) onConfirm();
        };

        modal.querySelector('.confirm-cancel').onclick = () => {
            modal.remove();
            if (onCancel) onCancel();
        };

        // Click outside to close
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
                if (onCancel) onCancel();
            }
        };
    }

    /**
     * Setup table sorting
     * @param {HTMLTableElement} table - Tabella da ordinare
     */
    static setupTableSorting(table) {
        const headers = table.querySelectorAll('th[data-sortable]');
        
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sortable;
                const currentSort = header.dataset.sort || 'none';
                const newSort = currentSort === 'asc' ? 'desc' : 'asc';
                
                // Reset other headers
                headers.forEach(h => {
                    h.dataset.sort = 'none';
                    h.querySelector('.sort-icon')?.remove();
                });
                
                // Set current header
                header.dataset.sort = newSort;
                
                // Add sort icon
                const icon = document.createElement('span');
                icon.className = 'sort-icon ml-1 material-symbols-outlined text-sm';
                icon.textContent = newSort === 'asc' ? 'arrow_upward' : 'arrow_downward';
                header.appendChild(icon);
                
                // Sort table
                UIHelper.sortTable(table, column, newSort);
            });
        });
    }

    /**
     * Ordina tabella
     * @param {HTMLTableElement} table - Tabella
     * @param {string} column - Colonna
     * @param {string} direction - Direzione 'asc' o 'desc'
     */
    static sortTable(table, column, direction) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.children[column].textContent.trim();
            const bVal = b.children[column].textContent.trim();
            
            const aNum = parseFloat(aVal);
            const bNum = parseFloat(bVal);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return direction === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            return direction === 'asc' 
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }
}

// Auto-initializza tema quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
    UIHelper.initializeTheme();
});

// Export per uso globale
window.UIHelper = UIHelper;
