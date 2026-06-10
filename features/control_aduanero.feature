Feature: Control Aduanero FD

  @login @smoke @control_aduanero
  Scenario Outline: Login exitoso por pais
    Given el usuario abre Control Aduanero FD
    When el usuario inicia sesion en el pais "<pais>"
    And acepta el modal informativo
    Then debe visualizar la pantalla de guias madre para el usuario "Erick Estrada"

    Examples:
      | pais        |
      | Guatemala   |
      | Honduras    |
      | El Salvador |
