// Los botones no envían ni validan el formulario.
const botonesCancelar = document.querySelectorAll('.cancelar-popup');
botonesCancelar.forEach(function (boton) {
    boton.addEventListener('click', function () {
        window.close();
    });
});
