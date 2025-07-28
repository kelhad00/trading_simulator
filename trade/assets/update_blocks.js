window.updateTimeline = function() {
    try {
        window.itemSizes = {};

        const timelineDiv = document.getElementById('timeline');
        if (!timelineDiv) {
            console.warn('Timeline non trouvée');
            return {};
        }

        // Sélectionner tous les blocs item-*
        const allElements = Array.from(document.querySelectorAll('[id^="item-"]'));

        // Total des largeurs de tous les blocs visibles
        let totalWidth = allElements.reduce((sum, el) => sum + el.offsetWidth, 0);

        allElements.forEach(el => {
            const width = el.offsetWidth;
            const height = el.offsetHeight;
            const percent = totalWidth ? (width / totalWidth) * 100 : 0;

            // Chercher un nœud texte pour afficher le pourcentage
            let labelNode = null;
            for (let node of el.childNodes) {
                if (node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== "") {
                    labelNode = node;
                    break;
                }
            }
            if (!labelNode) {
                for (let node of el.childNodes) {
                    if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'DIV') {
                        labelNode = node;
                        break;
                    }
                }
            }

            if (labelNode) {
                let displayedLabel = labelNode.textContent;
                const percentRegex = /\s*\(\d+(\.\d+)?%\)$/;
                displayedLabel = displayedLabel.replace(percentRegex, '').trim();
                labelNode.textContent = `${displayedLabel} (${percent.toFixed(1)}%)`;
            }

            // Adapter la largeur en fonction du pourcentage et taille timeline
            el.style.width = (timelineDiv.offsetWidth * percent / 100) + 'px';

            // Extraire label à partir de l'id
            let label = null;
            const id = el.id;
            if (id && id.startsWith("item-")) {
                const parts = id.split('-');
                if (parts.length >= 3) {
                    label = parts.slice(2).join(' ');
                }
            }

            // Déterminer le type de pattern s'il est visible dans un div
            let patternType = null;
            const typeDiv = Array.from(el.querySelectorAll('div'))
                .find(div => div.textContent === 'Avec pattern' || div.textContent === 'Sans pattern');
            if (typeDiv) {
                patternType = typeDiv.textContent === 'Avec pattern' ? 'with' : 'without';
            }

            window.itemSizes[el.id] = {
                width,
                height,
                label,
                pattern_type: patternType
            };
        });

        // Mettre un ResizeObserver sur chaque bloc s'il n'y en a pas déjà
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
