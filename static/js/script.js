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

    // --- Aquí puedes añadir más lógica JS para otras funcionalidades de tu sitio ---
    // Ejemplo:
    // const algunBoton = document.getElementById('miBotonEspecial');
    // if (algunBoton) {
    //   algunBoton.addEventListener('click', () => {
    //     console.log('Botón especial clickeado!');
    //   });
    // }

});