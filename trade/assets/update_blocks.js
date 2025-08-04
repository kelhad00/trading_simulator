window.updateTimeline = function () {
    try {
        window.itemSizes = {};

        const timelineDiv = document.getElementById('timeline');
        if (!timelineDiv) {
            console.warn('Timeline non trouvée');
            return {};
        }

        const allElements = Array.from(document.querySelectorAll('[id^="item-"]'));

        let totalWidth = allElements.reduce((sum, el) => sum + el.offsetWidth, 0);

        allElements.forEach(el => {
            const width = el.offsetWidth;
            const height = el.offsetHeight;
            const percent = totalWidth ? (width / totalWidth) * 100 : 0;

            // ✅ Trouver le label via strong imbriqué
            let displayedLabel = null;
            const strongEl = el.querySelector('div > strong');
            if (strongEl) {
                displayedLabel = strongEl.textContent.trim();
                // Supprimer ancien pourcentage s’il y en avait
                const percentRegex = /\s*\(\d+(\.\d+)?%\)$/;
                strongEl.textContent = `${displayedLabel.replace(percentRegex, '')} (${percent.toFixed(1)}%)`;
            }

            // Adapter la largeur
            el.style.width = (timelineDiv.offsetWidth * percent / 100) + 'px';

            // Fallback depuis l'id
            let label = displayedLabel;
            if (!label) {
                const id = el.id;
                if (id && id.startsWith("item-")) {
                    const parts = id.split('-');
                    if (parts.length >= 3) {
                        label = parts.slice(2).join(' ');
                    }
                }
            }

            // ✅ Trouver le type de pattern
            let patternType = null;
            const patternDiv = Array.from(el.querySelectorAll('div'))
                .find(div => div.textContent.trim() === 'Avec pattern' || div.textContent.trim() === 'Sans pattern');
            if (patternDiv) {
                patternType = patternDiv.textContent.trim() === 'Avec pattern' ? 'with' : 'without';
            }

            // Sauvegarder
            window.itemSizes[el.id] = {
                width,
                height,
                label,
                pattern_type: patternType
            };
        });

        // Observer les blocs
        allElements.forEach(el => {
            if (!el._resizeObserver) {
                const observer = new ResizeObserver(() => {
                    window.updateTimeline();
                });
                observer.observe(el);
                el._resizeObserver = observer;
            }
        });

        return window.itemSizes;
    } catch (e) {
        console.error('Erreur dans updateTimeline:', e);
        return {};
    }
};
