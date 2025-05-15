// static/js/script.js
// Aquí irá el JavaScript en el futuro si es necesario
console.log("Script.js cargado.");
document.addEventListener('DOMContentLoaded', function() {

    // --- Funcionalidad para filas de tabla clickeables ---
    const tablaLotes = document.getElementById('lotesTabla'); // Obtener la tabla por su ID

    if (tablaLotes) { // Verificar que la tabla exista en la página actual
        // Seleccionar solo las filas 'clickable-row' que tengan el atributo 'data-href' dentro del tbody
        const filasClickeables = tablaLotes.querySelectorAll('tbody tr.clickable-row[data-href]');

        filasClickeables.forEach(fila => {
            // 1. Hacer la fila enfocable mediante teclado
            fila.setAttribute('tabindex', '0');

            // 2. Evento para el clic del ratón
            fila.addEventListener('click', function() {
                // 'this.dataset.href' es seguro aquí porque no es una función flecha
                // y 'this' se refiere al elemento 'fila'
                const href = this.dataset.href;
                if (href) {
                    window.location.href = href;
                }
            });

            // 3. Evento para la activación mediante teclado (tecla Enter)
            fila.addEventListener('keydown', function(event) {
                // 'this.dataset.href' también es seguro aquí
                const href = this.dataset.href;
                if (event.key === 'Enter' && href) {
                    window.location.href = href;
                }
            });

            // NOTA: El estilo para :focus-visible se maneja mejor en CSS:
            // #lotesTabla tbody tr.clickable-row:focus-visible {
            //     outline: 2px solid var(--color-primario);
            //     outline-offset: -2px;
            //     background-color: var(--gris-hover-sutil); /* O el color de hover que elijas */
            // }
        });

        // Opcional: Añadir un mensaje si no se encontraron filas clickeables pero sí la tabla
        if (filasClickeables.length === 0) {
            console.log("Tabla 'lotesTabla' encontrada, pero no hay filas 'clickable-row' con 'data-href'.");
        }

    } else {
        // Opcional: Mensaje si la tabla no se encuentra en la página. Útil para depuración.
        // Solo mostrar si esperas que la tabla esté siempre. Si es opcional, este console.log puede ser ruidoso.
        // console.log("Elemento con ID 'lotesTabla' no encontrado en esta página.");
    }

            // --- Funcionalidad para Modal de Confirmación ---
    const confirmModal = document.getElementById('confirmActionModal');
    const confirmModalTitle = document.getElementById('confirmModalTitle');
    const confirmModalMessage = document.getElementById('confirmModalMessage');
    const confirmModalButtonConfirm = document.getElementById('confirmModalButtonConfirm');
    const confirmModalButtonCancel = document.getElementById('confirmModalButtonCancel');
    let currentFormToSubmit = null; // Variable para guardar el formulario a enviar

    function showConfirmModal(title, message, formToSubmit) {
        if (!confirmModal) return; // Salir si el modal no está en la página

        confirmModalTitle.textContent = title;
        confirmModalMessage.innerHTML = message; // Usamos innerHTML por si quieres pasar HTML básico
        currentFormToSubmit = formToSubmit;

        confirmModal.style.display = 'flex'; // Mostrar primero para que la transición funcione
        setTimeout(() => { // Pequeño delay para permitir que la transición CSS ocurra
            confirmModal.classList.add('active');
            confirmModalButtonConfirm.focus(); // Poner foco en el botón de confirmar
        }, 10);

        // Cerrar con tecla Escape
        document.addEventListener('keydown', handleEscapeKey);
    }

    function hideConfirmModal() {
        if (!confirmModal) return;

        confirmModal.classList.remove('active');
        // Esperar a que termine la transición antes de ocultar con display: none
        confirmModal.addEventListener('transitionend', function handler() {
            confirmModal.style.display = 'none';
            confirmModal.removeEventListener('transitionend', handler); // Limpiar el listener
        });
        currentFormToSubmit = null;
        document.removeEventListener('keydown', handleEscapeKey);
    }

    function handleEscapeKey(event) {
        if (event.key === 'Escape') {
            hideConfirmModal();
        }
    }

    if (confirmModalButtonConfirm) {
        confirmModalButtonConfirm.addEventListener('click', () => {
            if (currentFormToSubmit) {
                currentFormToSubmit.submit();
            }
            hideConfirmModal();
        });
    }

    if (confirmModalButtonCancel) {
        confirmModalButtonCancel.addEventListener('click', () => {
            hideConfirmModal();
        });
    }

    // Cerrar modal si se hace clic en el overlay (fuera del contenido del modal)
    if (confirmModal) {
        confirmModal.addEventListener('click', (event) => {
            if (event.target === confirmModal) { // Si el clic fue directamente en el overlay
                hideConfirmModal();
            }
        });
    }

    // --- FIN Funcionalidad para Modal de Confirmación ---


    // --- Modificar botones de eliminar para usar el modal ---
    const deleteButtons = document.querySelectorAll('.btn-confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevenir el envío inmediato del formulario
            const form = this.closest('form'); // Encontrar el formulario padre
            const providerName = this.dataset.providerName || 'este proveedor'; // Obtener nombre si está disponible
            const message = `¿Confirmas que quieres eliminar a <strong>${providerName}</strong>? Las cargas compradas a este provedor no se eliminarán.`;
            const title = "Confirmar Eliminación";
            showConfirmModal(title, message, form);
        });
    });


    // --- Aquí puedes añadir más lógica JS para otras funcionalidades de tu sitio ---
    // Ejemplo:
    // const algunBoton = document.getElementById('miBotonEspecial');
    // if (algunBoton) {
    //   algunBoton.addEventListener('click', () => {
    //     console.log('Botón especial clickeado!');
    //   });
    // }

});