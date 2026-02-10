# Sistema de Cadastro de Pacientes - Guia de Implementação

## 📋 Funcionalidades Implementadas

### 1. Criação de Leads na Gestão Comercial

**Fluxo:**
1. Acesse "Gestão Comercial" → Coluna "Entrada de Lead"
2. Clique em "Adicionar Card"
3. Preencha:
   - Responsável pelo Atendimento (nome do comercial)
   - Como chegou na plataforma (Indicação / Tráfego Pago / Vendedor Externo)
   - Opcionalmente, gerar link automático para o formulário do paciente
4. O sistema gera automaticamente:
   - ID do Lead (0001, 0002, etc.)
   - Link para enviar ao paciente
   - Card com todas as informações

### 2. Formulário de Cadastro de Paciente (4 Passos)

**Acesso:**
- Clique no link "Clique aqui para acessar o formulário" no card do lead
- Ou acesse diretamente: `http://localhost:5000?registerPaciente=true`

**Passo 1: Dados Informativos do Paciente**
- Nome Completo *
- CPF *
- Data de Nascimento * (detecta automaticamente se é menor de 18 anos)
  - Se menor de 18: Aparece seção para dados do responsável
- Telefone (WhatsApp) *
- Endereço Completo *
- E-mail *

**Passo 2: Dados Diagnóstico**
- Peso (kg) *
- Condição Principal para Atendimento *
  - Autismo
  - TDAH
  - Ansiedade/Depressão
  - Diabetes/Pré-diabetes
  - Fibromialgia
  - Epilepsia
  - Outro (com campo de especificação)
- Diagnósticos Prévios *
  - Hipertensão
  - Doenças cardíacas
  - Câncer
  - Distúrbios neurológicos
  - Alergias (com campo de especificação)
  - Nenhum
- Histórico Familiar Relevante *
  - Doenças genéticas
  - Diabetes
  - Alzheimer/Parkinson
  - Outro (com campo de especificação)
- Medicações em Uso (nome e dosagem)
- Cirurgias Anteriores

**Passo 3: Sintomas e Objetivos**
- Sintomas Atuais (duração, intensidade, fatores agravantes) *
- Objetivo da Consulta *
  - Iniciar tratamento com óleo de cannabis
  - Exames genéticos
  - Ajuste de suplementos
  - Segunda opinião médica
  - Outro (com campo de especificação)
- Exames Recentes (marque os anexados)
  - Hemograma completo
  - Teste genético
  - Laudo psiquiátrico
  - Imagens (RM/Tomografia)

**Passo 4: Hábitos**
- Hábitos *
  - Tabagismo
  - Consumo de álcool
  - Atividade física regular
  - Dieta específica (com campo de especificação)

### 3. Links de Formulário na IA

Os links dos formulários estão disponíveis na seção "Inteligência Artificial":
- **Coluna "Médico":**
  - Formulário Médico (para profissionais que querem trabalhar conosco)
  - Formulário Paciente (para pacientes preencherem seus dados)

### 4. Armazenamento de Dados

**Backend (API):**
- `/api/leads` - Gerenciar leads
  - GET - Listar todos os leads
  - POST - Criar novo lead
  - PUT `/api/leads/<id>` - Atualizar lead
  - DELETE `/api/leads/<id>` - Deletar lead

**Arquivo de Dados:**
- Leads: `data/leads.json`
- Pacientes: Salvos via API nos leads, ou em `data/leads.json`

**Persistência Local (Fallback):**
- Se o servidor não estiver disponível, os dados são salvos em localStorage

## 🔧 IDs Gerados Automaticamente

### ID do Lead
- Formato: 4 dígitos (0001, 0002, 0003, etc.)
- Gerado automaticamente quando o lead é criado
- Baseado no número máximo existente + 1

### ID do Paciente
- Mesmo sistema do lead
- Atribuído quando o formulário é submetido

## 📝 Campos Condicionais

1. **Seção de Responsável (Menores de 18 anos)**
   - Aparece automaticamente quando a data de nascimento é menor que 18 anos
   - Requer Nome e CPF do responsável

2. **Campos "Especificar"**
   - Aparecem quando a opção "Outro" é marcada
   - Disponível em:
     - Condição Principal para Atendimento
     - Alergias (Diagnósticos Prévios)
     - Histórico Familiar
     - Objetivo da Consulta
     - Dieta Específica (Hábitos)

## 🔗 URLs Públicas

- **Formulário do Paciente (genérico):**
  ```
  http://localhost:5000?registerPaciente=true
  ```

- **Formulário do Paciente (específico para um lead):**
  ```
  http://localhost:5000?registerPaciente=true&leadId=0001
  ```

- **Formulário do Médico:**
  ```
  http://localhost:5000?registerMedico=true
  ```

## 📊 Fluxo Completo

```
1. Comercial cria um Lead em "Gestão Comercial" → "Entrada de Lead"
   ↓
2. Sistema gera ID do Lead (0001, 0002, etc.)
   ↓
3. Card é criado com:
   - ID do Lead
   - Responsável pelo atendimento
   - Fonte (Indicação/Tráfego Pago/Vendedor Externo)
   - Link para enviar ao paciente
   ↓
4. Comercial envia link ao paciente
   ↓
5. Paciente preenche formulário em 4 passos
   ↓
6. Dados do paciente são salvos no backend
   ↓
7. Paciente recebe confirmação com seu ID
```

## 🎯 Próximas Melhorias (Opcionais)

### CRUD Dinâmico de Campos do Formulário
Para adicionar a capacidade de gerenciar campos do formulário via interface:
1. Criar interface admin para gerenciar questions/options
2. Armazenar definições de formulário em JSON/DB
3. Renderizar formulário dinamicamente baseado na definição

### Notificações
- E-mail de confirmação para o paciente
- Notificação para o responsável (menor de idade)
- Alertas para o comercial quando paciente preenche o formulário

### Integração com Kanban
- Mover card automaticamente quando paciente preenche formulário
- Mostrar status de preenchimento no card do lead

## 🐛 Troubleshooting

### Form não abre quando clico em "Adicionar Card"
1. Verifique se o JavaScript está carregado (F12 → Console)
2. Certifique-se de que está na coluna "Entrada de Lead" exatamente

### Dados não salvam
1. Verifique se o backend está rodando (`python app.py`)
2. Verifique se a pasta `data/` existe e tem permissão de escrita
3. Verifique o console do navegador (F12) para erros

### ID do Lead não aparece
1. Aguarde a resposta do servidor (pode levar alguns segundos)
2. Se aparecer "Cadastro salvo localmente", o servidor pode estar indisponível

