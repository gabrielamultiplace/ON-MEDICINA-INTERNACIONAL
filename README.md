# ON Medicina Internacional - Plataforma Avançada

## 📋 Visão Geral
Sistema completo de gestão para medicina com cannabis medicinal, incluindo Kanban para gestão de leads, médicos, financeiro, jurídico e IA.

---

## ✅ Funcionalidades Implementadas

### 1. **Sistema de Autenticação**
- Login seguro com email e senha
- Validação de força de senha
- Gerenciamento de sessão
- Reset de senha
- Criação de novos usuários

### 2. **Painel de Gestão (Kanban Principal)**
- 6 colunas: Comercial, Consultas, Acompanhamento, Financeiro, Renovação, Finalizada
- Drag & drop de cards entre colunas
- Adicionar/editar/deletar cards
- Priorização (Alta, Média, Baixa)
- Atribuição de responsáveis

### 3. **Gestão Comercial**
- Kanban específico para leads
- 5 colunas: Entrada de Lead, Atendimento, Formulário, Negociação, Fechado
- Criação de novo lead com ID automático
- Link progressivo para paciente preencher formulário
- Cards com informações de responsável e fonte

### 4. **Formulário Progressivo de Pacientes**
- Acesso por link público: `?registerPaciente=<id>`
- Uma pergunta por vez em modais
- Navegação: Próximo, Anterior, Pular
- Validação de campos obrigatórios
- 4 seções: Dados Informativos, Diagnóstico, Sintomas, Hábitos
- ~20 campos totais incluindo texto, data, select, multiselect

### 5. **Gestão de Médicos**
- Kanban de acompanhamento de médicos (Novo, Triagem, Acompanhamento, Ativo, Inativo)
- Formulário de cadastro: `?registerMedico=true`
- Campos: Nome, CPF, CRM, Especialidade, RQE, Email, Telefone, Banco, Agência, Conta, PIX
- Upload de foto e documentos (CRM)
- Edição e atualização de dados
- Admin list com grid de médicos

### 6. **Financeiro**
- Kanban de fluxo financeiro
- 4 colunas: Lançamentos, Conferência, Aprovação, Pagamento
- Cards com informações de transações
- Integração com banco de dados de médicos

### 7. **Judicial**
- Kanban para processos ANVISA e jurídicos
- 4 colunas: Abertos, Em análise, Protocolados, Concluídos
- Rastreamento de processos

### 8. **Importação de Medicamentos**
- Kanban para gestão de importações
- 4 colunas: Solicitado, Em Transporte, Recebido, Estoque
- Rastreamento de pedidos

### 9. **Inteligência Artificial**
- Kanban com 5 colunas: Desenvolvimento, Testes, Implementação, Produção, Médico
- Card pré-configurado com link do formulário médico
- Gerenciar campos do formulário de pacientes
  - Visualizar/deletar campos
  - Deletar seções inteiras
  - Adicionar novos campos customizados
  - Tipos: texto, email, número, data, textarea, select, multiselect

### 10. **Administrativo**
- Grid de módulos draggable
- 9 módulos pré-configurados:
  - Comercial
  - Financeiro
  - Recursos Humanos
  - Judicial
  - Importação Medicamento
  - Inteligência Artificial
  - Gestão de Médicos
  - Gestão de Leads
  - Relatórios
- Edição de módulos (título, ícone, itens)
- Adição e exclusão de módulos
- Reordenação drag & drop

### 11. **Configurações do Sistema**
- Gerenciamento de usuários
- Reset de senhas
- Parâmetros do sistema
- Integrações API
- Backup e segurança

### 12. **Recursos de UI/UX**
- Layout responsivo (desktop, tablet, mobile)
- Visualização vertical/horizontal customizável
- Temas com gradientes modernos
- Ícones Font Awesome
- Modais com drag & drop
- LocalStorage para persistência offline
- Animações suaves

---

## 🚀 Como Iniciar

### 1. **Verificar Configuração**
```bash
python verify_setup.py
```

### 2. **Instalar Dependências**
```bash
pip install -r requirements.txt
```

### 3. **Iniciar a Aplicação**
```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

---

## 🔐 Credenciais de Acesso

**Email:** gabrielamultiplace@gmail.com  
**Senha:** @On2025@

---

## 📁 Estrutura de Arquivos

```
Plataforma ON/
├── app.py                      # Backend Flask
├── index.html                  # Frontend
├── requirements.txt            # Dependências Python
├── data.db                     # Banco de dados SQLite
├── data/
│   ├── doctors.json           # Lista de médicos
│   ├── leads.json             # Lista de leads
│   └── leads_config.json      # Configuração do formulário
├── uploads/                   # Documentos de médicos
└── verify_setup.py           # Script de verificação
```

---

## 🔗 Variáveis de URL

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `?registerPaciente=<id>` | Abre formulário progressivo de paciente | `?registerPaciente=0001` |
| `?registerMedico=true` | Abre formulário de cadastro de médico | `?registerMedico=true` |
| `?runSelfTest=true` | Executa teste automático do Kanban | `?runSelfTest=true` |

---

## 📊 API Endpoints

### Autenticação
- `POST /api/login` - Login do usuário
- `POST /api/logout` - Logout
- `GET /api/me` - Dados do usuário logado

### Usuários
- `GET /api/users` - Lista de usuários
- `POST /api/users` - Criar novo usuário
- `POST /api/users/reset-password` - Resetar senha

### Médicos
- `GET /api/doctors` - Lista de médicos
- `POST /api/doctors` - Criar novo médico
- `PUT /api/doctors/<id>` - Atualizar médico
- `DELETE /api/doctors/<id>` - Deletar médico

### Leads
- `GET /api/leads` - Lista de leads
- `POST /api/leads` - Criar novo lead
- `GET /api/leads/<id>` - Obter lead
- `PUT /api/leads/<id>` - Atualizar lead
- `DELETE /api/leads/<id>` - Deletar lead

### Configurações
- `GET /api/leads-config` - Obter configuração do formulário
- `PUT /api/leads-config` - Atualizar configuração

---

## 💾 Persistência de Dados

### Banco de Dados SQLite
- **Usuários**: Tabela `users` com id, name, email, password_hash, role

### Arquivos JSON
- **Médicos**: `data/doctors.json`
- **Leads**: `data/leads.json`
- **Configuração de Formulário**: `data/leads_config.json`

### LocalStorage (Frontend)
- `painelKanbanData` - Dados do Kanban painel
- `comercialKanbanData` - Dados do Kanban comercial
- `financeiroKanbanData` - Dados do Kanban financeiro
- `judicialKanbanData` - Dados do Kanban judicial
- `importacaoKanbanData` - Dados do Kanban importação
- `iaKanbanData` - Dados do Kanban IA
- `gestaoMedicosKanbanData` - Dados do Kanban gestão médicos
- `adminModulesOrder` - Ordem dos módulos administrativos
- `adminModulesData` - Dados dos módulos administrativos
- `kanbanViewMode` - Modo de visualização (vertical/horizontal)

---

## 🔒 Segurança

✓ Senhas com hash (Werkzeug)  
✓ Validação de força de senha (8+ chars, maiúscula, minúscula, número)  
✓ Sessão segura com secret key  
✓ CSRF protection com session tokens  
✓ Validação de entrada no backend  

---

## 📱 Responsividade

- ✓ Desktop (1920x1080 e maiores)
- ✓ Laptop (1366x768)
- ✓ Tablet (768px)
- ✓ Mobile (480px)

---

## 🎨 Temas de Cores

| Cor | Hex | Uso |
|-----|-----|-----|
| Verde Medicinal | #0E4D42 | Principal |
| Verde Sálvia | #4A7A6A | Secundário |
| Violeta Calmante | #5E35B1 | Destaque |
| Azul Petróleo | #00897B | Destaque |
| Magenta Terapêutico | #D81B60 | Ações |

---

## 🧪 Testes

Para testar o Kanban com criação/renomeação/exclusão de colunas:
```
http://localhost:5000/?runSelfTest=true
```

Para testar todos os módulos:
```
http://localhost:5000/?runSelfTestAll=true
```

---

## 📝 Fluxos de Uso

### 1. Gestor Comercial - Criar Lead
1. Administrativo → Gestão Comercial
2. Clicar "Novo Lead"
3. Preencher: Responsável e Fonte
4. Link é gerado e copiado
5. Enviar ao paciente

### 2. Paciente - Preencher Formulário
1. Receber link: `http://localhost:5000?registerPaciente=0001`
2. Responder uma pergunta por vez
3. Navegar com Próximo/Anterior/Pular
4. Completar e ver confirmação

### 3. Médico - Cadastro
1. Acessar: `http://localhost:5000?registerMedico=true`
2. Preencher formulário completo
3. Upload de foto e documentos
4. Cadastro salvo e card criado

### 4. Administrador - Gerenciar Campos
1. Administrativo → IA
2. Clicar "Gerenciar Campos do Formulário"
3. Deletar/Adicionar campos
4. Mudanças salvas automaticamente

---

## ⚙️ Variáveis de Ambiente

```bash
# Secret key para sessão
export ON_MEDICINA_SECRET="seu-secret-aqui"
```

---

## 📞 Suporte

**Plataforma:** ON Medicina Internacional  
**Versão:** 2.0  
**Desenvolvido com:** Flask, SQLite, HTML5, CSS3, JavaScript

---

## 📋 Checklist de Funcionalidades

- [x] Autenticação e sessão
- [x] Painel Kanban principal
- [x] Gestão comercial (leads)
- [x] Formulário progressivo
- [x] Gestão de médicos
- [x] Kanban financeiro
- [x] Kanban judicial
- [x] Kanban importação
- [x] Kanban IA
- [x] Gerenciar campos
- [x] Kanban administrativo
- [x] Configurações do sistema
- [x] Responsividade
- [x] Persistência de dados
- [x] Upload de documentos
- [x] Drag & drop
- [x] LocalStorage
- [x] UI/UX moderna

✓ **Plataforma 100% funcional!**
