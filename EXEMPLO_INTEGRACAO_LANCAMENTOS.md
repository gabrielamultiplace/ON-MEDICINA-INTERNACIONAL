# 🔗 EXEMPLO PRÁTICO DE INTEGRAÇÃO

## Hooks para Sistema de Pacientes

Este arquivo contém os hooks de integração que devem ser adicionados ao sistema de pacientes quando forem registrar atividades.

---

## 1️⃣ HOOK PARA CONSULTA

Quando paciente registra uma consulta, adicione este código:

```javascript
// Em: sistema_pacientes.js (função de consulta)
// ===================================================

async function registrarConsulta(paciente, consultaData) {
    try {
        // ... código original de registro da consulta ...
        
        // 🎯 NOVO: Criar lançamento automático de receita
        const diasParaVencimento = 30;
        const dataVencimento = new Date(consultaData.data);
        dataVencimento.setDate(dataVencimento.getDate() + diasParaVencimento);
        
        const dadosLancamento = {
            data: consultaData.data,
            dataVencimento: dataVencimento.toISOString().split('T')[0],
            centroCusto: consultaData.tipo === 'online' ? 'Setores Operacionais' : 'Setores Operacionais',
            nomePaciente: paciente.nome,
            instituicao: 'Clínica',
            categoria: 'Receita com serviços',
            subcategoria: consultaData.tipo === 'online' ? 'Consulta Online' : 'Consulta Presencial',
            descricao: `Consulta ${consultaData.tipo === 'online' ? 'Online' : 'Presencial'} - ${paciente.nome} - Dr(a). ${consultaData.profissional}`,
            valor: consultaData.valor.toString(),
            formaPagamento: 'Serviço',
            statusPaciente: 'Ativo'
        };
        
        // Chamar função de automação
        if (typeof criarLancamentoAutomatico === 'function') {
            criarLancamentoAutomatico(dadosLancamento);
            console.log('✅ Lançamento automático criado para consulta');
        }
        
        return { sucesso: true, mensagem: 'Consulta registrada e lançada automaticamente' };
        
    } catch (erro) {
        console.error('❌ Erro ao registrar consulta:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

### Exemplo de Chamada

```javascript
// Quando usuário submete formulário de consulta
const consulta = {
    data: '2026-02-04',
    tipo: 'presencial', // ou 'online'
    profissional: 'Dr. João Silva',
    valor: 150.00,
    duracao: 30 // minutos
};

registrarConsulta(paciente, consulta);
```

---

## 2️⃣ HOOK PARA DISPENSAÇÃO DE MEDICAMENTO

Quando medicamento é dispensado ao paciente:

```javascript
// Em: sistema_estoque.js (função de dispensação)
// ===================================================

async function dispensarMedicamento(paciente, medicamento, quantidade) {
    try {
        // ... código original de dispensação ...
        
        // 🎯 NOVO: Criar lançamento automático de despesa
        const custoBaixa = medicamento.custo * quantidade;
        
        const dadosLancamento = {
            data: new Date().toISOString().split('T')[0],
            centroCusto: 'Setores Operacionais',
            nomePaciente: paciente.nome,
            instituicao: 'Estoque',
            categoria: 'Despesas Operacionais',
            subcategoria: 'Matéria Prima',
            descricao: `Medicamento ${medicamento.nome} - ${quantidade} unidades - Paciente ${paciente.nome}`,
            valor: custoBaixa.toString(),
            formaPagamento: 'Estoque'
        };
        
        // Chamar função de automação
        if (typeof criarLancamentoAutomatico === 'function') {
            criarLancamentoAutomatico(dadosLancamento);
            console.log('✅ Lançamento automático criado para medicamento');
        }
        
        return { sucesso: true, mensagem: 'Medicamento dispensado e lançado' };
        
    } catch (erro) {
        console.error('❌ Erro ao dispensar medicamento:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

### Exemplo de Chamada

```javascript
const medicamento = {
    nome: 'Amoxicilina 500mg',
    custo: 0.50,
    quantidade: 10
};

dispensarMedicamento(paciente, medicamento, 10);
```

---

## 3️⃣ HOOK PARA PAGAMENTO

Quando paciente efetua pagamento:

```javascript
// Em: sistema_pacientes.js (função de pagamento)
// ===================================================

async function registrarPagamentoPaciente(paciente, pagamentoData) {
    try {
        // ... código original de pagamento ...
        
        // 🎯 NOVO: Atualizar lançamentos relacionados
        const data = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
        const lancamentos = data.lancamentos || [];
        
        // Encontrar lançamentos pendentes deste paciente
        const lancamentosConciliados = lancamentos.map(l => {
            if (l.clienteFornecedor === paciente.nome && l.status === 'Lançado') {
                return {
                    ...l,
                    status: 'Conciliado',
                    dataExtrato: pagamentoData.data,
                    formaPagamento: pagamentoData.metodo
                };
            }
            return l;
        });
        
        // Atualizar localStorage
        data.lancamentos = lancamentosConciliados;
        localStorage.setItem('lancamentosData', JSON.stringify(data));
        
        // Atualizar interface
        if (typeof loadLancamentosTable === 'function') {
            loadLancamentosTable();
            updateLancamentosResumo();
        }
        
        console.log('✅ Pagamento registrado e lançamentos conciliados');
        return { sucesso: true, mensagem: 'Pagamento processado' };
        
    } catch (erro) {
        console.error('❌ Erro ao registrar pagamento:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

### Exemplo de Chamada

```javascript
const pagamento = {
    data: '2026-02-04',
    metodo: 'PIX',
    valor: 150.00,
    referencia: 'PIX-ABC123'
};

registrarPagamentoPaciente(paciente, pagamento);
```

---

## 4️⃣ HOOK PARA PLANO/PACOTE

Quando paciente adquire plano fidelidade:

```javascript
// Em: sistema_pacientes.js (função de plano)
// ===================================================

async function adquirirPlatoFidelidade(paciente, planoData) {
    try {
        // ... código original de plano ...
        
        // 🎯 NOVO: Criar lançamento automático de receita
        const dadosLancamento = {
            data: new Date().toISOString().split('T')[0],
            dataVencimento: new Date(new Date().setDate(new Date().getDate() + 30)).toISOString().split('T')[0],
            centroCusto: 'Setores Operacionais',
            nomePaciente: paciente.nome,
            instituicao: 'Clínica',
            categoria: 'Receita com serviços',
            subcategoria: 'Plano Fidelidade',
            descricao: `Plano Fidelidade ${planoData.tipo} - ${paciente.nome}`,
            valor: planoData.valor.toString(),
            formaPagamento: planoData.metodo || 'Cartão Crédito'
        };
        
        if (typeof criarLancamentoAutomatico === 'function') {
            criarLancamentoAutomatico(dadosLancamento);
            console.log('✅ Lançamento automático criado para plano');
        }
        
        return { sucesso: true, mensagem: 'Plano adquirido e lançado' };
        
    } catch (erro) {
        console.error('❌ Erro ao adquirir plano:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

---

## 5️⃣ HOOK PARA PRODUTO

Quando paciente compra produto:

```javascript
// Em: sistema_loja.js (função de venda)
// ===================================================

async function venderProduto(paciente, produtoData) {
    try {
        // ... código original de venda ...
        
        // 🎯 NOVO: Criar lançamento automático de receita
        const dadosLancamento = {
            data: new Date().toISOString().split('T')[0],
            centroCusto: 'Setores Operacionais',
            nomePaciente: paciente.nome,
            instituicao: 'Loja',
            categoria: 'Receita com produtos',
            subcategoria: produtoData.categoria, // Ex: 'Fitorerapico'
            descricao: `Produto ${produtoData.nome} - ${paciente.nome}`,
            valor: produtoData.valor.toString(),
            formaPagamento: produtoData.metodo || 'Cartão Débito'
        };
        
        if (typeof criarLancamentoAutomatico === 'function') {
            criarLancamentoAutomatico(dadosLancamento);
            console.log('✅ Lançamento automático criado para venda');
        }
        
        return { sucesso: true, mensagem: 'Produto vendido e lançado' };
        
    } catch (erro) {
        console.error('❌ Erro ao vender produto:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

---

## 🔐 FUNÇÃO AUXILIAR: Adicionar Dias

```javascript
// Usar em qualquer hook que precise calcular data futura
function adicionarDias(data, dias) {
    const resultado = new Date(data);
    resultado.setDate(resultado.getDate() + dias);
    return resultado;
}

// Exemplos de uso:
const amanha = adicionarDias(new Date(), 1);
const em30dias = adicionarDias(new Date(), 30);
const em90dias = adicionarDias(new Date(), 90);
```

---

## ✅ CHECKLIST DE INTEGRAÇÃO

Para cada módulo que quiser integrar:

- [ ] Copiar hook correspondente
- [ ] Adicionar ao arquivo JavaScript correto
- [ ] Testar com dados de exemplo
- [ ] Verificar se lançamento aparece em Financeiro
- [ ] Verificar se resumo é atualizado
- [ ] Validar valores e datas
- [ ] Testar com localStorage limpo
- [ ] Testar export CSV
- [ ] Documentar qualquer customização
- [ ] Treinar usuários

---

## 🎯 TESTE RÁPIDO

Para testar a integração sem sistema de pacientes:

```javascript
// Abrir console (F12) e executar:

criarLancamentoAutomatico({
    data: '2026-02-04',
    dataVencimento: '2026-03-06',
    centroCusto: 'Setores Operacionais',
    nomePaciente: 'João da Silva',
    instituicao: 'Clínica',
    categoria: 'Receita com serviços',
    subcategoria: 'Consulta Presencial',
    descricao: 'Consulta de teste',
    valor: '150.00',
    formaPagamento: 'Serviço'
});

// Verificar se apareceu em Lançamentos
// Fazer Ctrl+Shift+K para abrir Financeiro
```

---

## 🔄 FLUXO COMPLETO DE EXEMPLO

```
1. Paciente "Maria Silva" marca consulta para 04/02/2026
   └─→ registrarConsulta() é chamada
       └─→ criarLancamentoAutomatico() é chamada
           └─→ Lançamento aparece em Financeiro como "Lançado"

2. Maria paga com PIX na clínica
   └─→ registrarPagamentoPaciente() é chamada
       └─→ Lançamento muda para "Conciliado"
           └─→ Data extrato recebe 04/02/2026
               └─→ Forma pagamento muda para "PIX"

3. Gerente verifica Financeiro
   └─→ Vê todas as transações automáticas
       └─→ Pode exportar para análise
           └─→ Pode filtrar por paciente
               └─→ Dados sempre consistentes e auditáveis
```

---

## 📞 TROUBLESHOOTING DE INTEGRAÇÃO

### P: "Função criarLancamentoAutomatico não encontrada"
**R**: Certifique-se que:
1. index.html está carregado
2. Função está em `<script>` do index.html
3. Não há erro de console (F12 → Console)

### P: "localStorage não está funcionando"
**R**: Verificar:
1. Navegador permite localStorage
2. Não está em navegação privada
3. Cotas de storage não excedidas

### P: "Lançamento não aparece"
**R**: Verificar:
1. Dados estão em JSON válido
2. Valores são strings numéricas
3. Datas estão em formato YYYY-MM-DD
4. Categorias existem no sistema

### P: "Valores incorretos"
**R**: Verificar:
1. Valor é string, não número
2. Conversões de tipo (JSON)
3. Operações matemáticas

---

## 📝 TEMPLATE DE NOVO HOOK

```javascript
async function novaOperacao(paciente, dados) {
    try {
        // ... código original ...
        
        // 🎯 NOVO: Criar lançamento automático
        const dadosLancamento = {
            data: new Date().toISOString().split('T')[0],
            centroCusto: 'SELECIONAR',
            nomePaciente: paciente.nome,
            instituicao: 'SELECIONAR',
            categoria: 'SELECIONAR', // Receita ou Despesa
            subcategoria: 'SELECIONAR',
            descricao: 'DESCREVER_OPERACAO',
            valor: dados.valor.toString(),
            formaPagamento: 'SELECIONAR'
        };
        
        if (typeof criarLancamentoAutomatico === 'function') {
            criarLancamentoAutomatico(dadosLancamento);
        }
        
        return { sucesso: true };
        
    } catch (erro) {
        console.error('❌ Erro:', erro);
        return { sucesso: false, erro: erro.message };
    }
}
```

Copie este template, altere os valores em MAIÚSCULAS e está pronto!

---

**Versão**: 1.0  
**Data**: 04 de Fevereiro de 2026  
**Pronto para Uso**: ✅
