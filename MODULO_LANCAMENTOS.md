# 📝 MÓDULO DE LANÇAMENTOS - DOCUMENTAÇÃO COMPLETA

## 🎯 VISÃO GERAL

O módulo de Lançamentos foi criado para permitir o registro detalhado de todas as transações financeiras (receitas e despesas), com suporte para automação futura de dados de pacientes.

---

## 📊 ESTRUTURA DA TABELA DE LANÇAMENTOS

A tabela contém as seguintes colunas (conforme anexo fornecido):

| Campo | Descrição | Tipo | Obrigatório |
|-------|-----------|------|-------------|
| **Data Competência** | Data do evento financeiro | Date | ✅ Sim |
| **Data Vencimento** | Data de vencimento da obrigação | Date | ✅ Sim |
| **Centro de Custo** | Área responsável pelo lançamento | Select | ✅ Sim |
| **Cliente/Fornecedor** | Nome de quem gerou o movimento | Text | ✅ Sim |
| **Instituição Financeira** | Banco/instituição envolvida | Select | ✅ Sim |
| **Forma de Pagamento** | Método de pagamento utilizado | Select | ✅ Sim |
| **Categoria** | Categoria contábil (Receita/Despesa) | Select | ✅ Sim |
| **Subcategoria** | Subcategoria específica | Select | ✅ Sim |
| **Descrição** | Detalhes do lançamento | Textarea | ❌ Não |
| **Valor** | Valor da transação em R$ | Number | ✅ Sim |
| **Data Extrato** | Data que apareceu no extrato | Date | ❌ Não |
| **Status** | Situação do lançamento | Select | ✅ Sim |

---

## 🚀 COMO USAR

### 1️⃣ ACESSAR LANÇAMENTOS

```
Menu → Financeiro → Lançamentos
```

### 2️⃣ NOVO LANÇAMENTO

Clique em **"+ Novo Lançamento"** para abrir o formulário.

**Campos a preencher:**

1. **Data Competência**: Quando o evento ocorreu
2. **Data Vencimento**: Quando será cobrado/pago
3. **Centro de Custo**: 
   - Produtos, serviços ou Contratos
   - Setores Operacionais
   - Setores da Administração
4. **Cliente/Fornecedor**: Nome da parte envolvida
5. **Instituição Financeira**:
   - Banco do Brasil
   - Itaú
   - Caixa
   - Dinheiro
6. **Forma de Pagamento**:
   - Dinheiro
   - Cartão Crédito
   - Cartão Débito
   - Boleto
   - PIX
   - Cheque
   - Transferência
7. **Categoria**: (escolher antes de subcategoria)
8. **Subcategoria**: (atualiza conforme categoria)
9. **Descrição**: Detalhe extra (opcional)
10. **Valor**: Montante em reais
11. **Data Extrato**: Quando apareceu no extrato (opcional)
12. **Status**: Lançado / Conciliado / Pendente

### 3️⃣ FILTRAR LANÇAMENTOS

Use os filtros para encontrar lançamentos específicos:

- **Período**: Data início até data fim
- **Centro de Custo**: Filtrar por departamento
- **Status**: Por situação (Lançado, Conciliado, Pendente)

Clique em **"Filtrar"** para aplicar.

### 4️⃣ EDITAR/EXCLUIR

Cada linha tem botões de ação:
- **✏️ Editar**: Modificar dados (em desenvolvimento)
- **🗑️ Excluir**: Remover lançamento com confirmação

### 5️⃣ EXPORTAR DADOS

Clique em **"Exportar"** para baixar todos os lançamentos em formato CSV.

---

## 🔄 AUTOMAÇÃO COM PACIENTES

### Integração Futura

O sistema foi preparado para receber automação de:

**Quando um paciente faz uma consulta/atendimento:**
1. Sistema cria lançamento automático de receita
2. Vincula ao paciente responsável
3. Preenche: categoria, subcategoria, valor

**Quando um paciente usa medicamentos/produtos:**
1. Sistema cria lançamento automático de despesa
2. Vincula ao estoque
3. Atualiza categorias financeiras

### Como será feito

Campo **"Paciente (Automático)"** será preenchido automaticamente quando:
- Atividade de paciente for registrada
- Produto/medicamento for dispensado
- Procedimento for cobrado

---

## 📋 CATEGORIAS E SUBCATEGORIAS

### Receitas

**Receita com Produtos:**
- Receita com mercadorias
- Fitorerapico
- Microbiota
- Mitocondria
- Mulher

**Receita com Serviços:**
- Consulta Equipe
- Consulta Online
- Consulta Presencial
- Dentista
- Nutricionista
- Plano Fidelidade
- Tricologia

### Deduções

- Descontos
- Abatimentos
- Devoluções

### Despesas

**Despesas Operacionais:**
- Pessoal
- Aluguel
- Utilidades
- Matéria Prima
- Marketing

**Despesas Administrativas:**
- Contabilidade
- Jurídico
- Consultoria
- Escritório

**Despesas Financeiras:**
- Juros
- Taxas
- Multas

---

## 💾 ARMAZENAMENTO DE DADOS

Os lançamentos são armazenados em localStorage com a chave `lancamentosData`:

```javascript
{
  "lancamentos": [
    {
      "id": 1675000000000,
      "dataCompetencia": "2025-02-04",
      "dataVencimento": "2025-02-15",
      "centroCusto": "Setores Operacionais",
      "clienteFornecedor": "Paciente João Silva",
      "instituicao": "Itaú",
      "formaPagamento": "PIX",
      "categoria": "Receita com serviços",
      "subcategoria": "Consulta Presencial",
      "descricao": "Consulta oftalmológica",
      "valor": "150.00",
      "dataExtrato": "2025-02-04",
      "status": "Lançado",
      "paciente": ""
    }
  ]
}
```

---

## 📊 RESUMO DE LANÇAMENTOS

Na parte inferior da tabela, há um resumo com:

- **Total Receitas**: Soma de todas as receitas
- **Total Despesas**: Soma de todas as despesas
- **Resultado**: Receitas - Despesas (cor verde se positivo, vermelho se negativo)

Atualiza automaticamente a cada novo lançamento.

---

## 🔗 INTEGRAÇÃO COM OUTRAS ABAS

### Dashboard
- Dados de Lançamentos alimentam os KPIs
- Totalizações aparecem nos cards

### Fluxo de Caixa
- Lançamentos "Conciliados" aparecem no fluxo
- Atualiza saldos bancários

### Plano de Contas
- Cada lançamento vincula-se a uma conta
- Facilita reconciliação

### Centros de Custo
- Identifica qual departamento gerou o movimento
- Permite análise por centro

---

## 🔐 VALIDAÇÕES

Antes de salvar, o sistema verifica:

✅ Data Competência preenchida  
✅ Centro de Custo selecionado  
✅ Categoria selecionada  
✅ Valor preenchido  
✅ Formulário sem campos obrigatórios vazios  

Se algum campo obrigatório estiver vazio, sistema avisa com mensagem.

---

## 📱 RESPONSIVIDADE

A tabela de lançamentos é totalmente responsiva:

- **Desktop**: Todas as colunas visíveis
- **Tablet**: Scroll horizontal para colunas extras
- **Mobile**: Tabela com scroll horizontal

---

## 🎨 ESTILOS

### Status Visual

Os status são exibidos com cores:

- **Lançado** 🟢 Verde - Registrado no sistema
- **Conciliado** 🔵 Azul - Confirmado no extrato
- **Pendente** 🟠 Laranja - Aguardando confirmação

### Cores

- Cabeçalho: Gradiente verde (#0E4D42 → #4A7A6A)
- Valores: Verde escuro (#0E4D42)
- Linhas alternadas: Cinza claro para legibilidade
- Hover: Fundo claro #F9FBFA

---

## 🔧 FUNÇÕES JAVASCRIPT

### Principais Funções

```javascript
// Carrega a tabela de lançamentos
loadLancamentosTable()

// Abre modal para novo lançamento
openNovoLancamentoModal()

// Salva um lançamento
saveLancamento(btn)

// Edita um lançamento (em desenvolvimento)
editLancamento(id)

// Deleta um lançamento
deleteLancamento(id)

// Filtra lançamentos por critérios
filtrarLancamentos()

// Exporta em CSV
exportarLancamentos()

// Importa de pacientes (futura automação)
importarLancamentosDePatentes()

// Atualiza resumo
updateLancamentosResumo()
```

---

## 📈 EXEMPLO DE USO

### Scenario 1: Receita de Consulta

**Dados:**
- Data: 04/02/2025
- Paciente: Maria Silva
- Consulta Presencial
- Valor: R$ 150,00

**Passos:**
1. Clique "+ Novo Lançamento"
2. Preencha Data Competência: 04/02/2025
3. Cliente/Fornecedor: Maria Silva
4. Instituição: Dinheiro
5. Categoria: "Receita com serviços"
6. Subcategoria: "Consulta Presencial"
7. Descrição: "Consulta oftalmológica - Presencial"
8. Valor: 150.00
9. Status: Lançado
10. Clique "Salvar"

**Resultado:**
- Lançamento aparece na tabela
- Total Receitas aumenta em R$ 150,00
- Resultado atualiza automaticamente

### Scenario 2: Despesa de Aluguel

**Dados:**
- Data: 01/02/2025
- Aluguel escritório
- Valor: R$ 2.500,00

**Passos:**
1. Clique "+ Novo Lançamento"
2. Preencha Data Competência: 01/02/2025
3. Data Vencimento: 05/02/2025
4. Centro de Custo: "Setores da Administração"
5. Cliente/Fornecedor: Proprietário do Imóvel
6. Instituição: Banco do Brasil
7. Forma Pagamento: Transferência
8. Categoria: "Despesas Operacionais"
9. Subcategoria: "Aluguel"
10. Descrição: "Aluguel mensal - Fevereiro"
11. Valor: 2500.00
12. Status: Lançado
13. Clique "Salvar"

**Resultado:**
- Lançamento aparece na tabela
- Total Despesas aumenta em R$ 2.500,00
- Resultado fica negativo (red)

---

## 🆘 PROBLEMAS COMUNS

### Problema: "Subcategoria não aparece"
**Solução:** Selecione Categoria primeiro, depois Subcategoria

### Problema: "Dados sumiram após recarregar página"
**Solução:** localStorage está sendo usado. Verificar se está habilitado

### Problema: "Não consigo excluir um lançamento"
**Solução:** Deve clicar ok na confirmação

### Problema: "Exportar não funciona"
**Solução:** Verificar se há lançamentos para exportar

---

## 📝 PRÓXIMAS FUNCIONALIDADES

- [ ] Edição de lançamentos
- [ ] Importação automática de pacientes
- [ ] Sincronização com Asaas
- [ ] Relatório de lançamentos por período
- [ ] Análise de tendências
- [ ] Integração com estoque
- [ ] Webhooks para automação

---

## 🔗 RELACIONADOS

- [Centro de Custo](CENTRO_CUSTO_PLANO_CONTAS_IMPLEMENTADO.md)
- [Plano de Contas](CENTRO_CUSTO_PLANO_CONTAS_IMPLEMENTADO.md)
- [Fluxo de Caixa](README_IMPLEMENTACAO_FINAL.md)
- [Dashboard Financeiro](README_IMPLEMENTACAO_FINAL.md)

---

**Versão**: 1.0  
**Data**: 04 de Fevereiro de 2026  
**Status**: ✅ PRONTO PARA USO

Para mais informações, acesse o módulo em: **Financeiro → Lançamentos**
