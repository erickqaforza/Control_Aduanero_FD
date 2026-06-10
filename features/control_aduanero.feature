# language: es
Caracteristica: Control Aduanero FD

  @smoke @control_aduanero
  Escenario: Abrir la pagina principal
    Dado el usuario abre Control Aduanero FD
    Entonces el titulo de la pagina debe ser "Control Aduanero FD"