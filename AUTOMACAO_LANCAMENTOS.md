# 🤖 AUTOMAÇÃO DE LANÇAMENTOS - GUIA DE INTEGRAÇÃO

## 🎯 OBJETIVO

Automatizar a criação de lançamentos financeiros a partir de atividades de pacientes, eliminando digitação manual e garantindo consistência nos registros.

---

## 📋 FLUXO DE AUTOMAÇÃO

### 1️⃣ QUANDO UM PACIENTE FAZ UMA CONSULTA

```
Paciente registra Consulta
        ↓
Sistema detecta nova consulta
        ↓
Cria lançamento automático de RECEITA
        ↓
Preenche:
  • Data Competência: data da consulta
  • Data Vencimento: data da consulta + 30 dias
  • Centro de Custo: vinculado ao tipo de consulta
  • Cliente/Fornecedor: nome do paciente
  • Categoria: "Receita com serviços"
  • Subcategoria: tipo da consulta (Online/Presencial/etc)
  • Descrição: "Consulta de [paciente] - [tipo]"
  • Valor: preço da consulta (tabela de preços)
  • Status: "Lançado"
  • Paciente: nome do paciente
        ↓
Lançamento aparece automaticamente em Financeiro
```

### 2️⃣ QUANDO UM PACIENTE USA MEDICAMENTO

```
Medicamento dispensado ao paciente
        ↓
Sistema detecta saída de estoque
        ↓
Cria lançamento automático de DESPESA
        ↓
Preenche:
  • Data Competência: data da dispensação
  • Data Vencimento: idem
  • Centro de Custo: tipo de medicamento
  • Cliente/Fornecedor: nome do paciente
  • Categoria: "Despesas Operacionais"
  • Subcategoria: "Matéria Prima"
  • Descrição: "Medicamento [nome] - [quantidade] - [paciente]"
  • Valor: custo do medicamento
  • Status: "Lançado"
  • Paciente: nome do paciente
        ↓
Lançamento aparece automaticamente em Financeiro
```

### 3️⃣ QUANDO UM PACIENTE PAGA UMA FATURA

```
Paciente efetua pagamento
        ↓
Sistema detecta pagamento
        ↓
ATUALIZA lançamento existente
        ↓
Muda:
  • Status: "Lançado" → "Conciliado"
  • Data Extrato: data do pagamento
  • Forma de Pagamento: método utilizado
        ↓
Lançamento passa a aparecer conciliado
```

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### Passo 1: Criar Função de Integração

```javascript
// Função que será chamada quando paciente fizer atividade
function criarLancamentoAutomatico(dados) {
    const lancamento = {
        id: Date.now(),
        dataCompetencia: dados.data,
        dataVencimento: dados.dataVencimento || dados.data,
        centroCusto: dados.centroCusto,
        clienteFornecedor: dados.nomePaciente,
        instituicao: dados.instituicao || 'Consulta',
        formaPagamento: dados.formaPagamento || 'Serviço',
        categoria: dados.categoria,
        subcategoria: dados.subcategoria,
        descricao: dados.descricao,
        valor: dados.valor,
        dataExtrato: null,
        status: 'Lançado',
        paciente: dados.nomePaciente,
        autoizado: true  // Flag indicando que foi gerado automaticamente
    };

    const data = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
    if (!data.lancamentos) data.lancamentos = [];
    data.lancamentos.push(lancamento);

    localStorage.setItem('lancamentosData', JSON.stringify(data));
    loadLancamentosTable();
    updateLancamentosResumo();
}
```

### Passo 2: Integrar com Sistema de Pacientes

Quando paciente faz consulta (em `sistema_pacientes.js`):

```javascript
// Exemplo de integração no módulo de pacientes
function registrarConsultaPaciente(paciente, tipo, valor) {
    // ... código de registro da consulta ...
    
    // Criar lançamento automático
    criarLancamentoAutomatico({
        data: new Date().toISOString().split('T')[0],
        dataVencimento: adicionarDias(new Date(), 30).toISOString().split('T')[0],
        centroCusto: 'Setores Operacionais',
        nomePaciente: paciente.nome,
        instituicao: 'Clínica',
        categoria: 'Receita com serviços',
        subcategoria: tipo === 'online' ? 'Consulta Online' : 'Consulta Presencial',
        descricao: `Consulta ${tipo === 'online' ? 'Online' : 'Presencial'} - ${paciente.nome}`,
        valor: valor
    });
}
```

### Passo 3: Sincronizar com Estoque

Quando medicamento é dispensado (em `sistema_estoque.js`):

```javascript
function dispensarMedicamento(paciente, medicamento, quantidade) {
    // ... código de dispensação ...
    
    // Criar lançamento automático de despesa
    criarLancamentoAutomatico({
        data: new Date().toISOString().split('T')[0],
        centroCusto: 'Setores Operacionais',
        nomePaciente: paciente.nome,
        instituicao: 'Estoque',
        categoria: 'Despesas Operacionais',
        subcategoria: 'Matéria Prima',
        descricao: `Medicamento ${medicamento.nome} (${quantidade}) - ${paciente.nome}`,
        valor: medicamento.custoPorUnidade * quantidade
    });
}
```

---

## 📊 TABELA DE MAPEAMENTO

### Tipos de Consulta → Subcategorias

| Tipo Consulta | Subcategoria |
|---|---|
| Consulta Presencial | Consulta Presencial |
| Consulta Online | Consulta Online |
| Consulta com Nutricionista | Nutricionista |
| Consulta com Dentista | Dentista |
| Consulta Equipe | Consulta Equipe |
| Plano Fidelidade | Plano Fidelidade |

### Tipos de Produto → Subcategorias

| Produto | Categoria | Subcategoria |
|---|---|---|
| Medicamento | Despesas Operacionais | Matéria Prima |
| Vitaminas | Despesas Operacionais | Matéria Prima |
| Suplemento | Receita com produtos | Fitorerapico |
| Produto Natural | Receita com produtos | Microbiota |

### Formas de Pagamento → Automação

| Status Paciente | Forma Pagamento | Ação |
|---|---|---|
| Pagamento em dinheiro | Dinheiro | Conciliar imediatamente |
| Pagamento PIX | PIX | Conciliar em 1h |
| Pagamento Cartão | Cartão Débito | Conciliar em 1 dia |
| Pagamento Parcelado | Cartão Crédito | Criar parcelas |
| Fatura em aberto | - | Manter Pendente |

---

## 🔄 FLUXO DE CONCILIAÇÃO AUTOMÁTICA

### Regras de Conciliação

```javascript
// Função de conciliação automática
function conciliarLancamentosAutomaticos() {
    const data = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
    const lancamentos = data.lancamentos || [];

    lancamentos.forEach(lancamento => {
        if (lancamento.autorizado && lancamento.status === 'Lançado') {
            // Se foi pago em dinheiro, conciliar imediatamente
            if (lancamento.formaPagamento === 'Dinheiro') {
                lancamento.status = 'Conciliado';
                lancamento.dataExtrato = new Date().toISOString().split('T')[0];
            }
            // Se foi PIX, conciliar após 1h
            else if (lancamento.formaPagamento === 'PIX') {
                setTimeout(() => {
                    lancamento.status = 'Conciliado';
                    lancamento.dataExtrato = new Date().toISOString().split('T')[0];
                }, 3600000); // 1 hora
            }
            // Se foi cartão débito, conciliar próximo dia útil
            else if (lancamento.formaPagamento === 'Cartão Débito') {
                // ... lógica de dia útil ...
            }
        }
    });

    localStorage.setItem('lancamentosData', JSON.stringify(data));
}
```

---

## 📱 INTEGRAÇÃO COM SISTEMA ATUAL

### Modificações Necessárias

1. **Adicionar hook em registroPaciente()**
   - Quando paciente faz qualquer atividade
   - Chamar criarLancamentoAutomatico()

2. **Adicionar hook em dispensaMedicamento()**
   - Quando medicamento é removido do estoque
   - Chamar criarLancamentoAutomatico()

3. **Adicionar hook em registroPagamento()**
   - Quando paciente efetua pagamento
   - Chamar atualizarLancamento()

4. **Adicionar indicador visual**
   - Mostrar que lançamento foi gerado automaticamente
   - Flag "automatizado" na tabela

---

## 🎯 CAMPOS DINÂMICOS

### Valores que vêm do Sistema de Pacientes

```javascript
{
    // Do cadastro do paciente
    nomePaciente: paciente.nome,
    emailPaciente: paciente.email,
    telefonePaciente: paciente.telefone,
    
    // Do registro de consulta
    tipoConsulta: 'Presencial' | 'Online' | 'Equipe',
    datConsulta: consulta.data,
    duracao: consulta.duracao,
    profissional: profissional.nome,
    
    // Da tabela de preços
    valorConsulta: tabelaPrecos[tipoConsulta],
    desconto: consulta.desconto,
    
    // Do estoque
    medicamento: medicamento.nome,
    quantidadeUsada: medicamento.quantidade,
    custoBaixa: medicamento.custoPorUnidade,
    
    // Do pagamento
    dataPagamento: pagamento.data,
    metodoPagamento: pagamento.metodo,
    referenciaBancaria: pagamento.referencia
}
```

---

## 🔐 VALIDAÇÕES ANTES DE LANÇAR

```javascript
function validarDadosParaLancamento(dados) {
    const erros = [];
    
    // Validações obrigatórias
    if (!dados.nomePaciente) erros.push('Nome do paciente obrigatório');
    if (!dados.data) erros.push('Data do evento obrigatória');
    if (!dados.valor || dados.valor <= 0) erros.push('Valor deve ser maior que zero');
    if (!dados.categoria) erros.push('Categoria obrigatória');
    if (!dados.subcategoria) erros.push('Subcategoria obrigatória');
    
    // Validações de negócio
    if (dados.categoria === 'Receita' && !dados.metodoPagamento) 
        erros.push('Método de pagamento obrigatório para receitas');
    
    if (erros.length > 0) {
        console.error('Erros de validação:', erros);
        return false;
    }
    
    return true;
}
```

---

## 📈 BENEFÍCIOS DA AUTOMAÇÃO

✅ **Redução de Erros**
- Sem digitação manual
- Dados consistentes

✅ **Economia de Tempo**
- Menos digitação
- Mais tempo para análise

✅ **Rastreabilidade**
- Ligação paciente ↔ lançamento
- Auditoria facilitada

✅ **Conciliação Automática**
- Pagamentos registrados automaticamente
- Saldo atualizado em tempo real

✅ **Relatórios Precisos**
- Dados sempre atualizados
- Decisões baseadas em dados reais

---

## 🔗 INTEGRAÇÃO FUTURA

### Fase 1 (Atual)
- ✅ Estrutura de Lançamentos criada
- ✅ Interface funcional
- ⏳ Aguardando integração com pacientes

### Fase 2 (Próxima)
- ⏳ API de callback para sistema de pacientes
- ⏳ Webhooks para eventos
- ⏳ Sincronização em tempo real

### Fase 3 (Futura)
- ⏳ Inteligência Artificial para classificação
- ⏳ Previsão de receitas/despesas
- ⏳ Alertas automáticos

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Criar função criarLancamentoAutomatico()
- [ ] Integrar com registroPaciente()
- [ ] Integrar com dispensaMedicamento()
- [ ] Integrar com registroPagamento()
- [ ] Testar fluxo completo
- [ ] Implementar validações
- [ ] Adicionar logs de auditoria
- [ ] Criar documentação de API
- [ ] Treinar usuários
- [ ] Monitorar performance

---

## 🆘 TROUBLESHOOTING

### Problema: Lançamentos não aparecem
**Verificar:**
1. localStorage habilitado
2. Função criarLancamentoAutomatico() sendo chamada
3. Dados corretos sendo passados
4. Console para erros

### Problema: Valores incorretos
**Verificar:**
1. Tabela de preços atualizada
2. Cálculos de custo corretos
3. Descontos sendo aplicados

### Problema: Duplicatas de lançamentos
**Verificar:**
1. Função sendo chamada múltiplas vezes
2. Adicionar verificação de ID único
3. Implementar deduplicação

---

## 📞 SUPORTE

Para dúvidas sobre automação:
1. Verificar este guia
2. Revisar código de exemplo
3. Testar em desenvolvimento primeiro
4. Implementar em produção com cuidado

---

**Versão**: 1.0  
**Data**: 04 de Fevereiro de 2026  
**Status**: 🔄 PRONTO PARA INTEGRAÇÃO

Quando o sistema de pacientes estiver pronto, integre os hooks conforme descrito neste guia.
