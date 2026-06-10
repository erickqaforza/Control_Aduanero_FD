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

  @login @login_negativo @control_aduanero
  Scenario Outline: Login fallido por credenciales invalidas
    Given el usuario abre Control Aduanero FD
    When el usuario intenta iniciar sesion en el pais "Guatemala" con "<tipo_error>"
    Then debe visualizar un mensaje de credenciales invalidas

    Examples:
      | tipo_error            |
      | correo_incorrecto     |
      | contrasena_incorrecta |

  @guia_madre @control_aduanero
  Scenario Outline: Crear guia madre por pais y moneda
    Given el usuario abre Control Aduanero FD
    When el usuario inicia sesion en el pais "<pais>"
    And acepta el modal informativo
    And crea una guia madre con moneda "<moneda>"
    Then debe visualizar el mensaje de guia madre creada

    Examples:
      | pais        | moneda |
      | Guatemala   | GTQ    |
      | Guatemala   | USD    |
      | Guatemala   | HNL    |
      | Honduras    | GTQ    |
      | Honduras    | USD    |
      | Honduras    | HNL    |
      | El Salvador | GTQ    |
      | El Salvador | USD    |
      | El Salvador | HNL    |
