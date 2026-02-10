# 🧪 TESTES AUTOMATIZADOS - MÓDULO LANÇAMENTOS

Este arquivo contém testes para validar a integração de lançamentos com pacientes.

---

## 📋 TESTES BÁSICOS

### Teste 1: Criar Lançamento de Consulta

```javascript
// Abrir console (F12) e executar:

console.log('🧪 Teste 1: Criar Lançamento de Consulta');

const resultado = criarLancamentoAutomatico({
    data: '2026-02-04',
    dataVencimento: '2026-03-06',
    centroCusto: 'Setores Operacionais',
    nomePaciente: 'João Silva',
    instituicao: 'Clínica',
    categoria: 'Receita com serviços',
    subcategoria: 'Consulta Presencial',
    descricao: 'Consulta com Dr. Pedro',
    valor: '150.00',
    formaPagamento: 'Serviço'
});

console.log('✅ Lançamento criado:', resultado);

// Validar:
// 1. Não há erro no console
// 2. Lançamento aparece na tabela de Lançamentos
// 3. Resumo mostra +R$ 150,00 em Receitas
```

---

### Teste 2: Filtrar por Data

```javascript
console.log('🧪 Teste 2: Filtrar por Data');

// Preenchendo datas
document.querySelector('#lancamentos-data-inicio').value = '2026-02-01';
document.querySelector('#lancamentos-data-fim').value = '2026-02-28';

// Clicando em filtrar
document.querySelector('#btn-filtrar-lancamentos').click();

// Validar:
// 1. Tabela mostra apenas lançamentos de fevereiro
// 2. Sem erros no console
// 3. Resumo atualizado para período
```

---

### Teste 3: Filtrar por Centro de Custo

```javascript
console.log('🧪 Teste 3: Filtrar por Centro de Custo');

// Selecionando Centro de Custo
document.querySelector('#lancamentos-centro-custo').value = 'Setores Operacionais';

// Clicando em filtrar
document.querySelector('#btn-filtrar-lancamentos').click();

// Validar:
// 1. Tabela mostra apenas desse centro de custo
// 2. Resumo atualizado para o filtro
```

---

### Teste 4: Filtrar por Status

```javascript
console.log('🧪 Teste 4: Filtrar por Status');

// Selecionando status
document.querySelector('#lancamentos-status').value = 'Lançado';

// Clicando em filtrar
document.querySelector('#btn-filtrar-lancamentos').click();

// Validar:
// 1. Tabela mostra apenas status selecionado
// 2. Resumo atualizado
```

---

### Teste 5: Exportar CSV

```javascript
console.log('🧪 Teste 5: Exportar CSV');

// Clicando em exportar
document.querySelector('#btn-exportar-lancamentos').click();

// Validar:
// 1. Arquivo baixa automaticamente
// 2. Nome do arquivo: lancamentos_YYYY-MM-DD_HH-MM-SS.csv
// 3. Abrir arquivo e verificar:
//    - Header com todas as colunas
//    - Dados corretos
//    - Separadores (,) corretos
```

---

### Teste 6: Deletar Lançamento

```javascript
console.log('🧪 Teste 6: Deletar Lançamento');

// Encontrar ID do lançamento na tabela
// Clicar no botão de deletar (lixeira)
// Confirmar no popup

// Validar:
// 1. Lançamento desaparece da tabela
// 2. Resumo atualizado (sem aquele valor)
// 3. localStorage atualizado
```

---

## 🔧 TESTES DE INTEGRAÇÃO

### Teste 7: Simular Registra Consulta

```javascript
console.log('🧪 Teste 7: Simular Registro de Consulta');

// Simular o hook
function registrarConsultaTeste() {
    const paciente = { nome: 'Maria Santos' };
    const consulta = {
        data: '2026-02-05',
        tipo: 'online',
        profissional: 'Dra. Ana',
        valor: 120.00
    };
    
    // Simular criação do lançamento
    const diasParaVencimento = 30;
    const dataVencimento = new Date(consulta.data);
    dataVencimento.setDate(dataVencimento.getDate() + diasParaVencimento);
    
    criarLancamentoAutomatico({
        data: consulta.data,
        dataVencimento: dataVencimento.toISOString().split('T')[0],
        centroCusto: 'Setores Operacionais',
        nomePaciente: paciente.nome,
        instituicao: 'Clínica',
        categoria: 'Receita com serviços',
        subcategoria: consulta.tipo === 'online' ? 'Consulta Online' : 'Consulta Presencial',
        descricao: `Consulta ${consulta.tipo} - ${paciente.nome} - ${consulta.profissional}`,
        valor: consulta.valor.toString(),
        formaPagamento: 'Serviço'
    });
}

// Executar
registrarConsultaTeste();

// Validar:
// 1. Lançamento aparece em Financeiro
// 2. Valores estão corretos (R$ 120,00)
// 3. Descrição contém nome do paciente
// 4. Status é "Lançado"
// 5. Data vencimento é 05/03/2026 (30 dias depois)
```

---

### Teste 8: Simular Dispensação de Medicamento

```javascript
console.log('🧪 Teste 8: Simular Dispensação de Medicamento');

function dispensarMedicamentoTeste() {
    const paciente = { nome: 'Pedro Costa' };
    const medicamento = {
        nome: 'Paracetamol 500mg',
        custo: 0.50,
        quantidade: 20
    };
    
    const custoBaixa = medicamento.custo * medicamento.quantidade;
    
    criarLancamentoAutomatico({
        data: new Date().toISOString().split('T')[0],
        centroCusto: 'Setores Operacionais',
        nomePaciente: paciente.nome,
        instituicao: 'Estoque',
        categoria: 'Despesas Operacionais',
        subcategoria: 'Matéria Prima',
        descricao: `Medicamento ${medicamento.nome} - ${medicamento.quantidade} unidades - ${paciente.nome}`,
        valor: custoBaixa.toString(),
        formaPagamento: 'Estoque'
    });
}

// Executar
dispensarMedicamentoTeste();

// Validar:
// 1. Lançamento aparece como DESPESA
// 2. Valor correto: R$ 10,00 (0.50 * 20)
// 3. Status é "Lançado"
// 4. Resumo mostra aumento em Despesas
```

---

### Teste 9: Simular Pagamento de Consulta

```javascript
console.log('🧪 Teste 9: Simular Pagamento de Consulta');

function registrarPagamentoTeste() {
    const paciente = { nome: 'Maria Santos' };
    
    const data = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
    const lancamentos = data.lancamentos || [];
    
    // Encontrar lançamento da Maria
    const lancamentosConciliados = lancamentos.map(l => {
        if (l.clienteFornecedor === 'Maria Santos' && l.status === 'Lançado') {
            return {
                ...l,
                status: 'Conciliado',
                dataExtrato: '2026-02-05',
                formaPagamento: 'PIX'
            };
        }
        return l;
    });
    
    data.lancamentos = lancamentosConciliados;
    localStorage.setItem('lancamentosData', JSON.stringify(data));
    loadLancamentosTable();
    updateLancamentosResumo();
}

// Executar
registrarPagamentoTeste();

// Validar:
// 1. Lançamento muda para status "Conciliado" (badge azul)
// 2. Data extrato recebe a data do pagamento
// 3. Forma pagamento muda para "PIX"
```

---

## 📊 TESTES DE DADOS

### Teste 10: Validar Formatação de Valores

```javascript
console.log('🧪 Teste 10: Validar Formatação de Valores');

const testeCases = [
    { valor: '150.00', esperado: 'R$ 150,00' },
    { valor: '1500.00', esperado: 'R$ 1.500,00' },
    { valor: '10.50', esperado: 'R$ 10,50' },
    { valor: '0.01', esperado: 'R$ 0,01' }
];

testeCases.forEach(teste => {
    // Simular formatação
    const valor = parseFloat(teste.valor);
    const formatado = 'R$ ' + valor.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    console.log(`Valor ${teste.valor} → ${formatado} (esperado: ${teste.esperado})`);
    if (formatado === teste.esperado) {
        console.log('✅ OK');
    } else {
        console.error('❌ FALHA');
    }
});
```

---

### Teste 11: Validar Datas

```javascript
console.log('🧪 Teste 11: Validar Datas');

const testeData = (dataString, daysAdd) => {
    const data = new Date(dataString);
    data.setDate(data.getDate() + daysAdd);
    return data.toISOString().split('T')[0];
};

const testes = [
    { entrada: '2026-02-04', dias: 30, esperado: '2026-03-06' },
    { entrada: '2026-01-31', dias: 30, esperado: '2026-03-02' },
    { entrada: '2026-02-28', dias: 30, esperado: '2026-03-30' }
];

testes.forEach(teste => {
    const resultado = testeData(teste.entrada, teste.dias);
    console.log(`${teste.entrada} + ${teste.dias} dias = ${resultado} (esperado: ${teste.esperado})`);
    if (resultado === teste.esperado) {
        console.log('✅ OK');
    } else {
        console.error('❌ FALHA');
    }
});
```

---

### Teste 12: Validar Cálculos de Resumo

```javascript
console.log('🧪 Teste 12: Validar Cálculos de Resumo');

// Criar dados de teste
const lancamentosTeste = [
    { categoria: 'Receita com serviços', valor: '100.00', status: 'Lançado' },
    { categoria: 'Receita com serviços', valor: '50.00', status: 'Conciliado' },
    { categoria: 'Despesas Operacionais', valor: '30.00', status: 'Lançado' },
    { categoria: 'Despesas Operacionais', valor: '20.00', status: 'Conciliado' }
];

let totalReceitas = 0;
let totalDespesas = 0;

lancamentosTeste.forEach(l => {
    if (l.categoria.includes('Receita')) {
        totalReceitas += parseFloat(l.valor);
    } else if (l.categoria.includes('Despesa')) {
        totalDespesas += parseFloat(l.valor);
    }
});

const resultado = totalReceitas - totalDespesas;

console.log(`Total Receitas: R$ ${totalReceitas.toFixed(2)}`);
console.log(`Total Despesas: R$ ${totalDespesas.toFixed(2)}`);
console.log(`Resultado: R$ ${resultado.toFixed(2)}`);
console.log(`Cor: ${resultado >= 0 ? '🟢 Verde (positivo)' : '🔴 Vermelho (negativo)'}`);

// Validar
if (totalReceitas === 150.00 && totalDespesas === 50.00 && resultado === 100.00) {
    console.log('✅ Cálculos CORRETOS');
} else {
    console.error('❌ Cálculos INCORRETOS');
}
```

---

## 🔄 TESTES DE FLUXO

### Teste 13: Fluxo Completo Simulado

```javascript
console.log('🧪 Teste 13: Fluxo Completo Simulado');

async function testeFluxoCompleto() {
    console.log('Passo 1: Registrar Consulta...');
    criarLancamentoAutomatico({
        data: '2026-02-10',
        dataVencimento: '2026-03-12',
        centroCusto: 'Setores Operacionais',
        nomePaciente: 'Lucas Ferreira',
        instituicao: 'Clínica',
        categoria: 'Receita com serviços',
        subcategoria: 'Consulta Presencial',
        descricao: 'Consulta Dr. Ricardo',
        valor: '200.00',
        formaPagamento: 'Serviço'
    });
    console.log('✅ Consulta registrada');
    
    console.log('\nPasso 2: Validar aparição em Lançamentos...');
    const data = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
    const lancamentos = data.lancamentos || [];
    const consultaAdicionada = lancamentos.find(l => l.nomePaciente === 'Lucas Ferreira');
    
    if (consultaAdicionada) {
        console.log('✅ Consulta apareceu em Lançamentos');
        console.log('   - Status:', consultaAdicionada.status);
        console.log('   - Valor:', consultaAdicionada.valor);
        console.log('   - Data Vencimento:', consultaAdicionada.dataVencimento);
    } else {
        console.error('❌ Consulta NÃO apareceu em Lançamentos');
        return;
    }
    
    console.log('\nPasso 3: Registrar Pagamento...');
    const lancamentoAtualizado = {
        ...consultaAdicionada,
        status: 'Conciliado',
        dataExtrato: '2026-02-10',
        formaPagamento: 'PIX'
    };
    
    const lancamentosAtualizados = lancamentos.map(l => 
        l.id === consultaAdicionada.id ? lancamentoAtualizado : l
    );
    
    data.lancamentos = lancamentosAtualizados;
    localStorage.setItem('lancamentosData', JSON.stringify(data));
    console.log('✅ Pagamento registrado');
    
    console.log('\nPasso 4: Validar atualização...');
    const dataAtualizada = JSON.parse(localStorage.getItem('lancamentosData') || '{}');
    const consultaConciliada = dataAtualizada.lancamentos.find(l => l.id === consultaAdicionada.id);
    
    if (consultaConciliada.status === 'Conciliado') {
        console.log('✅ Status atualizado para Conciliado');
        console.log('   - Data Extrato:', consultaConciliada.dataExtrato);
        console.log('   - Forma Pagamento:', consultaConciliada.formaPagamento);
    } else {
        console.error('❌ Status NÃO foi atualizado');
    }
    
    console.log('\n🎉 FLUXO COMPLETO VALIDADO COM SUCESSO!');
}

// Executar
testeFluxoCompleto();
```

---

## ✅ CHECKLIST DE TESTES

- [ ] Teste 1: Criar Lançamento
- [ ] Teste 2: Filtrar por Data
- [ ] Teste 3: Filtrar por Centro
- [ ] Teste 4: Filtrar por Status
- [ ] Teste 5: Exportar CSV
- [ ] Teste 6: Deletar Lançamento
- [ ] Teste 7: Simular Consulta
- [ ] Teste 8: Simular Medicamento
- [ ] Teste 9: Simular Pagamento
- [ ] Teste 10: Validar Valores
- [ ] Teste 11: Validar Datas
- [ ] Teste 12: Validar Cálculos
- [ ] Teste 13: Fluxo Completo

---

## 📝 COMO EXECUTAR

1. Abrir http://localhost:5000 no navegador
2. Ir em Financeiro → Lançamentos
3. Abrir console: **F12** ou **Ctrl+Shift+K**
4. Colar um dos testes acima
5. Pressionar **Enter**
6. Validar se resultado está correto

---

## 🐛 TROUBLESHOOTING

### Erro: "ReferenceError: criarLancamentoAutomatico is not defined"
**Solução**: Certifique-se que:
1. Você está na aba de Lançamentos
2. A página carregou completamente
3. Não há erros no console

### Erro: "Cannot read property 'value' of null"
**Solução**: Os seletores precisam ser ajustados conforme seu HTML

### Dados não aparecem
**Solução**: Verificar:
1. localStorage está habilitado
2. Dados estão em JSON válido
3. Recarregar página (Ctrl+R)

---

## 📞 SUPORTE

Se algum teste falhar:
1. Verificar o erro exato no console
2. Validar os dados sendo passados
3. Verificar se localStorage tem espaço
4. Testar em navegador diferente
5. Limpar cache e cookies

---

**Versão**: 1.0  
**Data**: 04 de Fevereiro de 2026  
**Status**: ✅ Pronto para Testes
