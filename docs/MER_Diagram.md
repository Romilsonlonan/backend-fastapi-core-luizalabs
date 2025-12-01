# Modelo de Entidade e Relacionamento (MER) - Backend

Este documento apresenta o Modelo de Entidade e Relacionamento (MER) do backend, detalhando as principais entidades do sistema e seus relacionamentos.

## Diagrama Visual Detalhado

```plainText
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER (Usuários)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ id: Integer (PK)                                                           │
│ name: String                                                               │
│ email: String (UK)                                                         │
│ hashed_password: String                                                    │
│ profile_image_url: String (nullable)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1
                                      │
                                      ├─────────────────────────────────────┐
                                      │                                     │
┌─────────────────────────────────────────────────────────────────────────────┐ │
│                              CLUB (Clubes)                                 │ │
├─────────────────────────────────────────────────────────────────────────────┤ │
│ id: Integer (PK)                                                           │ │
│ name: String                                                               │ │
│ initials: String(3)                                                        │ │
│ city: String                                                               │ │
│ shield_image_url: String (nullable)                                        │ │
│ foundation_date: Date (nullable)                                           │ │
│ br_titles: Integer                                                         │ │
│ training_center: String (nullable)                                         │ │
│ espn_url: String (nullable)                                                │ │
└─────────────────────────────────────────────────────────────────────────────┘ │
                                      │                                     │
                                      │ 1                                   │
                                      │                                     │
                                      ├─────────────────────────────────────┘
                                      │ N
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PLAYER (Jogadores)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ id: Integer (PK)                                                           │
│ name: String                                                               │
│ jersey_number: Integer                                                     │
│ position: String                                                          │
│ age: Integer                                                               │
│ height: Float                                                              │
│ weight: Float                                                              │
│ nationality: String (nullable)                                             │
│ games: Integer                                                             │
│ substitute_appearances: Integer                                            │
│ goals: Integer                                                             │
│ assists: Integer                                                           │
│ shots: Integer                                                             │
│ shots_on_goal: Integer                                                     │
│ fouls_committed: Integer                                                   │
│ fouls_suffered: Integer                                                    │
│ defenses: Integer                                                          │
│ goals_conceded: Integer                                                    │
│ yellow_cards: Integer                                                      │
│ red_cards: Integer                                                         │
│ club_id: Integer (FK)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Legenda:

*   **PK**: Primary Key (Chave Primária)
*   **FK**: Foreign Key (Chave Estrangeira)
*   **UK**: Unique Key (Chave Única)
*   **1**: Relacionamento um-para-um
*   **N**: Relacionamento um-para-muitos

## Relacionamentos:

*   **CLUB 1:N PLAYER**: Um clube pode possuir muitos jogadores.
*   **PLAYER N:1 CLUB**: Muitos jogadores pertencem a um único clube.

## Explicação do Modelo:

O diagrama acima ilustra o modelo de entidade e relacionamento para o sistema, que é focado no gerenciamento de clubes e seus respectivos jogadores, com usuários administrativos separados.

*   **USER (Usuários)**: Representa os usuários do sistema, provavelmente com funções administrativas ou de gerenciamento. Cada usuário possui um `id` único, `name`, `email` (também único), uma `hashed_password` para segurança e uma `profile_image_url` opcional.
*   **CLUB (Clubes)**: Representa os clubes de futebol. Cada clube tem um `id` único, `name`, `initials` (com 3 caracteres), `city`, `shield_image_url` opcional, `foundation_date` opcional, `br_titles` (número de títulos brasileiros), `training_center` opcional e `espn_url` opcional.
*   **PLAYER (Jogadores)**: Representa os jogadores de futebol. Cada jogador possui um `id` único, `name`, `jersey_number`, `position`, `age`, `height`, `weight`, `nationality` opcional, e várias estatísticas de jogo como `games`, `substitute_appearances`, `goals`, `assists`, `shots`, `shots_on_goal`, `fouls_committed`, `fouls_suffered`, `defenses`, `goals_conceded`, `yellow_cards`, `red_cards`. A chave estrangeira `club_id` estabelece o relacionamento com a entidade `CLUB`, indicando a qual clube o jogador pertence.

Este modelo permite uma gestão clara e organizada dos dados de usuários, clubes e jogadores, facilitando a recuperação e manipulação das informações no backend.

### **Atualizações Recentes:**

*   **Funcionalidade de Edição de Clubes:** A rota `PATCH /clubs/{club_id}` foi atualizada para permitir a edição parcial dos dados de um clube. Campos como `name`, `initials`, `city`, `foundation_date`, `br_titles`, `training_center` e `espn_url` podem ser atualizados individualmente. O campo `shield_image_url` também pode ser atualizado através do upload de um novo arquivo de imagem.
*   **Campos Opcionais:** Os campos `foundation_date`, `training_center` e `espn_url` são opcionais e podem ser enviados como `None` ou strings vazias para limpar seus valores existentes no banco de dados, se necessário.
